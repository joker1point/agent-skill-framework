---
name: github
description: GitHub操作指南，包括仓库管理、PR操作、代码搜索等
tags: github, git, code
always: false
---

# GitHub 技能

GitHub相关操作的详细指南。

## 常用命令

### 仓库操作
```bash
# 克隆仓库
git clone https://github.com/username/repo.git

# 创建新分支
git checkout -b feature/new-feature

# 推送分支
git push origin feature/new-feature
```

### Pull Request
```bash
# 查看远程分支
git fetch origin

# 拉取PR分支
git checkout -b pr-branch origin/pr-branch

# 合并PR
git checkout main
git merge pr-branch
```

### GitHub CLI
```bash
# 安装 gh
# Windows: winget install GitHub.cli

# 查看PR列表
gh pr list

# 查看PR详情
gh pr view 123

# 合并PR
gh pr merge 123 --squash
```

## API调用
```bash
# 获取仓库信息
curl -s https://api.github.com/repos/username/repo

# 获取issue列表
curl -s https://api.github.com/repos/username/repo/issues
```

## 提示
- 使用 `gh auth login` 登录
- 设置 `GITHUB_TOKEN` 环境变量用于API认证
- 搜索代码用 `gh repo search`