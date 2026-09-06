# Skill 治理体系设计文档 — 多而不乱的架构

> 版本：v1.3（2026-09-05 初版 / 2026-09-06 增补第 11 章外部参考、第 12 章 L0 落地记录、第 13 章生命周期层）
> 状态：设计已落地为分散组件，本文档统一收编为体系
> 适用范围：个人 / 小团队的 Agent Skill 库（数百量级，当前 700+）

---

## 1. 问题定义

Skill 库规模增长后，必然出现四个失败模式：

| # | 失败模式 | 表现 |
|---|---------|------|
| F1 | **选不对** | 任务来了，不知道该用哪个 skill；调用了不合适的 skill |
| F2 | **管不住** | 重复安装、来源混乱、多工具（Claude Code / Cursor / TRAE）间不同步 |
| F3 | **改坏了** | 迭代优化时把核心方法论改坏，或核心知识被污染/泄露 |
| F4 | **不进化** | skill 陈旧失效，踩过的坑不沉淀，同类问题反复出现 |

**核心矛盾**：规模 ↑ 必然带来混乱度 ↑。治理目标不是"少"，而是"**多而不乱**"——每个失败模式对应一层治理机制，四层叠加构成完整体系。

---

## 2. 总体架构

```
┌────────────────────────────────────────────────────────────────┐
│                        任务请求（用户输入）                       │
└───────────────┬────────────────────────────────┬───────────────┘
                │ 快路径                          │ 慢路径（兜底）
                ▼                                ▼
┌───────────────────────────┐   ┌────────────────────────────────┐
│ L1 排序层                  │   │ 子Agent 全量检索                 │
│ 多指标综合排序 → Top-N      │   │ 触发条件：复杂任务 / 首轮效果不佳  │
│ 注入 system prompt         │   │ （skill-matcher subagent）       │
└─────────────┬─────────────┘   └───────────────┬────────────────┘
              │                                 │
              ▼                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    L2 存储管理层（skills-manager）                │
│   中央库 ~/.skills-manager/ → Preset 分组 → 软链接分发到各工具     │
│   SQLite: skills-manager.db（单一事实来源 Single Source of Truth）│
└─────────────────────────────┬──────────────────────────────────┘
                              │ 每个 skill 内部
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    L3 分区保护层（每个 skill 内部）                │
│   ┌─────────────────────────────────────────────────────────┐ │
│   │ 不可修改区（核心）           │ 可修改区（外围）              │ │
│   │ SKILL.md 元原则（≤15条）    │ references/*.md 经验卡片     │ │
│   │ 红线 / 方法论骨架           │ 模板 / 示例 / 临时结论         │ │
│   │ 变更需人工确认 + 日期标注    │ 使用中自由迭代                │ │
│   └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────┬──────────────────────────────────┘
                              │ 使用反馈回流
                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    L4 自进化层                                  │
│   使用数据 → 评估基准（with/without 对比）→ 触发分析 → 迭代       │
│   同一问题出现 3 次 → 升级为元原则（不可修改区）                   │
│   新经验与元原则冲突 → 触发元原则修订（带日期标注）                 │
└────────────────────────────────────────────────────────────────┘
```

**一句话总结**：排序解决"入口选择"（调用前），分区解决"写入安全"（迭代时），Manager 解决"物理秩序"（存储分发），自进化解决"时间秩序"（持续有效）；快慢双路径解决"注意力经济"（上下文纯净度）。

---

## 3. L1 排序层：多指标综合排序

### 3.1 为什么必须多指标

任何单一指标都会失真：

- 只看 **使用频率** → 马太效应，新 skill 永远没有曝光机会，长尾价值技能被埋没
- 只看 **star 数** → 社区热度 ≠ 个人场景匹配，热门 skill 可能对你无用
- 只看 **独特性** → 冷门但功能与热门 skill 重叠的会被高估

多指标加权可以在三个维度间互相制衡。

### 3.2 指标定义

| 指标 | 数据来源 | 含义 | 更新频率 |
|------|---------|------|---------|
| `usage_freq` | 调用日志 | 个人实证：最近 N 天该 skill 的触发次数（带时间衰减） | 每次会话 |
| `community_score` | GitHub star / 市场数据 | 社区验证：质量与维护活跃度的代理指标 | 每周 |
| `uniqueness` | skill 间相似度计算 | 不可替代性：与同库其他 skill 的功能距离（越独特分越高） | 安装/更新时 |
| `success_rate` | 评估基准 | 质量：该 skill 触发后任务完成率、with/without 提升比 | 每次评估 |
| `recency` | git log / 更新时间 | 新鲜度：避免陈旧 skill 占据前排 | 每次更新 |

