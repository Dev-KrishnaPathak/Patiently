"""
Debug script to check why only 16 tests are extracted from a 25+ test PDF
"""
import asyncio
import json
from database.sqlite_db import SQLiteDatabase

async def debug_extraction():
    """
    Check the latest document analysis to see what happened
    """
    db = SQLiteDatabase()
    await db.connect()
    
    # Get the most recent document
    query = """
        SELECT document_id, filename, upload_time 
        FROM documents 
        ORDER BY upload_time DESC 
        LIMIT 1
    """
    cursor = db.conn.execute(query)
    row = cursor.fetchone()
    
    if not row:
        print("❌ No documents found in database")
        return
    
    document_id = row[0]
    filename = row[1]
    upload_time = row[2]
    
    print(f"📄 Latest Document:")
    print(f"   ID: {document_id}")
    print(f"   File: {filename}")
    print(f"   Uploaded: {upload_time}")
    print(f"=" * 70)
    
    # Get the analysis
    query = "SELECT analysis_data FROM analyses WHERE document_id = ?"
    cursor = db.conn.execute(query, (document_id,))
    row = cursor.fetchone()
    
    if not row:
        print("❌ No analysis found for this document")
        return
    
    full_data = json.loads(row[0])
    analysis = full_data.get('analysis', {})
    
    # Extract info
    findings = analysis.get('findings', [])
    findings_count = len(findings)
    
    urgent = sum(1 for f in findings if f.get('status') == 'URGENT')
    monitor = sum(1 for f in findings if f.get('status') == 'MONITOR')
    normal = sum(1 for f in findings if f.get('status') == 'NORMAL')
    
    print(f"\n📊 Analysis Results:")
    print(f"   Total Findings: {findings_count}")
    print(f"   🔴 Urgent: {urgent}")
    print(f"   🟡 Monitor: {monitor}")
    print(f"   🟢 Normal: {normal}")
    
    if findings_count < 20:
        print(f"\n⚠️  WARNING: Only {findings_count} findings extracted!")
        print(f"   Expected: 25+ tests based on user report")
        print(f"   Possible issue: AI response truncation")
    
    # Check if there's a raw_response
    raw_response = analysis.get('raw_response', '')
    if raw_response:
        print(f"\n📝 Raw Response Available: {len(raw_response)} characters")
        
        # Try to count test patterns in raw response
        import re
        test_pattern = r'"test_name":\s*"([^"]+)"'
        matches = re.findall(test_pattern, raw_response)
        
        if matches:
            print(f"   Test names found in raw response: {len(matches)}")
            if len(matches) > findings_count:
                print(f"   🔍 FOUND MORE TESTS IN RAW RESPONSE!")
                print(f"      Parsed JSON has {findings_count} findings")
                print(f"      Raw response has {len(matches)} test names")
                print(f"      Missing: {len(matches) - findings_count} tests")
    
    # Show which tests were extracted
    print(f"\n📋 Extracted Tests:")
    for i, finding in enumerate(findings, 1):
        test_name = finding.get('test_name', 'Unknown')
        status = finding.get('status', 'N/A')
        value = finding.get('value', 'N/A')
        
        status_icon = {'URGENT': '🔴', 'MONITOR': '🟡', 'NORMAL': '🟢'}.get(status, '⚪')
        print(f"   {i:2d}. {status_icon} {test_name}: {value}")
    
    # Check extracted text
    extracted_text = full_data.get('extracted_text', '')
    if extracted_text:
        print(f"\n📄 Extracted Text Length: {len(extracted_text)} characters")
        
        # Try to count how many test results are in the extracted text
        # Look for common patterns like "Test Name ... value ... reference range"
        lines = extracted_text.split('\n')
        potential_tests = 0
        
        for line in lines:
            line = line.strip()
            # Very rough heuristic: lines with numbers and measurement units
            if any(unit in line.lower() for unit in ['mg/dl', 'g/dl', 'mmol', 'ng/ml', 'pg/ml', 'iu/ml', 'umol', '%', '/cumm', 'fl', 'mm/hr']):
                potential_tests += 1
        
        print(f"   Potential test result lines: {potential_tests}")
        
        if potential_tests > findings_count:
            print(f"   ⚠️  Text has ~{potential_tests} test lines, but only {findings_count} were extracted!")
    
    # Recommendations
    print(f"\n" + "=" * 70)
    print(f"🔧 DIAGNOSIS:")
    
    if findings_count < 20:
        print(f"   Issue: AI response truncation")
        print(f"\n💡 SOLUTIONS:")
        print(f"   1. max_tokens is set to 32000 - check if API supports this")
        print(f"   2. Try using recovery function on raw_response")
        print(f"   3. Consider splitting large PDFs into chunks")
        print(f"   4. Check backend logs for 'finish_reason: length' warning")
        print(f"\n🔧 Quick Fix:")
        print(f"   Run: python fix_existing_analysis.py")
        print(f"   This will try to recover all tests from raw_response")
    else:
        print(f"   ✅ Extraction looks complete")
    
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_extraction())
