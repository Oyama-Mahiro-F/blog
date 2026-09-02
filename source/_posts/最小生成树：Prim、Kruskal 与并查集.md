---
title: 最小生成树：Prim、Kruskal 与并查集
date: 2026-08-09 10:20:00
categories: 数据结构&算法
tags:
  - 图
  - 408
---

**最小生成树（MST）**：在**带权连通无向图**中，所有生成树中**边权之和最小**的那棵。恰有 `$n-1$` 条边。

**MST 性质（贪心理论基础）**：设 `$U$` 是 `$V$` 的真子集。若边 `$(u,v)$` 满足 `$u \in U$`、`$v \in V-U$`，且 `$(u,v)$` 在所有这样的边中权值最小，则必存在一棵 MST 包含 `$(u,v)$`。Prim 与 Kruskal 都是这一性质的体现——只是一个"加点"、一个"加边"。

| 算法 | 策略 | 时间 | 适合 |
|:---|:---|:---|:---|
| Prim | 加点（维护候选边集） | `$O(n^2)$` 或 `$O(e\log n)$` | 稠密图 |
| Kruskal | 加边（排序 + 并查集防环） | `$O(e\log e)$` | 稀疏图 |

## Prim 算法（加点法）

### 算法思想

- **类比**：向一棵"生长中的树"不断添加最近的顶点，直到覆盖全部 `$n$` 个顶点
- **辅助结构**：维护两个顶点集合——已选入 MST 的 `$U$` 和未选的 `$V-U$`，以及连接两集合的候选边
- **核心策略**（贪心）：每轮从候选边中选**权值最小**的一条 `$(u,v)$`（`$u \in U, v \in V-U$`），将 `$v$` 纳入 `$U$`，并更新候选边

**核心步骤**：
1. 任选起始顶点 `$v_0$`，`$U = \{v_0\}$`
2. 找连接 `$U$` 与 `$V-U$` 的最小权边 `$(u,v)$`
3. 将 `$v$` 加入 `$U$`，将 `$(u,v)$` 加入 MST
4. 用 `$v$` 的新邻接边更新候选边集
5. 重复 ②~④ 直至 `$|U| = n$`

> Prim 本质是 MST 性质的直接应用：每次贪心地选择跨越集合的最小边，共选 `$n-1$` 次。

### 执行过程示例

![Prim 算法执行过程](/blog/images/第6章 图.assets/2745283-20221107140303083-140056158.png)

| 步骤 | 刚入树的顶点 | 本步选出的最小边 |
|:---|:---|:---|
| 初始 | A | A-B (1) |
| Step 1 | B | A-D (4) |
| Step 2 | D | D-F (2) |
| Step 3 | F | A-C (5) |
| Step 4 | C | C-E (3) |
| Step 5 | E | *(生成树构建完成)* |

### 复杂度

| 实现方式 | 时间复杂度 |
|:---|:---|
| 邻接矩阵 | `$O(n^2)$` |
| 堆优化 + 邻接表 | `$O(e\log n)$` |

**适合**：稠密图

## Kruskal 算法（加边法）

### 算法思想

- **类比**：将图中所有边按权值从小到大排序，依次"试探"每条边——能加就加，不能加（会成环）就跳过
- **辅助结构**：**并查集（Union-Find）**——维护顶点所属的连通分量，快速判断两个顶点是否已在同一集合
- **核心策略**（贪心）：每次从剩余的边中选**权值最小**且**不会形成回路**的边加入 MST

**核心步骤**：
1. 将所有边按权值升序排序
2. 初始化并查集，每个顶点自成一个集合
3. 依次取出每条边 `$(u,v)$`：
   - 若 `$u$` 和 `$v$` **不在同一集合** → 加入 MST，合并两集合
   - 若 `$u$` 和 `$v$` **已在同一集合** → 跳过（加入会成环）
4. 重复 ③ 直至选出 `$n-1$` 条边

> Kruskal 本质：全局范围内贪心选最小边，用并查集保证不破坏树结构（无环）。

![Kruskal 算法执行过程](/blog/images/第6章 图.assets/2745283-20221107140326521-464551758.png)

### 伪代码

```
1. 边集 E 按权值升序排序
2. 初始化并查集（每个顶点独立）
3. count = 0
4. 对每条边 (u, v)（按序）：
     if Find(u) != Find(v):        # 不成环
         (u,v) 加入 MST
         Union(u, v)
         count++
         if count == n-1: break
```

### 复杂度

| 项目 | 说明 |
|:---|:---|
| 时间复杂度 | `$O(e\log e)$`（排序主导） |
| 适合 | 稀疏图 |

## 并查集（Union-Find）

Kruskal 之所以能 `$O(1)$` 判环，靠的就是并查集。它用**双亲表示法**（树结构）管理不相交集合，支持**查**（Find，找根）和**并**（Union，合并）。

> **核心思想**：每个集合用一棵树表示，树的根代表整个集合。`parent[i]` 存结点 i 的双亲，根结点的 `parent = -1`。

### 存储结构与初始化

```c
#define MAXSIZE 100

int parent[MAXSIZE];           // 双亲数组，parent[i]=-1 表示 i 是根

void InitSet(int n) {
    for (int i = 0; i < n; i++)
        parent[i] = -1;        // 初始每个元素自成一个集合（各自的根）
}
```

### 查找 Find（朴素版）

沿着 parent 链一直向上，直到找到根（parent = -1）。