### 3.3 综合分公式

```
score = w1·norm(usage_freq)      # 0.35 个人实证最重
      + w2·norm(community_score) # 0.15 社区验证
      + w3·norm(uniqueness)      # 0.20 不可替代性
      + w4·norm(success_rate)    # 0.20 质量
      + w5·norm(recency)         # 0.10 新鲜度
```

权重设计原则：
- **个人实证 > 社区验证**：自己的使用数据比 star 数更真实
- **独特性权重必须足够高**：防止前排全是"通用但可互相替代"的 skill
- 各指标先归一化（min-max 或 z-score），消除量纲差异

### 3.4 排序结果的用途

1. **system prompt 注入**：Top-N（如 30-50 个）skill 的 name + description 注入上下文，其余不占注意力
2. **冷启动曝光**：新装 skill 给予 `recency` 加成，保证至少 N 次曝光机会后由真实 usage 决定去留
3. **淘汰预警**：长期 score 低于阈值且 usage=0 的 skill，进入"待清理"清单（不自动删除，人工确认）

---

## 4. L2 存储管理层：skills-manager 统一管理

### 4.1 核心原则

- **单一事实来源**：所有 skill 的原始副本只存于中央库 `~/.skills-manager/skills/`，SQLite（`skills-manager.db`）记录全部元数据
- **单一管理入口**：安装 / 更新 / 删除 / 启用禁用 / 标签，全部通过 `skills-manager-cli` 或桌面应用操作，禁止手工散拷
- **项目级最小注入**：项目只通过软链接挂载真正需要的 skill，节约上下文
- **多工具分发**：Preset（预设分组）→ 软链接同步到 Claude Code / Cursor / Codex / TRAE 等各工具的 skills 目录

### 4.2 架构

```
中央库 ~/.skills-manager/skills/（+ skills-manager.db 元数据）
        │
        ├── Preset "Web Dev"     → skill1 ✓, skill2 ✓
        ├── Preset "Code Analysis" → skill2 ✓, skill3 ✓
        └── Preset "Team Core"   → ...
                │
                ▼ 软链接分发
~/.claude/skills/   ~/.cursor/skills/   .trae/...   各项目 .agents/skills/
```

### 4.3 元数据模型（DB schema 扩展）

现有 `skills` 表（id, name, description）基础上扩展：

```sql
ALTER TABLE skills ADD COLUMN category     TEXT;  -- 分类（classify_skills.py 产出）
ALTER TABLE skills ADD COLUMN score        REAL;  -- L1 综合分
ALTER TABLE skills ADD COLUMN usage_freq   INTEGER DEFAULT 0;
ALTER TABLE skills ADD COLUMN community_score REAL DEFAULT 0;
ALTER TABLE skills ADD COLUMN uniqueness   REAL DEFAULT 0;
ALTER TABLE skills ADD COLUMN success_rate REAL DEFAULT 0;
ALTER TABLE skills ADD COLUMN mutable      INTEGER DEFAULT 0;  -- L3: 1=可修改区技能
ALTER TABLE skills ADD COLUMN last_used    TIMESTAMP;
ALTER TABLE skills ADD COLUMN source_url   TEXT;  -- 溯源
```

### 4.4 分类体系

按功能域分类（关键词规则 + 人工校对），当前类目：dev-tools / doc-suite / web-browser / ai-research / design-creative / comm-suite / deploy-cloud 等（见 `classify_skills.py`）。分类用于：

- 浏览导航（人类视角）
- 独特性计算的候选范围缩小（同分类内先比对）
- Preset 的组装单元

---

## 5. L3 分区保护层：可修改区 / 不可修改区

### 5.1 设计动机

自进化（L4）意味着 skill 会被持续修改，但**核心方法论必须稳定**。不设分区，进化过程本身会成为最大的质量风险（一次错误迭代毁掉整个 skill），也防不住核心知识被污染或蒸馏。

### 5.2 分区定义

```
my-skill/
├── SKILL.md              ← 【不可修改区】元原则层
│                            核心方法论骨架、红线、触发规则
│                            上限 15 条元原则
│                            变更条件：人工确认 + 日期标注（如 "2026-09-05 修订"）
├── references/           ← 【可修改区】经验卡片层
│   ├── lesson-*.md          场景/问题/根因/方案/反模式/溯源 六元组
│   └── ...                  使用中自由追加、修改、淘汰
├── templates/            ← 【可修改区】模板
└── evals/                ← 【可修改区】评估用例（随经验同步更新）
```

