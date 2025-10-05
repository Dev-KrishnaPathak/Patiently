"""
Test script to verify Cerebras API is working with real analysis
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from services.llama_analyzer import LlamaAnalyzer

async def test_analysis():
    analyzer = LlamaAnalyzer()
    
    # Sample lab report text
    sample_report = """
    PATIENT: John Doe
    DATE: October 5, 2025
    
    COMPLETE BLOOD COUNT (CBC)
    WBC: 12.5 K/uL (Normal: 4.5-11.0)
    RBC: 4.2 M/uL (Normal: 4.5-5.5)
    Hemoglobin: 11.8 g/dL (Normal: 13.5-17.5)
    Platelets: 180 K/uL (Normal: 150-400)
    
    METABOLIC PANEL
    Glucose: 145 mg/dL (Normal: 70-100)
    Creatinine: 1.4 mg/dL (Normal: 0.6-1.2)
    Sodium: 138 mEq/L (Normal: 136-145)
    Potassium: 4.2 mEq/L (Normal: 3.5-5.0)
    
    LIPID PANEL
    Total Cholesterol: 240 mg/dL (Normal: <200)
    LDL: 160 mg/dL (Normal: <100)
    HDL: 38 mg/dL (Normal: >40)
    Triglycerides: 220 mg/dL (Normal: <150)
    """
    
    print("🧪 Testing Cerebras API with real medical document analysis...")
    print("=" * 60)
    
    try:
        # Test classification
        print("\n1️⃣ Testing document classification...")
        doc_type = await analyzer.classify_document(sample_report)
        print(f"✅ Document Type: {doc_type}")
        
        # Test analysis
        print("\n2️⃣ Testing medical analysis...")
        analysis = await analyzer.analyze_document(sample_report, doc_type)
        print(f"✅ Analysis completed!")
        print(f"   Overall Status: {analysis.get('overall_status', 'N/A')}")
        print(f"   Findings: {len(analysis.get('findings', []))} items")
        print(f"   Summary: {analysis.get('overall_summary', 'N/A')[:100]}...")
        
        # Show sample findings
        if analysis.get('findings'):
            print("\n📋 Sample Findings:")
            for i, finding in enumerate(analysis['findings'][:3], 1):
                print(f"\n   {i}. {finding.get('test_name', 'Unknown')}")
                print(f"      Value: {finding.get('value', 'N/A')}")
                print(f"      Status: {finding.get('status', 'N/A')}")
                print(f"      Plain English: {finding.get('plain_english', 'N/A')[:80]}...")
        
        # Test questions
        print("\n3️⃣ Testing question generation...")
        questions = await analyzer.generate_questions(analysis.get('findings', []), doc_type)
        print(f"✅ Generated {len(questions)} questions")
        if questions:
            print(f"   Example: {questions[0].get('question', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - Cerebras API is working!")
        print("🎉 Real medical analysis is ENABLED!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nCheck:")
        print("1. API key is correct in .env file")
        print("2. You have internet connection")
        print("3. Cerebras API service is available")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_analysis())
    exit(0 if success else 1)
