# -*- coding: utf-8 -*-
"""
plot_bench.py -- 把 bench_6_2.cpp / bench_count.exe 产出的 CSV 画成图，供 PPT 使用。

运行：
    python plot_bench.py
输出（全部写入 figures/）：
    fig_1_height.png          堆高 h 与 n、d 的关系
    fig_2_cmp_extract.png     EXTRACT-MAX 平均比较次数（验证 O(d log_d n)）
    fig_3_time_extract.png    EXTRACT-MAX 墙钟耗时
    fig_4_time_insert.png     INSERT / INCREASE-KEY 墙钟耗时
    fig_5_tradeoff.png        「比较最优 d=3」vs「墙钟最优 d≈8」的权衡
"""
import csv
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 中文显示
# 与汇报 PPT 统一：中文用宋体，数学用 STIX（Times 系），颜色取湖南大学讲义配色
plt.rcParams["font.sans-serif"] = ["SimSun", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif"]
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 150
plt.rcParams["font.size"] = 11

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "figures")
os.makedirs(OUT, exist_ok=True)

DS = [2, 3, 4, 8, 16]
NS = [10000, 30000, 100000, 300000, 1000000]
# 讲义配色：暗红 #A93733 / 正红 #C00000 / 高亮绿 #8DC63F / 深绿 #538225 / 灰 #808080
COLORS = {2: "#A93733", 3: "#C00000", 4: "#8DC63F", 8: "#538225", 16: "#808080"}
MARK = {2: "o", 3: "s", 4: "^", 8: "D", 16: "v"}


def load(path, value_col):
    tab = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tab[(int(r["d"]), int(r["n"]), r["op"])] = float(r[value_col])
    return tab


timing = load(os.path.join(DATA, "timing.csv"), "ns_per_op")
counts = load(os.path.join(DATA, "counts.csv"), "cmp_per_op")
heights = {}
with open(os.path.join(DATA, "heights.csv"), newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        heights[(int(r["d"]), int(r["n"]))] = int(r["height"])


def finish(fig, name):
    fig.tight_layout()
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor="white")
    plt.close(fig)
    print("saved", p)


# ----------------------------------------------------------------------------
# 图 1：堆高 h 与 n、d 的关系
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.6, 4.6))
for d in DS:
    xs = [n for n in NS]
    ys = [math.floor(math.log((n - 1) * (d - 1) + 1) / math.log(d)) for n in NS]
    ax.plot(xs, ys, marker=MARK[d], color=COLORS[d], lw=2, label=f"d = {d}")
# 理论 log_d n
xs = [n for n in NS]
ax.plot(xs, [math.log(n, 2) for n in NS], "--", color="#808080", lw=1.3, alpha=.8,
        label=r"参考：$\log_2 n$")
ax.set_xscale("log")
ax.set_xlabel("元素个数 n（对数轴）")
ax.set_ylabel("堆高 h（边数）")
ax.set_title("d 叉堆的高度：$h=\\Theta(\\log_d n)$  ——   d 越大树越矮", fontsize=13)
ax.grid(alpha=.3, which="both", ls=":")
ax.legend(title="叉数 d", frameon=False, ncol=2)
finish(fig, "fig_1_height.png")

# ----------------------------------------------------------------------------
# 图 2：EXTRACT-MAX 平均比较次数
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.6, 4.6))
for d in DS:
    ys = [counts[(d, n, "extract")] for n in NS]
    ax.plot(NS, ys, marker=MARK[d], color=COLORS[d], lw=2, label=f"d = {d}（实测）")
    # 理论 d*log_d n
    ax.plot(NS, [d * math.log(n, d) for n in NS], color=COLORS[d], ls=":", lw=1.2, alpha=.8)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("元素个数 n（对数轴）")
ax.set_ylabel("每次 EXTRACT-MAX 的平均比较次数")
ax.set_title("EXTRACT-MAX 的比较次数：实测（实线）与 $d\\log_d n$（虚线）吻合", fontsize=13)
ax.grid(alpha=.3, which="both", ls=":")
ax.legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.13))
finish(fig, "fig_2_cmp_extract.png")

# ----------------------------------------------------------------------------
# 图 3：EXTRACT-MAX 墙钟耗时
# ----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.6, 4.6))
for d in DS:
    ys = [timing[(d, n, "extract")] for n in NS]
    ax.plot(NS, ys, marker=MARK[d], color=COLORS[d], lw=2, label=f"d = {d}")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("元素个数 n（对数轴）")
