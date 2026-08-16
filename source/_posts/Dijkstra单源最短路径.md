---
title: Dijkstra 单源最短路径算法
date: 2026-08-09 11:10:00
categories: 数据结构&算法
tags:
  - 图
  - 408
---

**问题描述**：对于给定的有向图 $G = (V, E)$ 及单个源点 $V_s$，求 $V_s$ 到其余各顶点的最短路径。

Dijkstra（迪杰斯特拉）提出了一个**按路径长度递增次序产生最短路径**的算法。

## 基本思想

从源点到其他各顶点的最短路径中，按其长度的**递增次序**依次求出——先求出长度最小的一条，然后长度第二小的，依此类推。

**核心机制**：
- 设 $S$ 为**已求得最短路径的终点集**，初始 $S = \{V_s\}$
- **关键结论**：设下一条最短路径的终点为 $V_j$，则该路径所经过的所有**中间顶点必定在 $S$ 中**——只有最后一条弧才是从 $S$ 内顶点连接到 $S$ 外顶点 $V_j$

**算法流程**：
1. 初始化：$dist[V_s] = 0$，其余为 $\infty$；$S = \{V_s\}$
2. 每轮从 $V - S$ 中选 $dist[]$ 最小的顶点 $u$，加入 $S$（确定 $u$ 的最短路径）
3. 用 $u$ 更新其所有邻接点 $v$：若 $dist[u] + w(u,v) < dist[v]$，则更新 $dist[v]$
4. 重复 ②③ 直到 $S = V$

> **限制**：Dijkstra **不允许负权边**——若存在负权，已确定的 $dist$ 可能被进一步缩小，贪心失效。

![Dijkstra 负权边失效示例](/blog/images/第6章 图.assets/image-20260703174225050.png)

## 核心公式

下一条最短路径的终点 $V_j$ 必定是不在 $S$ 中且 $dist$ 值最小的顶点：

$$dist[j] = \text{Min}\{\ dist[k]\ \mid\ V_k \in V - S\ \}$$

**初始化**：

$$dist[i] = \begin{cases}
0 & i = s \\[4pt]
w_{si} & i \neq s\ \text{且}\ \langle V_s, V_i \rangle \in E \\[4pt]
\infty & i \neq s\ \text{且}\ \langle V_s, V_i \rangle \notin E
\end{cases}$$

**松弛（修改）**：对 $V - S$ 中的每个顶点 $V_k$：若 $dist[j] + w_{jk} < dist[k]$，则 $dist[k] = dist[j] + w_{jk}$。

## 算法实现

![Dijkstra 最短路径实例](/blog/images/第6章 图.assets/dijkstra.png)

```c++
BOOLEAN final[MAX_VEX];                      // 标记顶点是否已确定最短路径
int pre[MAX_VEX], dist[MAX_VEX];             // pre[] 记录前驱，dist[] 记录最短距离

void Dijkstra_path(AdjGraph *G, int v) {     // 从图 G 中的顶点 v 出发求到其余各顶点的最短路径
    int j, k, m, min;

    for (j = 0; j < G->vexnum; j++) {        // 各数组的初始化
        pre[j] = v;
        final[j] = FALSE;
        dist[j] = G->adj[v][j];              // 邻接矩阵：直接取源点行
    }
    dist[v] = 0;
    final[v] = TRUE;                         // 设置 S = {v}

    for (j = 0; j < G->vexnum - 1; j++) {    // 对其余 n-1 个顶点
        m = 0;
        while (final[m]) m++;                // 找不在 S 中的第一个顶点

        min = INFINITY;
        for (k = 0; k < G->vexnum; k++)      // 求出当前最小的 dist[k] 值
            if (!final[k] && dist[k] < min) {
                min = dist[k];
                m = k;
            }

        final[m] = TRUE;                     // 将第 m 个顶点并入 S 中

        for (k = 0; k < G->vexnum; k++)      // 修改 dist 和 pre 数组的值
            if (!final[k] && (dist[m] + G->adj[m][k] < dist[k])) {
                dist[k] = dist[m] + G->adj[m][k];
                pre[k] = m;                  // 记录前驱，用于回溯最短路径
            }
    }
}
// 邻接矩阵 O(n²)   邻接表+堆优化 O(e log n)
```

> `pre[]` 数组用于**回溯最短路径**：从终点沿 `pre[]` 反向追溯至源点，即可得到完整路径序列。

## 复杂度分析

| 实现方式 | 时间复杂度 | 空间复杂度 |
|:---|:---|:---|
| 邻接矩阵 | $O(n^2)$ | $O(n)$（dist[] + final[]） |
| 邻接表 + 小根堆 | $O(e\log n)$ | $O(n+e)$ |
| 邻接表（无堆优化） | $O(n^2)$ | $O(n+e)$ |

**逐项拆解（邻接矩阵 $O(n^2)$）**：
- 初始化：$O(n)$
- 外层循环 $n$ 轮，每轮：选 dist 最小顶点 $O(n)$ + 松弛 $n$ 个邻接点 $O(n)$
- 总计：$O(n) + n \times O(n) = O(n^2)$

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| Dijkstra | 单源、按路径长度**递增**次序确定；**不允许负权边** |
| 复杂度 | 矩阵 $O(n^2)$、堆优化 $O(e\log n)$ |
| pre[] 回溯 | 记录前驱，沿 pre[] 反向追溯可还原最短路径 |
| 负权边处理 | Dijkstra ❌、Floyd ✅、Bellman-Ford ✅ |
