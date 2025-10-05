"""
Script to fix existing analysis by extracting findings from raw_response
"""
import asyncio
import json
import sys
import re
from database.sqlite_db import SQLiteDatabase

def extract_findings_from_raw_response(raw_response: str):
    """
    Extract findings from the raw JSON response that got cut off
    """
    findings = []
    
    try:
        # The raw_response contains valid JSON objects for findings, just incomplete array
        # Extract each complete finding object
        pattern = r'\{\s*"test_name":\s*"([^"]+)",\s*"value":\s*"([^"]*)",\s*"normal_range":\s*"([^"]*)",\s*"status":\s*"([^"]*)",\s*"plain_english":\s*"([^"]*)",\s*"what_it_means":\s*"([^"]*)",\s*"clinical_significance":\s*"([^"]*)",\s*"recommendations":\s*\[(.*?)\]\s*\}'
        
        matches = re.finditer(pattern, raw_response, re.DOTALL)
        
        for match in matches:
            # Parse recommendations
            recs_text = match.group(8)
            recommendations = re.findall(r'"([^"]+)"', recs_text) if recs_text.strip() else []
            
            finding = {
                "test_name": match.group(1),
                "value": match.group(2),
                "normal_range": match.group(3),
                "status": match.group(4),
                "plain_english": match.group(5),
                "what_it_means": match.group(6),
                "clinical_significance": match.group(7),
                "recommendations": recommendations
            }
            findings.append(finding)
        
        print(f"✅ Extracted {len(findings)} findings from raw response")
        return findings
        
    except Exception as e:
        print(f"❌ Failed to extract findings: {str(e)}")
        return []

async def fix_analysis():
    """
    Fix the existing analysis by extracting findings from raw_response
    """
    db = SQLiteDatabase()
    await db.connect()
    
    # Get the document
    document_id = "6c5e8f4e-4a76-49d4-af3e-01aa84cf5b58"
    
    print(f"📋 Fetching analysis for document: {document_id}")
    
    # Get the analysis
    query = "SELECT analysis_data FROM analyses WHERE document_id = ?"
    cursor = db.conn.execute(query, (document_id,))
    row = cursor.fetchone()
    
    if not row:
        print(f"❌ No analysis found for document {document_id}")
        return
    
    analysis_json = row[0]
    full_data = json.loads(analysis_json)
    
    analysis = full_data.get('analysis', {})
    print(f"📊 Current findings count: {len(analysis.get('findings', []))}")
    
    raw_response = analysis.get('raw_response', '')
    if not raw_response:
        print("❌ No raw_response found in analysis")
        print(f"Available keys in analysis: {list(analysis.keys())}")
        return
    
    print(f"📄 Raw response length: {len(raw_response)} characters")
    
    # Extract findings from raw response
    findings = extract_findings_from_raw_response(raw_response)
    
    if not findings:
        print("❌ Could not extract findings from raw response")
        return
    
    # Count by status
    urgent = sum(1 for f in findings if f.get('status') == 'URGENT')
    monitor = sum(1 for f in findings if f.get('status') == 'MONITOR')
    normal = sum(1 for f in findings if f.get('status') == 'NORMAL')
    
    print(f"\n📈 Findings breakdown:")
    print(f"   🔴 URGENT: {urgent}")
    print(f"   🟡 MONITOR: {monitor}")
    print(f"   🟢 NORMAL: {normal}")
    print(f"   📊 TOTAL: {len(findings)}")
    
    # Update analysis
    full_data['analysis']['findings'] = findings
    full_data['analysis']['urgent_findings_count'] = urgent
    full_data['analysis']['monitor_findings_count'] = monitor
    full_data['analysis']['normal_findings_count'] = normal
    if 'error' in full_data['analysis']:
        del full_data['analysis']['error']  # Clear the error
    
    # Save back to database
    update_query = "UPDATE analyses SET analysis_data = ? WHERE document_id = ?"
    db.conn.execute(update_query, (json.dumps(full_data), document_id))
    db.conn.commit()
    
    print(f"\n✅ Successfully updated analysis with {len(findings)} findings!")
    print(f"\n🌐 Test it:")
    print(f"   curl http://localhost:8000/api/document/{document_id}/analysis")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(fix_analysis())
