---
title: 最短路径：Dijkstra 与 Floyd
date: 2026-08-09 11:10:00
categories: 数据结构&算法
tags:
  - 图
  - 408
---

最短路径是图最常见的应用。**Dijkstra** 解决**单源**最短路径（一个源点到其余各点），采用贪心；**Floyd** 解决**多源**最短路径（每对顶点之间），采用动态规划。两者对负权边的态度截然不同，是 408 高频区分点。

| 算法 | 类型 | 思想 | 时间 | 负权边 |
|:---|:---|:---|:---|:---:|
| Dijkstra | 单源 | 贪心（按路径长度递增确定） | `$O(n^2)$` / `$O(e\log n)$` | ❌ |
| Floyd | 多源 | 动态规划（逐点作中转） | `$O(n^3)$` | ✅（不允许负环） |

## Dijkstra 算法（单源）

### 问题描述

对于给定的有向图 `$G = (V, E)$` 及单个源点 `$V_s$`，求 `$V_s$` 到其余各顶点的最短路径。Dijkstra 提出了一个**按路径长度递增次序产生最短路径**的算法。

### 基本思想

从源点到其他各顶点的最短路径中，按其长度的**递增次序**依次求出——先求出长度最小的一条，然后长度第二小的，依此类推。

**核心机制**：
- 设 `$S$` 为**已求得最短路径的终点集**，初始 `$S = \{V_s\}$`
- **关键结论**：设下一条最短路径的终点为 `$V_j$`，则该路径所经过的所有**中间顶点必定在 `$S$` 中**——只有最后一条弧才是从 `$S$` 内顶点连接到 `$S$` 外顶点 `$V_j$`

**算法流程**：
1. 初始化：`$dist[V_s] = 0$`，其余为 `$\infty$`；`$S = \{V_s\}$`
2. 每轮从 `$V - S$` 中选 `$dist[]$` 最小的顶点 `$u$`，加入 `$S$`（确定 `$u$` 的最短路径）
3. 用 `$u$` 更新其所有邻接点 `$v$`：若 `$dist[u] + w(u,v) < dist[v]$`，则更新 `$dist[v]$`
4. 重复 ②③ 直到 `$S = V$`

> **限制**：Dijkstra **不允许负权边**——若存在负权，已确定的 `$dist$` 可能被进一步缩小，贪心失效。

![Dijkstra 负权边失效示例](/blog/images/第6章 图.assets/image-20260703174225050.png)

### 核心公式

下一条最短路径的终点 `$V_j$` 必定是不在 `$S$` 中且 `$dist$` 值最小的顶点：

$$dist[j] = \text{Min}\{\ dist[k]\ \mid\ V_k \in V - S\ \}$$

**初始化**：

$$dist[i] = \begin{cases}
0 & i = s \\[4pt]
w_{si} & i \neq s\ \text{且}\ \langle V_s, V_i \rangle \in E \\[4pt]
\infty & i \neq s\ \text{且}\ \langle V_s, V_i \rangle \notin E
\end{cases}$$

**松弛（修改）**：对 `$V - S$` 中的每个顶点 `$V_k$`：若 `$dist[j] + w_{jk} < dist[k]$`，则 `$dist[k] = dist[j] + w_{jk}$`。

### 算法实现

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

### 复杂度分析

| 实现方式 | 时间复杂度 | 空间复杂度 |
|:---|:---|:---|
| 邻接矩阵 | `$O(n^2)$` | `$O(n)$`（dist[] + final[]） |
| 邻接表 + 小根堆 | `$O(e\log n)$` | `$O(n+e)$` |
| 邻接表（无堆优化） | `$O(n^2)$` | `$O(n+e)$` |

**逐项拆解（邻接矩阵 `$O(n^2)$`）**：
- 初始化：`$O(n)$`
- 外层循环 `$n$` 轮，每轮：选 dist 最小顶点 `$O(n)$` + 松弛 `$n$` 个邻接点 `$O(n)$`
- 总计：`$O(n) + n \times O(n) = O(n^2)$`

## Floyd 算法（多源）

### 问题描述

求**每一对顶点之间**的最短路径。允许负权，**不允许负环**。

> 核心递推式：`$dist[i][j] = \min(dist[i][j],\ dist[i][k] + dist[k][j])$`

### 基本思想

Floyd 算法采用**动态规划**思想：依次尝试将每个顶点作为**中转点**，若从 `$V_i$` 先到 `$V_k$` 再到 `$V_j$` 比当前已知的 `$dist[i][j]$` 更短，则更新。

- 初始：`$dist[i][j] = w_{ij}$`（直接边的权值，无边则为 `$\infty$`）
- 第 `$k$` 轮：允许中转点为 `$\{V_0, V_1, \dots, V_k\}$`，更新所有顶点对的最短距离
- `$n$` 轮后，`$dist[i][j]$` 即为 `$V_i$` 到 `$V_j$` 的最终最短路径长度

