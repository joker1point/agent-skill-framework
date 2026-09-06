"""
更新分类规则，重点关注开发辅助类skill
新增专门的开发相关分类，并将分类结果写入数据库
"""
import sqlite3
import json
import re

DB_PATH = r"C:\Users\biren\.skills-manager\skills-manager.db"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, name, description FROM skills ORDER BY name")
rows = cur.fetchall()
skills = [dict(r) for r in rows]

CATEGORIES = {
    "dev-tools": {
        "label": "开发工具",
        "keywords": ["dev", "code", "cli", "flutter", "react", "android", "frontend",
                     "fullstack", "shader", "tdd", "mcp-builder", "mcporter", "skill-creator",
                     "skill-scanner", "skill-vetter", "setup-pre-commit", "cangjie", "cnb-skill",
                     "flutter", "native-dev", "miniprogram", "static-app", "api-gateway",
                     "capability-evolver", "task-implement", "task-alignment", "handoff",
                     "agent-team", "fintech-engineer", "claude-code-tips", "half-clone",
                     "version-check", "hn-summarize", "reddit-fetch", "superpowers",
                     "code-review", "code-simplifier"],
    },
    "dev-ops": {
        "label": "开发运维",
        "keywords": ["deploy", "vercel", "netlify", "cloudflare", "html-deploy",
                     "web-deploy", "cloudbase", "edgeone", "tencentcloud", "cloudq",
                     "shippage", "github-pages", "devcontainer", "docker", "kubernetes",
                     "k8s", "performance", "optimization", "debug", "crash", "diagnose",
                     "testing", "test", "audit", "lint", "pre-commit", "ci-cd", "build",
                     "release", "update-deps", "upgrade", "expo-upgrade"],
    },
    "dev-security": {
        "label": "开发安全",
        "keywords": ["security", "vulnerability", "audit", "secure", "crypto",
                     "semgrep", "codeql", "sarif", "fuzzing", "mutation", "constant-time",
                     "zeroize", "supply-chain", "risk", "trail-of-bits", "trailmark",
                     "skills-security-check", "secure-contract", "c-review"],
    },
    "dev-productivity": {
        "label": "开发效率",
        "keywords": ["task", "project", "planning", "management", "ccpm", "claude-task-master",
                     "plannotator", "annotate", "review", "goal", "handoff", "workflow",
                     "oneredoak", "compound-engineering", "skill-seekers", "skill-improver",
                     "spec-to-code", "compliance", "second-opinion", "ask-questions",
                     "underspecified", "interpreter", "context-building", "entry-point",
                     "dwarf", "fp-check", "modern-python", "property-based", "coverage",
                     "harness", "wycheproof", "ossfuzz", "libfuzzer", "aflpp", "libafl",
                     "cargo-fuzz", "atheris", "sharp-edges", "insecure-defaults",
                     "ralph-loop", "planning-with-files"],
    },
    "dev-debug": {
        "label": "调试诊断",
        "keywords": ["debug", "troubleshoot", "chrome-mcp", "buttercup", "differential-review",
                     "mutation-testing", "variant-analysis", "constant-time-analysis",
                     "dimensional-analysis", "token-integration", "algorand", "cairo",
                     "cosmos", "solana", "substrate", "ton", "firebase-apk", "firebase",
                     "apk-scanner"],
    },
    "dev-testing": {
        "label": "测试工具",
        "keywords": ["testing", "test", "unittest", "integration", "e2e", "playwright",
                     "pytest", "mutation", "property", "coverage", "fuzz", "address-sanitizer",
                     "wycheproof", "ruzzy", "testing-handbook", "fuzzing-dictionary",
                     "fuzzing-obstacles", "harness-writing"],
    },
    "doc-suite": {
        "label": "文档处理",
        "keywords": ["docx", "pdf", "xlsx", "pptx", "markdown", "md-to", "markitdown",
                     "pdfkit", "qmd", "minimax-docx", "minimax-pdf", "minimax-xlsx",
                     "citation", "file-diff", "document", "design-doc-mermaid", "diagram",
                     "mermaid", "deck-generator", "notebooklm"],
    },
    "web-browser": {
        "label": "浏览器与网页",
        "keywords": ["browser", "web-scraper", "web-access", "web-search", "web-deploy",
                     "clawbrowser", "browserwing", "smooth-browser", "stealth-browser",
                     "browser-use", "browser-cash", "agent-browser", "xurl", "peekaboo"],
    },
    "ai-research": {
        "label": "AI与研究",
        "keywords": ["research", "arxiv", "perplexity", "tavily", "autoresearch",
                     "deep-research", "llm-wiki", "paper-quick", "jiaozhen", "factcheck",
                     "oracle", "model-usage", "agent-mbti", "capability", "openai-skills"],
    },
    "design-creative": {
        "label": "设计与创意",
        "keywords": ["design", "figma", "canvas", "diagram", "infographic", "gif",
                     "sticker", "excalidraw", "brand", "awesome-design", "deck-generator",
                     "nano-banana", "openai-image", "songsee", "zoom-out", "smart-page",
                     "caveman", "darwin-skill", "landing-page", "redesign", "ui-ux-pro-max"],
    },
    "video-production": {
        "label": "视频制作",
        "keywords": ["video", "moneyprinterturbo", "opencut", "vimax", "toonflow",
                     "openmontage", "palmier-pro", "open-generative-ai", "generative-ai",
                     "remotion", "video-frames", "script-gen"],
    },
    "comm-suite": {
        "label": "邮件与通讯",
        "keywords": ["email", "gmail", "mail", "imsg", "dingtalk", "lark", "wecom",
                     "qq-email", "agentmail", "himalaya", "imap", "smtp", "porteden",
                     "blogwatcher"],
    },
    "finance-data": {
        "label": "金融与数据",
        "keywords": ["stock", "finance", "futu", "market", "earnings", "westock",
                     "macro", "football-bayes", "conversion-ops", "growth-engine",
                     "outbound-engine", "sales", "competitorsmart", "seo", "csv-summarizer",
                     "data-analysis", "lingxi", "neodata"],
    },
    "content-creation": {
        "label": "内容创作",
        "keywords": ["content", "novel", "writer", "blog", "podcast",
                     "humanizer", "khazix", "guizang", "wechat-article", "x-longform",
                     "my-novel", "novel-writing", "open-novel", "fbs-bookwriter",
                     "video-script", "news-summary", "tech-news", "aihot", "github-trending",
                     "github-ai", "tencent-news", "avoid-ai-writing"],
    },
    "travel-lifestyle": {
        "label": "出行与生活",
        "keywords": ["weather", "travel", "flight", "12306", "didi", "ctrip",
                     "airbnb", "airchina", "aviation", "meituan", "travel-cn",
                     "travel-planning", "tencent-weather", "habit-tracker", "goal-tracker",
                     "study-planner", "open-lesson", "tutor", "academic", "education",
                     "football", "grill", "health", "plan-tracker"],
    },
    "wechat-social": {
        "label": "微信与社交",
        "keywords": ["wechat", "weixin", "weread", "ima-skills", "kdocs", "tencent-docs",
                     "jinshuju", "tencent-survey", "qq", "weiyun", "baidu-drive",
                     "bdpan", "obsidian", "note", "apple-notes", "apple-reminders",
                     "things-mac", "caldav", "trello", "workrally", "team-ops",
                     "colleague", "vip-skill", "yourself", "nuwa", "yingmi",
                     "persona-switch", "idea-validator", "teachany", "tutor-skills",
                     "resume", "anti-distill", "impeccable", "material-organizer",
                     "tencentos", "tapd", "qcc", "tencent-yunzhi"],
    },
    "search-tools": {
        "label": "搜索工具",
        "keywords": ["search", "tavily", "perplexity", "web-search-exa", "migraq",
                     "gifgrep", "flyai", "gog", "wacli", "libtv", "install-futu",
                     "mac", "tmux", "sag", "skyline"],
    },
    "monitoring": {
        "label": "监控告警",
        "keywords": ["sentry", "logging", "cls", "analytics", "error", "trace"],
    },
}