```c
int Find(int x) {
    while (parent[x] != -1)
        x = parent[x];         // 沿着双亲链向上爬
    return x;                  // 返回根的下标
}
```

### 合并 Union（朴素版）

将一棵树的根挂到另一棵树的根下面。

```c
void Union(int a, int b) {
    int rootA = Find(a);
    int rootB = Find(b);
    if (rootA != rootB)
        parent[rootB] = rootA;  // B 的根挂到 A 的根下面
}
```

### 路径压缩优化（Find 优化）

查找时把沿途所有结点**直接挂到根下面**，摊还后接近 `$O(1)$`。

```c
int Find_Compress(int x) {
    if (parent[x] == -1)
        return x;
    return parent[x] = Find_Compress(parent[x]);  // 递归压缩，挂到根
}
```

```
压缩前：0→1→2→根3           压缩后：0→根3, 1→根3, 2→根3
  [3]                            [3]
   │                            / | \
  [2]                          [0][1][2]
   │
  [1]
   │
  [0]
```

### 按秩合并优化（Union 优化）

将**矮树**挂到**高树**下面，避免退化成链。需要额外 `rank[]` 数组。

```c
int rank[MAXSIZE];             // rank[i] = 以 i 为根的树的高度（近似）

void InitSet_Rank(int n) {
    for (int i = 0; i < n; i++) {
        parent[i] = -1;
        rank[i] = 0;           // 初始高度为 0
    }
}

void Union_Rank(int a, int b) {
    int rootA = Find_Compress(a);
    int rootB = Find_Compress(b);
    if (rootA == rootB) return;

    if (rank[rootA] < rank[rootB])
        parent[rootA] = rootB;          // 矮的挂到高的
    else if (rank[rootA] > rank[rootB])
        parent[rootB] = rootA;
    else {
        parent[rootB] = rootA;          // 等高时任选，新根高度+1
        rank[rootA]++;
    }
}
```

```
按秩合并：把矮树挂高树下              不按秩：可能退化成链
  高[0]  +  矮[2]                        [0]
   / \       │                           /
 [1] [3]    [4]                        [2]    → O(n) ❌
                                       /
  合并后树高 O(log n) ✓               [1]
                                     /
                                   [4]
```

### 完整实现（路径压缩 + 按秩合并）

```c
int Find(int x) {
    if (parent[x] == -1)
        return x;
    return parent[x] = Find(parent[x]);
}

void Union(int a, int b) {
    int ra = Find(a), rb = Find(b);
    if (ra == rb) return;
    if (rank[ra] < rank[rb])  parent[ra] = rb;
    else if (rank[ra] > rank[rb]) parent[rb] = ra;
    else { parent[rb] = ra; rank[ra]++; }
}
```

> 双优化后 `Find` 和 `Union` 的摊还时间复杂度接近 `$O(\alpha(n))$`，其中 `$\alpha$` 是反阿克曼函数，实际中可视为常数。

## Prim vs Kruskal 对比

| 维度 | Prim | Kruskal |
|:---|:---|:---|
| 策略 | 加点（维护候选边集） | 加边（排序 + 并查集防环） |
| 时间 | `$O(n^2)$` 或 `$O(e\log n)$` | `$O(e\log e)$` |
| 适合 | 稠密图 | 稀疏图 |
| 依赖结构 | 邻接矩阵/邻接表 | 并查集 |

## MST 唯一性讨论

| 条件 | 唯一性 |
|:---|:---|
| 图中**所有边的权值互不相等** | MST **一定唯一** |
| 存在权值相等的边 | MST **不一定唯一**（可能有多棵权值和相等的 MST） |

**408 考点**：
1. 唯一性判定：若所有边权值互异 → MST 唯一（充分非必要条件）
2. 不唯一时，不同 MST 的**边权之和一定相等**
3. 对带权连通无向图，若任意两条边的权值均不相等，则 MST 唯一；反之不一定，还需看等权边是否构成"可替换圈"

> **核心记忆**：权值全不同 → MST 唯一；有权值相等的边 → 不一定唯一，需具体分析。

## 交互演示

### Prim 最小生成树

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/prim.html" title="Prim 最小生成树" loading="lazy" allowfullscreen></iframe>
</div>

### Kruskal 最小生成树

<div class="algo-demo">
  <iframe src="/blog/images/第6章 图.assets/kruskal.html" title="Kruskal 最小生成树" loading="lazy" allowfullscreen></iframe>
</div>

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| MST 定义 | 带权连通图边权和最小的生成树，`$n-1$` 条边 |
| MST 性质 | 连接 `$U$` 与 `$V-U$` 的**最小权边必属于某棵 MST**（贪心基础） |
| Prim | **加点法**，`$O(n^2)$`、堆优化 `$O(e\log n)$，适合稠密图 |
| Kruskal | **加边法**+并查集防环，`$O(e\log e)$，适合稀疏图 |
| 并查集查/并 | Find 找根（parent==-1），Union 将一树根挂另一树根下 |
| 路径压缩 | 沿途结点**直接挂到根**下，摊还接近 `$O(1)$` |
| 按秩合并 | **矮树挂高树**下，避免退化为链（`$O(\log n)$`） |
| 并查集双优化 | 摊还复杂度接近 **$O(\alpha(n))$**，`$\alpha$` 为反阿克曼函数 |
| MST 唯一性 | 边权全互异→**一定唯一**；有等权边→可能不唯一但**权值和相等** |
