---
title: 串的模式匹配：KMP 算法
date: 2026-08-09 12:55:00
categories: 数据结构&算法
tags:
  - 串
  - 408
---

KMP 算法**利用模式串自身的结构信息**（`next` 数组），避免主串指针 $i$ 的回溯，每次匹配失败时 $j$ 回溯到 `next[j]`。匹配时间复杂度 $O(n+m)$。

## 核心概念

- **前缀**：除最后一个字符外，字符串的所有头部子串
- **后缀**：除第一个字符外，字符串的所有尾部子串
- **最长公共前后缀**：前缀和后缀集合的交集中，最长的那个元素

| 模式串 T | 前缀 | 后缀 | 最长公共前后缀长度 |
|:---|:---|:---|:---:|
| `"a"` | $\varnothing$ | $\varnothing$ | 0 |
| `"ab"` | `{a}` | `{b}` | 0 |
| `"aba"` | `{a, ab}` | `{a, ba}` | 1（`"a"`） |
| `"abab"` | `{a, ab, aba}` | `{b, ab, bab}` | 2（`"ab"`） |

## next 数组定义

在模式串中（下标从 1 开始），`next[i]` 表示模式串中以下标 $i$ 处字符结尾的子串的最大相同前后缀的长度：

$$
next[j] = \begin{cases}
0 & \text{当 } j = 1 \\
\text{max}\{k \mid 1 < k < j \text{ 且 } T[1..k-1] = T[j-k+1..j-1]\} & \text{当此集合非空} \\
1 & \text{其他情况}
\end{cases}
$$

```
模式串 T = "abcac" 的 next 数组:

j:       1            2            3            4            5
T[j]:    a            b            c            a            c
next[j]: 0            1            1            1            2
```

## KMP 匹配过程（C++ 代码）

```c++
int Index_KMP(SString S, SString T, int next[]) {
    int i = 1, j = 1;
    while (i <= S.length && j <= T.length) {
        if (j == 0 || S.ch[i] == T.ch[j]) {
            i++; j++;
        } else {
            j = next[j];                     // i 不回溯，j 回溯到 next[j]
        }
    }
    if (j > T.length) return i - T.length;   // 匹配成功
    return 0;                                 // 匹配失败
}
```

## next 数组的求法

```c++
void Get_Next(SString T, int next[]) {
    int i = 1, j = 0;
    next[1] = 0;
    while (i < T.length) {
        if (j == 0 || T.ch[i] == T.ch[j]) {
            i++; j++;
            next[i] = j;                      // 记录最长公共前后缀长度
        } else {
            j = next[j];                      // 失配时回溯 j
        }
    }
}
```

> 双指针递推：相等则 i++、j++ 且 next[i]=j；不等则 j=next[j]。

**实例**：主串 `"BBC ABCDAB ABCDABCDABDE"`，模式串 `"ABCDABD"`

| j | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| T[j] | A | B | C | D | A | B | D |
| 公共前后缀长 | — | 0 | 0 | 0 | 0 | 1 ("A") | 2 ("AB") |
| next[j] | 0 | 1 | 1 | 1 | 1 | 2 | 3 |

**匹配关键点**：$S[12..17]$ = `"ABCDAB"` 已匹配 6 个字符后 $S[18]$ ≠ $T[7]$，由于 `next[7]=3`，$j$ 回退到 3——利用已匹配的 `"AB"` 前缀，**$i$ 不动**继续比较 $S[18]$ 和 $T[3]$。

## nextval 数组（改进版）

当 $T[i] = T[next[i]]$ 时，$nextval[i] = nextval[next[i]]$，**跳过必然再次失配**的回溯：

```c++
void Get_NextVal(SString T, int nextval[]) {
    int i = 1, j = 0;
    nextval[1] = 0;
    while (i < T.length) {
        if (j == 0 || T.ch[i] == T.ch[j]) {
            i++; j++;
            if (T.ch[i] != T.ch[j])
                nextval[i] = j;
            else
                nextval[i] = nextval[j];      // 相等时继承
        } else {
            j = nextval[j];
        }
    }
}
```

**nextval 图解**（以 `T = "ABCDABD"` 为例）：

```
T[j]:    A   B   C   D   A   B   D
next:    0   1   1   1   1   2   3

j=5:  T[5]=A, next[5]=1, T[1]=A
      A = A  → nextval[5] = nextval[1] = 0   ← 避免回溯后再比同一个 A

j=6:  T[6]=B, next[6]=2, T[2]=B
      B = B  → nextval[6] = nextval[2] = 1   ← 避免回溯后再比同一个 B

结果:  nextval: 0   1   1   1   0   1   3
```

> **nextval 改进原理**：若 $T[j] = T[next[j]]$，即回溯后还是同一个字符，必然再次失配——直接跳到更远的 `nextval[next[j]]`。

## BF vs KMP 对比

| 维度 | BF | KMP |
|:---|:---|:---|
| 主串回溯 | $i$ 回溯 | $i$ **不回溯** |
| 时间复杂度 | $O(nm)$（最坏） | $O(n+m)$ |
| 额外空间 | $O(1)$ | $O(m)$（next 数组） |
| 适用场景 | 模式串短 | 模式串长 / 字符集小 |

## 交互演示

<div class="algo-demo">
  <iframe src="/blog/images/第10章 串.assets/kmp.html" title="KMP 匹配过程" loading="lazy" allowfullscreen></iframe>
</div>

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| KMP 思想 | **i 永不回溯**，失配时 j 跳到 next[j]，利用模式串自身结构；匹配时间 **$O(n+m)$** |
| next 定义 | $next[j]=\begin{cases}0 & \text{当 } j=1\\ \max\{k\mid 1<k<j \text{ 且 } T[1..k-1]=T[j-k+1..j-1]\} & \text{当此集合非空}\\ 1 & \text{其他}\end{cases}$；$next[1]=0$，其余无公共前后缀为 1 |
| next 实例 | "ABCDABD"：next = **0 1 1 1 1 2 3** |
| nextval 改进 | 若 $T[i]=T[next[i]]$，则 $nextval[i]=nextval[next[i]]$——**跳过必然再次失配**的回溯 |
| nextval 实例 | "ABCDABD"：nextval = **0 1 1 1 0 1 3** |
| KMP 空间 | next（nextval）数组 **$O(m)$**；BF 仅 $O(1)$ |