### 5.3 分区规则

| 规则 | 内容 |
|------|------|
| 写入门槛 | 可修改区：子 agent / 自动流程可直接写。不可修改区：必须人工确认，git commit 留痕 |
| 晋升通道 | 可修改区同一问题出现 **3 次** → 提炼为元原则，晋升到不可修改区（写入 SKILL.md） |
| 修订通道 | 新经验与既有元原则**冲突** → 不许静默覆盖，必须触发元原则修订，修订处标注日期 |
| 容量控制 | 元原则 ≤ 15 条（超限必须合并或淘汰旧条目），防止不可修改区膨胀 |
| 溯源要求 | 每张经验卡片必须带"溯源"字段指回原始出处（文档/对话/项目），不可凭空生成 |
| 安全边界 | 不可修改区同时是 anti-distill（反蒸馏）的保护对象：对外分享时核心知识中性化，仅可修改区可导出 |

### 5.4 分层的信息学依据

- 不可修改区 = **低熵高稳定**：变更成本高、频率低、影响全局
- 可修改区 = **高熵高迭代**：变更成本低、频率高、影响局部
- 晋升机制 = 熵减通道：把散落的经验（高熵）收敛为原则（低熵）

---

## 6. L4 自进化层：使用中持续迭代

### 6.1 进化闭环

```
使用/踩坑 → 记录（usercontext 会话级）
    → 蒸馏（经验卡片进 references/，即 dev-lessons 模式）
    → 评估（skill_benchmark: with_skill vs without_skill 对比）
    → 触发分析（skill_trigger_analyzer: 假阳性/假阴性统计）
    → 迭代 SKILL.md 描述 / 断言 / 元原则
    ↻ 循环，全程留 iteration-N 快照可回滚
```

### 6.2 进化的三类信号

| 信号 | 来源 | 动作 |
|------|------|------|
| 触发信号 | skill_trigger_analyzer | 假阳性 → 收紧 description；假阴性 → 放宽 |
| 效果信号 | skill_benchmark / usage success_rate | with/without 无提升 → 降权或整改 |
| 经验信号 | 会话中的踩坑记录（usercontext） | 蒸馏为经验卡片；3 次重复 → 晋升元原则 |

### 6.3 防退化约束

- 每次迭代保留 `iteration-N` 快照（skill-workspace 机制），支持回滚
- 评估报告 HTML 可视化（eval_viewer），迭代间可比对
- 不可修改区的变更走 git 留痕 + 人工确认，杜绝"进化变退化"

---

## 7. 检索架构：快慢双路径

### 7.1 快路径（默认）

排序后的 Top-N skill 元数据（name + description）直接注入 system prompt。特点：

- 零额外延迟，命中常规任务
- 上下文成本受控：只注入 N 个，而非全库 700+

### 7.2 慢路径（子 agent 兜底检索）

**触发条件（两个，满足其一）**：

1. **复杂任务前**：任务涉及多领域 / 用户明确要求检索 / 快路径 Top-N 明显覆盖不住
2. **效果不佳时**：首轮执行结果不好，怀疑是 skill 选错了

**执行方式**：派 skill-matcher 子 agent 对全库（或分类子集）做一遍语义检索，返回最合适的 skill 列表，再重新执行任务。

**设计本质**：700+ skill 不可能全部注入上下文还能保持模型注意力。快慢双路径 = 用"延迟检索"换"上下文纯净度"，等价于 CPU 的 L1 缓存 vs 全盘搜索：

- L1（快路径）= 排序预取，命中率靠 L1 排序层保障
- 全盘搜索（慢路径）= 排序失灵时的纠错机制

**关键认知**：慢路径不是性能妥协，而是**必要的冗余**——任何静态排序都存在长尾失误，必须有运行时纠错通道。

---

## 8. 与现有组件的映射

