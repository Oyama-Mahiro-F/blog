# -*- coding: utf-8 -*-
"""生成博客四科 Markmap 思维导图（source/mindmaps/<科目>知识导图.md + .html）

- 文章链接自动从 source/_posts/<文件名>.md 的 front matter date 生成：
  /blog/<date>/<文件名>/
- 生成后自检所有链接对应的源文章是否存在
- 用法：python gen_mindmaps.py
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(ROOT, 'source', '_posts')
OUT = os.path.join(ROOT, 'source', 'mindmaps')

def post_date(stem):
    with open(os.path.join(POSTS, stem + '.md'), encoding='utf-8') as f:
        m = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', f.read(400), re.M)
    if not m:
        raise SystemExit('no date in front matter: ' + stem)
    return m.group(1)

def L(stem):
    d = post_date(stem).replace('-', '/')
    return '📖 [%s](/blog/%s/%s/)' % (stem, d, stem)

SUBJECTS = {
'数据结构知识导图': [
 ('绪论与算法分析', ['数据结构与算法基础']),
 ('线性表', ['顺序表的基本操作', '单链表的建立-头插法与尾插法', '单链表的插入与删除',
   '单链表的查找-按序号与按值', '单链表删除重复节点', '循环链表与双链表']),
 ('栈与队列', ['顺序栈的实现', '链栈的实现', '括号匹配算法', '表达式求值算法', '进制转换算法',
   '循环队列的实现', '链式队列的实现']),
 ('串', ['串的模式匹配-BF算法', '串的模式匹配-KMP算法']),
 ('数组与特殊矩阵', ['数组与特殊矩阵压缩']),
 ('树', ['二叉树的递归遍历', '二叉树的非递归遍历与层序遍历', '中序线索化算法',
   '树与森林的存储转换与遍历', '二叉排序树BST', 'AVL平衡二叉树与旋转', '哈夫曼树的构造与编码']),
 ('图', ['图的存储-邻接矩阵', '图的存储-邻接表', '十字链表与邻接多重表',
   '深度优先搜索DFS', '广度优先搜索BFS',
   'Prim最小生成树算法', 'Kruskal最小生成树算法', '并查集算法',
   'Dijkstra单源最短路径', 'Floyd多源最短路径', '拓扑排序算法', '关键路径算法']),
 ('查找', ['顺序查找算法', '折半查找算法', '分块查找算法',
   'B树与B加树', '红黑树算法', '散列表哈希表']),
 ('排序', ['直接插入排序', '折半插入排序', '希尔排序', '冒泡排序', '快速排序',
   '简单选择排序', '堆排序', '归并排序', '基数排序', '外部排序']),
 ('算法拓展', ['三数组最小距离']),
],
'操作系统知识导图': [
 ('概述', ['操作系统概述']),
 ('进程管理', ['进程与线程', 'CPU调度算法', '进程同步与互斥', '死锁']),
 ('内存管理', ['内存管理：连续分配与分页分段', '虚拟内存与页面置换算法']),
 ('文件管理', ['文件管理']),
 ('输入输出管理', ['IO管理与磁盘']),
],
'计算机组成原理知识导图': [
 ('计算机系统概述', ['计算机系统概述与性能指标']),
 ('数据的表示和计算', ['定点数的表示与运算', '浮点数与IEEE754']),
 ('存储器层次结构', ['存储系统与主存储器', 'Cache与虚拟存储器']),
 ('指令系统', ['指令系统']),
 ('中央处理器', ['CPU结构与控制器', '指令流水线']),
 ('总线系统', ['总线系统']),
 ('输入输出系统', ['IO系统：中断与DMA']),
],
}

def main():
    os.makedirs(OUT, exist_ok=True)
    failed = False
    for name, groups in SUBJECTS.items():
        lines = ['# %s（408）' % name[:-4], '',
                 '> 点击节点展开/折叠；点击 📖 进入对应文章。本文件为 Markmap 大纲源文件，可导入 XMind / 幕布。', '']
        for group, stems in groups:
            lines.append('## %s' % group)
            for s in stems:
                if not os.path.exists(os.path.join(POSTS, s + '.md')):
                    print('[MISS] %s: %s' % (name, s))
                    failed = True
                    continue
                lines.append('- %s' % L(s))
            lines.append('')
        md = os.path.join(OUT, name + '.md')
        with open(md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        html = os.path.join(OUT, name + '.html')
        subprocess.run('npx -y markmap-cli "%s" -o "%s" --offline --no-open'
                       % (md, html), check=True, cwd=ROOT, shell=True)
        print('OK %s (%d groups)' % (name, len(groups)))
    sys.exit(1 if failed else 0)

if __name__ == '__main__':
    main()
