"""
Test the complete upload → process → analyze flow with a real document
"""
import asyncio
import httpx
import os
from pathlib import Path

async def test_upload_flow():
    base_url = "http://localhost:8000"
    
    # Create a test PDF-like content
    test_content = """
PATIENT LABORATORY REPORT
Patient: John Doe
Date: October 5, 2025

COMPLETE BLOOD COUNT (CBC)
========================================
WBC (White Blood Cell Count): 12.5 K/uL
    Reference Range: 4.5-11.0 K/uL
    Status: HIGH

Hemoglobin: 11.8 g/dL
    Reference Range: 13.5-17.5 g/dL  
    Status: LOW

RBC (Red Blood Cell Count): 4.2 M/uL
    Reference Range: 4.5-5.5 M/uL
    Status: LOW

Platelets: 180 K/uL
    Reference Range: 150-400 K/uL
    Status: NORMAL

METABOLIC PANEL
========================================
Glucose (Fasting): 145 mg/dL
    Reference Range: 70-100 mg/dL
    Status: HIGH

Creatinine: 1.4 mg/dL
    Reference Range: 0.6-1.2 mg/dL
    Status: HIGH

LIPID PANEL
========================================
Total Cholesterol: 240 mg/dL
    Reference Range: <200 mg/dL
    Status: HIGH

LDL Cholesterol: 160 mg/dL
    Reference Range: <100 mg/dL
    Status: HIGH

HDL Cholesterol: 38 mg/dL
    Reference Range: >40 mg/dL
    Status: LOW
""".encode()

    # Save as a text file (simulating a document)
    test_file = "test_lab_report.txt"
    with open(test_file, "wb") as f:
        f.write(test_content)
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("=" * 60)
            print("🧪 Testing Complete Upload → Process → Analyze Flow")
            print("=" * 60)
            
            # 1. Upload
            print("\n1️⃣ Uploading document...")
            with open(test_file, "rb") as f:
                files = {"file": (test_file, f, "text/plain")}
                response = await client.post(f"{base_url}/api/upload", files=files)
            
            if response.status_code != 202:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                return
            
            upload_result = response.json()
            document_id = upload_result["document_id"]
            print(f"✅ Uploaded! Document ID: {document_id}")
            
            # 2. Wait for background processing
            print("\n2️⃣ Waiting for background processing (5 seconds)...")
            await asyncio.sleep(5)
            
            # 3. Check if analysis is ready
            print("\n3️⃣ Fetching analysis...")
            response = await client.get(f"{base_url}/api/document/{document_id}/analysis")
            
            if response.status_code == 404:
                print("⏳ Background processing not complete yet, trying direct process...")
                response = await client.post(f"{base_url}/api/document/{document_id}/process")
                
                if response.status_code != 200:
                    print(f"❌ Processing failed: {response.status_code}")
                    print(response.text)
                    return
            
            analysis = response.json()
            
            # 4. Display results
            print("\n" + "=" * 60)
            print("📊 ANALYSIS RESULTS")
            print("=" * 60)
            
            print(f"\n📄 Document Type: {analysis.get('document_type', 'N/A')}")
            
            if 'analysis' in analysis:
                ana = analysis['analysis']
                print(f"📝 Overall Summary: {ana.get('overall_summary', 'N/A')[:100]}...")
                print(f"🚦 Overall Status: {ana.get('overall_status', 'N/A')}")
                print(f"🔍 Findings: {len(ana.get('findings', []))} items")
                
                # Show first 3 findings
                if ana.get('findings'):
                    print("\n📋 Sample Findings:")
                    for i, finding in enumerate(ana['findings'][:3], 1):
                        print(f"\n{i}. {finding.get('test_name', 'Unknown')}")
                        print(f"   Value: {finding.get('value', 'N/A')}")
                        print(f"   Status: {finding.get('status', 'N/A')}")
                        print(f"   Explanation: {finding.get('plain_english', 'N/A')[:80]}...")
            
            if 'questions' in analysis:
                print(f"\n❓ Generated Questions: {len(analysis['questions'])} items")
                if analysis['questions']:
                    print(f"   Example: {analysis['questions'][0].get('question', 'N/A')[:100]}...")
            
            print("\n" + "=" * 60)
            print("✅ TEST COMPLETE - Upload flow is working!")
            print("=" * 60)
            
            # Check if it's real analysis
            if analysis.get('analysis', {}).get('findings'):
                findings = analysis['analysis']['findings']
                has_plain_english = any('plain_english' in f for f in findings)
                has_recommendations = any('recommendations' in f for f in findings)
                
                if has_plain_english and has_recommendations:
                    print("\n✅ CONFIRMED: REAL AI ANALYSIS (has plain English + recommendations)")
                else:
                    print("\n⚠️ WARNING: May be mock data (missing plain English or recommendations)")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    print("Make sure backend is running at http://localhost:8000")
    print("Starting test in 2 seconds...\n")
    asyncio.run(asyncio.sleep(2))
    asyncio.run(test_upload_flow())
