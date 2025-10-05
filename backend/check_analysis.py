import sqlite3
import json

conn = sqlite3.connect('docusage.db')
cursor = conn.cursor()
cursor.execute('SELECT analysis_data FROM analyses ORDER BY created_at DESC LIMIT 1')
data = json.loads(cursor.fetchone()[0])

print(f"Status: {data['analysis']['overall_status']}")
print(f"Findings: {len(data['analysis']['findings'])}")
print(f"Questions: {len(data['questions'])}")
print("\nFirst question:")
print(json.dumps(data['questions'][0], indent=2))