def classify(skill_name, description):
    name_lower = skill_name.lower()
    desc_lower = (description or "").lower()
    for cat_id, cat in CATEGORIES.items():
        for kw in cat["keywords"]:
            if kw in name_lower or kw in desc_lower:
                return cat_id
    return "other"


result = {}
uncategorized = []

for s in skills:
    cat = classify(s["name"], s["description"])
    if cat == "other":
        uncategorized.append(s["name"])
    else:
        result.setdefault(cat, []).append(s)

print("=" * 70)
print(f"Total skills: {len(skills)}")
print(f"Categorized: {len(skills) - len(uncategorized)}")
print(f"Uncategorized: {len(uncategorized)}")
print("=" * 70)

# 重点输出开发相关分类
dev_categories = ["dev-tools", "dev-ops", "dev-security", "dev-productivity", "dev-debug", "dev-testing", "monitoring"]
other_categories = [c for c in CATEGORIES if c not in dev_categories]

print("\n" + "=" * 70)
print("【重点关注：开发辅助类 Skill】")
print("=" * 70)

for cat_id in dev_categories:
    cat = CATEGORIES[cat_id]
    items = result.get(cat_id, [])
    print(f"\n## {cat['label']} ({cat_id}) — {len(items)} skills")
    for s in items:
        desc = s['description'][:60] if s['description'] else ""
        print(f"  - {s['name']:35s} {desc}")

