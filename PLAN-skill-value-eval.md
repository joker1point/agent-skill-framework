# PLAN · 技能价值与自主路由评估（v2 用例设计草案）

> 状态：**已执行（2026-09-29）** —— 4 批 37 evals 零 error；结果页 `skill-workspace/skill-value-viz.html`。
> 首跑修正：sm-02 断言收紧（详见 §1 表）；weather 对照（iteration-7）出现两轮反转，已如实记录。
> 上级背景：weather 三方对比（iteration-6）证明「技能是否改变结果」在**冗余知识**上测不出差异。
> 本实验验证条件化结论：**技能 = 模型不具备的私有知识载体时，价值才成立**。
> （与 `usercontext/2026-09-28` 里写下的下一步「换技能含模型不具备的独有知识任务」一致。）

## 0. 要回答的三个假设

| # | 假设 | 判定方式 |
|---|---|---|
| H1 | 技能承载"模型不可能知道"的私有知识时，技能有效（with / agentic ≫ without） | 8 条用例，断言钉私有 token |
| H2 | 知识冗余时（weather），技能无增益（三臂趋同） | weather 对照题 |
| H3 | 多技能场景下，自主加载免除"人工逐题选技能"；静态注入没有路由能力 | agentic trace 的 `loaded_skills` + 固定注入臂 |

## 1. 用例总表（8 条；断言全部钉"模型不可能知道"的 token）

| id | 技能 | 问题（不含答案 token，避免泄题） | 断言（钉的 token） | without 预期 | 技能内出处 |
|---|---|---|---|---|---|
| pn-01 | preset-navigator | 这些技能和 Preset 的数据存在哪个文件里？用什么查？ | contains `skills-manager.db` + regex `sqlite3\|SELECT` | 挂 | 技能 §1 核心数据库 |
| pn-02 | preset-navigator | 怎么查当前激活的是哪个 Preset？ | contains `active_scenario` | 挂 | §2.5 |
| pn-03 | preset-navigator | 想知道一个技能被分在哪些 Preset 里，用什么查？ | contains `scenario_skills` | 挂 | §2.4 关联表 |
| sm-01 | skills-manager | 这些 AI 工具的 skills 中央库装在哪个目录？ | contains `.skills-manager` | 挂 | 核心概念图 / 项目级管理 |
| sm-02 | skills-manager | 把一个技能加进某个 Preset 的命令是什么？ | contains `skills-manager-cli` + regex `presets\s+add-skill`（首跑发现原 `["presets","add-skill"]` 会被编造答案蒙中，已收紧） | 挂 | §8 Preset 管理 |
| ct-01 | code-tools | 做 PR 审查、要一张代码审查图谱，用哪个工具？ | contains `code-review-graph` | 挂 | 工具总览表 |
| ct-02 | code-tools | 团队共享 + 语义检索的代码库记忆方案用哪个？ | contains `codebase-memory-mcp` | 挂 | 工具总览表 |
| wx-01 | weather（对照） | 伦敦现在多少度？ | contains `度`（沿用现有措辞风格） | 三臂预期都过 | —（冗余知识） |

断言写法示例（沿用现有 `evals.json` 格式）：

```json
{
  "id": 12, "name": "pn-active-scenario",
  "prompt": "怎么查当前激活的是哪个 Preset？",
  "expected_output": "说明用 active_scenario 表查询",
  "assertions": [
    {"type": "contains", "name": "has_active_scenario_table", "substring": "active_scenario"},
    {"type": "length", "name": "min_length", "min_length": 10}
  ]
}
```

## 2. 实验结构（三臂 + 一臂）

- **实验一（技能价值）**：每个技能 3 臂 —— `agentic` / `with_skill`（该技能，= 人工已选对）/ `without_skill`。
- **实验二（无人工路由）**：对非 weather 的 7 条题加跑 `with_skill_weather`（固定注入 weather 正文）——
  如实标注「模拟未路由工况」，测静态注入失去人工路由后的实际表现。
- agentic 臂天然带路由证据：每题 trace 的 `loaded_skills` 应等于被考技能（H3 判定）。

## 3. 断言预检（跑批前，零成本）

1. 逐 token 在技能正文中 grep 命中（防手滑写错 token）；
2. 人工确认 token 非公开常识（不会被模型先验覆盖）；
3. **跑批后若"预期没中"：先修断言 / 换题，再谈结论**（评估集先自证——沿用你的纪律）。

## 4. 运行与成本

- 新增 `run_skill_value_eval.py`（小脚本）：参数化技能名 + 固定注入臂；
  复用 `SkillEvals.create_eval_file` / `SkillBenchmark` / `AgenticExecutor`，不复制逻辑。
- 落点：`skills/<name>/evals/evals.json`；结果自动进 `skill-workspace/<name>/iteration-1/`。
- 规模：24 evals（8 题 × 3 臂）+ 7 evals（固定注入）≈ **31 evals ≈ 40+ 次模型调用**；分 4 批（按技能）。
- 限流：沿用退避（429 已实测可扛）；**含 error 的批次整体作废重跑**。
- 预计 15–25 分钟（串行）。

## 5. 预期结果 & 若证伪

- H1 成立 → 报告页 v2 主结论：「技能有效 ≠ 天生有效——**技能 = 私有知识载体**；weather 测不出是因为知识冗余」。
- H3 成立（路由命中 + 固定注入挂非本域题）→ 补上自主加载 vs 静态注入的边界证据。
- 任一预期没中（如 without 蒙对 token、agentic 路由错）：如实记入结果，修断言或换题，**不硬圆**。

## 6. 诚实边界（将写进报告页）

- `with_skill` = oracle（人工已指定正确技能）；人工逐题路由时静态可等价——本对比测的是**自动化程度**，不是"静态一定差"。
- 断言是文本级（contains / regex）：测"答案体现了独有知识"，不等于端到端任务成功率。
- 每技能 1–3 题，n 小：结论定性；引用带模型 + 日期 + 数据版本。

## 7. 本轮不碰

- weather iteration-1..6 数据与断言（报告页 v1 原样保留）。
- 报告页本身（P1 重排等数据到位后一起做）。

## 8. 执行顺序（批准后）

1. 写 `run_skill_value_eval.py` + 4 个技能的 `evals.json`；
2. 跑断言预检（零成本）；
3. 分 4 批跑 + 固定注入臂；
4. 汇总结果 → 报告页 v2 重排（P1）。
