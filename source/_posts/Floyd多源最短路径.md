---
title: Floyd 多源最短路径算法
date: 2026-08-09 11:15:00
categories: 数据结构&算法
tags:
  - 图
  - 408
---

求**每一对顶点之间**的最短路径。允许负权，**不允许负环**。

> 核心递推式：$dist[i][j] = \min(dist[i][j],\ dist[i][k] + dist[k][j])$

## 基本思想

Floyd 算法采用**动态规划**思想：依次尝试将每个顶点作为**中转点**，若从 $V_i$ 先到 $V_k$ 再到 $V_j$ 比当前已知的 $dist[i][j]$ 更短，则更新。

- 初始：$dist[i][j] = w_{ij}$（直接边的权值，无边则为 $\infty$）
- 第 $k$ 轮：允许中转点为 $\{V_0, V_1, \dots, V_k\}$，更新所有顶点对的最短距离
- $n$ 轮后，$dist[i][j]$ 即为 $V_i$ 到 $V_j$ 的最终最短路径长度

## 算法实现（仅求长度）

```c++
void Floyd(MGraph G, int dist[][MAXV]) {
    for (int i = 0; i < G.vexnum; i++)          // 初始化
        for (int j = 0; j < G.vexnum; j++)
            dist[i][j] = G.edges[i][j];

    for (int k = 0; k < G.vexnum; k++)          // 中转点
        for (int i = 0; i < G.vexnum; i++)       // 起点
            for (int j = 0; j < G.vexnum; j++)   // 终点
                if (dist[i][k] + dist[k][j] < dist[i][j])
                    dist[i][j] = dist[i][k] + dist[k][j];
}
// O(n³)  O(n²)
```

## 算法实现（记录路径）

`Path[i][j]` 保存从 $V_i$ 到 $V_j$ 的最短路径所经过的**中转顶点**。若 `Path[i][j] = k`：从 $V_i$ 到 $V_j$ 经过 $V_k$。

```c++
int A[MAX_VEX][MAX_VEX];                         // 最短距离矩阵
int Path[MAX_VEX][MAX_VEX];                      // 路径矩阵（记录中转顶点）

void Floyd_path(AdjGraph *G) {
    int j, k, m;
    for (j = 0; j < G->vexnum; j++)              // 各数组的初始化
        for (k = 0; k < G->vexnum; k++) {
            A[j][k] = G->adj[j][k];              // 邻接矩阵直接赋值
            Path[j][k] = -1;                     // -1 表示无中转顶点
        }

    for (m = 0; m < G->vexnum; m++)              // 中转点
        for (j = 0; j < G->vexnum; j++)          // 起点
            for (k = 0; k < G->vexnum; k++)      // 终点
                if ((A[j][m] + A[m][k]) < A[j][k]) {
                    A[j][k] = A[j][m] + A[m][k]; // 修改最短距离
                    Path[j][k] = m;              // 记录中转顶点
                }
}
// O(n³)  O(n²)
```

**输出路径**（递归回溯）：

```c++
void PrintPath(int j, int k) {
    if (Path[j][k] == -1) {                      // 直接边，无中转
        printf(" → %d", k);
        return;
    }
    PrintPath(j, Path[j][k]);                    // 前半段：j → 中转点
    PrintPath(Path[j][k], k);                    // 后半段：中转点 → k
}
// 调用: printf("%d", start); PrintPath(start, end);
```

## 实例：依次加入中转点

![Floyd 算法实例](/blog/images/第6章 图.assets/Gemini_Generated_Image_kpktzmkpktzmkpkt.png)

| 轮次 | 允许中转点 | 更新结果 |
|:---|:---|:---|
| Step 1 (k=0) | $V_0$ | $A[2][1]$：$\infty$ → 7（借道 $V_0$），Path[2][1]=0 |
| Step 2 (k=1) | $V_0, V_1$ | $A[0][2]$：8 → 6（借道 $V_1$），Path[0][2]=1 |
| Step 3 (k=2) | 全部 | $A[1][0]$：$\infty$ → 9（借道 $V_2$），Path[1][0]=2 |

## 复杂度分析

| 实现方式 | 时间复杂度 | 空间复杂度 |
|:---|:---|:---|
| 邻接矩阵 | $O(n^3)$ | $O(n^2)$（dist[n][n] 矩阵） |

> Floyd 因其简洁的三重循环结构，虽然复杂度 $O(n^3)$ 较高，但常数因子小，适合 $n$ 较小（如 $n \leq 200$）的全源最短路径问题。

## 负权边与负权回路

| 算法 | 负权边 | 原因 |
|:---|:---:|:---|
| **Dijkstra** | ❌ | 贪心：已确定顶点不再更新 |
| **Floyd** | ✅ | 动态规划：所有顶点轮流作中转点，反复松弛直至收敛 |
| **Bellman-Ford** | ✅ | 对所有边松弛 $n-1$ 轮，允许已被更新的顶点再次被修正 |

**负权回路**：回路边权之和为负数时，每绕一圈路径长度减少——最短路径**不存在**（可无限缩短）。

![负权回路示例](/blog/images/第6章 图.assets/image-20260703174409035.png)

| 问题 | 结论 |
|:---|:---|
| 有负权回路时是否存在最短路径？ | **不存在**——可无限绕圈趋近 $-\infty$ |
| 如何检测负权回路？ | Floyd：若某 $dist[i][i] < 0$（对角元为负），则存在负环 |

> **408 核心记忆**：Dijkstra **不能有负权边**；Floyd **可以有负权边，不能有负权回路**；Bellman-Ford **不能有负权回路，但可以检测负权回路**（第 $n$ 轮仍有更新则存在负环）。

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| Floyd | 多源动态规划三重循环 $O(n^3)$、空间 $O(n^2)$；允许负权、**不允许负环** |
| 负环检测 | Floyd 对角元 $dist[i][i]<0$；Bellman-Ford 第 $n$ 轮仍更新 |
| 路径记录 | Path[i][j]=k 表示经过中转点 k，递归回溯输出 |