ax.set_ylabel("每次 EXTRACT-MAX 耗时（纳秒）")
ax.set_title("EXTRACT-MAX 墙钟耗时：n 很大时 d ≈ 4~8 反而最快（缓存效应）", fontsize=13)
ax.grid(alpha=.3, which="both", ls=":")
ax.legend(title="叉数 d", frameon=False, ncol=2)
finish(fig, "fig_3_time_extract.png")

# ----------------------------------------------------------------------------
# 图 4：INSERT / INCREASE-KEY 墙钟耗时
# ----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.4))
for j, op, title in [(0, "insert", "INSERT"), (1, "increase", "INCREASE-KEY")]:
    ax = axes[j]
    for d in DS:
        ys = [timing[(d, n, op)] for n in NS]
        ax.plot(NS, ys, marker=MARK[d], color=COLORS[d], lw=2, label=f"d = {d}")
    ax.set_xscale("log")
    ax.set_xlabel("元素个数 n（对数轴）")
    ax.set_ylabel("单次操作耗时（纳秒）")
    ax.set_title(f"{title}：树越浅越快，大 d 有优势", fontsize=12)
    ax.grid(alpha=.3, which="both", ls=":")
fig.suptitle("只沿一条父链、每层 O(1) 的两个操作：$\\Theta(\\log_d n)$", fontsize=13)
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.06, 1, 0.94))
fig.savefig(os.path.join(OUT, "fig_4_time_insert.png"), facecolor="white")
plt.close(fig)
print("saved fig_4_time_insert.png")

# ----------------------------------------------------------------------------
# 图 5：权衡 —— 比较次数最优 vs 墙钟最优
# ----------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))

# 左：理论 d/ln d 曲线，最小值在 d = e
ax = axes[0]
import numpy as np
dd = np.linspace(1.6, 16, 400)
ax.plot(dd, dd / np.log(dd), color="#A93733", lw=2.2)
ax.axvline(math.e, color="#C00000", ls="--", lw=1.5)
ax.annotate("最优 $d=e\\approx2.718$\n（整数取 d = 3）", xy=(math.e, 2.75),
            xytext=(3.3, 5.05), color="#C00000", fontsize=11,
            arrowprops=dict(arrowstyle="->", color="#C00000"))
ax.scatter([d for d in DS], [d / math.log(d) for d in DS], color="#A93733", zorder=5, s=28)
for d in DS:
    ax.annotate(f"{d}", (d, d / math.log(d)), textcoords="offset points",
                xytext=(3, 5), fontsize=9, color="#A93733")
ax.set_xlabel("叉数 d")
ax.set_ylabel("每层的比较成本 $d/\\ln d$")
ax.set_ylim(2.4, 6.4)
ax.set_title("理论：EXTRACT-MAX 的比较代价在 d = e 处最小", fontsize=12)
ax.grid(alpha=.3, ls=":")

# 右：n = 10^6 时，比较次数 vs 墙钟耗时
ax = axes[1]
N = 1000000
xs = list(range(len(DS)))
cmpv = [counts[(d, N, "extract")] for d in DS]
timv = [timing[(d, N, "extract")] for d in DS]
b = ax.bar([x - 0.2 for x in xs], cmpv, width=0.4, color="#A93733",
           label="比较次数 / 次")
ax.set_ylim(0, 95)
ax.set_ylabel("每次 EXTRACT-MAX 的比较次数", color="#A93733")
ax.tick_params(axis="y", labelcolor="#A93733")
ax.set_xticks(xs)
ax.set_xticklabels([f"d={d}" for d in DS])
ax2 = ax.twinx()
ax2.plot(xs, timv, color="#538225", marker="o", lw=2.2, label="耗时 / ns")
ax2.set_ylim(0, 470)
ax2.set_ylabel("每次 EXTRACT-MAX 耗时（纳秒）", color="#538225")
ax2.tick_params(axis="y", labelcolor="#538225")
for i, v in enumerate(timv):
    ax2.annotate(f"{v:.0f}ns", (i, v), textcoords="offset points",
                 xytext=(0, 9), ha="center", fontsize=9, color="#538225")
ax.set_title("n = $10^6$：比较最少的是 d=3，但最快的是 d≈4~8", fontsize=12)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, frameon=False, fontsize=9, ncol=2,
          loc="upper center", bbox_to_anchor=(0.5, -0.12))
ax.grid(alpha=.3, axis="y", ls=":")
fig.suptitle("瓶颈的本质：比较次数（算法代价）≠ 墙钟时间（含缓存效应）", fontsize=13)
fig.tight_layout(rect=(0, 0.04, 1, 0.94))
fig.savefig(os.path.join(OUT, "fig_5_tradeoff.png"), facecolor="white")
plt.close(fig)
print("saved fig_5_tradeoff.png")

print("全部图片已生成到", OUT)