| 体系层 | 已落地组件 | 位置 |
|--------|-----------|------|
| L1 排序 | `check_top_skills.py`（十大必装校验）、`scan_skills.py` | 本仓库根目录 |
| L1 分类 | `classify_skills.py` / `classify_skills_v2.py`（关键词分类） | 本仓库根目录 |
| L2 管理 | skills-manager（中央库 + Preset + 软链接 + SQLite） | `skills/skills-manager/SKILL.md`，DB: `~/.skills-manager/skills-manager.db` |
| L3 分区 | dev-lessons（references 经验卡片 + SKILL.md 元原则 ≤15）、anti-distill（核心保护） | `~/.agents/skills/dev-lessons/` |
| L4 进化 | `skill_benchmark.py`（with/without）、`skill_trigger_analyzer.py`（触发优化）、`eval_viewer.py`（报告）、darwin-skill（hill-climbing 优化） | 本仓库根目录 / skill 库 |
| 快路径 | system prompt 中的 skill 列表注入 | Trae / 各 IDE 配置 |
| 慢路径 | skill-matcher 子 agent | Agent 工具链 |
| 进化原料 | usercontext 会话记录（`usercontext/<date>/usercontext.md`） | 本仓库 `usercontext/` |

---

## 9. 度量与验收

| 指标 | 定义 | 目标 |
|------|------|------|
| 快路径命中率 | 常规任务正确命中 skill 的比例 | > 90% |
| 慢路径触发率 | 需要子 agent 兜底检索的任务占比 | < 20%（过高说明 L1 排序失效） |
| 上下文占用 | system prompt 中 skill 元数据 token 数 | 受控（Top-N 上限） |
| 进化有效率 | 迭代后 benchmark 提升的比例 | > 50% |
| 元原则稳定性 | 不可修改区月变更条数 | ≤ 3（频繁变更说明分区失效） |
| 重复率 | 库内功能重复的 skill 对数量 | 持续下降 |

---

## 10. 设计要点回顾（为什么这套体系成立）

1. **每个失败模式都有专属解药**：排序↔选不对，Manager↔管不住，分区↔改坏了，自进化↔不进化。不存在"一招通吃"，因此是四层而非一层。
2. **排序解决冷启动，分区解决演进安全**：排序是入口选择问题（调用前），分区是写入安全问题（迭代时），两者组合让 skill **既敢进化又不会进化坏**。
3. **晋升机制是体系的灵魂**："同问题 3 次晋升元原则"让体系具备熵减能力——经验自然沉淀为原则，原则又约束新经验的写入。
4. **慢路径是必要的冗余**：任何静态排序都有长尾失误，运行时纠错通道保证体系下限。

---

## 11. 外部参考吸收：mattpocock/skills（v1.1 增补）

> 源：https://github.com/mattpocock/skills （253k stars，"Skills For Real Engineers"）
> 哲学基线对照：该项目走"**小而组合**"路线（约 20 个 skill，创建期防熵）；本体系走"**多而治之**"路线（700+，规模化治熵）。两者互补：可在创建期吸收其防熵机制，减缓库增长速度。

### 11.1 六个可吸收机制 → 映射到四层

| # | 机制 | mattpocock 做法 | 映射层 | 对本体系的修正 |
|---|------|----------------|--------|---------------|
| 1 | **双轴分类法**（最重要） | skill 按"谁能调用"分两轴：**user-invoked**（仅 `/命令` 触发，职责是编排）与 **model-invoked**（用户或模型自动触发，承载可复用纪律）。铁律：user-invoked 可调用 model-invoked，**绝不调用另一个 user-invoked**（防编排链失控） | L1 | 新增 `invocation` 字段。**只有 model-invoked 进入 Top-N 排序池**；user-invoked 进斜杠命令注册表，不参与自动注入竞争。700+ skill 中编排类 skill 本就不该被自动触发，此举直接缩减排序池规模 |
| 2 | **组合式原语** | `grilling` 仅 12 行，被 grill-me / grill-with-docs / triage / wayfinder / improve-codebase-architecture 五个编排 skill 复用 | L1 独特性 + L4 | 新增**创建期检查**：新建 skill 前先查"已有原语 + 新编排"能否覆盖。独特性从"事后检测重复"前移到"事前防止重复" |
| 3 | **路由元技能（ask-matt）** | 一个 user-invoked skill，职责仅为"帮你选对该库哪个 skill/流程" | 检索架构 | 在快慢双路径之间补出**第三路径：用户主动路由**。排序失灵时用户不必等子 agent 兜底，`/ask` 直达 |
| 4 | **`.out-of-scope/` 负知识台账** | 被拒绝的功能决策写成独立 md 存档（如 question-limits.md），防止同一提案被反复重议 | L4 | "3 次晋升"是**正知识**沉淀通道；补一条**负知识**通道：淘汰/拒绝的进化方向记录在案，杜绝重复提案、重复踩坑 |
| 5 | **Changesets 版本化** | package.json + .changeset + CHANGELOG + semver release（v1.2.3）+ CI 同步插件版本 | L2 | skill 库按**产品**版本化管理。DB 增加 `version` 字段；破坏性修改（元原则变更）升 major，经验卡片追加升 patch |
| 6 | **双安装哲学** | 两种互斥安装方式：plugin（只读订阅，随上游自动更新）vs skills.sh（拷贝为自有文件，可魔改）。并明确警告"两种都装 = 每个 skill 存两份" | L3 | 分区思想从"skill 内部"扩展到"分发链"：**订阅（只读软链）= 不可修改区，分叉（拷贝）= 可修改区**。skills-manager 的软链机制天然对应前者；本地魔改版需显式标记为 fork 并改名防冲突 |

