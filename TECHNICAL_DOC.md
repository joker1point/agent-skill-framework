# Skill Framework 技术文档

## 目录

1. [设计思路](#1-设计思路)
2. [架构总览](#2-架构总览)
3. [核心模块 API 说明](#3-核心模块-api-说明)
4. [使用指南](#4-使用指南)
5. [最佳实践](#5-最佳实践)
6. [真实迭代案例](#6-真实迭代案例)
7. [技能管理与 Preset 体系](#7-技能管理与-preset-体系)
8. [附录](#附录)

***

## 1. 设计思路

### 1.1 问题背景

AI Agent 的技能（Skill）本质上是**注入到上下文窗口的指令和知识**。一个技能是否有效，传统上只能靠人工"看起来对了"来判断。这带来三个问题：

- **不可验证**：技能修改后不知道是变好了还是变差了
- **不可追踪**：模型升级后技能可能失效却无人知晓
- **不可迭代**：没有反馈循环来指导改进

### 1.2 核心理念

参考 Anthropic 的 [skill-creator](https://github.com/anthropics/skills) 设计，本框架将软件工程的测试方法论引入技能管理：

| 软件工程  | 技能框架                    |
| ----- | ----------------------- |
| 单元测试  | 评估用例 (evals)            |
| 性能基准  | 基准测试 (benchmark)        |
| CI/CD | 迭代对比 (iteration)        |
| 代码审查  | 触发分析 (trigger analyzer) |

### 1.3 两类技能的区分

**能力增强型 (Capability Uplift)**：让模型做到原本做不到的事。例如 weather 技能让模型能查询实时天气。这类技能随模型进化可能变得不必要。但至少在现在的模型能力来看，这类技能仍能显著提高模型执行任务的成功率和显著减少它的执行任务时间

**偏好编码型 (Encoded Preference)**：让模型按团队流程做事。例如代码审查技能规定审查步骤。这类技能更持久，但价值取决于对流程的忠实度。

两类技能都需要测试，但关注点不同。本框架同时支持。

### 1.4 渐进式上下文加载

技能采用三级加载，避免上下文膨胀：

```
Level 1: 元数据 (name + description)  → 始终在上下文中 (~100词)
Level 2: SKILL.md 正文                → 技能触发时加载 (<500行)
Level 3: 附加资源 (scripts/references) → 按需加载 (无限制)
```

***

## 2. 架构总览

```
┌──────────────────────────────────────────────────────┐
│                    用户 / 测试脚本                     │
├──────────────────────────────────────────────────────┤
│  run_real_eval.py  (端到端入口)                       │
├──────────┬───────────┬───────────────┬───────────────┤
│ Evals    │ Benchmark  │ Trigger       │ EvalViewer    │
│ (测试)   │ (基准)     │ Analyzer      │ (可视化)      │
│          │            │ (触发分析)     │               │
├──────────┴───────────┴───────────────┴───────────────┤
│            AgentExecutor (执行器接口)                 │
├────────────────────┬─────────────────────────────────┤
│  RealAgentExecutor │  MockAgentExecutor              │
│  (真实 LLM 调用)    │  (模拟执行, 用于开发测试)         │
├────────────────────┴─────────────────────────────────┤
│              SkillsLoader (技能加载器)                │
├──────────────────────────────────────────────────────┤
│              skills/ (技能目录)                       │
│  ├── weather/SKILL.md + evals/evals.json             │
│  ├── github/SKILL.md                                 │
│  └── ...                                             │
└──────────────────────────────────────────────────────┘
```

### 模块职责

| 模块          | 文件                          | 职责                |
| ----------- | --------------------------- | ----------------- |
| 技能加载器       | `skills_loader.py`          | 扫描、解析、加载 SKILL.md |
| LoadSkill工具 | `load_skill_tool.py`        | Agent 可调用的技能加载工具  |
| 评估框架        | `skill_evals.py`            | 定义断言类型、执行评估       |
| 基准测试        | `skill_benchmark.py`        | 多配置对比、迭代管理、结果聚合   |
| 触发分析        | `skill_trigger_analyzer.py` | 分析描述质量、优化触发       |
| HTML报告      | `eval_viewer.py`            | 生成交互式可视化报告        |
| 真实执行器       | `real_agent_executor.py`    | 调用 LLM API 真实执行   |

***

## 3. 核心模块 API 说明

### 3.1 SkillsLoader - 技能加载器

```python
from skills_loader import SkillsLoader
from pathlib import Path

loader = SkillsLoader(Path("skills"))

# 列出所有技能
loader.list_skills()  # ['code-tools', 'github', 'weather', ...]

# 获取技能内容（正文）
loader.get_content("weather")  # <skill name="weather">...</skill>

# 构建技能摘要（用于 system prompt）
loader.build_skills_summary()

# 获取 always 技能
loader.get_always_skills()  # ['summarize']

# 为上下文加载多个技能
loader.load_skills_for_context(["weather", "github"])
```

### 3.2 SkillEvals - 评估测试框架

支持 5 种断言类型：

| 类型             | 参数                             | 说明        |
| -------------- | ------------------------------ | --------- |
| `contains`     | `substring`, `case_sensitive`  | 输出包含指定子串  |
| `contains_all` | `substrings`, `case_sensitive` | 输出包含所有子串  |
| `not_contains` | `substring`                    | 输出不包含指定子串 |
| `regex`        | `pattern`, `case_insensitive`  | 输出匹配正则    |
| `length`       | `min_length`, `max_length`     | 输出长度在范围内  |

```python
from skill_evals import SkillEvals

evals = SkillEvals(Path("skills"))

# 创建评估用例
evals.create_eval_file("weather", [
    {
        "id": 1,
        "name": "basic_query",
        "prompt": "北京今天天气",
        "expected_output": "天气信息",
        "assertions": [
            {"type": "contains", "name": "has_weather", "substring": "天气"},
            {"type": "regex", "name": "has_temp", "pattern": "\\d+°?C"},
            {"type": "length", "name": "not_empty", "min_length": 10}
        ]
    }
])

# 加载评估
eval_cases = evals.load_evals("weather")

# 评估输出
results = evals.evaluate_output(eval_cases[0], "北京今天：⛅️ +14°C")
for r in results:
    print(f"{r.assertion_name}: {'✓' if r.passed else '✗'} - {r.evidence}")
```

### 3.3 SkillBenchmark - 基准测试

```python
from skill_benchmark import SkillBenchmark, BenchmarkConfig
from real_agent_executor import create_default_executor

executor = create_default_executor(Path("skills"))
benchmark = SkillBenchmark(
    skills_dir=Path("skills"),
    workspace_dir=Path("skill-workspace"),
    executor=executor  # 注入真实执行器
)

# 定义对比配置
configs = [
    BenchmarkConfig(name="with_skill", skill_name="weather"),
    BenchmarkConfig(name="without_skill", baseline=True)
]

# 运行基准测试
summary = benchmark.run_benchmark("weather", configs, iteration=1)

print(summary.pass_rates)     # {'with_skill': 66.7, 'without_skill': 66.7}
print(summary.delta_pass_rate) # 0.0

# A/B 测试两个技能版本
summary = benchmark.run_ab_test("weather", "weather_v1", "weather_v2")

# 对比迭代
comparison = benchmark.compare_iterations("weather", 1, 2)
# {'pass_rate_change': {'with_skill': {'iteration_a': 66.7, 'iteration_b': 100.0, 'delta': 33.3}}}
```

### 3.4 RealAgentExecutor - 真实执行器

```python
from real_agent_executor import RealAgentExecutor

executor = RealAgentExecutor(
    api_key="your-api-key",
    base_url="https://apihub.agnes-ai.com/v1",
    model="agnes-1.5-flash",
    skills_dir=Path("skills"),
    max_tokens=1024,
    temperature=0.0  # 评估时用 0 保证可复现
)

# with_skill: 将技能内容注入 system prompt
output, tokens, duration = executor.execute("北京天气", skill_name="weather")

# baseline: 不注入技能
output, tokens, duration = executor.execute("北京天气", skill_name=None)
```

**注入机制**：with\_skill 时，技能正文被注入到 system prompt 中：

```
你是一个有帮助的 AI 助手。请根据用户的问题给出准确、简洁的回答。

=== 已加载技能: weather ===
# 天气查询技能
使用免费服务查询天气...
=== 技能结束 ===
请在回答时参考以上技能知识。
```

### 3.5 SkillTriggerAnalyzer - 触发优化

```python
from skill_trigger_analyzer import SkillTriggerAnalyzer

analyzer = SkillTriggerAnalyzer(Path("skills"))

sample_prompts = [
    "北京天气怎么样",
    "帮我查天气",
    "写一个排序算法",  # 不应触发
]

# 分析触发质量
analysis = analyzer.analyze_trigger("weather", sample_prompts)
print(f"质量分数: {analysis.quality_score}/100")
print(f"假阳性: {analysis.false_positives}")  # 不该触发却触发了
print(f"假阴性: {analysis.false_negatives}")  # 该触发却没触发

# 自动优化描述
result = analyzer.optimize_description("weather", sample_prompts)
print(f"原始: {result['original_description']}")
print(f"优化: {result['optimized_description']}")

# 批量分析所有技能
results = analyzer.batch_analyze(sample_prompts)
for r in results:
    print(f"{r.skill_name}: {r.quality_score}/100")
```

### 3.6 EvalViewer - 可视化报告

```python
from eval_viewer import EvalViewer

viewer = EvalViewer(Path("skill-workspace"))

# 生成 HTML 报告
html = viewer.generate_html("weather", iteration=4)

# 保存到文件
path = viewer.save_html("weather", iteration=4)
# → skill-workspace/weather/iteration-4/eval-viewer.html
```

HTML 报告包含三个标签页：

- **Summary** - 通过率、Token、耗时汇总
- **Detailed Results** - 每个评估用例的输出和断言详情
- **Comparison** - 迭代间对比

***

## 4. 使用指南

### 4.1 为现有技能添加评估

1. 在技能目录下创建 `evals/evals.json`：

```
skills/
└── my-skill/
    ├── SKILL.md
    └── evals/
        └── evals.json    ← 新建
```

1. 编写评估用例：

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "name": "basic_test",
      "prompt": "用户会问的问题",
      "expected_output": "期望输出的描述",
      "assertions": [
        {"type": "contains", "name": "check_keyword", "substring": "关键词"}
      ]
    }
  ]
}
```

1. 运行评估：

```python
from skill_benchmark import SkillBenchmark, BenchmarkConfig
from real_agent_executor import create_default_executor

executor = create_default_executor(Path("skills"))
benchmark = SkillBenchmark(Path("skills"), Path("skill-workspace"), executor=executor)

configs = [
    BenchmarkConfig(name="with_skill", skill_name="my-skill"),
    BenchmarkConfig(name="without_skill", baseline=True)
]

summary = benchmark.run_benchmark("my-skill", configs, iteration=1)
```

### 4.2 创建新技能

1. 创建技能目录和 SKILL.md：

```markdown
---
name: my-skill
description: 技能描述，包含触发关键词和适用场景
---

# 技能标题

具体指令和知识内容...
```

1. 添加评估用例（见 4.1）
2. 运行迭代评估直到满意

### 4.3 迭代优化流程

```python
# Iteration 1: 初次评估
summary_v1 = benchmark.run_benchmark("my-skill", configs, iteration=1)

# 分析失败原因，优化技能或断言
# ...

# Iteration 2: 重新评估
summary_v2 = benchmark.run_benchmark("my-skill", configs, iteration=2)

# 对比迭代
comparison = benchmark.compare_iterations("my-skill", 1, 2)
# 查看 pass_rate_change.delta
```

***

## 5. 最佳实践

### 5.1 断言设计

**好的断言：**

```json
{"type": "regex", "name": "has_temperature", "pattern": "\\d+°?C"}
{"type": "contains_all", "name": "has_city_and_temp", "substrings": ["北京", "度"]}
```

**不好的断言：**

```json
{"type": "contains", "name": "has_weather", "substring": "天气"}
```

问题：baseline 输出"我无法提供天气数据"也会通过，无法区分。

**原则：** 断言应该能区分"给出了有效数据"和"解释了为什么做不到"。

### 5.2 评估用例设计

- **覆盖典型场景**：至少3个用例覆盖核心功能
- **包含边界情况**：空输入、极端输入、无关输入
- **prompt 要真实**：用用户真正会问的问法
- **断言要客观**：避免主观判断，用可程序验证的条件

### 5.3 迭代心态

- **Iteration 1 的 100% 通过率是警告**：很可能是断言太宽松
- **关注 Delta**：with\_skill 应该比 without\_skill 表现更好
- **耗时也是指标**：技能通常让回答更快（直接给答案 vs 长篇解释）
- **断言也需要迭代**：发现误判时优先修断言，而不是改技能迁就断言

### 5.4 技能描述优化

描述是触发的唯一依据，遵循 Anthropic 的建议：

- **要"推一把"**：不要只写功能，还要写触发场景
- **包含具体关键词**：用户可能用的词都要覆盖
- **避免过度宽泛**：太宽会导致假阳性

```yaml
# 不好
description: 查询天气

# 好
description: 获取当前天气和天气预报（无需API密钥）。当用户询问天气、温度、
降雨、风速等气象信息时使用此技能，即使用户没有明确说"天气"二字。
```

### 5.5 可维护性建议

- 评估用例和技能一起版本管理
- 每次修改技能后运行一次基准测试
- 保留历史迭代数据用于回归对比
- 模型升级后重新运行所有技能的评估

***

## 6. 真实迭代案例

以下是 weather 技能的真实迭代过程，展示框架如何发现和解决问题。

### Iteration 3: 初始评估

**断言设计：**

```json
{"type": "contains", "name": "mentions_weather", "substring": "天气"}
{"type": "length", "name": "min_length", "min_length": 20}
```

**结果：**

| 配置             | Pass Rate | 问题                                           |
| -------------- | --------- | -------------------------------------------- |
| with\_skill    | 66.7%     | 输出 `北京今天：⛅️ +14°C` 只有13字符，不满足 min\_length=20 |
| without\_skill | 100%      | 输出 `我无法提供实时的天气数据...` 包含"天气"且足够长              |

**Delta: -33.3%** — 技能反而让通过率下降了？

### 分析

问题不在技能，而在断言：

1. `contains "天气"` 误判了 baseline 的"我无法提供天气数据"为通过
2. `min_length=20` 惩罚了 with\_skill 的简洁有效输出

### Iteration 4: 优化断言

**改进的断言：**

```json
{"type": "contains", "name": "mentions_weather", "substring": "天气"}
{"type": "regex", "name": "has_temperature", "pattern": "\\d+°?C|温度|度"}
{"type": "length", "name": "min_length", "min_length": 10}
```

新增温度检测正则，降低最小长度要求。

**结果：**

| 配置             | Pass Rate | 变化     |
| -------------- | --------- | ------ |
| with\_skill    | 66.7%     | 持平     |
| without\_skill | 66.7%     | -33.3% |

**Delta: 0.0%** — 现在公平了。

### 关键洞察

| 指标           | with\_skill | without\_skill | 说明          |
| ------------ | ----------- | -------------- | ----------- |
| Pass Rate    | 66.7%       | 66.7%          | 断言仍需优化      |
| Avg Tokens   | 748         | 495            | 技能注入增加上下文   |
| Avg Duration | 11.1s       | 25.2s          | **技能快2.3倍** |

技能的真正价值体现在**耗时**上：with\_skill 直接给出天气数据（11s），baseline 只能长篇解释无法提供数据（25s）。

### 下一步迭代方向

1. 增加断言检测"是否提供了实际数据"vs"是否解释了无法提供"
2. 将耗时作为评估指标之一
3. 扩展评估用例数量
4. 测试不同模型的技能效果差异

***

## 附录

### 参考

- [Anthropic Skill Creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [Improving skill-creator (Blog)](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)
- [Anthropic Skills Repo](https://github.com/anthropics/skills)

### 评估文件 JSON Schema

```json
{
  "skill_name": "string",
  "created_at": "ISO8601",
  "evals": [
    {
      "id": "number",
      "name": "string",
      "prompt": "string",
      "expected_output": "string",
      "files": ["string"],
      "assertions": [
        {
          "type": "contains|contains_all|not_contains|regex|length",
          "name": "string",
          "substring": "string (for contains/not_contains)",
          "substrings": ["string (for contains_all)"],
          "pattern": "string (for regex)",
          "min_length": "number (for length)",
          "max_length": "number (for length)",
          "case_sensitive": "boolean",
          "case_insensitive": "boolean"
        }
      ]
    }
  ]
}
```

***

## 7. 技能管理与 Preset 体系

### 7.1 问题背景

当技能库规模从十几个增长到 300+，传统逐个管理方式遇到三个核心问题：

| 问题        | 影响         | 典型症状                                                    |
| --------- | ---------- | ------------------------------------------------------- |
| **上下文膨胀** | 系统提示词占用过多  | 数百个技能摘要挤占工作台，模型注意力分散                                    |
| **误触发率高** | 不相关技能被加载   | 简短的关键词命中多个技能，浪费 token                                   |
| **维护成本高** | 重复/相似技能难识别 | 同一功能 2-3 个变体（`gmail`/`email-skill-2`/`imap-smtp-email`） |

**解决方案**：引入**中央技能库 + Preset 预设分组**的分层管理架构。

### 7.2 核心概念

#### 7.2.1 三层架构

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: 中央技能库 (~/.skills-manager/skills/)                  │
│  - 技能原件统一存储                                               │
│  - 302 个技能，零重复                                              │
│  - 文件名即唯一标识                                               │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: Preset 预设 (SQLite: scenarios + scenario_skills)        │
│  - 按使用场景分组                                                  │
│  - 27 个 Preset 覆盖 100% 技能                                    │
│  - 切换 Preset = 批量切换技能集                                    │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: Agent 工作目录 (~/.claude/skills/, ~/.cursor/skills/...)  │
│  - 软链接或复制模式                                                │
│  - 同一个中央库可同步到多个 Agent                                   │
└─────────────────────────────────────────────────────────────────┘
```

#### 7.2.2 Preset 生命周期

```
[中央库]  ──install──>  [Preset: 场景A]  ──apply──>  [Agent A: 已加载]
                           │
                           └──apply──>  [Agent B: 已加载]
```

**关键设计**：

- 一个技能可属于多个 Preset（如 `gmail` 同时在"通讯协作"和"邮件增强"中）
- 切换 Preset 是**一次性复制**，不是实时同步
- 禁用技能是"软删除"：保留在中央库但停止写入 Agent 目录

#### 7.2.3 存储结构（SQLite）

skills-manager 使用 SQLite (`~/.skills-manager/skills-manager.db`) 存储元数据：

```sql
-- 技能表
CREATE TABLE skills (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    source_type TEXT,    -- 'git' | 'local' | 'skillssh' | 'import'
    source_ref TEXT,     -- Git URL 或本地路径
    central_path TEXT,   -- 中央库路径
    enabled INTEGER,     -- 0/1
    ...
);

-- Preset 表（内部叫 scenario，向后兼容）
CREATE TABLE scenarios (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    sort_order INTEGER
);

-- Preset-Skill 关联表
CREATE TABLE scenario_skills (
    scenario_id TEXT,
    skill_id TEXT,
    added_at INTEGER,
    sort_order INTEGER,
    PRIMARY KEY (scenario_id, skill_id)
);

-- 当前激活的 Preset
CREATE TABLE active_scenario (
    key TEXT PRIMARY KEY,
    scenario_id TEXT
);
```

### 7.3 27 个 Preset 全景

按"先有 Preset，再有 Skill"原则，Preset 数量应与项目类型数量相当（约 20-30）。**过多 = 切换成本上升；过少 = 粒度太粗**。

| 类别     | Preset  | 数量 | 典型技能                                                    |
| ------ | ------- | -- | ------------------------------------------------------- |
| **开发** | Web开发   | 13 | frontend-dev, vercel-deploy, cloudflare                 |
| <br /> | 移动开发    | 8  | android-native-dev, flutter-dev, wechat-miniprogram     |
| <br /> | 开发运维    | 18 | cli-anything-hub, web-performance-audit, diagnose       |
| **内容** | 文档处理    | 12 | docx, pdf, xlsx, pptx-generator                         |
| <br /> | 内容创作    | 10 | content-creator, novel-writer, humanizer                |
| <br /> | 写作出版    | 16 | novel, khazix-writer, wechat-publisher                  |
| <br /> | 音视频     | 10 | openai-whisper, remotion-video-toolkit, nano-banana-pro |
| <br /> | 设计创意    | 8  | figma, canvas-design, infographic-maker                 |
| **研究** | 研究分析    | 10 | deep-research, arxiv-reader, perplexity, tavily         |
| <br /> | 教育学习    | 11 | academic-tutor, study-planner, teachany                 |
| **商业** | 金融数据    | 8  | stock-analysis, futuapi, macro-monitor                  |
| <br /> | 营销增长    | 12 | growth-engine, seo-ops, sales-pipeline                  |
| <br /> | 电商运营    | 12 | admapix, ecomseer, wechatpay-product-coupon             |
| <br /> | 法律金融    | 7  | legal-logic-analysis, tencent-esign-contract            |
| **生活** | 出行生活    | 9  | weather, 12306, didi-ride-skill                         |
| <br /> | 出行交通    | 11 | flight-tracker, meituan-travel, aviation-weather        |
| **协作** | 通讯协作    | 7  | gmail, dingtalk-unified, lark-unified                   |
| <br /> | 邮件增强    | 9  | imap-smtp-email, gog, porteden-email                    |
| <br /> | 效率工具    | 23 | apple-notes, obsidian, handoff, summarize               |
| <br /> | 云存储阅读   | 10 | baidu-drive, kdocs, weread-skills                       |
| **系统** | Agent系统 | 25 | agent-mbti, persona-switch, capability-evolver          |
| <br /> | 浏览器自动化  | 6  | browser, smooth-browser, web-scraper                    |
| <br /> | 浏览器扩展   | 7  | playwright-browser-automation, stagehand-browser-cli    |
| <br /> | 腾讯生态    | 29 | andonq, cloudbase, tencent-docs, smart-page             |
| <br /> | 技能管理    | 6  | skill-creator, mcp-builder, mcporter                    |
| **信息** | 搜索资讯    | 6  | multi-search-engine, aihot, tech-news-digest            |

**总计：302 个技能 → 27 个 Preset，零重复。**

### 7.4 Preset 设计原则

#### 7.4.1 划分依据

| 维度       | 依据                    | 反例               |
| -------- | --------------------- | ---------------- |
| **使用场景** | "我要做 X" → 激活 X Preset | 按字母分组（无意义）       |
| **互斥优先** | 同一项目类型不会同时用           | 全部塞进 "Default"   |
| **粒度适中** | 单 Preset 5-30 个技能     | 100+ 技能 = 粒度太粗   |
| **可组合**  | 跨场景技能可重复归属            | 强制技能只属于一个 Preset |

#### 7.4.2 命名规范

- **中文名 + 英文 key**：`Web开发` (key: `web-dev`)
- **场景导向而非工具导向**：`内容创作` 而非 `写作工具`
- **避免厂商名作为主分类**：`腾讯生态` 是子集不是主轴

#### 7.4.3 粒度判断

```
302 个技能
  ├── 1 个 Preset      → 粒度太粗，用户要选 300+ 技能
  ├── 100 个 Preset    → 粒度太细，难记住
  ├── 20-30 个 Preset  → ✅ 黄金区间（本次采用 27）
  └── 0 个 Preset      → 默认全加载，上下文爆炸
```

### 7.5 关联管理

#### 7.5.1 关联关系类型

| 关系      | 说明               | SQL 实现                       |
| ------- | ---------------- | ---------------------------- |
| **1:N** | 一个技能属于多个 Preset  | `scenario_skills` 联合主键       |
| **N:1** | 多个技能归属同一 Preset  | 同上                           |
| **M:N** | Preset 间通过共享技能关联 | 查询 `WHERE skill_id IN (...)` |

#### 7.5.2 共享技能示例

`handoff`（对话交接）同时属于：

- **效率工具**（知识管理场景）
- **Agent系统**（能力工具场景）

这种共享是有意为之的：避免强制用户选择"我到底用哪个 Preset"。

#### 7.5.3 冲突处理

如果一个 Preset 启用 + 另一个 Preset 禁用同一技能，**最后同步的 Preset 获胜**。避免方法是：在 Preset 设计时考虑互斥，或使用 `scenario_skill_tools` 表做精细控制。

### 7.6 自动化管理脚本

#### 7.6.1 技能扫描

```python
# scan_skills.py
import sqlite3

DB = r"C:\Users\biren\.skills-manager\skills-manager.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name, description FROM skills ORDER BY name")
for name, desc in cur.fetchall():
    print(f"{name}|{(desc or '')[:80]}")
conn.close()
```

#### 7.6.2 自动分类

```python
# classify_skills.py - 基于关键词的自动分类
CATEGORIES = {
    "web-dev": ["frontend", "vercel", "react", "html", "css"],
    "docs":     ["docx", "pdf", "xlsx", "markdown"],
    "research": ["research", "arxiv", "perplexity"],
    # ... 更多类别
}

def classify(name, desc):
    for cat_id, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in name.lower() or kw in (desc or "").lower():
                return cat_id
    return "other"
```

#### 7.6.3 批量创建 Preset

```python
# create_presets.py
import sqlite3, uuid, time

DB = r"C:\Users\biren\.skills-manager\skills-manager.db"
NOW = int(time.time() * 1000)

PRESETS = {
    "web-dev": {
        "label": "Web开发",
        "skills": ["frontend-dev", "vercel-deploy", ...]
    },
    # ...
}

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 读取 skill name → id 映射
cur.execute("SELECT id, name FROM skills")
name_to_id = {name: sid for sid, name in cur.fetchall()}

for sort_idx, (preset_id, preset) in enumerate(PRESETS.items(), 1):
    scenario_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO scenarios (id, name, sort_order, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (scenario_id, preset["label"], sort_idx, NOW, NOW)
    )
    for skill_idx, skill_name in enumerate(preset["skills"]):
        skill_id = name_to_id.get(skill_name)
        if skill_id:
            cur.execute(
                "INSERT OR IGNORE INTO scenario_skills "
                "(scenario_id, skill_id, added_at, sort_order) VALUES (?, ?, ?, ?)",
                (scenario_id, skill_id, NOW, skill_idx)
            )
conn.commit()
conn.close()
```

#### 7.6.4 验证覆盖率

```python
# verify_presets.py
cur.execute("""
    SELECT s.name, COUNT(ss.skill_id) as count
    FROM scenarios s
    LEFT JOIN scenario_skills ss ON s.id = ss.scenario_id
    GROUP BY s.id
    ORDER BY s.sort_order
""")

# 检查未分配技能
cur.execute("""
    SELECT name FROM skills
    WHERE id NOT IN (SELECT skill_id FROM scenario_skills)
""")
```

### 7.7 维护流程

#### 7.7.1 日常维护

| 任务     | 频率    | 操作                                                  |
| ------ | ----- | --------------------------------------------------- |
| 检查技能更新 | 每周    | `skills-manager-cli skills check --all`             |
| 同步更新   | 按需    | `skills-manager-cli skills update --all`            |
| 重新分类   | 新增技能时 | 更新 `classify_skills.py` 关键词                         |
| 备份数据库  | 重要操作前 | `Copy-Item skills-manager.db skills-manager.db.bak` |

#### 7.7.2 备份与回滚

```powershell
# 备份
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
Copy-Item "C:\Users\biren\.skills-manager\skills-manager.db" `
          "C:\Users\biren\.skills-manager\skills-manager.db.bak.$ts"

# 回滚
Copy-Item "C:\Users\biren\.skills-manager\skills-manager.db.bak.20260626_120000" `
          "C:\Users\biren\.skills-manager\skills-manager.db" -Force
```

#### 7.7.3 添加新 Preset

```python
new_preset = {
    "my-new-preset": {
        "label": "我的新场景",
        "description": "做什么用的",
        "skills": ["skill-a", "skill-b", "skill-c"],
    }
}
# 追加到 create_presets.py，重新运行
```

#### 7.7.4 添加新技能到 Preset

```python
cur.execute("SELECT id FROM scenarios WHERE name = ?", ("Web开发",))
scenario_id = cur.fetchone()[0]

cur.execute("SELECT id FROM skills WHERE name = ?", ("new-skill",))
skill_id = cur.fetchone()[0]

cur.execute(
    "INSERT OR IGNORE INTO scenario_skills (scenario_id, skill_id, added_at, sort_order) "
    "VALUES (?, ?, ?, ?)",
    (scenario_id, skill_id, int(time.time() * 1000), 999)
)
```

### 7.8 常见问题与解决方案

#### 7.8.1 安装后技能不显示

**症状**：技能在中央库中，但 Agent 工作目录没有

**根因**：默认安装是 library-only，需要 `--sync` 或添加到 Preset

**解决**：

```bash
skills-manager-cli skills install <skill> --sync
# 或
skills-manager-cli presets add-skill <preset> <skill>
skills-manager-cli skills sync
```

#### 7.8.2 没有活动 Preset

**症状**：`skills sync` 报错

**解决**：

```bash
skills-manager-cli presets list           # 列出所有 Preset
skills-manager-cli presets apply "Default"  # 激活一个
```

#### 7.8.3 导入的技能无法更新

**症状**：`npx skills add` 安装的技能不能 `update`

**根因**：缺乏 Git 源元数据，被识别为 `source_type=local`

**解决**：

```bash
skills-manager-cli skills adopt ~/.claude/skills/my-skill \
  --git-url https://github.com/me/my-skill --git-subpath ""
```

#### 7.8.4 Windows 软链接权限问题

**症状**：`symlink_dir` 失败

**解决**：

1. 启用开发者模式（设置 → 隐私和安全 → 开发者选项）
2. 或使用管理员权限运行终端
3. skills-manager 已自动降级为 junction 或 copy

#### 7.8.5 重复技能

**症状**：多个功能相同的技能（如 `gmail` + `email-skill` + `imap-smtp-email`）

**解决方案**：

- **保留全部**：分别归属不同 Preset，按需选用
- **标记偏好**：用 tag 区分（`tag: email-primary` vs `tag: email-legacy`）
- **删除重复**：手动 uninstall 一个，更新元数据

#### 7.8.6 数据库锁定

**症状**：`database is locked`

**根因**：桌面应用和 CLI 同时写 SQLite

**解决**：

- skills-manager 已设 `busy_timeout=5s`，会自动重试
- 避免同时运行桌面端和 CLI
- CLI 修改后重启桌面端刷新内存缓存

### 7.9 性能与最佳实践

#### 7.9.1 性能指标

| 指标          | 目标            | 实际                       |
| ----------- | ------------- | ------------------------ |
| Preset 切换时间 | < 1s          | \~200ms（SQLite 写入）       |
| 同步到 Agent   | < 5s          | 取决于技能数，30个技能 \~3s        |
| 系统提示词大小     | < 2000 tokens | 单 Preset 摘要 \~500 tokens |
| 数据库大小       | < 10MB        | 当前 \~2MB                 |

#### 7.9.2 最佳实践

1. **预设粒度适中**：20-30 个 Preset，5-30 个技能/Preset
2. **跨场景技能共享**：允许一个技能属于多个 Preset
3. **定期重构**：每季度审视一次 Preset 划分
4. **保留历史**：所有脚本和数据库备份都加时间戳
5. **避免大杂烩**：不要为了"全"把无关技能塞进一个 Preset
6. **结合软链接**：项目级用 symlink + 中央库用 Preset
7. **优先按需加载**：单个技能可直接 `load_skill` 而不必走 Preset

#### 7.9.3 避免的反模式

| 反模式                      | 问题     | 改进           |
| ------------------------ | ------ | ------------ |
| 一个 Default Preset 包含所有技能 | 失去分组意义 | 拆分为场景 Preset |
| 100+ 技能的大 Preset         | 等同于没分组 | 按功能再细分       |
| Preset 按字母命名             | 难记忆    | 按场景命名        |
| 技能不允许跨 Preset            | 重复维护   | 允许共享         |
| 没有 tag                   | 难以筛选   | 添加 tag 字段    |

### 7.10 完整工作流示例

```python
# 1. 扫描所有技能
skills = scan_all_skills()

# 2. 自动分类
categorized = classify_by_keywords(skills)

# 3. 手动审核未分类技能
review_uncategorized(categorized["other"])

# 4. 创建 Preset
create_presets_batch(PRESET_DEFINITIONS)

# 5. 验证覆盖率
verify_assignment_coverage()

# 6. 备份数据库
backup_database()
```

### 7.11 与 symlink 模式的对比

| 维度       | Preset 模式               | symlink 模式（宝玉方案） |
| -------- | ----------------------- | ---------------- |
| **适用场景** | 多 Agent 同步              | 项目内单 Agent       |
| **物理位置** | 中央库                     | 开源项目仓库           |
| **更新机制** | `skills update --all`   | `git pull`       |
| **跨平台**  | Windows 软链接降级为 junction | 同左               |
| **粒度**   | 技能级别                    | 技能级别             |
| **可发现性** | 桌面端可视化                  | 命令行              |

**最佳实践**：两者结合使用

- **Preset** 用于"激活什么技能"
- **symlink** 用于"技能物理存放位置"

### 7.12 扩展性

#### 7.12.1 水平扩展

如果技能增长到 1000+：

- 按领域再分二级 Preset（如 `开发/前端`、`开发/后端`）
- 引入子分组（folder-like）

#### 7.12.2 垂直扩展

单 Preset 内部可以：

- 用 tag 做更细粒度的开关
- 用 `scenario_skill_tools` 做按工具的独立控制
- 用 `active_scenario` 做"上次激活的记忆"

#### 7.12.3 跨机器同步

```bash
# 备份到 Git
cd ~/.skills-manager
git init
git remote add origin git@github.com:me/skills-backup.git
git add .
git commit -m "chore: update skills"
git push
```

> **注意**：SQLite 数据库本身不进 Git 备份（可通过扫描重建），但 Preset 关联关系如果走 Git Backup 功能会自动持久化。

***

