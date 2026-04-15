#!/usr/bin/env python3
"""
Homework Pusher - 自动推送作业到远程 Git 仓库
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_git(args, cwd=None, check=False):
    """运行 git 命令并返回结果"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check,
            encoding='utf-8'
        )
        return result
    except FileNotFoundError:
        print("[ERR] 错误：未找到 git 命令，请确保 Git 已安装并添加到 PATH")
        sys.exit(1)


def find_git_root(start_path=None):
    """从起始路径向上查找 Git 仓库根目录"""
    if start_path is None:
        start_path = Path(__file__).resolve().parent
    
    current = start_path
    for _ in range(20):  # 最多向上查找 20 层
        if (current / '.git').exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def check_status(repo_root):
    """检查仓库状态，返回结构化信息"""
    # 分支信息
    branch_result = run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_root)
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
    
    # 远程信息
    remote_result = run_git(['remote', '-v'], cwd=repo_root)
    has_remote = bool(remote_result.stdout.strip())
    
    # 变更文件（短格式）
    status_result = run_git(['status', '--porcelain'], cwd=repo_root)
    files = []
    for line in status_result.stdout.strip().split('\n'):
        if not line:
            continue
        status = line[:2]
        filepath = line[3:].strip()
        files.append({'status': status, 'path': filepath})
    
    # 检查是否有未 pull 的更新
    ahead_behind = run_git(['rev-list', '--left-right', '--count', f'origin/{branch}...{branch}'], cwd=repo_root)
    behind = 0
    if ahead_behind.returncode == 0:
        parts = ahead_behind.stdout.strip().split()
        if len(parts) == 2:
            behind = int(parts[0])
    
    return {
        'branch': branch,
        'has_remote': has_remote,
        'files': files,
        'behind': behind
    }


def print_status(status):
    """打印仓库状态"""
    print(f"\n[分支] 当前分支: {status['branch']}")
    print(f"[远程] 远程仓库: {'已配置' if status['has_remote'] else '未配置'}")
    
    if status['behind'] > 0:
        print(f"[WARN] 远程领先 {status['behind']} 个提交，建议先执行 git pull")
    
    if not status['files']:
        print("[OK] 没有需要提交的更改")
        return
    
    print(f"\n[文件] 待提交文件 ({len(status['files'])} 个):")
    print("-" * 50)
    for f in status['files']:
        status_map = {
            'M ': '修改  ', ' M': '修改  ',
            'A ': '新增  ', ' A': '新增  ',
            'D ': '删除  ', ' D': '删除  ',
            '??': '未跟踪',
            'R ': '重命名',
        }
        label = status_map.get(f['status'], f"{f['status']:4s}")
        print(f"  [{label}] {f['path']}")
    print("-" * 50)


def generate_commit_message(files, custom_msg=None):
    """生成提交信息"""
    if custom_msg:
        return custom_msg
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    if not files:
        return f"update homework - {date_str}"
    
    # 如果有 html/css/js 文件，推断为前端作业
    extensions = set()
    for f in files:
        ext = Path(f).suffix.lower()
        if ext:
            extensions.add(ext)
    
    if {'.html', '.css', '.js'} & extensions:
        return f"submit: 前端作业更新 - {date_str}"
    if '.py' in extensions:
        return f"submit: Python 作业更新 - {date_str}"
    if '.java' in extensions:
        return f"submit: Java 作业更新 - {date_str}"
    if {'.cpp', '.c', '.h'} & extensions:
        return f"submit: C/C++ 作业更新 - {date_str}"
    
    return f"submit: 作业更新 - {date_str}"


def do_push(repo_root, files, message):
    """执行 git add/commit/push"""
    # git add
    for f in files:
        result = run_git(['add', f], cwd=repo_root, check=False)
        if result.returncode != 0:
            print(f"[ERR] git add 失败: {f}")
            print(f"      {result.stderr.strip()}")
            return False
    print(f"[OK] git add 完成 ({len(files)} 个文件)")
    
    # git commit
    result = run_git(['commit', '-m', message], cwd=repo_root, check=False)
    if result.returncode == 0:
        print(f"[OK] git commit: {message}")
    elif "nothing to commit" in (result.stdout + result.stderr):
        print("[INFO] 没有变更需要提交")
        return True
    else:
        print(f"[ERR] git commit 失败: {result.stderr.strip()}")
        return False
    
    # git push
    branch = run_git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_root).stdout.strip()
    result = run_git(['push', 'origin', branch], cwd=repo_root, check=False)
    if result.returncode == 0:
        print("[OK] git push 成功")
        return True
    else:
        err = result.stderr.strip()
        print(f"[ERR] git push 失败: {err}")
        if "rejected" in err.lower() or "behind" in err.lower():
            print("[TIP] 提示：远程仓库有更新，请先执行 'git pull' 后再推送")
        return False


def main():
    parser = argparse.ArgumentParser(description='Homework Pusher - 自动推送作业到 Git 仓库')
    parser.add_argument('--status', '-s', action='store_true', help='仅查看仓库状态')
    parser.add_argument('--all', '-a', action='store_true', help='提交所有更改')
    parser.add_argument('--files', '-f', help='提交指定文件，用逗号分隔')
    parser.add_argument('--message', '-m', help='自定义提交信息')
    
    args = parser.parse_args()
    
    # 查找仓库根目录
    repo_root = find_git_root()
    if not repo_root:
        print("[ERR] 错误：当前目录不在 Git 仓库中，请先执行 'git init'")
        sys.exit(1)
    
    # 检查 git 配置
    name_result = run_git(['config', 'user.name'], cwd=repo_root)
    email_result = run_git(['config', 'user.email'], cwd=repo_root)
    if not name_result.stdout.strip() or not email_result.stdout.strip():
        print("[ERR] 错误：Git 用户名或邮箱未配置")
        print("      请执行：")
        print("      git config user.name '你的姓名'")
        print("      git config user.email '你的邮箱'")
        sys.exit(1)
    
    status = check_status(repo_root)
    
    if args.status:
        print_status(status)
        sys.exit(0)
    
    # 检查远程仓库
    if not status['has_remote']:
        print("[ERR] 错误：未配置远程仓库 origin")
        print("      请执行：git remote add origin <仓库地址>")
        sys.exit(1)
    
    if not status['files']:
        print("[INFO] 没有需要提交的作业文件")
        sys.exit(0)
    
    # 确定要提交的文件
    if args.all:
        files_to_commit = [f['path'] for f in status['files']]
    elif args.files:
        files_to_commit = [f.strip() for f in args.files.split(',')]
    else:
        # 默认提交所有
        files_to_commit = [f['path'] for f in status['files']]
    
    # 生成提交信息
    msg = generate_commit_message(files_to_commit, args.message)
    
    print(f"\n[START] 开始推送作业到远程仓库...")
    print(f"        仓库: {repo_root}")
    print(f"        文件: {', '.join(files_to_commit)}")
    print(f"        提交: {msg}\n")
    
    success = do_push(repo_root, files_to_commit, msg)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
