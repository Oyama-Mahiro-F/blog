# AGENTS.md — 博客（Hexo）编辑与部署规范

> 本文件是 `D:\blog2` 项目内**面向 AI 代理**的操作指令。凡在本仓库修改文章、主题、脚本，默认遵守本规范。
> 它沉淀了编写/构建/部署过程中**实际踩过的坑**，以及**用户明确提出的要求**。遇到相关场景请优先对照本文件。

## 1. 项目概览

- **框架**：Hexo 8.x（`npx hexo ...`），主题 `hexo-theme-indigo`（Material Design，EJS + Less）
- **定位**：考研 408 复习笔记博客，内容分 `数据结构&算法`、`计算机网络`、`博客` 三类
- **数学渲染**：KaTeX **服务端预渲染**（自定义插件 `scripts/katex.js`，非客户端 JS）
- **搜索**：`hexo-generator-json-content` 构建时生成 `public/content.json`，前端 `themes/indigo/source/js/search.js` 匹配
- **部署**：GitHub Pages，仓库 `Oyama-Mahiro-F/blog`，`root: /blog/`，静态站推 `gh-pages` 分支

### 关键目录

```
D:\blog2\
├─ source\_posts\                      ← 文章（Markdown）
├─ source\images\第N章 XX.assets\      ← 文章配图 / 算法可视化 HTML
├─ scripts\katex.js                    ← KaTeX 服务端渲染（已修复，勿回退到全局正则版）
├─ themes\indigo\
│   ├─ source\css\_partial\article.less ← 正文样式（表格等，已改内边距）
│   └─ _config.yml                      ← 主题配置（menu/toc/搜索等）
├─ public\                             ← 生成产物（已 gitignore）
├─ .deploy_git\                        ← 部署仓库（已 gitignore，勿提交）
└─ push.py / push.bat                  ← 旧上传脚本（本环境会因 schannel 失败，勿依赖）
```

## 2. 文章编写规范

### 2.1 Front Matter

```yaml
---
title: 文章标题
date: 2026-08-26 09:00:00
categories: 计算机网络        # 数据结构&算法 / 计算机网络 / 博客
tags:
  - 网络                      # 主题标签（也用作侧栏"标签"页）
  - 408
---
```

- 分类自动生成分类页（`计算机网络`、`数据结构&算法` 等），无需改代码；每篇文章可从笔记取出单章内容成文。
- 文章结语**无需人工序号**（见 §3），序号统一交给侧栏 TOC（`themes/indigo/_config.yml` 的 `toc.list_number: true`）。

### 2.2 正文格式

- 中文为主，术语中英对照（如 `GBN, Go-Back-N`）。
- 表格统一 `|:---|` 对齐，列数一致；对比一律用表格（GBN vs SR、IP vs MAC、IPv4 vs IPv6 等）。
- 考点/易错提醒用引用块：
  ```markdown
  > **考点**：……（一句话，加粗关键词）
  > **易错点**：……
  ```
- 公式：行内 `$...$`，独立块 `$$...$$`；KaTeX 表格内也能渲染（提取器会把表格单元格里的 `$...$` 一并处理）。
- 例题要完整：题目 → 数据/公式 → 结果表 → 验算 → 考点。
- 结尾通常附"高频考点速记"表（`| 考点 | 记忆 |`）。

### 2.3 ℹ️ 重要坑：`~` 会被解析成删除线（务必转义）

Markdown 里 **`~` 是删除线标记**。同一行/单元格内出现**成对 `~`** 时，markdown 会把两个 `~` 之间的内容包成 `<del>`，导致范围表达（如 `1~126`）显示成 `1` + 删除线 + `126`。

- **触发**：一个单元格/段落里有 **≥2 个 `~`** 时（如 `A：1~126（/8）；B：128~191（/16）；C：192~223（/24）`，3 个 `~` 成对 → 中间内容被划删除线）。
- **规避**：区间 `~` 一律写成 HTML 实体 **`&#126;`**（浏览器仍显示 `~`，但不会被当作 markdown 标记）。
  ```markdown
  A：1&#126;126（/8）；B：128&#126;191（/16）；C：192&#126;223（/24）   ✅
  A：1~126（/8）；B：128~191（/16）；C：192~223（/24）              ❌ 出现 <del>
  ```
- 单个 `~`（每单元格一个，如 `1 ~ 126` 带空格）安全，但**为稳妥，单元格含 ≥2 个 `~` 时统一转义**。

### 2.4 图片

