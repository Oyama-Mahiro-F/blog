---
title: 广度优先搜索 BFS（图的遍历）
date: 2026-08-09 10:55:00
categories: 数据结构&算法
tags:
  - 图
  - 408
---

## 算法思想

- **类比**：树的**层序遍历**——先访问完同一深度的所有顶点，再推进到下一深度
- **辅助结构**：**队列**（FIFO）——先被访问的顶点，其邻接点也先被探索
- **搜索方式**：从起始顶点出发，依次访问其所有未访问邻接点并入队；然后出队下一个顶点，重复此过程，直至队列为空

**核心步骤**：
1. 起始顶点入队，标记已访问
2. 队头顶点出队 → 访问
3. 将该顶点的所有**未访问**邻接点依次入队并标记
4. 重复 ②③ 直至队列空

> BFS 按"距起点由近到远"的顺序访问顶点，因此可用于求**无权图最短路径**。

## 具体实现

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

## BFS 遍历入口（处理非连通图）

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

## 广度优先生成树/森林

- **生成树**：对**连通图** BFS 时，所有顶点 + 所有首次发现邻接点的边（树边）构成**广度优先生成树**，$n$ 个顶点、$n-1$ 条树边
- **横跨边（Cross Edge）**：连接同一层或相邻层顶点、但不在生成树中的边
- **生成森林**：对**非连通图** BFS 时，每个连通分量各产生一棵生成树，总边数 $= n-k$
- **BFS 树性质**：从根到任意顶点的路径对应**无权图最短路径**；无向连通图的 BFS 树中**没有回边**（Back Edge）

## DFS vs BFS 对比

| 维度 | DFS 生成树/森林 | BFS 生成树/森林 |
|:---|:---|:---|
| 树高 | 高（沿一条路深入） | 低（按层展开） |
| 宽度 | 窄 | 宽 |
| 非树边类型 | 回边（Back Edge） | 横跨边（Cross Edge） |
| 根到顶点路径 | 不保证最短 | **最短路径**（无权图） |

## 交互演示

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/bfs.html" title="BFS 广度优先搜索" loading="lazy" allowfullscreen></iframe>
</div>

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| BFS | 用**队列**，类比层序遍历，可求**无权图最短路径** |
| 时间复杂度 | 邻接表 $O(n+e)$、矩阵 $O(n^2)$ |
| 遍历调用次数 | 等于连通分量数 $k$ |
| BFS 树非树边 | 只有**横跨边**（Cross Edge） |
| DFS/BFS 唯一区别 | 邻接点搜索次序不同——因此两者时间复杂度相同 |
