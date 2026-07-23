# 个人博客

基于 [Hexo](https://hexo.io/) 搭建，使用 Material Design 风格的 [hexo-theme-indigo](https://github.com/yscoder/hexo-theme-indigo) 主题。

## 目录

- [本地运行](#本地运行)
- [创建文章](#创建文章)
- [侧栏菜单配置](#侧栏菜单配置)
- [数学公式（KaTeX）](#数学公式katex)
- [搜索功能](#搜索功能)
- [目录（TOC）](#目录toc)
- [关于页面](#关于页面)
- [头像和作者名](#头像和作者名)
- [部署到 GitHub Pages](#部署到-github-pages)

---

## 本地运行

```bash
# 安装依赖
npm install

# 启动本地服务器（默认端口 5000）
npx hexo server -p 5000

# 访问
# http://localhost:5000/
```

生成静态文件（不启动服务器）：

```bash
npx hexo generate
```

---

## 创建文章

```bash
# 创建新文章
npx hexo new "文章标题"
```

文章保存在 `source/_posts/` 目录下，文件名为 `文章标题.md`。

### 文章 Front Matter

每篇文章顶部需要 YAML 格式的元数据：

```yaml
---
title: 文章标题
date: 2026-07-23 14:00:00
categories: 分类名称
tags:
  - 标签1
  - 标签2
mathjax: true    # 启用数学公式渲染（可选）
---
```

- `categories`：文章分类，会出现在侧栏"分类"页面
- `tags`：文章标签，会出现在侧栏"标签"页面
- `mathjax: true`：如果文章包含数学公式，需要设置此项

### 分类页面

创建新分类后，需确保 `source/categories/index.md` 存在，内容如下：

```yaml
---
title: 分类
date: 2026-07-23 01:28:50
type: categories
layout: categories
---
```

### 标签页面

`source/tags/index.md`：

```yaml
---
title: 标签
date: 2026-07-23 01:29:00
type: tags
layout: tags
---
```

---

## 侧栏菜单配置

编辑 `themes/indigo/_config.yml` 中的 `menu` 部分：

```yaml
menu:
  home:
    text: 主页
    url: /
  user:
    text: 关于
    url: /about
  archives:
    text: 归档
    url: /archives
  tags:
    text: 标签
    url: /tags
  th-list:
    text: 分类
    url: /categories
  github:
    text: GitHub
    url: https://github.com/你的用户名
    target: _blank        # 新标签页打开
  book:
    text: 笔记
    url: https://外部链接
    target: _blank
```

- 键名（如 `home`、`user`）决定前端显示的图标（FontAwesome 图标类名 `icon-{键名}`）
- `text`：菜单显示文字
- `url`：链接地址，支持站内路径（`/` 开头）和外部链接（`https://` 开头）
- `target: _blank`：可选，在新标签页打开链接

---

## 数学公式（KaTeX）

博客使用 **KaTeX 服务端渲染**，公式在构建时预渲染为 HTML，无需客户端 JavaScript。

### 启用公式

在文章 Front Matter 中添加 `mathjax: true`：

```yaml
---
title: 文章标题
mathjax: true
---
```

### 语法

- 行内公式：`$E = mc^2$`
- 独立公式：`$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$`

### 技术细节

- `scripts/katex.js`：在 Hexo `after_render:html` 过滤器中将 `$...$` 替换为 KaTeX HTML
- `themes/indigo/source/css/katex.min.css`：本地 KaTeX 样式表
- 依赖包：`katex`、`he`（HTML 实体解码）

---

## 搜索功能

点击顶部导航栏的 🔍 图标使用搜索。输入关键词后实时匹配文章标题、标签和正文内容。

### 技术实现

- `hexo-generator-json-content`：构建时生成 `content.json`，包含所有文章数据
- `themes/indigo/source/js/search.js`：前端异步加载 JSON，正则匹配并渲染结果

### 配置（`_config.yml`）

```yaml
jsonContent:
  meta: false
  pages: false
  posts:
    title: true
    date: true
    path: true
    text: true
    tags: true
```

---

## 目录（TOC）

文章页面右侧自动显示目录，基于文章中的 `##`、`###`、`####` 标题生成。

### 配置（`themes/indigo/_config.yml`）

```yaml
toc:
  list_number: true   # 显示数字编号，设为 false 关闭
```

---

## 关于页面

关于页面位于 `source/about/index.md`，侧栏链接为"关于"。

```yaml
---
title: 关于
date: 2026-07-23 15:00:00
layout: page
---

这里写自我介绍内容...
```

---

## 头像和作者名

### 头像

替换 `themes/indigo/source/img/avatar.jpg` 为你的头像图片。

### 作者名

修改 `_config.yml`：

```yaml
author: 你的名字
```

### 邮箱

修改 `themes/indigo/_config.yml`：

```yaml
email: your-email@example.com
```

### 站点标题

修改 `_config.yml`：

```yaml
title: 站点标题
subtitle: ''    # 副标题，留空则不显示
```

---

## 部署到 GitHub Pages

### 首次部署

1. 在 GitHub 创建仓库（如 `blog`）
2. 配置 `_config.yml`：

```yaml
url: https://你的用户名.github.io/blog
root: /blog/

deploy:
  type: git
  repo: https://github.com/你的用户名/blog.git
  branch: gh-pages
```

3. 安装部署插件并部署：

```bash
npm install hexo-deployer-git
npx hexo clean
npx hexo deploy
```

4. 在 GitHub 仓库 Settings → Pages 中确认 Source 为 `gh-pages` 分支

### 日常更新

```bash
# 写完文章后
npx hexo clean
npx hexo deploy
```

### 源码管理

博客源码（`master` 分支）和生成的静态网站（`gh-pages` 分支）分离：

```bash
# 推送源码
git add -A
git commit -m "更新内容"
git push origin master
```

---

## 主题自定义修改记录

以下是对原主题的修改汇总，升级主题时需注意保留：

| 文件 | 修改 |
|------|------|
| `themes/indigo/source/css/_partial/loading.less` | `.fade` / `.fade-scale` 默认 `opacity: 1`（修复内容不可见） |
| `themes/indigo/layout/_partial/post/toc.ejs` | 移除 `post-toc-shrink` 类（修复 TOC 不显示） |
| `themes/indigo/layout/_partial/plugins/mathjax.ejs` | 清空内容（改用 KaTeX 服务端渲染） |
| `themes/indigo/layout/_partial/head.ejs` | 添加 KaTeX CSS 引用 |
| `themes/indigo/layout/_partial/script.ejs` | Waves.js 改为本地加载 |
| `themes/indigo/scripts/plugins.js` | 注入 lodash `_` 到 EJS 模板上下文 |
| `themes/indigo/source/js/waves.min.js` | 从 CDN 下载到本地 |
| `themes/indigo/source/css/katex.min.css` | 从 CDN 下载到本地 |
| `scripts/katex.js` | 新增：KaTeX 服务端渲染脚本 |

---

## 技术栈

- **框架**：[Hexo](https://hexo.io/) 8.x
- **主题**：[hexo-theme-indigo](https://github.com/yscoder/hexo-theme-indigo)（Material Design）
- **数学渲染**：[KaTeX](https://katex.org/)（服务端预渲染）
- **搜索**：hexo-generator-json-content + 前端正则匹配
- **部署**：GitHub Pages（gh-pages 分支）
- **CSS 预处理**：Less
- **模板引擎**：EJS
