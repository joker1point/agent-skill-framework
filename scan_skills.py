import sqlite3
import json

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT name, description FROM skills ORDER BY name")
rows = cur.fetchall()
skills = [dict(r) for r in rows]

print(f"Total registered skills: {len(skills)}")
print("---")
for s in skills:
    desc = (s["description"] or "")[:80]
    print(f"{s['name']}|{desc}")

conn.close()
