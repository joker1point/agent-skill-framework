# -*- coding: utf-8 -*-
"""L0 落地（正确姿势）：写 skills-manager 文件级元数据创建「核心开发」场景
事实来源：~/.skills-manager/skills/.skills-manager/{scenarios,scenario-skills}/
写入后由 CLI 任意命令触发 reindex 重建 DB。
"""
import json
import os
import sqlite3
import uuid

DB = os.path.expandvars(r"%USERPROFILE%\.skills-manager\skills-manager.db")
META = os.path.expanduser(r"~\.skills-manager\skills\.skills-manager")

SKILLS = [
    # 开发工作流 (8)
    "github", "tdd", "diagnose", "grill-me",
    "task-alignment", "task-implement", "zoom-out", "oracle",
    # 前端/Web (5)
    "impeccable", "redesign-existing-projects", "landing-page-generator",
    "agent-browser-core", "shader-dev",
    # 平台部署 (5)
    "cloudflare-worker-builder", "edgeone-pages-deploy",
    "github-pages-auto-deploy", "cnb-skill", "migraq",
    # 移动端 (2)
    "ios-application-dev", "tdesign-miniprogram",
    # Python (3)
    "python-performance-optimization", "python-testing-patterns", "data-visualization",
    # Skill/MCP 工程 (10)
    "mcp-builder", "skills-security-check", "anti-distill", "darwin-skill",
    "capability-evolver", "prompt-engineering-expert", "cangjie-skill",
    "nuwa-skill", "skill-creator", "qmd",
    # 知识/研究 (3)
    "llm-wiki", "excalidraw-diagram", "web-search-exa",
]

SCENARIO_ID = str(uuid.uuid4())

# 1. 取 skill_id
conn = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
cur = conn.cursor()
cur.execute("SELECT id, name FROM skills")
id_by_name = dict((n, i) for i, n in cur.fetchall())
conn.close()
missing = [s for s in SKILLS if s not in id_by_name]
if missing:
    raise SystemExit(f"[ABORT] 中央库缺少: {missing}")

# 2. 幂等：同名场景已存在则复用其 ID
scn_dir = os.path.join(META, "scenarios")
for fn in os.listdir(scn_dir):
    if fn.endswith(".json"):
        with open(os.path.join(scn_dir, fn), encoding="utf-8") as f:
            if json.load(f).get("name") == "核心开发":
                raise SystemExit(f"[ABORT] 元数据中已存在「核心开发」: {fn}")

# 3. 写场景文件
scenario = {
    "schema_version": 1,
    "scenario_id": SCENARIO_ID,
    "name": "核心开发",
    "description": "纯开发核心集：工作流/前端/部署/Python/Skill工程（L0裁剪）",
    "icon": "⌨️",
    "sort_order": 29,
}
with open(os.path.join(scn_dir, f"{SCENARIO_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(scenario, f, ensure_ascii=False, indent=2)

# 4. 写 membership 文件
mem_dir = os.path.join(META, "scenario-skills", SCENARIO_ID)
os.makedirs(mem_dir, exist_ok=True)
for order, name in enumerate(SKILLS):
    member = {
        "schema_version": 1,
        "scenario_id": SCENARIO_ID,
        "skill_id": id_by_name[name],
        "sort_order": order,
        "tools": {},
    }
    with open(os.path.join(mem_dir, f"{id_by_name[name]}.json"), "w", encoding="utf-8") as f:
        json.dump(member, f, ensure_ascii=False, indent=2)

print(f"[OK] 元数据已写入: 场景 {SCENARIO_ID}, {len(SKILLS)} 个 membership")
print("下一步: 任意 CLI 命令触发 reindex → presets apply 核心开发")
