import os
import json
import logging
from typing import Dict, List, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class LlamaAnalyzer:
    """
    Interfaces with Meta Llama via Cerebras API for medical document analysis
    """

    def __init__(self):
        # Don't raise here so the app can start without the key; check before calls instead
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        if not self.api_key:
            logger.warning("CEREBRAS_API_KEY is not set; LlamaAnalyzer will be disabled until configured.")

        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        self.model = "llama3.1-8b"  # Cerebras supports: llama3.1-8b, llama3.1-70b (if you have access)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json"
        }

    async def _call_llama(self, messages: List[Dict], temperature: float = 0.3) -> str:
        """
        Make API call to Cerebras/Llama. Raises RuntimeError if API key is missing.
        """
        if not self.api_key:
            raise RuntimeError("Cerebras API key not configured")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:  # Increased timeout for large responses
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 32000,  # Doubled to 32k to handle very large lab reports (50+ tests)
                    "top_p": 1.0,  # Use full probability distribution (no sampling truncation)
                    "seed": 12345  # Fixed seed for deterministic responses
                }

                response = await client.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()

                result = response.json()
                # Defensive parsing
                if not result:
                    raise RuntimeError("Empty response from Llama API")

                # Check if response was truncated
                if "choices" in result and len(result["choices"]) > 0:
                    finish_reason = result["choices"][0].get("finish_reason")
                    if finish_reason == "length":
                        logger.warning("⚠️  AI response was TRUNCATED due to max_tokens limit!")
                        logger.warning(f"   Consider increasing max_tokens beyond 16000")
                    
                    # Log token usage for debugging
                    if "usage" in result:
                        usage = result["usage"]
                        logger.info(f"📊 Token usage: prompt={usage.get('prompt_tokens')}, completion={usage.get('completion_tokens')}, total={usage.get('total_tokens')}")

                # Some APIs nest choices differently; try common shapes
                try:
                    return result["choices"][0]["message"]["content"]
                except Exception:
                    # fallback: try top-level 'content'
                    if isinstance(result, dict) and "content" in result:
                        return result["content"]
                    raise RuntimeError("Unexpected Llama API response shape")

        except httpx.HTTPStatusError as e:
            logger.error(f"Cerebras API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Llama API call failed: {str(e)}")
            raise

    async def classify_document(self, text: str) -> str:
        """
        Classify the type of medical document
        """
        messages = [
            {
                "role": "system",
                "content": "You are a medical document classifier. Classify the document into one of these categories: Lab Results, Imaging Report, Pathology Report, Discharge Summary, Doctor's Notes, or Other. Respond with ONLY the category name."
            },
            {
                "role": "user",
                "content": f"Classify this medical document:\n\n{text[:1000]}"
            }
        ]

        classification = await self._call_llama(messages, temperature=0.1)
        return classification.strip()

    async def analyze_document(self, text: str, document_type: str,
                               patient_context: Optional[Dict] = None) -> Dict:
        """
        Main analysis: Translate medical jargon, identify findings, flag abnormalities
        """
        context_str = ""
        if patient_context:
            context_str = f"\nPatient Context: Age {patient_context.get('age', 'unknown')}, Gender {patient_context.get('gender', 'unknown')}"

        system_prompt = f"""You are a medical translator helping patients understand their health records.

DOCUMENT TYPE: {document_type}
{context_str}

EXTRACTION STRATEGY:
1. **Read the ENTIRE document from start to finish**
2. **Identify EVERY line that contains a test result** (test name + value + reference range)
3. **Count the total number of tests** before you start generating JSON
4. **Create one finding object for each and every test** - NO EXCEPTIONS

CRITICAL CLASSIFICATION RULES (STATUS FIELD):

**URGENT (🔴)** - Immediate medical attention needed:
- Value is OUTSIDE the normal range (above max OR below min)
- Borderline values at risk boundary (within 5-10% of range limits)
- Critical markers significantly elevated or depleted
- Example: B12 at 210 pg/mL (normal: 200-900) = URGENT (borderline low)
- Example: Hemoglobin 10.2 (normal: 12-16) = URGENT (below range)
- Example: Cholesterol 240 (normal: <200) = URGENT (above range)

**MONITOR (🟡)** - Watch carefully, may need intervention:
- Value is technically within range but approaching boundaries (10-20% from limits)
- Suboptimal levels that could improve
- Trending toward abnormal even if currently "normal"
- Example: B12 at 250 pg/mL (normal: 200-900) = MONITOR (low-normal, should be higher)
- Example: Vitamin D at 32 ng/mL (normal: 30-100) = MONITOR (barely adequate)
- Example: TSH at 3.8 (normal: 0.4-4.0) = MONITOR (high-normal)

**NORMAL (🟢)** - Healthy, optimal range:
- Value is comfortably within the normal range
- At least 20% away from both upper and lower limits
- No concerns or follow-up needed
- Example: B12 at 500 pg/mL (normal: 200-900) = NORMAL (middle of range)
- Example: Vitamin D at 55 ng/mL (normal: 30-100) = NORMAL (optimal)

**BE SMART ABOUT BORDERLINE VALUES:**
- Just because a value is "technically in range" doesn't mean it's healthy
- Low-normal values (near bottom of range) often need attention
- High-normal values (near top of range) can indicate early problems
- Context matters: B12 at 210 is technically normal but functionally deficient
- When in doubt between NORMAL and MONITOR, choose MONITOR for patient safety

TASK FOR EACH TEST:
- Provide plain English explanation (8th grade reading level, 1-2 sentences max)
- State the normal range and patient's value
- **Classify intelligently using the rules above** - don't just check if in range!
- Explain clinical significance (1 sentence max)

**CRITICAL: Your findings array MUST contain the same number of items as there are test results in the document. If you see 31 tests, output 31 findings. If you see 28 tests, output 28 findings. DO NOT SKIP OR COMBINE TESTS.**

SYSTEMATIC APPROACH:
1. Scan document: COUNT all tests first
2. Generate findings: Create JSON object for each test in order
3. Classify smartly: Apply borderline logic for each value
4. Verify: Double-check your findings array length matches the count

OUTPUT EFFICIENCY RULES:
- Keep explanations CONCISE (1-2 sentences each field)
- Use simple words (8th grade level)
- Be direct and clear
- **RESPOND WITH ONLY VALID JSON - NO MARKDOWN, NO PREAMBLE, NO EXPLANATION**
- **INCLUDE ALL FINDINGS - DO NOT TRUNCATE THE LIST**

REQUIRED OUTPUT FORMAT - MUST BE VALID JSON:
{{
  "overall_summary": "2-3 sentence summary",
  "overall_status": "NORMAL|MONITOR|URGENT",
  "findings": [
    {{
      "test_name": "Vitamin B12",
      "value": "210 pg/mL",
      "normal_range": "200-900 pg/mL",
      "status": "URGENT",
      "plain_english": "Your B12 is at the very bottom of the normal range, which is borderline deficient.",
      "what_it_means": "B12 helps produce red blood cells and maintain nervous system health.",
      "clinical_significance": "Values this low can cause fatigue, weakness, and neurological symptoms even though technically 'normal'.",
      "recommendations": ["Consider B12 supplementation", "Retest in 3 months", "Discuss with doctor"]
    }}
  ],
  "urgent_findings_count": 1,
  "monitor_findings_count": 2,
  "normal_findings_count": 9
}}

YOUR RESPONSE MUST START WITH {{ AND END WITH }} - NOTHING ELSE."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this document and respond with ONLY valid JSON (no markdown, no preamble):\n\n{text}"}
        ]

        response = await self._call_llama(messages, temperature=0.0)  # Completely deterministic

        try:
            # Parse JSON response; strip markdown fences and preamble if present
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            # Sometimes LLM adds text before JSON like "Here's the analysis:"
            # Find the first { and last } to extract just the JSON
            first_brace = response.find('{')
            last_brace = response.rfind('}')
            if first_brace != -1 and last_brace != -1:
                response = response[first_brace:last_brace+1]

            # Try to close incomplete JSON if it's missing closing braces
            # This handles cases where the response was cut off mid-JSON
            if response.count('{') > response.count('}'):
                logger.warning("⚠️  Detected incomplete JSON - attempting to close it")
                # Count how many closing braces we need
                missing_closes = response.count('{') - response.count('}')
                
                # Try to close the findings array and main object
                if '"findings"' in response and not response.rstrip().endswith(']}'):
                    # Close findings array if incomplete
                    response = response.rstrip().rstrip(',') + ']'
                
                # Add remaining closing braces
                response += '}' * missing_closes
                logger.info(f"   Added {missing_closes} closing braces to complete JSON")

            analysis = json.loads(response.strip())
            
            # Validate and fix count mismatches
            findings = analysis.get('findings', [])
            findings_count = len(findings)
            
            # Recalculate counts from actual findings
            urgent_count = sum(1 for f in findings if f.get('status') == 'URGENT')
            monitor_count = sum(1 for f in findings if f.get('status') == 'MONITOR')
            normal_count = sum(1 for f in findings if f.get('status') == 'NORMAL')
            
            # Fix any count mismatches
            analysis['urgent_findings_count'] = urgent_count
            analysis['monitor_findings_count'] = monitor_count
            analysis['normal_findings_count'] = normal_count
            
            # Log the number of findings for debugging consistency
            logger.info(f"✅ Successfully extracted {findings_count} findings from analysis")
            logger.info(f"   🔴 Urgent: {urgent_count}")
            logger.info(f"   🟡 Monitor: {monitor_count}")
            logger.info(f"   🟢 Normal: {normal_count}")
            
            # Warn if the response might have been truncated
            if findings_count < 20:
                logger.warning(f"⚠️  Only {findings_count} findings extracted - PDF might have more tests!")
                logger.warning(f"   If you uploaded a comprehensive lab report, the AI response may have been truncated.")
            
            return analysis

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Llama response as JSON: {str(e)}")
            logger.error(f"Response was: {response[:500]}")
            
            # Try to salvage findings from incomplete JSON
            findings = self._extract_findings_from_incomplete_json(response)
            
            return {
                "overall_summary": "Analysis completed but formatting issue occurred.",
                "overall_status": "MONITOR",
                "findings": findings,
                "raw_response": response,
                "error": "JSON parse error - recovered findings"
            }

    def _extract_findings_from_incomplete_json(self, text: str) -> List[Dict]:
        """
        Extract findings from incomplete/malformed JSON response
        """
        import re
        findings = []
        
        try:
            # Try to find all test_name patterns and extract the finding object
            # Look for pattern: {"test_name": "...", "value": "...", ...}
            pattern = r'\{\s*"test_name":\s*"([^"]+)"[^}]*"value":\s*"([^"]*)"[^}]*"normal_range":\s*"([^"]*)"[^}]*"status":\s*"([^"]*)"[^}]*"plain_english":\s*"([^"]*)"'
            
            matches = re.finditer(pattern, text, re.DOTALL)
            
            for match in matches:
                finding = {
                    "test_name": match.group(1),
                    "value": match.group(2),
                    "normal_range": match.group(3),
                    "status": match.group(4),
                    "plain_english": match.group(5)
                }
                
                # Try to extract additional fields if present
                finding_text = text[match.start():min(match.end() + 500, len(text))]
                
                what_match = re.search(r'"what_it_means":\s*"([^"]*)"', finding_text)
                if what_match:
                    finding["what_it_means"] = what_match.group(1)
                
                sig_match = re.search(r'"clinical_significance":\s*"([^"]*)"', finding_text)
                if sig_match:
                    finding["clinical_significance"] = sig_match.group(1)
                
                rec_match = re.search(r'"recommendations":\s*\[(.*?)\]', finding_text)
                if rec_match:
                    recs = re.findall(r'"([^"]+)"', rec_match.group(1))
                    finding["recommendations"] = recs
                else:
                    finding["recommendations"] = []
                
                findings.append(finding)
            
            logger.info(f"Recovered {len(findings)} findings from incomplete JSON")
            return findings
            
        except Exception as e:
            logger.error(f"Failed to extract findings from incomplete JSON: {str(e)}")
            return []

    async def generate_questions(self, findings: List[Dict], document_type: str) -> List[Dict]:
        """
        Generate personalized questions for doctor based on findings
        """
        # Create detailed findings summary with actual values
        findings_details = []
        for f in findings:
            test_name = f.get('test_name', 'Unknown')
            value = f.get('value', 'N/A')
            normal_range = f.get('normal_range', 'N/A')
            status = f.get('status', 'NORMAL')
            plain_english = f.get('plain_english', '')
            
            findings_details.append(
                f"• {test_name}: {value} (Normal: {normal_range}) - Status: {status}\n  Meaning: {plain_english}"
            )
        
        findings_summary = "\n".join(findings_details)

        system_prompt = """You are a medical advisor helping a patient prepare specific questions for their doctor based on THEIR ACTUAL test results.