### 算法实现（仅求长度）

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

### 算法实现（记录路径）

`Path[i][j]` 保存从 `$V_i$` 到 `$V_j$` 的最短路径所经过的**中转顶点**。若 `Path[i][j] = k`：从 `$V_i$` 到 `$V_j$` 经过 `$V_k$`。

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

### 实例：依次加入中转点

![Floyd 算法实例](/blog/images/第6章 图.assets/Gemini_Generated_Image_kpktzmkpktzmkpkt.png)

| 轮次 | 允许中转点 | 更新结果 |
|:---|:---|:---|
| Step 1 (k=0) | `$V_0$` | `$A[2][1]$`：`$\infty$` → 7（借道 `$V_0$`），Path[2][1]=0 |
| Step 2 (k=1) | `$V_0, V_1$` | `$A[0][2]$`：8 → 6（借道 `$V_1$`），Path[0][2]=1 |
| Step 3 (k=2) | 全部 | `$A[1][0]$`：`$\infty$` → 9（借道 `$V_2$`），Path[1][0]=2 |

### 复杂度分析

| 实现方式 | 时间复杂度 | 空间复杂度 |
|:---|:---|:---|
| 邻接矩阵 | `$O(n^3)$` | `$O(n^2)$`（dist[n][n] 矩阵） |

> Floyd 因其简洁的三重循环结构，虽然复杂度 `$O(n^3)$` 较高，但常数因子小，适合 `$n$` 较小（如 `$n \leq 200$`）的全源最短路径问题。

### 负权边与负权回路

| 算法 | 负权边 | 原因 |
|:---|:---:|:---|
| **Dijkstra** | ❌ | 贪心：已确定顶点不再更新 |
| **Floyd** | ✅ | 动态规划：所有顶点轮流作中转点，反复松弛直至收敛 |
| **Bellman-Ford** | ✅ | 对所有边松弛 `$n-1$` 轮，允许已被更新的顶点再次被修正 |

**负权回路**：回路边权之和为负数时，每绕一圈路径长度减少——最短路径**不存在**（可无限缩短）。

![负权回路示例](/blog/images/第6章 图.assets/image-20260703174409035.png)

| 问题 | 结论 |
|:---|:---|
| 有负权回路时是否存在最短路径？ | **不存在**——可无限绕圈趋近 `$-\infty$` |
| 如何检测负权回路？ | Floyd：若某 `$dist[i][i] < 0$`（对角元为负），则存在负环 |

> **408 核心记忆**：Dijkstra **不能有负权边**；Floyd **可以有负权边，不能有负权回路**；Bellman-Ford **不能有负权回路，但可以检测负权回路**（第 `$n$` 轮仍有更新则存在负环）。

## Dijkstra vs Floyd 对比

| 维度 | Dijkstra | Floyd |
|:---|:---|:---|
| 解决类型 | 单源（一个起点） | 多源（每对顶点） |
| 思想 | 贪心 | 动态规划 |
| 时间复杂度 | `$O(n^2)$` / `$O(e\log n)$` | `$O(n^3)$` |
| 空间复杂度 | `$O(n)$` / `$O(n+e)$` | `$O(n^2)$` |
| 负权边 | ❌ 不允许 | ✅ 允许 |
| 负权回路 | ❌（直接失效） | ❌ 不允许（可检测） |
| 路径回溯 | `pre[]` 数组反向追溯 | `Path[][]` 递归回溯 |

> **易错点**：Floyd 虽然允许负权边，但**不允许负权回路**——一旦存在负环，最短路径无意义。Dijkstra 遇到负权边会给出错误结果，而不是报错，务必审题看清边权符号。

## 交互演示

### Dijkstra 单源最短路径

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/dijkstra.html" title="Dijkstra 最短路径" loading="lazy" allowfullscreen></iframe>
</div>

### Floyd 多源最短路径

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/floyd.html" title="Floyd 多源最短路径" loading="lazy" allowfullscreen></iframe>
</div>

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| Dijkstra | 单源、按路径长度**递增**次序确定；**不允许负权边** |
| Dijkstra 复杂度 | 矩阵 `$O(n^2)$`、堆优化 `$O(e\log n)$` |
| pre[] 回溯 | 记录前驱，沿 pre[] 反向追溯可还原最短路径 |
| Floyd | 多源动态规划三重循环 `$O(n^3)$`、空间 `$O(n^2)$`；允许负权、**不允许负环** |
| 负环检测 | Floyd 对角元 `$dist[i][i]<0$`；Bellman-Ford 第 `$n$` 轮仍更新 |
| 路径记录 | Path[i][j]=k 表示经过中转点 k，递归回溯输出 |
| 负权边处理 | Dijkstra ❌、Floyd ✅、Bellman-Ford ✅（可检负环） |