- 配图**直接从考研笔记复制**（用户要求）：`D:\university_learning\考研\...\笔记\第N章 XX.assets\*.png` → `source\images\第N章 XX.assets\`。
- 引用路径统一：`![说明](/blog/images/第N章 XX.assets/文件名.png)`（带 `/blog/` 前缀，注意 URL 中文须可用）。
- 起名用可读英文/中文（如 `ip-分类地址.png`、`gbn-时序图.png`），避免长 hash。

## 3. 正文标题不带序号（用户明确要求）

TOC 侧栏已按 `list_number` 自动编号（`1.`、`1.1.`），所以**正文标题不要加** `一、二、三…` 或 `1.` 前缀，否则与 TOC 重复。

```markdown
## 分类 IP 地址（A/B/C/D/E）   ✅   （TOC 显示 "1. 分类 IP 地址..."）
## 一、分类 IP 地址（A/B/C/D/E） ❌   与 TOC 序号重复
```

## 4. 已修复的已知怪癖（勿回退）

| 问题 | 现象 | 修复位置 / 结论 |
|---|---|---|
| **KaTeX 注入标题属性** | 标题含 `$...$` 时，KaTeX HTML 被替换进标题的 `id`/`href`/`title`，产生 `class="headerlink"` 垃圾、污染 TOC | `scripts/katex.js` 的 `renderInto` 改为**三遍式**：① 拆 `$$` 外层 `<p>`；② **只替换文本节点**（`/(<[^>]*>)|xxKATEXMATH(\d+)xx/g` 匹配 `<...>` 时原样返回）；③ 残余占位符（属性内）替换为**可读 TeX 源码并 HTML 转义**。勿回退到原来的 `replace(MATH_RE, renderOne)` 全局版 |
| **表格内边距过小** | 单元格里的高 KaTeX 分数（`\frac`）贴上下边框，排列过密 | `themes/indigo/source/css/_partial/article.less`：`td,th { padding: 8px 10px; vertical-align: middle; }`（原来是 `padding: 0 10px`） |
| **`~` 删除线** | 见 §2.3 | 用 `&#126;` 转义 |
| **正文标题序号** | 见 §3 | 标题不带 `一、二、三…` |

## 5. 构建与验证

- **增量构建可能不生效**：`npx hexo generate` 有时输出 `0 files generated`，且**不检测 `.less`/主题改动**（改 `article.less` 后 CSS 不变）。改主题样式后**必须**先 `npx hexo clean` 再 `npx hexo generate` 全量重建。
- **验证渲染**：读 `public/2026/MM/DD/<标题>/index.html`，检查：
  - KaTeX 占位符泄漏 = 0（`grep KATEXMATH`）
  - heading 的 `id`/`href` 里**无** `<span class="katex">`（即 §4 未回退）
  - 正文标题无序号；`<del>` 数量符合预期（不应误出现）
- **公式计数**：`class="katex"` 数应≈文章公式数；`katex-display` 独立块数。

## 6. 部署（用户要求：写完直接自动部署）

### 6.1 环境坑（本机 git 必须这样，否则 push 失败）

- **schannel TLS 后端不可用**：报 `schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e)`。必须改用 OpenSSL 后端：`-c http.sslBackend=openssl`。
- **全局 `~/.gitconfig` 不可写**（权限受限）：`gh auth setup-git` 会报 `could not lock config file ... Permission denied`。改用 **gh token 内嵌 URL** 推送。
- `gh cli` 已登录且有 `repo` 权限（`gh auth status` 可查），`gh api` 可访问 GitHub。
- `Invoke-WebRequest` / `curl` 访问 `github.io` 也会因 schannel 失败，**验证线上内容用 `gh api` 读 gh-pages 分支 blob**。

### 6.2 推送命令（模板）

```powershell
$tok = gh auth token
$url = "https://oauth2:$tok@github.com/Oyama-Mahiro-F/blog.git"
git -C D:\blog2 -c http.sslBackend=openssl push $url master            # 推源码
git -C D:\blog2\.deploy_git -c http.sslBackend=openssl push $url master:gh-pages  # 推静态站
```

> 不要打印 token；上面用 `$tok` 变量避免明文。

### 6.3 部署步骤（自动执行）

1. `npx hexo clean && npx hexo generate`（改主题后必做；只改文章可 `generate`）
2. 提交源码并推 `master`：`git add -A && git commit -m "..."` → 按 6.2 push master
3. 刷新部署仓库：
   ```powershell
   $dep = "D:\blog2\.deploy_git"
   Get-ChildItem $dep -Force | Where-Object { $_.Name -ne '.git' } | Remove-Item -Recurse -Force
   Copy-Item "D:\blog2\public\*" $dep -Recurse -Force
   git -C $dep add -A
   git -C $dep -c user.name="Oyama-Mahiro-F" -c user.email="614682480@qq.com" commit -m "Site updated"
   ```
4. 按 6.2 推 `gh-pages`（`.deploy_git` 的本地 `master` 推远程 `gh-pages`）。
5. 验证：
   ```powershell
   gh api repos/Oyama-Mahiro-F/blog/branches/master   --jq '.commit.sha'
   gh api repos/Oyama-Mahiro-F/blog/branches/gh-pages --jq '.commit.sha'
   # 读取线上某文件 blob（用 gh api .../git/trees/<sha>?recursive=1 找 sha，再读 blob）
   ```
   GitHub Pages 构建约 1 分钟后生效，刷新页面可见。

### 6.4 踩坑备忘

- `push.py / push.bat` 在当前环境会因 schannel 失败（它调 `npx hexo deploy`，内部 git 用 schannel）。勿用它，按 6.3 手动流程。
- `.deploy_git` 和 `public` 都在 `.gitignore` 中，**不要**把生成产物提交到 `master` 源码仓库。
- Level：仓库提交作者用 `Oyama-Mahiro-F <614682480@qq.com>`（与现有历史一致）。

## 7. 常用命令

```bash
npx hexo server -p 5000     # 本地预览
npx hexo generate           # 构建
npx hexo clean              # 清空 public 与 db
git -C D:\blog2 status      # 查看改动
```
