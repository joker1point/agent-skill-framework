---
name: skills-manager
description: 使用 skills-manager 管理所有 AI 编码工具的 Skills，支持中央库、Preset、软链接同步
tags: skill-management, skills-manager, preset, sync, symlink
always: false
---

# Skills Manager 技能管理

使用 `skills-manager` 统一管理所有 AI 编码工具的 Skills，结合宝玉的极客经验。

## 核心概念

```
┌─────────────────────────────────────────────────────────────────┐
│                      中央技能库 (~/.skills-manager/skills/)      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Skill 1       │  │   Skill 2       │  │   Skill 3       │ │
│  │  (原始副本)      │  │  (原始副本)      │  │  (原始副本)      │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Preset (预设分组)                         │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Web Dev:  skill1 ✓, skill2 ✓, skill3 ✗                 │ │
│  │  Code Analysis:  skill2 ✓, skill3 ✓                      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Claude Code     │  │ Cursor          │  │ Codex           │
│ ~/.claude/skills│  │ ~/.cursor/skills│  │ ~/.codex/skills │
│ ├─ skill1 (🔗)  │  │ ├─ skill1 (🔗)  │  │ ├─ skill2 (🔗)  │
│ └─ skill2 (🔗)  │  │ ├─ skill2 (🔗)  │  │ └─ skill3 (🔗)  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 安装方式

### 方式一：桌面应用（推荐）

下载地址：https://github.com/xingkongliang/skills-manager/releases

### 方式二：CLI 工具

```bash
# 克隆仓库
git clone https://github.com/xingkongliang/skills-manager.git ~/GitHub/skills-manager

# 安装依赖
cd ~/GitHub/skills-manager
npm install

# 构建 CLI（需要 Rust）
npm run cli:install

# 验证安装
skills-manager-cli --json repo status
```

## 核心命令

### 1. 查看状态

```bash
# 查看仓库状态
skills-manager-cli --json repo status

# 查看已检测到的工具
skills-manager-cli --json tools list

# 列出所有技能
skills-manager-cli --json skills list

# 查看单个技能详情
skills-manager-cli --json skills show <skill-name>
```

### 2. 安装技能

```bash
# 从 skills.sh 市场安装
skills-manager-cli skills install vercel-labs/agent-skills@react-best-practices --sync

# 从 GitHub 安装（支持子目录）
skills-manager-cli skills install https://github.com/anthropics/skills.git --sync
skills-manager-cli skills install https://github.com/foo/bar/tree/main/skills/baz --sync

# 从本地目录安装
skills-manager-cli skills install ./my-skill --sync
```

**关键选项：**
- `--sync`: 安装后自动同步到所有启用的 Agent（推荐）
- `--sync-preset <name>`: 安装到指定 Preset

### 3. 搜索技能

```bash
skills-manager-cli --json skills search "react performance" --limit 5
```

### 4. 更新技能

```bash
# 检查更新
skills-manager-cli skills check --all

# 更新单个技能
skills-manager-cli skills update <skill-name>

# 更新所有技能
skills-manager-cli skills update --all
```

### 5. 删除技能

```bash
# 预览删除
skills-manager-cli skills remove <skill> --dry-run

# 确认删除
skills-manager-cli skills remove <skill> --yes
```

### 6. 启用/禁用

```bash
skills-manager-cli skills disable <skill>
skills-manager-cli skills enable <skill>
```

### 7. 同步技能

```bash
# 同步当前 Preset 到所有 Agent
skills-manager-cli skills sync

# 预览同步目标
skills-manager-cli skills sync --dry-run

# 同步到特定 Preset
skills-manager-cli skills sync --preset "Web Dev"

# 只同步到单个 Agent
skills-manager-cli skills sync --tool claude_code
```

### 8. Preset 管理

```bash
# 列出所有 Preset
skills-manager-cli presets list

# 查看当前 Preset
skills-manager-cli presets current

# 添加技能到 Preset
skills-manager-cli presets add-skill <preset> <skill>...

# 从 Preset 移除技能
skills-manager-cli presets remove-skill <preset> <skill>...

# 应用 Preset（设为当前并同步）
skills-manager-cli presets apply <preset>
```

### 9. 标签管理

```bash
skills-manager-cli skills tag add <skill> web frontend
skills-manager-cli skills tag remove <skill> frontend
skills-manager-cli skills tag list <skill>
skills-manager-cli skills tag list
```

### 10. 导入已有技能

```bash
# 预览待导入的技能
skills-manager-cli skills adopt ~/.claude/skills --dry-run

