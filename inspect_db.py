# -*- coding: utf-8 -*-
"""查询候选 skill 是否在中央库（名称精确/前缀匹配）"""
import sqlite3

DB = r"C:\Users\biren\.skills-manager\skills-manager.db"
CANDIDATES = ["code-review", "code-simplifier", "superpowers", "webapp-testing",
              "ui-ux-pro-max", "ralph-loop", "skill-creator", "port-feature-from-reference"]

conn = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
cur = conn.cursor()
for name in CANDIDATES:
    cur.execute("SELECT name FROM skills WHERE name = ? OR name LIKE ?", (name, name + "%"))
    rows = [r[0] for r in cur.fetchall()]
    print(f"{name}: {rows if rows else 'NOT IN DB'}")
conn.close()
