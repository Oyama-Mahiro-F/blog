---
title: 图的遍历：DFS 与 BFS
date: 2026-08-09 10:50:00
categories: 数据结构&算法
tags:
  - 图
  - 408
---

图的遍历指从某顶点出发**访问所有可达顶点各一次**。`DFS`（深度优先）用**栈**类比先序遍历，`BFS`（广度优先）用**队列**类比层序遍历——两者只是邻接点的**搜索次序**不同，因此时间复杂度完全相同。

| 维度 | DFS | BFS |
|:---|:---|:---|
| 辅助结构 | 栈（递归隐式系统栈） | 队列（FIFO） |
| 类比 | 树的先序遍历 | 树的层序遍历 |
| 树高/宽度 | 树高，窄 | 树低，宽 |
| 非树边 | 回边（Back Edge） | 横跨边（Cross Edge） |
| 典型用途 | 检测环、拓扑排序、强连通分量 | 无权图最短路径 |

## 深度优先搜索 DFS

### 算法思想

- **类比**：树的**先序遍历**——访问顶点后，立即沿第一条边深入，走不通再退回
- **辅助结构**：**栈**（递归隐式使用系统栈）——后访问的顶点先被回溯
- **搜索方式**：从起始顶点出发，沿邻接点链"一条路走到黑"；当无未访问邻接点时**回溯**到上一个顶点，继续探索其他分支

**核心步骤**：
1. 访问当前顶点，标记已访问
2. 找其第一个未访问邻接点，递归深入
3. 若无未访问邻接点（死胡同），回溯到上一层
4. 重复直至所有可达顶点均已访问

> DFS 按"深度优先、逐分支探索"的顺序访问顶点，适合**检测环、拓扑排序、强连通分量**等场景。

**DFS 遍历实例**：

![DFS 深度优先遍历实例](/blog/images/第6章 图.assets/image-20260702234510127.png)

### 具体实现（递归）

```c++
typedef enum {FALSE, TRUE} BOOLEAN;           // 布尔类型定义
BOOLEAN Visited[MAX_VEX];                     // 全局访问标志数组

void DFS(ALGraph *G, int v) {
    LinkNode *p;
    Visited[v] = TRUE;                       // 置访问标志，访问顶点 v
    Visit(v);                                // 访问顶点 v（如 printf）

    p = G->AdjList[v].firstarc;              // 链表的第一个结点
    while (p != NULL) {
        if (!Visited[p->adjvex])             // 邻接点未被访问
            DFS(G, p->adjvex);               // 从该邻接点出发深度优先搜索
        p = p->nextarc;                      // 遍历下一个邻接点
    }
}
// 邻接表 O(n+e)   邻接矩阵 O(n²)
```

### DFS 遍历入口（处理非连通图）

```c++
void DFS_traverse_Graph(ALGraph *G) {
    int v;
    for (v = 0; v < G->vexnum; v++)
        Visited[v] = FALSE;              // 访问标志初始化

    for (v = 0; v < G->vexnum; v++)      // 逐一检查每个顶点
        if (!Visited[v])                 // 未访问则启动一次 DFS
            DFS(G, v);
}
```

- 对于**无向图**：调用 `DFS()` 的次数 = **连通分量数**
- 对于**连通图**：只需调用 1 次 `DFS(G, 0)` 即可遍历所有顶点

### 深度优先生成树/森林

- **生成树**：对**连通图** DFS 时，所有顶点 + 所有引起递归的边（树边）构成**深度优先生成树**，包含 `$n$` 个顶点、`$n-1$` 条树边
- **回边（Back Edge）**：图中其余未走过的边（不在生成树中）
- **生成森林**：对**非连通图** DFS 时，每个连通分量各产生一棵生成树，总边数 `$ = n-k$`（`$k$` 为连通分量数）
- 无向连通图的 DFS 树中**没有横跨边**（Cross Edge）

![深度优先生成树示例](/blog/images/第6章 图.assets/image-20260703151450264.png)

![深度优先生成森林示例](/blog/images/第6章 图.assets/image-20260703151738055.png)

## 广度优先搜索 BFS

### 算法思想

- **类比**：树的**层序遍历**——先访问完同一深度的所有顶点，再推进到下一深度
- **辅助结构**：**队列**（FIFO）——先被访问的顶点，其邻接点也先被探索
- **搜索方式**：从起始顶点出发，依次访问其所有未访问邻接点并入队；然后出队下一个顶点，重复此过程，直至队列为空

