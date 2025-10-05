"""
Test consistency of test extraction by uploading same PDF twice
"""
import asyncio
import httpx
import json
from pathlib import Path

async def test_consistency():
    base_url = "http://localhost:8000/api"
    
    # Find a PDF to test with
    pdf_path = None
    for ext in ['*.pdf']:
        pdfs = list(Path('.').rglob(ext))
        if pdfs:
            pdf_path = pdfs[0]
            break
    
    if not pdf_path:
        print("❌ No PDF files found in current directory")
        return
    
    print(f"📄 Testing with PDF: {pdf_path}")
    print(f"=" * 60)
    
    results = []
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        for i in range(2):
            print(f"\n🔄 Upload #{i+1}...")
            
            # Upload PDF
            with open(pdf_path, 'rb') as f:
                files = {'file': (pdf_path.name, f, 'application/pdf')}
                response = await client.post(f"{base_url}/upload", files=files)
            
            if response.status_code != 200:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                continue
            
            upload_result = response.json()
            document_id = upload_result.get('document_id')
            print(f"   ✅ Uploaded: {document_id}")
            
            # Wait for processing
            print(f"   ⏳ Waiting for analysis...")
            await asyncio.sleep(3)
            
            # Get analysis (with retry)
            max_retries = 10
            analysis = None
            
            for retry in range(max_retries):
                response = await client.get(f"{base_url}/document/{document_id}/analysis")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('analysis', {}).get('findings'):
                        analysis = data['analysis']
                        break
                
                print(f"   ⏳ Retry {retry+1}/{max_retries}...")
                await asyncio.sleep(2)
            
            if not analysis:
                print(f"   ❌ Analysis not ready after {max_retries} retries")
                continue
            
            findings = analysis.get('findings', [])
            findings_count = len(findings)
            
            urgent = sum(1 for f in findings if f.get('status') == 'URGENT')
            monitor = sum(1 for f in findings if f.get('status') == 'MONITOR')
            normal = sum(1 for f in findings if f.get('status') == 'NORMAL')
            
            result = {
                'upload': i+1,
                'document_id': document_id,
                'total': findings_count,
                'urgent': urgent,
                'monitor': monitor,
                'normal': normal,
                'test_names': [f.get('test_name') for f in findings]
            }
            
            results.append(result)
            
            print(f"   📊 Findings: {findings_count} total")
            print(f"      🔴 Urgent: {urgent}")
            print(f"      🟡 Monitor: {monitor}")
            print(f"      🟢 Normal: {normal}")
    
    # Compare results
    print(f"\n" + "=" * 60)
    print(f"📈 COMPARISON:")
    print(f"=" * 60)
    
    if len(results) == 2:
        r1, r2 = results[0], results[1]
        
        print(f"Upload #1: {r1['total']} tests (🔴 {r1['urgent']}, 🟡 {r1['monitor']}, 🟢 {r1['normal']})")
        print(f"Upload #2: {r2['total']} tests (🔴 {r2['urgent']}, 🟡 {r2['monitor']}, 🟢 {r2['normal']})")
        
        if r1['total'] == r2['total']:
            print(f"\n✅ CONSISTENT: Both uploads extracted {r1['total']} tests")
            
            # Check if same tests
            set1 = set(r1['test_names'])
            set2 = set(r2['test_names'])
            
            if set1 == set2:
                print(f"✅ EXACT MATCH: Same tests extracted")
            else:
                missing_in_2 = set1 - set2
                missing_in_1 = set2 - set1
                
                if missing_in_2:
                    print(f"⚠️  Tests in upload #1 but not #2: {missing_in_2}")
                if missing_in_1:
                    print(f"⚠️  Tests in upload #2 but not #1: {missing_in_1}")
        else:
            diff = abs(r1['total'] - r2['total'])
            print(f"\n❌ INCONSISTENT: Difference of {diff} tests")
            
            set1 = set(r1['test_names'])
            set2 = set(r2['test_names'])
            
            missing_in_2 = set1 - set2
            missing_in_1 = set2 - set1
            
            if missing_in_2:
                print(f"\n⚠️  Tests in upload #1 but NOT in #2:")
                for test in missing_in_2:
                    print(f"   - {test}")
            
            if missing_in_1:
                print(f"\n⚠️  Tests in upload #2 but NOT in #1:")
                for test in missing_in_1:
                    print(f"   - {test}")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_consistency())