CRITICAL REQUIREMENTS:
1. Generate 3-5 questions that reference THE ACTUAL TEST VALUES from their results
2. Include specific numbers and test names from their report
3. Prioritize abnormal results (URGENT and MONITOR status) over normal ones
4. Make each question actionable and conversational
5. Focus on: treatment options, lifestyle changes, medication, follow-up testing, root causes

EXAMPLE (if Vitamin D is 18 ng/mL with normal range 30-50):
"My Vitamin D level is 18 ng/mL, which is below the normal range of 30-50. What dosage of Vitamin D supplement should I take to bring it back to normal?"

EXAMPLE (if Hemoglobin A1c is 7.2% with normal <5.7%):
"My A1c is 7.2%, which indicates prediabetes. What dietary and lifestyle changes do you recommend to lower it below 5.7%?"

RESPOND WITH ONLY VALID JSON - NO MARKDOWN, NO PREAMBLE, NO EXPLANATIONS.

REQUIRED OUTPUT FORMAT:
{{
  "questions": [
    {{
      "priority": "URGENT",
      "question": "[Question with ACTUAL test name and value from their results]",
      "category": "Treatment"
    }},
    {{
      "priority": "IMPORTANT",
      "question": "[Another specific question with actual numbers]",
      "category": "Lifestyle"
    }}
  ]
}}

