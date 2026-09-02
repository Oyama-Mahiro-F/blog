---
title: 二叉排序树（BST）的查找、插入与删除
date: 2026-08-09 10:30:00
categories: 数据结构&算法
tags:
  - 树
  - 408
---

二叉排序树（Binary Search Tree, BST）将查找表组织为一棵**有序的二叉树**——利用"左小右大"的性质，每次比较后可排除左子树或右子树，将查找范围缩小一半。

## 定义与性质

- 左子树所有结点值 < 根结点值
- 右子树所有结点值 > 根结点值
- 左右子树也各是一棵 BST

| 性质 | 说明 |
|:---|:---|
| 中序遍历 BST | 得到**递增**有序序列 |
| 最小元素 | 最左下结点（沿左链走到底） |
| 最大元素 | 最右下结点（沿右链走到底） |

## 结构定义

```c
typedef int KeyType;                         // 关键字类型

typedef struct BSTNode {
    KeyType key;                             // 关键字
    struct BSTNode *Lchild, *Rchild;         // 左、右孩子指针
} BSTNode;
```

## 查找操作

**(1) 非递归实现**

```c++
BSTNode *BST_Search(BSTNode *T, KeyType key) {
    BSTNode *p = T;                      // 从根开始
    while (p != NULL && !EQ(p->key, key)) {
        if (LT(key, p->key)) {           // key 小于当前结点关键字
            p = p->Lchild;               // 走左子树
        } else {
            p = p->Rchild;               // 走右子树
        }
    }
    if (p != NULL && EQ(p->key, key)) {
        return p;                        // 查找成功
    }
    return NULL;                         // 查找失败
}
```

**(2) 递归实现**

```c++
BSTNode *BST_Search(BSTNode *T, KeyType key) {
    if (T == NULL) {
        return NULL;                     // 查找失败（空树）
    }
    if (EQ(T->key, key)) {
        return T;                        // 查找成功
    } else if (LT(key, T->key)) {
        return BST_Search(T->Lchild, key);  // 递归搜左子树
    } else {
        return BST_Search(T->Rchild, key);  // 递归搜右子树
    }
}
```

**查找过程示例**：

```
BST:          12
             /  \
            4   24
               /  \
              15   27
                \
                 18

查找 key = 18: 12→24→15→18（4次比较，成功）
查找 key = 20: 12→24→15→NULL（4次比较，失败）
```

## 插入操作

插入过程本质是**先查找、后挂入**——找到应插入的位置（空指针处），再新建结点挂上去。若关键字已存在则**不插入**（BST 关键字唯一）。

```c++
void Insert_BST(BSTNode *&T, KeyType key) {
    if (T == NULL) {                          // 空树 → 新结点作为根
        BSTNode *x = (BSTNode *)malloc(sizeof(BSTNode));
        x->key = key;
        x->Lchild = x->Rchild = NULL;
        T = x;
    } else if (LT(key, T->key)) {             // key 小 → 插入左子树
        Insert_BST(T->Lchild, key);
    } else if (!EQ(T->key, key)) {            // key 大且不相等 → 插入右子树
        Insert_BST(T->Rchild, key);
    }
    // EQ 相等时：已存在，不插入，直接返回
}
```

## 构建操作

利用插入操作，从空树开始逐个插入每个结点，即可建立一棵 BST。

```c++
BSTNode *Create_BST() {
    KeyType key;
    BSTNode *T = NULL;                     // 初始为空树
    scanf("%d", &key);
    while (key != 65535) {                 // 65535 为输入结束标志
        Insert_BST(T, key);                // 逐个插入
        scanf("%d", &key);
    }
    return T;                              // 返回构造好的 BST 根指针
}
```

> 通过改变插入顺序，同一组关键字可以构造出形态不同的 BST——这是影响查找效率的关键。

## 删除操作（三种情况）

| 情况 | 被删结点的孩子 | 操作 |
|:---|:---|:---|
| ① | **叶子结点**（无孩子） | 直接删除 |
| ② | **只有一个孩子** | 用孩子替代该结点 |
| ③ | **有两个孩子** | 用**中序前驱**（左子树最大）或**中序后继**（右子树最小）替换，转而删除前驱/后继 |

![BST 删除三种情况](/blog/images/第7章 查找.assets/image-20260705173911003.png)

![BST 删除三种情况示例](/blog/images/第7章 查找.assets/image-20260705173938676.png)

```c++
void BST_Delete(BSTNode *&T, KeyType key) {
    if (T == NULL) {
        return;
    }
    if (LT(key, T->key)) {
        BST_Delete(T->Lchild, key);           // key 小 → 去左子树删
    } else if (LT(T->key, key)) {
        BST_Delete(T->Rchild, key);           // key 大 → 去右子树删
    } else {                                  // 找到待删结点
        if (T->Lchild == NULL) {              // 只有右孩子或无孩子
            BSTNode *p = T;
            T = T->Rchild;
            free(p);
        } else if (T->Rchild == NULL) {       // 只有左孩子
            BSTNode *p = T;
            T = T->Lchild;
            free(p);
        } else {                              // 有两孩子 → 找中序后继
            BSTNode *s = T->Rchild;
            while (s->Lchild != NULL) {
                s = s->Lchild;                // 右子树最左下
            }
            T->key = s->key;                  // 替换值
            BST_Delete(T->Rchild, s->key);    // 递归删后继
        }
    }
}
```

## 性能分析

| 情况 | ASL | 树高 |
|:---|:---|:---|
| 最好（平衡） | $O(\log n)$ | $\lceil \log_2(n+1) \rceil$ |
| 最坏（单支/退化为链表） | $O(n)$ | $n$ |
| 平均 | $O(\log n)$ | 取决于插入顺序 |

> **关键因素**：BST 的形状取决于**关键字的插入次序**——按有序序列插入会**退化为单链表**（$h=n$），查找效率降为 $O(n)$。

## 交互演示

<div class="algo-demo">
  <iframe src="/blog/images/第7章 查找.assets/bst.html" title="二叉排序树" loading="lazy" allowfullscreen></iframe>
</div>

## 高频考点速记

| 考点 | 记忆 |
|:---|:---|
| BST 性质 | 左小右大；**中序递增**；最小=最左下、最大=最右下 |
| BST 插入 | 先查找后挂入；关键字唯一，相等不插入 |
| BST 删除 | 叶直接删 / 单支孩子顶替 / 双支用**中序前驱或后继**替换 |
| BST 退化 | 有序插入退化为单链表 $h=n$，查找 $O(n)$；平均 $O(\log n)$ |