print("\n" + "=" * 70)
print("【其他分类】")
print("=" * 70)

for cat_id in other_categories:
    cat = CATEGORIES[cat_id]
    items = result.get(cat_id, [])
    print(f"\n## {cat['label']} ({cat_id}) — {len(items)} skills")
    for s in items:
        print(f"  - {s['name']}")

if uncategorized:
    print(f"\n## 未分类 — {len(uncategorized)} skills")
    for name in uncategorized:
        print(f"  - {name}")

# 将分类结果写入数据库
print("\n" + "=" * 70)
print("写入数据库...")
print("=" * 70)

cur.execute("DROP TABLE IF EXISTS skill_categories")
cur.execute("""
    CREATE TABLE skill_categories (
        skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
        category_id TEXT NOT NULL,
        category_label TEXT NOT NULL,
        PRIMARY KEY(skill_id, category_id)
    )
""")

for cat_id, cat in CATEGORIES.items():
    for s in result.get(cat_id, []):
        cur.execute(
            "INSERT INTO skill_categories (skill_id, category_id, category_label) VALUES (?, ?, ?)",
            (s["id"], cat_id, cat["label"])
        )

conn.commit()
print(f"已将 {sum(len(v) for v in result.values())} 个skill分类写入数据库")

# 创建开发辅助预设
print("\n创建开发辅助预设...")
cur.execute("SELECT id FROM scenarios WHERE name = ?", ("开发辅助",))
existing = cur.fetchone()

now_ms = int(time.time() * 1000) if 'time' in dir() else 0
import time
now_ms = int(time.time() * 1000)

dev_skill_ids = []
for cat_id in dev_categories:
    for s in result.get(cat_id, []):
        dev_skill_ids.append(s["id"])

if existing:
    scenario_id = existing["id"]
    cur.execute("DELETE FROM scenario_skills WHERE scenario_id = ?", (scenario_id,))
    print("更新现有预设")
else:
    scenario_id = str(uuid.uuid4()) if 'uuid' in dir() else ""
    import uuid
    scenario_id = str(uuid.uuid4())
    cur.execute("SELECT MAX(sort_order) as max_sort FROM scenarios")
    max_sort = cur.fetchone()["max_sort"] or 0
    cur.execute("""
        INSERT INTO scenarios (id, name, description, icon, sort_order, created_at, updated_at)
        VALUES (?, ?, ?, NULL, ?, ?, ?)
    """, (scenario_id, "开发辅助", "开发工具、运维、安全、效率、调试、测试等开发全流程辅助工具集", max_sort + 1, now_ms, now_ms))
    print("创建新预设")

for idx, skill_id in enumerate(dev_skill_ids):
    cur.execute("""
        INSERT OR IGNORE INTO scenario_skills (scenario_id, skill_id, added_at, sort_order)
        VALUES (?, ?, ?, ?)
    """, (scenario_id, skill_id, now_ms, idx))

conn.commit()
print(f"开发辅助预设已包含 {len(dev_skill_ids)} 个skill")

conn.close()

print("\n" + "=" * 70)
print("分类完成！")
print("=" * 70)