Priority levels:
- URGENT: For critical/abnormal results that need immediate attention
- IMPORTANT: For values to monitor or borderline results
- FOLLOWUP: For normal results or general wellness questions

Categories: Treatment, Lifestyle, Medication, Testing, Prevention, General

YOUR RESPONSE MUST START WITH {{ AND END WITH }} - NOTHING ELSE."""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Document Type: {document_type}\n\nTest Results:\n{findings_summary}\n\nGenerate specific questions based on THESE ACTUAL VALUES. Respond with ONLY valid JSON:"
            }
        ]

        response = await self._call_llama(messages, temperature=0.3)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            # Sometimes LLM adds text before JSON; extract just the JSON object
            first_brace = response.find('{')
            last_brace = response.rfind('}')
            if first_brace != -1 and last_brace != -1:
                response = response[first_brace:last_brace+1]

            questions_data = json.loads(response.strip())
            questions = questions_data.get("questions", [])
            
            # Clean up any LLM formatting quirks where it includes "question": in the text
            for q in questions:
                if "question" in q and isinstance(q["question"], str):
                    # Remove any leading '"question": "' patterns
                    q["question"] = q["question"].replace('"question": "', '').strip('"')
                    q["question"] = q["question"].replace('",', '').strip()
            
            return questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {str(e)}")
            logger.error(f"Response was: {response[:500]}")
            return self._extract_questions_from_text(response)

    def _extract_questions_from_text(self, text: str) -> List[Dict]:
        """
        Fallback: Extract questions from unstructured text
        """
        questions = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if '?' in line and len(line) > 20:
                priority = "FOLLOWUP"
                if any(word in line.lower() for word in ['urgent', 'critical', 'immediate']):
                    priority = "URGENT"
                elif any(word in line.lower() for word in ['important', 'should', 'treatment']):
                    priority = "IMPORTANT"

                questions.append({
                    "priority": priority,
                    "question": line.lstrip('0123456789.-) '),
                    "category": "General"
                })

        return questions[:5]

    async def generate_summary(self, text: str, document_type: str) -> str:
        """
        Generate a patient-friendly summary of the entire document
        """
        messages = [
            {
                "role": "system",
                "content": "Summarize this medical document in 2-3 sentences using simple language. Focus on the key takeaways a patient needs to know."
            },
            {
                "role": "user",
                "content": f"Document Type: {document_type}\n\n{text[:2000]}"
            }
        ]

        summary = await self._call_llama(messages, temperature=0.4)
        return summary.strip()
