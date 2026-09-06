# Skill Framework - 可迭代的 AI Agent 技能系统

一个完整的 AI Agent 技能（Skill）管理框架，支持技能的**创建、加载、评估、基准测试和迭代优化**。通过真实 LLM API 执行评估，让技能从"看起来能用"变成"验证过能用"。

## 核心特性

- **技能加载系统** - 按需加载，渐进式上下文管理
- **评估测试框架** - 5种断言类型，JSON驱动的测试用例
- **基准测试** - with_skill vs without_skill 真实对比
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
python run_real_eval.py
```

这会使用 Agnes AI API 对 weather 技能运行真实评估，生成基准测试报告和 HTML 可视化。

### 查看报告

打开 `skill-workspace/weather/iteration-4/eval-viewer.html` 查看交互式评估报告。

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
├── real_agent_executor.py     # 真实 LLM 执行器
└── run_real_eval.py           # 端到端评估脚本
```

## 迭代工作流

```
1. 编写技能 (SKILL.md)
       ↓
2. 创建评估用例 (evals.json)
       ↓
3. 运行基准测试 (with_skill vs without_skill)
       ↓
4. 查看报告 → 分析失败
       ↓
5. 优化技能或断言
       ↓
6. 重新运行 → 对比迭代
       ↻ 重复直到满意
```

## 配置

LLM 配置默认使用 Agnes AI，可通过环境变量覆盖：

```bash
export AGNES_API_KEY="your-api-key"
export AGNES_BASE_URL="https://apihub.agnes-ai.com/v1"
export AGNES_MODEL="agnes-1.5-flash"
```

也支持任何 OpenAI 兼容的 API。

## 文档

- [TECHNICAL_DOC.md](TECHNICAL_DOC.md) - 评估 / 基准测试框架的完整技术文档
- [SKILL_GOVERNANCE.md](SKILL_GOVERNANCE.md) - Skill 治理体系设计文档：四层治理 + 快慢双路径检索 + L0 项目级裁剪落地记录 + 双重挤压下的生命周期管理

## License

MIT