**核心步骤**：
1. 起始顶点入队，标记已访问
2. 队头顶点出队 → 访问
3. 将该顶点的所有**未访问**邻接点依次入队并标记
4. 重复 ②③ 直至队列空

> BFS 按"距起点由近到远"的顺序访问顶点，因此可用于求**无权图最短路径**。

### 具体实现

```c++
typedef enum {FALSE, TRUE} BOOLEAN;           // 布尔类型定义
BOOLEAN Visited[MAX_VEX];                     // 全局访问标志数组

typedef struct Queue {                        // 定义一个队列保存将要访问的顶点
    int elem[MAX_VEX];                        // 队列元素（存顶点下标）
    int front, rear;                          // 队头、队尾指针
} Queue;

void BFS(ALGraph *G, int v) {                 // v 是起始顶点在 AdjList 中的下标
    LinkNode *p;
    Queue *Q = (Queue *)malloc(sizeof(Queue));
    Q->front = Q->rear = -1;                  // 初始化空队列

    if (!Visited[v]) {                        // v 尚未访问
        Q->elem[++Q->rear] = v;               // v 入队
        while (Q->front != Q->rear) {         // 队列非空
            int w = Q->elem[++Q->front];      // 队头元素出队
            Visited[w] = TRUE;                // 置访问标志
            Visit(w);                         // 访问队首元素

            p = G->AdjList[w].firstarc;       // w 的第一个邻接点
            while (p != NULL) {
                if (!Visited[p->adjvex])      // 邻接点未被访问
                    Q->elem[++Q->rear] = p->adjvex;  // 入队
                p = p->nextarc;               // 遍历下一个邻接点
            }
        }
    }
}
// 邻接表 O(n+e)   邻接矩阵 O(n²)
```

### BFS 遍历入口（处理非连通图）

```c++
void BFS_traverse_Graph(ALGraph *G) {
    int k;
    for (k = 0; k < G->vexnum; k++)
        Visited[k] = FALSE;              // 访问标志初始化

    for (int i = 0; i < G->vexnum; i++)  // 逐一检查每个顶点
        if (!Visited[i])                 // 未访问则启动一次 BFS
            BFS(G, i);
}
```

- 对于**无向图**：调用 `BFS()` 的次数 = **连通分量数**
- 对于**连通图**：只需调用 1 次 `BFS(G, 0)`

### 广度优先生成树/森林

- **生成树**：对**连通图** BFS 时，所有顶点 + 所有首次发现邻接点的边（树边）构成**广度优先生成树**，`$n$` 个顶点、`$n-1$` 条树边
- **横跨边（Cross Edge）**：连接同一层或相邻层顶点、但不在生成树中的边
- **生成森林**：对**非连通图** BFS 时，每个连通分量各产生一棵生成树，总边数 `$ = n-k$`
- **BFS 树性质**：从根到任意顶点的路径对应**无权图最短路径**；无向连通图的 BFS 树中**没有回边**（Back Edge）

### DFS vs BFS 生成树对比

| 维度 | DFS 生成树/森林 | BFS 生成树/森林 |
|:---|:---|:---|
| 树高 | 高（沿一条路深入） | 低（按层展开） |
| 宽度 | 窄 | 宽 |
| 非树边类型 | 回边（Back Edge） | 横跨边（Cross Edge） |
| 根到顶点路径 | 不保证最短 | **最短路径**（无权图） |

> **考点**：DFS 与 BFS 的**唯一本质区别**是邻接点的搜索次序——一个用栈深入、一个用队列逐层。因此两者时间复杂度完全相同，都是邻接表 `$O(n+e)$`、矩阵 `$O(n^2)$`。

## 交互演示

### DFS 深度优先搜索

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/dfs.html" title="DFS 深度优先搜索" loading="lazy" allowfullscreen></iframe>
</div>

### BFS 广度优先搜索

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/bfs.html" title="BFS 广度优先搜索" loading="lazy" allowfullscreen></iframe>
</div>

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| DFS | 用**栈**（递归），类比先序遍历 |
| BFS | 用**队列**，类比层序遍历，可求**无权图最短路径** |
| 时间复杂度 | 两者相同：邻接表 `$O(n+e)$`、矩阵 `$O(n^2)$` |
| 遍历调用次数 | 等于连通分量数 `$k$`；连通图只调用 1 次 |
| DFS 树非树边 | 只有**回边**（Back Edge）；DFS 树高 > BFS 树 |
| BFS 树非树边 | 只有**横跨边**（Cross Edge） |
| 唯一区别 | 邻接点搜索次序不同——因此两者时间复杂度相同 |
