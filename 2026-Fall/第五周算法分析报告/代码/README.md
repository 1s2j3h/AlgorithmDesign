# 思考题 6-2「对 d 叉堆的分析」—— 代码说明

《算法导论》第三版 · 第 6 章（堆排序）· 第 6.5 节（优先队列）· 思考题 6-2
配套课堂讲义：`02-1 高级数据结构-堆.pdf`

---

## 1. 文件清单

| 文件 | 作用 |
|---|---|
| `dary_heap.hpp` | d 叉最大堆核心实现（单头文件，模板可复用） |
| `test_6_2.cpp` | 6-2(a)~(e) 的演示 + 断言校验 + 与 `std::priority_queue` 随机对拍 |
| `bench_6_2.cpp` | 复杂度实测：同一源码编译成「时间版」和「比较次数版」 |
| `plot_bench.py` | 把实测 CSV 画成 PNG（供 PPT 使用） |
| `data/` | 实测输出：`timing.csv` / `counts.csv` / `heights.csv` |
| `figures/` | 生成的 5 张图 |
| `build_run.bat` | 一键编译 + 运行（Windows） |

## 2. 一键运行

```bat
build_run.bat
```

或手动编译（MinGW-w64，g++ 15.2.0 实测通过）：

```bash
g++ -O2 -std=c++17 -static -o test_6_2.exe    test_6_2.cpp          # 正确性
g++ -O2 -std=c++17 -static -o bench_time.exe  bench_6_2.cpp         # 时间实测
g++ -O2 -std=c++17 -static -DDARY_HEAP_COUNT -o bench_count.exe bench_6_2.cpp  # 比较次数实测
python plot_bench.py                                                # 画图
```

## 3. 核心下标公式（6-2(a)）

数组 `A[1..n]` 层序存放，`A[0]` 作哨兵：

```
PARENT(i)   = floor((i - 2) / d) + 1        ,  i > 1
CHILD(i, j) = d * (i - 1) + j + 1           ,  1 <= j <= d
```

`d = 2` 时退化为课堂讲的二叉堆 `PARENT(i) = floor(i/2)`。

## 4. 各操作复杂度（6-2(b)~(e)）

| 操作 | 过程 | 运行时间 |
|---|---|---|
| `MAX-HEAPIFY` | 每层比较 d 个孩子后下沉 | `O(d log_d n)` |
| `EXTRACT-MAX` | 摘根 + 末元素补根 + `MAX-HEAPIFY` | `O(d log_d n)` |
| `INCREASE-KEY` | 增大关键字后沿父链上浮 | `O(log_d n)` |
| `INSERT` | 尾部放 `-∞` + 一次 `INCREASE-KEY` | `O(log_d n)` |
| `BUILD-MAX-HEAP` | Floyd 自底向上建堆 | `O(n)` |

堆高：`h = Θ(log_d n)`，且
`log_d((d-1)n + 1) - 1  <=  h  <=  log_d((d-1)(n-1) + 1)`。

## 5. 实测结论（本机 RTX/CPU 环境，g++ -O2）

* **比较次数**在 `d = 3` 处最少，与理论最优 `d = e ≈ 2.718` 一致；
  实测 `n = 10^6` 时 `EXTRACT-MAX` 平均比较次数：
  `d=2 → 37`、`d=3 → 35`、`d=4 → 38`、`d=8 → 51`、`d=16 → 77`。
* **墙钟时间**却在 `d ≈ 4~8` 处最快（每次运行有抖动，量级为数百纳秒；
  `d = 2` 通常最慢，慢约 25%~40%）—— 这是**缓存局部性**带来的：
  树越浅，随机访存的「层数」越少，缓存未命中越少。
* 因此：**算法代价最优 ≠ 工程实现最优**，选 d 要结合工作负载与缓存。

## 6. 交付说明

* 演示/汇报：先跑 `test_6_2.exe` 证明正确，再跑 `bench_*.exe` 出数据，
  最后用 `plot_bench.py` 出图放进 PPT。
