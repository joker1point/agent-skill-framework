---
name: preset-navigator
description: 查询本地 skills-manager 数据库，发现可用的 Skill 和 Preset 分组。当用户问"有哪些 skill"、"装了什么"、"用什么工具"、"Preset 列表"等问题时使用。也用于自动判断当前任务需要激活哪个 Preset。
tags: skills, preset, navigation, meta
always: false
---

# Preset Navigator

你是一个**技能导航员**。你的职责是帮助用户和 Agent 快速发现、查询、组织本地 Skill 资源。

## 1. 核心数据库

所有 skill 元数据存储在 SQLite 数据库：

```
~/.skills-manager/skills-manager.db
```

**核心表结构**：

| 表名 | 用途 |
|------|------|
| `skills` | 全部已注册技能（name、description、enabled、central_path） |
| `scenarios` | Preset 分组（name、description、sort_order） |
| `scenario_skills` | Preset 与技能的关联表 |
| `active_scenario` | 当前激活的 Preset |

## 2. 如何查询

使用 `read_file` 工具读取本文件后，再用 `run_command` 执行 Python + sqlite3 查询。**不要试图直接读 SQLite 二进制文件**。

### 2.1 列出所有 Preset

```python
import sqlite3
DB = r"%USERPROFILE%\.skills-manager\skills-manager.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name, description, sort_order FROM scenarios ORDER BY sort_order")
for name, desc, order in cur.fetchall():
    print(f"{order:2d}. {name} - {desc or ''}")
conn.close()
```

### 2.2 列出 Preset 下的所有技能

```python
cur.execute("""
    SELECT s.name, s.description
    FROM scenario_skills ss
    JOIN skills s ON s.id = ss.skill_id
    JOIN scenarios sc ON sc.id = ss.scenario_id
    WHERE sc.name = ?
    ORDER BY ss.sort_order
""", ("Web开发",))
```

### 2.3 搜索技能

按关键词搜索 description：

```python
cur.execute("""
    SELECT name, description
    FROM skills
    WHERE description LIKE ?
       OR name LIKE ?
    ORDER BY name
""", (f"%{keyword}%", f"%{keyword}%"))
```

### 2.4 查找技能所属 Preset

```python
cur.execute("""
    SELECT sc.name
    FROM scenario_skills ss
    JOIN skills s ON s.id = ss.skill_id
    JOIN scenarios sc ON sc.id = ss.scenario_id
    WHERE s.name = ?
""", ("gmail",))
```

### 2.5 查看当前激活的 Preset

```python
cur.execute("SELECT scenario_id FROM active_scenario WHERE key = 'current'")
active = cur.fetchone()
if active:
    cur.execute("SELECT name FROM scenarios WHERE id = ?", (active[0],))
    print("Active:", cur.fetchone()[0])
```

## 3. 当前 Preset 全景（27 个）

开发类（3 个）：
- **Web开发** (13) - frontend-dev, vercel-deploy, cloudflare
- **移动开发** (8) - android-native-dev, flutter-dev, wechat-miniprogram
- **开发运维** (18) - cli-anything-hub, web-performance-audit, diagnose

内容类（5 个）：
- **文档处理** (12) - docx, pdf, xlsx, pptx-generator
- **内容创作** (10) - content-creator, novel-writer, humanizer
- **写作出版** (16) - novel, khazix-writer, wechat-publisher
- **音视频** (10) - openai-whisper, remotion-video-toolkit, nano-banana-pro
- **设计创意** (8) - figma, canvas-design, infographic-maker

研究教育类（2 个）：
- **研究分析** (10) - deep-research, arxiv-reader, perplexity, tavily
- **教育学习** (11) - academic-tutor, study-planner, teachany

商业类（4 个）：
- **金融数据** (8) - stock-analysis, futuapi, macro-monitor
- **营销增长** (12) - growth-engine, seo-ops, sales-pipeline
- **电商运营** (12) - admapix, ecomseer, wechatpay-product-coupon
- **法律金融** (7) - legal-logic-analysis, tencent-esign-contract

生活类（2 个）：
- **出行生活** (9) - weather, 12306, didi-ride-skill
- **出行交通** (11) - flight-tracker, meituan-travel, aviation-weather

协作类（4 个）：
- **通讯协作** (7) - gmail, dingtalk-unified, lark-unified
- **邮件增强** (9) - imap-smtp-email, gog, porteden-email
- **效率工具** (23) - apple-notes, obsidian, handoff, summarize
- **云存储阅读** (10) - baidu-drive, kdocs, weread-skills

系统类（4 个）：
- **Agent系统** (25) - agent-mbti, persona-switch, capability-evolver
- **浏览器自动化** (6) - browser, smooth-browser, web-scraper
- **浏览器扩展** (7) - playwright-browser-automation, stagehand-browser-cli
- **腾讯生态** (29) - andonq, cloudbase, tencent-docs, smart-page

信息类（2 个）：
- **技能管理** (6) - skill-creator, mcp-builder, mcporter
- **搜索资讯** (6) - multi-search-engine, aihot, tech-news-digest

**总计：302 个技能，覆盖 27 个 Preset**。

## 4. 典型使用场景

### 场景 A：用户问"你能做什么"

```python
# 列出所有 Preset
for p in presets:
    print(f"- {p['name']}: {p['description']}")
# 然后用 1-2 句话总结"我的能力范围"
```

### 场景 B：自动判断用哪个 Preset

根据用户输入关键词匹配 Preset：
- 含"邮件/gmail" → 通讯协作
- 含"部署/vercel/netlify" → Web开发
- 含"微信/公众号" → 写作出版
- 含"股票/财报" → 金融数据
- 含"天气/火车/12306" → 出行生活

### 场景 C：查找特定能力的 Skill

```python
keyword = extract_keyword(user_query)
cur.execute("SELECT name, description FROM skills WHERE description LIKE ?", (f"%{keyword}%",))
```

### 场景 D：建议切换 Preset

当用户开始新类型任务时：

```python
# 1. 找到当前激活的 Preset
# 2. 分析用户新需求属于哪个 Preset
# 3. 提示用户："建议切换到 X Preset"
```

## 5. 物理位置

技能文件实际存储位置：
- 中央库：`%USERPROFILE%\.skills-manager\skills\`
- 项目的 `.agents/skills/`（如果有）

每个 Skill 是一个目录，包含 `SKILL.md` 等文件。

## 6. 注意事项

- **只读查询**：本 skill 不修改数据库。修改请用 skills-manager 桌面端。
- **路径使用 r""**：Windows 路径前缀加 `r` 避免转义。
- **database is locked**：如果报错，等几秒重试，避免和桌面端同时写入。
- **首次运行**：建议先 `SELECT COUNT(*) FROM skills` 确认数据库可访问。

## 7. 进一步操作

| 用户需求 | 推荐操作 |
|----------|----------|
| 看完整 Preset 列表 | 调 §2.1 |
| 查 Preset 详情 | 调 §2.2 |
| 找特定 Skill | 调 §2.3 |
| 改 Preset 关联 | 用桌面端 |
| 装新 Skill | 用桌面端或 npx skills add |
| 切换 Preset | 用桌面端 |
