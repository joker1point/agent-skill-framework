# 批量清理计划 · Skills Manager

- 生成：2026-10-10 21:09（`python batch_plan.py` 可重跑；只读，不改库）

## 0. 机制结论（先说清楚能做到什么）

- `update_status` 值域只有 up_to_date / source_missing / update_available / error——**app 没有"冻结/忽略"状态**，靠改库伪造会被下一轮检查覆盖。
- `enabled` 是唯一启停开关（当前 341 条全为 1）；自动更新是全局的（最近一次 2026-10-07）。
- 结论：本计划里的动作分两类——**场景成员调整**（可在 app 场景管理里做）与**按需投放/归档**（内容决策）；不建议用 DB 伪状态。

## 1. 开发辅助瘦身（核心）

- 现状：**31 条 / ≈ 3,327 token**（占库 24%）
- 其中 **0 条已在更具体的场景里**（重复编组）；只有 31 条是"纯开发辅助"成员
- 建议：把重复成员从 开发辅助 移出 → 瘦身后 **31 条 / ≈ 3,327 token**

### 建议移出（0 条 → 只保留在其最具体场景）

| 技能 | 保留在 | 该场景规模 |
|---|---|---:|

### 建议保留在 开发辅助（31 条）

english-exam-writing-reviewer、idea-validator、lexiang-knowledge-base、grill-me、healthcheck、sag、meituan-coupon-workbuddy、lingxi-financialsearch-skill、meituan-huisheng-coupon、sino-drug-instructions-search、deck-generator、mtunion-product-ai-guide、tapd-openapi、workrally、fintech-engineer、caldav-calendar、fadada-document-sign、football-bayes、conversion-ops、promo-creator-skills、ima-skills、gif-sticker-maker、charity-writing-assistant、competitorsmart、habit-tracker、product-showcase-site、goal-tracker、model-usage、ctrip-wendao、github-ai-trends、crash-expert-skill

## 2. 未投放清单（104 → 分三类）

- **盘上活跃但未纳入管理**：30 条（这些在 agent 目录里存在，绕开 manager 分发，与"第二事实源"问题重叠）
  - agent-email、aippt、archify、baidu-ai-map、find-skills、hithink-mcp、hypit、ima、lark-setup、lexiang-knowledge-base、mcd-mcp、meituan-paotui、mtunion-product-ai-guide、notion、personal-mail-skill、qclaw-cron-skill、qclaw-env、qclaw-generate-image、qclaw-rules、qclaw-skill-creator、qqmusic、tabbit、tencentads、tencentmap-webservice-skill、tongdaxin-mcp、wecomcli-setup、wendao-partner-qclaw-skill、xbrowser、youdaonote、yuandian
- **已属场景但从未投放**：64 条（编了组、没投放——多半是有意保留在库里的仓库货）
  - api-gateway、brand-guidelines、caldav-calendar、caveman、charity-finance-assistant、charity-writing-assistant、cn-ecommerce-search、colleague-skill、competitorsmart、content-factory、conversion-ops、crash-expert-skill、ctrip-wendao、deck-generator、design-taste-frontend、ecommerce-copywriter、email-daily-summary、english-exam-writing-reviewer、english-intensive-reader、fadada-document-sign、finance-ops、fintech-engineer、flight-tracker、football-bayes、gif-sticker-maker、github-ai-trends、globepilot-ai-agent-2、goal-tracker、golden-pdf、grill-me、habit-tracker、healthcheck、idea-validator、ima-skills、knowledge-framework-builder、libtv-skill、lingxi-financialsearch-skill、marketing-skills、material-organizer、meituan-coupon-workbuddy、meituan-huisheng-coupon、model-usage、nano-pdf、neodata-financial-search、note-organizer、notebooklm-studio、novel、novel-writing、open-lesson、open-novel-writing、openai-image-gen、openai-whisper、openai-whisper-api、openclaw-assets-to-workbuddy、podcast-ops、product-showcase-site、promo-creator-skills、resume-assistant、sag、sino-drug-instructions-search…
- **真孤儿（不在任何场景）**：10 条
  - dev-lessons、find-skills-2、flyai-2、lexiang-knowledge-base-2、qcc-company-2、tc-chengxin、tencent-docs-2、tencent-musician-skills-2、tencent-news-2、weiyun-2

## 3. 上游异常（63 + 2）

- source_missing 63 条，来源分布：workbuddy 市场目录 62、qclaw 1
  - 处置选项：① 保持现状（只是标记，无副作用）② 确认不用的直接归档删除 ③ 重新指定源（gh 等）。**不建议改 update_status 伪造状态。**
- error 2 条：find-skills（failed to send request: 无法与服务器建立连接
; class=Os (2)）；grill-me（failed to send request: 无法与服务器建立连接
; class=Os (2)）——GitHub 连不上，等网络或删除源
