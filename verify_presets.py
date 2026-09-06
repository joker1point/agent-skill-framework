import sqlite3

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("""
    SELECT s.name AS scenario_name, s.description, COUNT(ss.skill_id) AS skill_count
    FROM scenarios s
    LEFT JOIN scenario_skills ss ON s.id = ss.scenario_id
    GROUP BY s.id
    ORDER BY s.sort_order
""")
rows = cur.fetchall()

print(f"Total presets: {len(rows)}")
print("=" * 60)
total = 0
for r in rows:
    print(f"  {r['scenario_name']:12s} | {r['skill_count']:3d} skills | {r['description']}")
    total += r["skill_count"]
print("=" * 60)
print(f"Total linked skills: {total}")

cur.execute("SELECT scenario_id FROM active_scenario WHERE key = 'current'")
active = cur.fetchone()
print(f"Active preset: {active['scenario_id'] if active else 'None'}")

conn.close()