# 导入所有技能
skills-manager-cli skills adopt ~/.claude/skills

# 导入并关联 Git 源
skills-manager-cli skills adopt ~/.claude/skills/my-skill \
  --git-url https://github.com/me/my-skill --git-subpath ""
```

## 宝玉的极客经验

### 原则一：Skills 只装在项目里，不装全局

中央库管理所有技能，但项目只装真正需要的，节约上下文空间。

### 原则二：用软链接来安装 Skills

```bash
# 第一步：下载开源 Skills 到统一目录
git clone https://github.com/baoyu-skills ~/GitHub/baoyu-skills

# 第二步：在项目中创建软链接
mklink /D .agents/skills/baoyu-comic ~/GitHub/baoyu-skills/skills/baoyu-comic

# 第三步：给 Agent 建入口
mklink /D .claude/skills .agents/skills
```

### 原则三：不用记命令，让 Agent 帮你干

直接用自然语言告诉 Agent：
> 帮我把 baoyu-skills 项目里的 baoyu-comic 这个 skill 链接到当前项目

### 原则四：更新只需一次

```bash
cd ~/GitHub/baoyu-skills
git pull
```

所有项目自动同步更新。

## 项目级技能管理

按照宝玉经验，结合 skills-manager：

```bash
# 初始化项目技能目录
mkdir -p .agents/skills

# 将技能从中央库链接到项目
mklink /D .agents/skills/code-tools ~/.skills-manager/skills/code-tools

# 创建 Agent 入口
mklink /D .claude/skills .agents/skills
```

## 常用场景

### 场景一：开始新项目

```bash
# 查看可用技能
skills-manager-cli --json skills list

# 安装需要的技能到项目
skills-manager-cli skills install code-tools --sync

# 或者用软链接方式
mklink /D .agents/skills/code-tools ~/.skills-manager/skills/code-tools
```

### 场景二：团队协作

```bash
# 创建团队 Preset
skills-manager-cli presets create "Team Core"

# 添加团队共用技能
skills-manager-cli presets add-skill "Team Core" code-tools github weather

# 同步到所有 Agent
skills-manager-cli presets apply "Team Core"
```

### 场景三：技能更新

```bash
# 检查更新
skills-manager-cli skills check --all

# 更新所有技能
skills-manager-cli skills update --all

# 同步到项目
skills-manager-cli skills sync
```

## 配置文件

### Agent 路径配置

在 `~/.skills-manager/settings.json` 中配置：

```json
{
  "tools": {
    "claude_code": {
      "skillsPath": "~/.claude/skills"
    },
    "cursor": {
      "skillsPath": "~/.cursor/skills"
    },
    "trae": {
      "skillsPath": "./.claude/skills"
    }
  }
}
```

### Git 备份配置

```bash
# 在设置中配置远程仓库
skills-manager-cli git remote set-url origin git@github.com:me/my-skills-backup.git

# 同步到 Git
skills-manager-cli git commit -m "chore: update skills"
skills-manager-cli git push
```

## 支持的工具

- Cursor
- Claude Code
- Codex
- Grok
- OpenCode
- Amp
- Kilo Code
- Roo Code
- Goose
- Gemini CLI
- GitHub Copilot
- Windsurf
- TRAE IDE
- Antigravity

## 常见问题

### Q: 安装成功但技能不显示在 Agent 中

A: 默认安装到中央库，需要同步：
```bash
skills-manager-cli skills sync
```

### Q: 没有活动 Preset

A: 创建或选择一个 Preset：
```bash
skills-manager-cli presets list
skills-manager-cli presets apply "Default"
```

### Q: 导入的技能无法更新

A: 需要关联 Git 源：
```bash
skills-manager-cli skills adopt ~/.claude/skills/my-skill \
  --git-url https://github.com/me/my-skill --git-subpath ""
```

### Q: Windows 软链接权限问题

A: 启用开发者模式或使用管理员权限运行终端。

## 最佳实践

1. **分类管理**: 使用 Preset 按项目类型分组技能
2. **项目专属**: 只在项目中安装真正需要的技能
3. **定期更新**: 定期运行 `skills check --all` 和 `skills update --all`
4. **Git 备份**: 使用 Git 备份技能库，方便多机同步
5. **标签分类**: 使用标签对技能进行归类筛选
6. **按需同步**: 使用 `--tool` 参数只同步到特定 Agent