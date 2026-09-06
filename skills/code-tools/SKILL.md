---
name: code-tools
description: 代码理解与分析工具集，包含代码图谱、依赖分析、代码审查等6个开源工具
tags: code-analysis, code-graph, mcp, code-review
always: false
---

# 代码理解工具集

本技能包含6个代码理解与分析的开源工具，按需克隆使用。

## 工具总览

| 工具 | 用途 | 适用场景 |
|------|------|----------|
| **Understand-Anything** | 全栈代码理解与可视化仪表盘 | 人和Agent都用 + 可视化仪表盘 |
| **codegraph** | 轻量级代码图谱 | 给Agent一张轻量的纯结构图 |
| **code-review-graph** | 代码审查图谱 | 专做代码审查/PR把关 |
| **codebase-memory-mcp** | 代码库记忆MCP | 团队共享 + 性能 + 语义检索 |
| **emerge** | 代码依赖可视化 | 只想给人看一张依赖图 |
| **codegraph-rust** | Rust代码图谱 | 想要集大成的全栈参考 |

---

## 1. Understand-Anything

**GitHub**: https://github.com/Egonex-AI/Understand-Anything

**描述**: 全栈代码理解工具，提供可视化仪表盘，人和Agent都可以使用。

**适用场景**:
- 需要代码可视化仪表盘
- 人和Agent共享代码理解
- 需要集大成的全栈参考

**克隆命令**:
```bash
git clone https://github.com/Egonex-AI/Understand-Anything ~/GitHub/Understand-Anything
```

**启动**:
```bash
cd ~/GitHub/Understand-Anything
npm install
npm run dev
```

**特性**:
- 代码可视化仪表盘
- 支持多语言
- MCP插件支持

---

## 2. codegraph

**GitHub**: https://github.com/colbymchenry/codegraph

**描述**: 轻量级代码图谱工具，专为Agent设计，提供纯结构视图。

**适用场景**:
- 给Agent一张轻量的纯结构图
- 中小型/多语言monorepo
- 需要跨文件调用链分析

**克隆命令**:
```bash
git clone https://github.com/colbymchenry/codegraph ~/GitHub/codegraph
```

**安装**:
```bash
cd ~/GitHub/codegraph
pip install -e .
```

**使用**:
```bash
codegraph analyze /path/to/codebase
codegraph serve
```

**特性**:
- MCP插件方式接入
- 轻量级，不占用太多资源
- 专注于代码结构分析

---

## 3. code-review-graph

**GitHub**: https://github.com/tirth8205/code-review-graph

**描述**: 代码审查图谱工具，专注于PR审查和代码质量分析。

**适用场景**:
- 专做代码审查/PR把关
- 需要代码质量分析
- 团队协作代码审查

**克隆命令**:
```bash
git clone https://github.com/tirth8205/code-review-graph ~/GitHub/code-review-graph
```

**使用**:
```bash
cd ~/GitHub/code-review-graph
pip install -e .
code-review-graph analyze <repo-path>
```

**特性**:
- PR审查分析
- 代码质量评估
- MCP插件支持

---

## 4. codebase-memory-mcp

**GitHub**: https://github.com/DeusData/codebase-memory-mcp

**描述**: 代码库记忆MCP工具，提供语义检索和团队共享功能。

**适用场景**:
- 团队共享代码知识
- 需要高性能语义检索
- 大型代码库的记忆管理

**克隆命令**:
```bash
git clone https://github.com/DeusData/codebase-memory-mcp ~/GitHub/codebase-memory-mcp
```

**安装**:
```bash
cd ~/GitHub/codebase-memory-mcp
pip install -r requirements.txt
```

**启动**:
```bash
python -m codebase_memory_mcp serve
```

**特性**:
- 语义检索
- 团队共享
- 高性能
- MCP插件

---

## 5. emerge

**GitHub**: https://github.com/glato/emerge

**描述**: 代码依赖可视化工具，生成依赖关系图。

**适用场景**:
- 只想给人看一张依赖图
- 需要可视化代码依赖关系
- 快速理解项目结构

**克隆命令**:
```bash
git clone https://github.com/glato/emerge ~/GitHub/emerge
```

**安装**:
```bash
cd ~/GitHub/emerge
pip install emerge-viz
```

**使用**:
```bash
emerge --scan /path/to/codebase
emerge --serve
```

**特性**:
- 依赖关系可视化
- 支持多种语言
- 生成交互式图表

---

## 6. codegraph-rust

**GitHub**: https://github.com/Jakedismo/codegraph-rust

**描述**: Rust实现的代码图谱工具，集大成的全栈参考。

**适用场景**:
- 需要集大成的全栈参考
- 大型/多语言monorepo
- 高性能代码分析

**克隆命令**:
```bash
git clone https://github.com/Jakedismo/codegraph-rust ~/GitHub/codegraph-rust
```

**安装**:
```bash
cd ~/GitHub/codegraph-rust
cargo build --release
```

**使用**:
```bash
./target/release/codegraph analyze /path/to/codebase
```

**特性**:
- Rust高性能实现
- 全栈代码分析
- MCP插件支持

---

## 使用策略

### 如何选择工具

```
中小型仓库                    → Claude Code自带够用
大型/多语言monorepo            → 加一层code graph
只想给人看依赖图              → emerge
给Agent轻量结构图             → codegraph
专做代码审查/PR把关           → code-review-graph
团队共享+性能+语义检索         → codebase-memory-mcp
集大成全栈参考                → codegraph-rust
人和Agent都用+可视化仪表盘     → Understand-Anything
```

### 按需克隆流程

1. **识别需求**: 根据任务类型选择合适的工具
2. **克隆项目**: 使用对应的git clone命令
3. **安装依赖**: 按文档安装依赖
4. **启动服务**: 运行工具并连接到Agent
5. **完成清理**: 任务完成后可保留或删除

### MCP连接

除emerge外，其余5个工具都通过MCP协议接入：

```bash
# 在.claude/settings.json中配置
{
  "tools": {
    "mcp": {
      "servers": [
        {
          "id": "codegraph",
          "command": ["python", "-m", "codegraph.mcp"],
          "cwd": "~/GitHub/codegraph"
        }
      ]
    }
  }
}
```

---

## 注意事项

- **网络要求**: 需要能够访问GitHub
- **资源占用**: 大型工具如Understand-Anything和codegraph-rust需要较多内存
- **环境依赖**: Rust工具需要安装Rust环境
- **MCP协议**: 需要确保Claude Code支持MCP协议
- **并行使用**: 多个工具可以同时运行，但注意资源占用