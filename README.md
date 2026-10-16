# Skill Framework - 可迭代的 AI Agent 技能系统

一个完整的 AI Agent 技能（Skill）管理框架，支持技能的**创建、加载、评估、基准测试和迭代优化**。通过真实 LLM API 执行评估，让技能从"看起来能用"变成"验证过能用"。

## 核心特性

- **技能加载系统** - 按需加载，渐进式上下文管理
- **评估测试框架** - 5种断言类型，JSON驱动的测试用例
- **基准测试** - 三方对比：without_skill / with_skill（静态注入）/ agentic（技能自主加载）
- **Agentic 执行器** - 真 tool-use loop：模型通过 `load_skill` 自主决定加载哪个技能，含指数退避重试、只读工具重复调用短路、轮数 / token 预算 / 墙钟三重上限与无工具收尾降级
- **触发优化** - 分析假阳性/假阴性，自动优化描述
- **可视化报告** - 交互式HTML报告，一键查看迭代对比
- **真实执行** - 集成 OpenAI 兼容 API（默认 Agnes AI）

## 快速开始

### 安装依赖

```bash
pip install openai pyyaml
```

### 运行真实评估

```bash
python run_real_eval.py          # 两方对比（with_skill vs without_skill）
python run_agentic_eval.py       # 三方对比（agentic / with_skill / without_skill）
python run_agentic_eval.py smoke # 单条 agentic 执行，打印完整轨迹
```

这会使用 Agnes AI API 对 weather 技能运行真实评估，生成基准测试报告和 HTML 可视化。

### 查看报告

打开 `skill-workspace/weather/iteration-N/eval-viewer.html` 查看交互式评估报告。

## 项目结构

```
├── skills/                    # 技能目录
│   └── weather/
│       ├── SKILL.md           # 技能定义
│       └── evals/
│           └── evals.json     # 评估用例
├── skill-workspace/           # 评估工作区（自动生成）
│   └── weather/
│       └── iteration-N/       # 每次迭代的结果
│           ├── benchmark.json
│           ├── benchmark.md
│           └── eval-viewer.html
├── skills_loader.py           # 技能加载器
├── load_skill_tool.py         # LoadSkill 工具
├── skill_evals.py             # 评估测试框架
├── skill_benchmark.py         # 基准测试系统
├── skill_trigger_analyzer.py  # 触发优化分析器
├── eval_viewer.py             # HTML 报告生成器
├── agentic_executor.py        # agentic loop 执行器（技能自主加载 + 退避重试 + 轨迹）
├── real_agent_executor.py     # 静态注入执行器（单次调用）
├── run_real_eval.py           # 两方对比评估脚本
├── run_agentic_eval.py        # 三方对比评估脚本
└── test_agentic_executor.py   # loop 逻辑测试（mock client，16 用例）
```

## 迭代工作流

```
1. 编写技能 (SKILL.md)
       ↓
2. 创建评估用例 (evals.json)
       ↓
3. 运行基准测试（三方对比，agentic 配置逐条记录技能加载轨迹）
       ↓
4. 查看报告 → 分析失败
       ↓
5. 优化技能或断言
       ↓
6. 重新运行 → 对比迭代
       ↻ 重复直到满意
```

## 实测：单次调用 vs agentic loop（2026-09-28）

weather 技能 3 个用例，agnes-3.0-flash，数据见 `skill-workspace/weather/iteration-6/`：

| 配置 | 通过率 | 均 Tokens | 均耗时 | 均轮数 | 均工具调用 |
|---|---|---|---|---|---|
| agentic（自主加载） | 100.0% | 1556 | 11.1s | 1.7 | 0.7 |
| with_skill（静态注入） | 66.7% | 609 | 3.0s | 1.0 | 0.0 |
| without_skill | 66.7% | 411 | 13.6s | 1.0 | 0.0 |

**结论与边界（如实标注）**：

- agentic loop 已验证可用：3/3 以 `final_answer` 收尾；2 个用例自主加载了 weather 技能，1 个判断无需加载。
- **本轮差异不足以支撑"技能有效"的结论**：`with_skill` 与 `without_skill` 通过率相同（+0.0pp），
  且出现反向差异（`weather_query_location` 在静态注入下未通过、无技能反而通过）——
  说明现有断言区分度不足，模型常识即可覆盖大部分用例。下一轮应换「技能含模型不具备的独有知识」的任务。
- 成本：agentic 的 token ≈ 基线 2.6×（多轮调用重复发送上下文），这是自主加载的固有权衡。
- 稳定性：免费额度会触发 429；执行器内置指数退避 + 随机抖动（对齐 `agent-fault-tolerance-design`），实测一次重试后恢复。
- 限流会污染跑批（iteration-5 有 5/9 因 429 失败，数据不可用），跑批前建议确认额度或加大退避参数。

## 配置

LLM 配置默认使用 Agnes AI，可通过环境变量覆盖：

```bash
export AGNES_API_KEY="your-api-key"
export AGNES_BASE_URL="https://apihub.agnes-ai.com/v1"
export AGNES_MODEL="agnes-3.0-flash"   # agnes-1.5-flash 已于 2026-09 下架（503 model_not_found）
```

也支持任何 OpenAI 兼容的 API（需支持 function calling）。

> 探测某模型是否支持 function calling：`python probe_api_capabilities.py`

## 文档

- [TECHNICAL_DOC.md](TECHNICAL_DOC.md) - 评估 / 基准测试框架的完整技术文档
- [SKILL_GOVERNANCE.md](SKILL_GOVERNANCE.md) - Skill 治理体系设计文档：四层治理 + 快慢双路径检索 + L0 项目级裁剪落地记录 + 双重挤压下的生命周期管理

## License

MIT
