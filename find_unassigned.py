import sqlite3

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT s.id, s.name, s.description
    FROM skills s
    WHERE s.id NOT IN (SELECT skill_id FROM scenario_skills)
    ORDER BY s.name
""")
rows = cur.fetchall()
print(f"Unassigned skills: {len(rows)}")
print("=" * 70)
for r in rows:
    desc = (r["description"] or "")[:70]
    print(f"{r['name']}|{desc}")

conn.close()
