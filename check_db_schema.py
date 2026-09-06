import sqlite3

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for row in cur.fetchall():
    print(row[0])
    print("---")

print("\n\n=== skills table sample ===")
cur.execute("SELECT * FROM skills LIMIT 3")
cols = [d[0] for d in cur.description]
print(f"Columns: {cols}")
for row in cur.fetchall():
    print(dict(zip(cols, row)))

print("\n\n=== scenarios count ===")
cur.execute("SELECT COUNT(*) FROM scenarios")
print(f"Total scenarios: {cur.fetchone()[0]}")

print("\n\n=== skills count ===")
cur.execute("SELECT COUNT(*) FROM skills")
print(f"Total skills: {cur.fetchone()[0]}")

conn.close()
