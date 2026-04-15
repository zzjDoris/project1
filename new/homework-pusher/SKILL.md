---
name: homework-pusher
description: 自动将当前项目中的作业/代码文件推送到远程 Git 仓库。触发方式：用户说"推送作业"、"提交作业到git"、"git push 作业"、"上传作业"、"把代码推到仓库"、"提交今天的作业"等。
---

# Homework Pusher

自动检测本地 Git 变更，帮助用户将作业文件一键提交并推送到远程仓库。

## 工作流程

```
1. 检查 Git 状态 → 2. 确认提交文件 → 3. 生成提交信息 → 4. 执行 commit & push
```

## 触发条件

当用户说以下任意语句时触发本 skill：
- "推送作业"
- "提交作业到 git"
- "git push 作业"
- "上传作业"
- "把代码推到仓库"
- "提交今天的作业"
- "自动推送当前更改"

## 执行步骤

### Step 1: 检查 Git 状态
运行 `scripts/push_homework.py --status` 获取：
- 当前分支名称
- 修改/新增/删除的文件列表
- 远程仓库配置情况
- 是否有未 pull 的远程更新

### Step 2: 确认提交范围
向用户展示变更文件列表，确认提交方式：
- **全部提交**：提交所有已修改和未跟踪的文件
- **部分提交**：仅提交用户指定的文件
- **取消**：不执行任何操作

### Step 3: 生成提交信息
根据提交内容自动生成 message，优先级：
1. 用户明确提供的提交信息
2. 自动推断：`submit: <课程/作业名> - YYYY-MM-DD`
3. 兜底信息：`update homework - YYYY-MM-DD`

### Step 4: 执行 Git 推送
运行 `scripts/push_homework.py` 执行：
```bash
git add <选中的文件>
git commit -m "<提交信息>"
git push origin <当前分支>
```

## 脚本使用指南

```bash
# 查看仓库状态
python scripts/push_homework.py --status

# 提交所有更改（自动推断提交信息）
python scripts/push_homework.py --all

# 提交指定文件
python scripts/push_homework.py --files "index.html,style.css"

# 自定义提交信息
python scripts/push_homework.py --all --message "完成第四章前端作业"
```

## 错误处理

- **无 Git 仓库**：提示用户先 `git init`
- **无远程仓库**：提示用户先 `git remote add origin <url>`
- **推送被拒绝**：提示用户先执行 `git pull` 再推送
- **无变更**：提示没有需要提交的文件
- **未配置用户名/邮箱**：提示用户配置 git 用户信息
