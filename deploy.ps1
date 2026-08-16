# ============================================================
#  deploy.ps1 — 一键上传 GitHub 并部署 GitHub Pages
#
#  功能流程：
#    1. git add -A（暂存所有改动）
#    2. git commit（可自定义提交信息）
#    3. git push origin master（上传源码）
#    4. hexo clean + generate（重新构建静态网站）
#    5. hexo deploy（部署到 gh-pages 分支）
#
#  用法：
#    .\deploy.ps1                       # 自动生成提交信息 "Update: 日期 时间"
#    .\deploy.ps1 -m "新增文章"          # 自定义提交信息
#    .\deploy.ps1 -SkipDeploy           # 只上传源码，不部署网站
#    .\deploy.ps1 -SkipPush             # 只部署网站，不上传源码
# ============================================================

param(
    [string]$m = "",          # 提交信息，缺省自动生成
    [switch]$SkipDeploy,      # 跳过构建与部署
    [switch]$SkipPush         # 跳过源码推送
)

# 切到脚本所在目录（项目根目录），无论从哪里调用
Set-Location $PSScriptRoot
$ErrorActionPreference = 'Stop'

# ---------- 输出辅助 ----------
function Write-Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Ok  ($msg) { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  [失败] $msg" -ForegroundColor Red }

# ---------- 0. 生成默认提交信息 ----------
if (-not $m) {
    $m = "Update: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}
Write-Host "提交信息: $m" -ForegroundColor DarkGray

# ---------- 1. 提交改动 ----------
Write-Step "1/5 检查并提交改动"
$status = git status --short 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "当前目录不是 Git 仓库？"
    exit 1
}
$hasChanges = [bool]$status
if (-not $hasChanges) {
    Write-Host "  没有检测到任何改动，跳过 commit/push。" -ForegroundColor Yellow
} else {
    Write-Host "  以下文件将被提交：" -ForegroundColor DarkGray
    $status | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }

    git add -A
    if ($LASTEXITCODE -ne 0) { Write-Fail "git add 失败"; exit 1 }

    git commit -m $m
    if ($LASTEXITCODE -ne 0) { Write-Fail "git commit 失败"; exit 1 }
    Write-Ok "已提交: $m"
}

# ---------- 2. 推送源码 ----------
if (-not $SkipPush -and $hasChanges) {
    Write-Step "2/5 推送源码到 GitHub (master)"
    git push origin master
    if ($LASTEXITCODE -ne 0) { Write-Fail "git push 失败"; exit 1 }
    Write-Ok "源码已推送"
} elseif (-not $hasChanges) {
    Write-Host "  无改动，跳过源码推送" -ForegroundColor Yellow
} else {
    Write-Host "  已跳过源码推送 (-SkipPush)" -ForegroundColor Yellow
}

# ---------- 3. 清理并构建 ----------
if (-not $SkipDeploy) {
    Write-Step "3/5 清理并构建静态网站"
    npx hexo clean
    if ($LASTEXITCODE -ne 0) { Write-Fail "hexo clean 失败"; exit 1 }
    npx hexo generate
    if ($LASTEXITCODE -ne 0) { Write-Fail "hexo generate 失败"; exit 1 }
    $fileCount = (Get-ChildItem public -Recurse -File -ErrorAction SilentlyContinue).Count
    Write-Ok "构建完成，共 $fileCount 个文件"

    # ---------- 4. 部署到 gh-pages ----------
    Write-Step "4/5 部署到 GitHub Pages (gh-pages)"
    npx hexo deploy
    if ($LASTEXITCODE -ne 0) { Write-Fail "hexo deploy 失败"; exit 1 }
    Write-Ok "网站已部署"

    # ---------- 5. 验证远端状态 ----------
    Write-Step "5/5 验证部署结果"
    $master = git ls-remote origin refs/heads/master
    $pages  = git ls-remote origin refs/heads/gh-pages
    Write-Host "  master  : $master" -ForegroundColor DarkGray
    Write-Host "  gh-pages: $pages"  -ForegroundColor DarkGray
    Write-Ok "全部完成！"

    Write-Host "`n  🌐 https://oyama-mahiro-f.github.io/blog/" -ForegroundColor Green
    Write-Host "  （GitHub Pages 缓存刷新约需 1-2 分钟）" -ForegroundColor DarkGray
} else {
    Write-Host "  已跳过构建与部署 (-SkipDeploy)" -ForegroundColor Yellow
    Write-Ok "源码上传完成！"
}
