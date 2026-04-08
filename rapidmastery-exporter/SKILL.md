---
name: rapidmastery-exporter
description: 导出 RapidMastery 学习记录到本地仓库并自动推送到远程。当你完成一次 RapidMastery 学习会话后，使用此 skill 保存学习成果到 study-notes/ 目录，并自动执行 git add/commit/push。触发方式：说"导出今天的学习记录"、"保存学习笔记"、"git push 学习记录"等。
---

# RapidMastery Exporter - 学习记录导出器

自动保存 RapidMastery 学习会话到本地仓库，并推送到远程。

## 工作流程

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  1. 收集内容     │ →  │  2. 生成文件     │ →  │  3. Git 推送     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 使用方法

### 启动导出

完成 RapidMastery 学习后，使用以下方式启动：

```
/rapidmastery-exporter [主题名]
```

或自然语言：
- "导出今天的学习记录"
- "保存 React Hooks 学习笔记"
- "把刚才的学习内容推送到仓库"

### 步骤 1：收集学习内容

**方式 A：直接粘贴（推荐）**
- 将 RapidMastery 对话中的关键内容复制
- 粘贴给 Kimi，会按结构化格式保存

**方式 B：使用模板**
- 如果对话内容过长，使用 `assets/learning-template.md` 模板
- 手动填入关键学习点

### 步骤 2：自动生成文件

文件将自动保存到 `study-notes/` 目录，命名格式：

```
study-notes/
├── 2025-01-15-react-hooks.md
├── 2025-01-18-python-decorators.md
└── README.md (自动生成索引)
```

### 步骤 3：自动 Git 推送

运行脚本自动提交：

```bash
python scripts/export_learning.py --topic "主题名" --file "文件路径"
```

或直接：

```bash
# 手动添加并推送
python scripts/export_learning.py --push-only
```

## 文件结构

每个学习记录文件包含：

```markdown
# [主题]

**学习时间**: YYYY-MM-DD HH:mm  
**目标深度**: apply/master/know  
**掌握程度**: ⭐⭐⭐☆☆

## 核心概念

- 概念 1：...
- 概念 2：...

## 费曼讲解记录

我的理解：...
追问要点：...

## 刻意练习

完成的练习：...
薄弱点：...

## 复习计划

- [ ] 1天后：...
- [ ] 3天后：...
- [ ] 7天后：...

## 原始对话摘录

<details>
<summary>展开查看完整对话</summary>
...
</details>
```

## Git 提交规范

提交信息格式：`[主题] 学习记录 - YYYY-MM-DD`

示例：
- `[React Hooks] 学习记录 - 2025-01-15`
- `[Python装饰器] 学习记录 - 2025-01-18`

## 脚本使用

### export_learning.py

```bash
# 完整流程：创建文件 + git 提交 + 推送
python scripts/export_learning.py --topic "主题名" --content "内容"

# 仅推送现有文件
python scripts/export_learning.py --push-only

# 批量提交所有未提交的笔记
python scripts/export_learning.py --commit-all
```

## 注意事项

1. **对话历史**: Kimi CLI 的 skill 无法直接访问对话历史，需要用户主动提供/粘贴内容
2. **文件命名**: 自动使用 `日期-主题.md` 格式，主题会自动转义为文件名安全格式
3. **README 索引**: 每次导出后自动更新 `study-notes/README.md` 索引文件
4. **Git 配置**: 确保已配置 git user.name 和 user.email
5. **远程仓库**: 确保已添加远程仓库 origin

## 快速命令

| 命令 | 作用 |
|------|------|
| `导出学习记录` | 启动导出流程 |
| `查看学习笔记` | 列出所有已保存的笔记 |
| `推送学习记录` | 仅执行 git push |
