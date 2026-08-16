"""
博客上传 + GitHub Pages 部署脚本
用法：双击 push.bat 或执行 python push.py
功能：git commit -> push master -> hexo clean/generate -> hexo deploy -> 验证
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_URL_SSH = 'git@github.com:Oyama-Mahiro-F/blog.git'
REPO_URL_HTTPS = 'https://github.com/Oyama-Mahiro-F/blog.git'
SITE_URL = 'https://oyama-mahiro-f.github.io/blog/'


def run(cmd, cwd=ROOT, check=True):
    """执行 shell 命令，返回 (success, output_text)"""
    print(f'  $ {cmd}')
    r = subprocess.run(cmd, shell=True, cwd=cwd,
                       capture_output=True, encoding='utf-8', errors='replace')
    out = (r.stdout or '').strip()
    err = (r.stderr or '').strip()
    if r.returncode != 0 and check:
        # "nothing to commit" / "dubious ownership" 等不算致命错误
        if any(kw in out or kw in err for kw in ('nothing to commit', 'dubious ownership', 'up to date')):
            return True, out
        if err:
            print(f'  [错误] {err}')
        return False, err
    return True, out


def run_interactive(cmd, cwd=ROOT):
    """执行需要用户交互的命令（如 git push 登录弹窗、hexo deploy）"""
    print(f'  $ {cmd}')
    r = subprocess.run(cmd, shell=True, cwd=cwd)
    return r.returncode == 0


def fix_safe_directory():
    """修复换电脑后 git dubious ownership 问题"""
    r = subprocess.run('git status', shell=True, cwd=ROOT,
                       capture_output=True, encoding='utf-8', errors='replace')
    if 'dubious ownership' in (r.stderr or '') or 'dubious ownership' in (r.stdout or ''):
        print('[预检] 修复目录权限...')
        subprocess.run(f'git config --global --add safe.directory "{ROOT}"', shell=True)
        path = ROOT.replace('\\', '/')
        print(f'  已添加 safe.directory: {path}')


def check_git_user():
    """检查 git user.name / user.email 是否配置；未配置则引导输入"""
    print('[预检] 检查 Git 用户配置...')
    name = ''
    email = ''
    try:
        r = subprocess.run('git config user.name', shell=True, cwd=ROOT,
                           capture_output=True, encoding='utf-8', errors='replace')
        name = (r.stdout or '').strip()
        r = subprocess.run('git config user.email', shell=True, cwd=ROOT,
                           capture_output=True, encoding='utf-8', errors='replace')
        email = (r.stdout or '').strip()
    except Exception:
        pass

    if name and email:
        print(f'  [OK] {name} <{email}>')
        return True

    print('  [警告] Git 用户信息未配置，提交时需要。')
    if not name:
        name = input('  请输入你的 GitHub 用户名: ').strip()
    if not email:
        email = input('  请输入你的 GitHub 邮箱: ').strip()
    if name and email:
        subprocess.run(f'git config user.name "{name}"', shell=True, cwd=ROOT)
        subprocess.run(f'git config user.email "{email}"', shell=True, cwd=ROOT)
        print(f'  [OK] 已设置: {name} <{email}>')
        return True
    print('  [跳过] 未输入，提交时可能失败。')
    return False


def check_git_remote():
    """检查是否能连接到 GitHub，自动切换 HTTPS"""
    print('[预检] 检查 GitHub 连接...')
    ok, out = run('git remote get-url origin', check=False)
    if not ok:
        print('  [错误] 未找到远程仓库 origin')
        return False

    current_url = out.strip()
    print(f'  远程地址: {current_url}')

    # 如果当前是 SSH 但连不上，尝试切回 HTTPS
    if 'git@' in current_url:
        print('  检测到 SSH 地址，测试连接...')
        try:
            r = subprocess.run('git ls-remote --exit-code origin HEAD', shell=True, cwd=ROOT,
                               capture_output=True, encoding='utf-8', errors='replace', timeout=10)
            if r.returncode != 0:
                raise Exception('SSH 连接失败')
        except Exception:
            print('  SSH 不可用，切换为 HTTPS...')
            run(f'git remote set-url origin {REPO_URL_HTTPS}', check=False)
            current_url = REPO_URL_HTTPS
            print(f'  已切换: {current_url}')

    # 测试连接（带超时 — GitHub 国内有时慢）
    print('  正在检测连接（最多等待 10 秒）...')
    try:
        r = subprocess.run('git ls-remote --exit-code origin HEAD', shell=True, cwd=ROOT,
                           capture_output=True, encoding='utf-8', errors='replace', timeout=10)
        if r.returncode == 0:
            print('  [OK] GitHub 连接正常')
            return True
        err = (r.stderr or '').strip()
    except subprocess.TimeoutExpired:
        err = '连接超时'
    except Exception as e:
        err = str(e)

    print(f'  [警告] 预检未通过 ({err})，跳过检测，推送时重试。')
    print(f'  如果推送也失败，浏览器打开 https://github.com 检查网络。')
    return True  # 不阻塞，push 时还会再试


def main():
    print('=' * 50)
    print('  博客 -> GitHub 上传 + Pages 部署工具')
    print('=' * 50)
    print()

    # ---- 预检 ----
    fix_safe_directory()
    check_git_user()
    if not check_git_remote():
        print()
        input('修复后按回车重试，或直接关闭窗口退出...')
        return
    print()

    # ---- 1. Git add & commit ----
    print('[1/6] Git 提交...')
    ok, _ = run('git add -A', check=False)
    if not ok:
        print('  [失败] git add 出错')
        input('按回车退出...')
        return

    # 检查是否有内容可提交
    r = subprocess.run('git diff --cached --quiet', shell=True, cwd=ROOT)
    if r.returncode == 0:
        print('  没有新变更，跳过提交。')
    else:
        ok, _ = run('git commit -m "更新博客"')
        if not ok:
            print('  [失败] git commit 出错')
            input('按回车退出...')
            return
        print('  完成。')
    print()

    # ---- 2. Push 源码 ----
    print('[2/6] 推送到 GitHub master（如需登录请在弹出的窗口中授权）...')
    if not run_interactive('git push origin master'):
        print()
        print('  [推送失败] 常见原因:')
        print('    1. 网络问题 - 浏览器访问 github.com 试试')
        print('    2. 首次推送需授权 - 弹出的 GitHub 登录窗口点 "Sign in with browser"')
        print('    3. 远程有冲突 - 先 git pull 再重试')
        input('按回车退出...')
        return
    print('  完成。')
    print()

    # ---- 3. 清理 ----
    print('[3/6] 清理构建缓存...')
    ok, out = run('npx hexo clean')
    if not ok:
        print('  [失败] hexo clean 出错')
        input('按回车退出...')
        return
    print('  完成。')
    print()

    # ---- 4. 构建 ----
    print('[4/6] 生成静态网站...')
    ok, out = run('npx hexo generate')
    if not ok:
        print('  [失败] hexo generate 出错')
        input('按回车退出...')
        return
    print('  完成。')
    print()

    # ---- 5. 部署 ----
    print('[5/6] 部署到 GitHub Pages（gh-pages 分支）...')
    if not run_interactive('npx hexo deploy'):
        print()
        print('  [部署失败] 常见原因:')
        print('    1. 网络问题 - 浏览器访问 github.com 试试')
        print('    2. 首次部署需授权 - 弹出的 GitHub 登录窗口点 "Sign in with browser"')
        input('按回车退出...')
        return
    print('  完成。')
    print()

    # ---- 6. 验证 ----
    print('[6/6] 验证部署结果...')
    ok, out = run('git ls-remote origin refs/heads/gh-pages', check=False)
    if ok:
        print(f'  gh-pages 分支: {out[:60]}')
    ok, out = run('git ls-remote origin refs/heads/master', check=False)
    if ok:
        print(f'  master 分支:   {out[:60]}')
    print()

    print('=' * 50)
    print('  ✓ 全部完成！')
    print(f'  网站: {SITE_URL}')
    print('  (等待约 1 分钟后刷新页面即可看到更新)')
    print('=' * 50)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n已取消。')
    except Exception as e:
        print(f'\n[异常] {e}')
    input('按回车退出...')