### 11.2 采纳的 DB schema 增量

```sql
ALTER TABLE skills ADD COLUMN invocation  TEXT DEFAULT 'model';   -- 'user' | 'model'
ALTER TABLE skills ADD COLUMN version     TEXT DEFAULT '0.1.0';   -- semver
ALTER TABLE skills ADD COLUMN install_mode TEXT DEFAULT 'symlink'; -- 'symlink'(订阅) | 'fork'(自有)
```

### 11.3 哲学取舍记录（不采纳项）

| mattpocock 做法 | 不采纳原因 |
|----------------|-----------|
| 库规模控制在 ~20 个 | 个人工作流横跨开发/创作/运营多域，规模刚需在数百级，靠治理而非收缩解决 |
| repo 级写作规范（如禁 em-dash，全库手改执行） | 边际收益低；仅在 skill-creator 流程内加 lint 建议即可 |

### 11.4 冲突检测：对现有设计的验证

- **"可修改区/不可修改区"被独立验证**：双安装哲学（subscribe vs own）与本体系 L3 分区是同构思想在两个粒度的出现——skill 内部分区（文件级）与分发链分区（副本级）。设计可信度提升。
- **一个新增失败模式浮出**：F5 **重复安装**（"装了两遍 = 每个 skill 两份"）。skills-manager 中央库 + 各工具目录软链的分发方式天然免疫，但 adopt 导入外部已存在技能时需查重，纳入 F2 管不住的治理范围。

---

## 12. L0 项目级裁剪：落地记录（2026-09-06）

### 12.1 执行结果

| 项 | 前 | 后 |
|---|----|----|
| 激活场景 | 开发辅助（100 skill，大杂烩） | **核心开发（36 skill，纯开发集）** |
| `~/.trae-cn/skills` | 101 | 37 |
| `~/.claude/skills` | 102 | 38 |
| `~/.cursor/skills` | — | 36 |
| `~/.codex/skills` | — | 37 |

「核心开发」场景构成（36）：开发工作流 8（github/tdd/diagnose/grill-me/task-alignment/task-implement/zoom-out/oracle）+ 前端 5 + 平台部署 5 + 移动端 2 + Python 3 + Skill/MCP 工程 10 + 知识研究 3。所有原场景保留，随时 `presets apply` 切回。

### 12.2 关键踩坑：DB 不是事实来源（重要！）

**现象**：直接向 `skills-manager.db` 的 scenarios/scenario_skills 表 INSERT，数据在下次 CLI 调用时被静默清除。

**根因**（源码 `src-tauri/src/core/sync_metadata.rs`）：skills-manager 采用**文件级元数据为单一事实来源**的架构：

```
~/.skills-manager/skills/.skills-manager/     ← 真正的事实来源（隐藏在中央库内）
├── schema.json
├── skills/<skill_id>.json                    ← SkillMetaFile
├── scenarios/<scenario_id>.json              ← ScenarioMetaFile
└── scenario-skills/<scenario_id>/<skill_id>.json  ← membership + tools 开关
```

每次 CLI/GUI 启动执行 `reindex_from_metadata`：从上述文件全量重建 DB，**删除元数据中不存在的记录**。DB 只是缓存/投影。

**正确姿势**：写元数据 JSON → 跑任意 CLI 命令触发 reindex → `presets apply <场景名>` 激活并同步各工具目录软链。

### 12.3 操作要点

