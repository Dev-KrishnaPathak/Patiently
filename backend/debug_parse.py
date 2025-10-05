import sqlite3
import json

conn = sqlite3.connect('docusage.db')
cursor = conn.cursor()
cursor.execute('SELECT analysis_data FROM analyses ORDER BY created_at DESC LIMIT 1')
data = json.loads(cursor.fetchone()[0])

print("=== RAW RESPONSE FROM LLM ===")
raw = data['analysis'].get('raw_response', '')
print(raw[:1000])  # First 1000 chars
print("\n\n=== ATTEMPTING TO PARSE ===")

# Try the same logic as the code
response = raw
if "```json" in response:
    response = response.split("```json")[1].split("```")[0]
elif "```" in response:
    response = response.split("```")[1].split("```")[0]

# Extract JSON
first_brace = response.find('{')
last_brace = response.rfind('}')
if first_brace != -1 and last_brace != -1:
    response = response[first_brace:last_brace+1]

print("First 500 chars after extraction:")
print(response[:500])

try:
    parsed = json.loads(response.strip())
    print("\n✅ Successfully parsed!")
    print(f"Findings count: {len(parsed.get('findings', []))}")
except Exception as e:
    print(f"\n❌ Parse failed: {e}")
