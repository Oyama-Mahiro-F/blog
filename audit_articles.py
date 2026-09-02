# -*- coding: utf-8 -*-
"""审计 _posts 文章粒度：字数 / 章节数，标记过碎或过大。"""
import os, re, glob
from collections import defaultdict

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "source", "_posts")
rows = []
problems = []

for f in sorted(glob.glob(os.path.join(POSTS, "*.md"))):
    raw = open(f, encoding="utf-8").read()
    t = raw.replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    if not m:
        problems.append("无 front matter: " + os.path.basename(f))
        continue
    fm = m.group(1)
    cm = re.search(r"^categories:\s*(.+)$", fm, re.M)
    cat = cm.group(1).strip() if cm else "?"
    dm = re.search(r"^date:\s*(.+)$", fm, re.M)
    date = dm.group(1).strip()[:10] if dm else "?"
    tm = re.search(r"^title:\s*(.+)$", fm, re.M)
    title = tm.group(1).strip() if tm else "?"
    body = t[m.end():]
    h2 = re.findall(r"^##\s+(.+)$", t, re.M)
    n = len(re.sub(r"\s", "", body))
    rows.append((cat, os.path.basename(f), title, n, len(h2), date))

d = defaultdict(list)
for r in rows:
    d[r[0]].append(r)

out = []
for c in ["数据结构&算法", "计算机组成原理", "操作系统", "计算机网络", "博客"]:
    if c not in d:
        continue
    lst = sorted(d[c], key=lambda x: x[3])
    out.append("=" * 72)
    out.append("【%s】%d 篇 / %s 字" % (c, len(lst), format(sum(x[3] for x in lst), ",")))
    out.append("=" * 72)
    for cat, fn, title, n, h2, date in lst:
        flag = "碎" if n < 3000 else ("大" if n > 16000 else "  ")
        out.append("%s %6d字 %2d节  %s" % (flag, n, h2, fn))
if problems:
    out.append("")
    out.append("!! 问题: " + "; ".join(problems))

txt = "\n".join(out)
print(txt)
open(os.path.join(os.path.dirname(POSTS), "audit_result.txt"), "w", encoding="utf-8").write(txt)