1. **DB 锁**：桌面应用运行时持 WAL 锁，CLI 报 `xShmMap` 错误。关掉应用即可（WAL 无数据丢失风险）。
2. **沙箱**：CLI 需要写 `~/.skills-manager/.skills-manager.lock`，在 IDE 沙箱内会报 os error 5，需非沙箱执行。
3. **工具目录残留**：apply 后残留 1-2 个手工软链（tabbit / vercel-react-best-practices，宝玉模式），非场景管理范围，保留。
4. **本项目脚本**：`create_core_dev_scenario.py`（写元数据建场景，幂等）、`inspect_db.py`（只读盘点，immutable=1 可绕 WAL 锁）。

### 12.4 后续（可选，未做）

- 项目级 `.agents/skills`（本项目 25 个）二次裁剪：视频类 skill 与本项目的视频评估脚本相关，未动；若当前阶段纯做治理开发，可再省 ~15 个描述位。
- L1 两级注入 / L2 两阶段检索：待 L0 token 收益验证后再投资。

---

## 13. L5 生命周期层：双重挤压与吸收审计（2026-09-06 增补）

### 13.1 双重挤压

skill 正被两股外部力量持续挤压：

| 挤压力 | 吸收对象 | 典型牺牲品 |
|-------|---------|-----------|
| **模型智力上升** | 补偿型 skill（弥补模型短板） | 纪律执行类、格式约定类、"怎么思考"框架类 |
| **harness 架构优化** | 包装型 skill（包装外部能力） | 部署包装（harness 内置一键部署后）、浏览器操作（内置 browser 工具后）、流程编排 |

### 13.2 四类幸存区（判据：非通用性）

| 幸存类别 | 例 | 不被吸收的原因 |
|---------|---|--------------|
| 1. 特定领域且非强制流程 | charity-writing-assistant（六大公益平台规范）、sino-drug | 训练数据不含；足够通用的强制流程终会被 harness 护栏编码 |
| 2. 神秘小众癖好 | caveman 模式、个人文风偏好 | 对单个用户太 specific，通用引擎永远不值得做 |
| 3. 价值判断 | design-taste-frontend 的反俗套哲学、resume-assistant 的防幻觉红线 | 是立场不是能力——模型是能力引擎，不是立场持有者 |
| 4. 低复杂度自动化 | weather、nano-pdf、sag | 长尾集成经济学：harness 只做 top-N 集成，长尾归 skill |

**统一判据：通用性经济学的死角**。凡通用到值得被吸收的，终将被吸收；幸存的是太专（1）、太私（2）、太有立场（3）、太长尾（4）的部分。推论：skill 库的终局不是"更多"，而是"更怪"——越通用死得越快，越私人活得越久。

### 13.3 吸收审计协议

**触发**：每次模型升级 / harness 大版本优化后。

**三问过滤**（对每个 skill）：
1. **智力测试**：新模型是否已原生具备其核心价值？
2. **吸收测试**：harness 是否已内置该能力？
3. **幸存测试**：是否落在四类幸存区？

判定：1 或 2 任一命中 → 淘汰候选；3 命中 → 保留。

**降本设计**：
- 不必全量人工审查——高频 skill 失效会被自然感知（效果下降、不再被选中）
- L1 排序层的使用频率数据兼任**吸收探测器**：模型升级后某 skill 使用率断崖式下跌 = 被吸收的强信号
- 批量审计可派子 agent 按三问过滤

**退役不删除**：淘汰 skill 进负知识台账（11.4 的 `.out-of-scope` 机制），记录"被 XX 模型版本 / harness 功能吸收"，防止后续被重新安装。

### 13.4 与现有层的耦合

- **L1 排序层**：「新鲜度」指标语义升级——从"是否维护"到"是否仍被需要"
- **L4 自进化层**：补上缺失的**死亡相**。完整生命周期 = 出生（创建）→ 生活（排序/进化）→ 死亡（吸收审计）；dev-lessons 三层管道（capture / distill / evolve）增加 retire
- **创建期信号**：新 skill 设计优先落在幸存区；纯补偿型 skill 投入即折旧，创建前自问"下两次模型升级后它还活着吗"
- **风险提示**：当前使用频率最高的一批（superpowers / code-review 等纪律型）恰属最高风险的补偿型类别——每次模型升级应**优先**审计它们

---

*本文档持续演进：v1.0（2026-09-05）四层治理 + 快慢双路径初版；v1.1 增补外部参考吸收（mattpocock/skills）；v1.2 增补 L0 项目级裁剪落地记录；v1.3 增补 L5 生命周期层（双重挤压与吸收审计）。*
