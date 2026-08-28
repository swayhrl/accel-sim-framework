建议非常明确：

> **不要把整段聊天记录直接扔给 Codex 当主要上下文。**
>
> 最好由我整理一份 **`CODEX_HANDOFF.md` 作为唯一的“任务总说明”**，聊天记录最多作为补充参考。

原因是我们现在已经讨论了很多轮，其中有些方案后来被修改了。例如第 11 页原先有“重新合并评估”，现在已经取消。如果直接把聊天记录交给 Codex，它需要自己判断“哪一版才是最终决定”，很容易把废案也捡回来。

------

# 1. 最推荐的交接方式

建议形成三层信息：

```text
CODEX_HANDOFF.md
    ↓
当前最终决策，Codex 首先读它
    ↓
docs/storyboard/
    ↓
逐页详细规格
    ↓
sources/ + assets/
    ↓
论文、已有 drawio、实验图脚本等原始材料
```

其中：

## `CODEX_HANDOFF.md`

相当于**总指挥文件**。

只写已经决定的事情，例如：

- PPT 的目的；
- 汇报约 50–60 页；
- 三项工作关系；
- 前 11 页故事线；
- 第 8 页是核心母图；
- 哪些页面引用已有图片；
- 哪些页面必须原创；
- 哪些已有 drawio 不要重新画；
- 数据图必须从脚本生成；
- 使用 `research-drawio`；
- 后续使用 `presentation-skill`；
- 当前任务只做哪些页面；
- 哪些事情暂时不要做。

Codex 每次开始工作都可以先：

```text
Read CODEX_HANDOFF.md first.
Treat it as the authoritative project specification.
```

这样很稳定。

------

# 2. 聊天记录要不要给 Codex？

可以给，但我建议只作为：

```text
references/chat_history/
```

或者干脆不提供。

因为 `CODEX_HANDOFF.md + storyboard` 已经应该包含全部重要决策。

如果以后 Codex 对某个决策问：

> 为什么第 8 页是这样设计？

我们再把相关聊天片段补给它即可。

所以信息优先级建议明确规定：

```text
Priority 1
CODEX_HANDOFF.md

Priority 2
docs/storyboard/*.md

Priority 3
已有 drawio / scripts / papers

Priority 4
chat history

如果发生冲突：
以前三者为准，不以聊天旧版本为准。
```

这个规则我会直接写进 handoff。

------

# 3. 目录我建议现在就规范起来

尤其你已经有：

- 已经改绘好的 `.drawio`
- 数据图生成脚本
- 论文 PDF
- 后续 PPT
- 外部素材

现在正适合一次定好。

我推荐：

```text
gpu_phd_presentation/
│
├── CODEX_HANDOFF.md
│
├── README.md
│
├── docs/
│   │
│   ├── storyboard/
│   │   ├── 00_overall_story.md
│   │   ├── 01_opening_slides_01_11.md
│   │   ├── 02_work1_latebind.md
│   │   ├── 03_work2_c2p.md
│   │   ├── 04_work3_tls.md
│   │   └── 05_summary.md
│   │
│   ├── visual/
│   │   ├── visual_language.md
│   │   ├── figure_inventory.md
│   │   └── source_policy.md
│   │
│   └── notes/
│       └── ...
│
├── sources/
│   │
│   ├── papers/
│   │   ├── FRC_EuroPar2018.pdf
│   │   ├── C2P_MICRO2026.pdf
│   │   ├── TLS_Cache.pdf
│   │   ├── MCM_GPU_ISCA2017.pdf
│   │   ├── SAC_ISCA2023.pdf
│   │   └── ...
│   │
│   ├── official/
│   │   ├── nvidia/
│   │   ├── amd/
│   │   └── ...
│   │
│   └── reference_ppt/
│       └── 通用图形处理器的并发优化研究.pptx
│
├── figures/
│   │
│   ├── drawio/
│   │   ├── existing/
│   │   │   ├── frc/
│   │   │   ├── c2p/
│   │   │   └── tls/
│   │   │
│   │   └── original/
│   │       ├── opening/
│   │       ├── latebind/
│   │       ├── c2p/
│   │       └── tls/
│   │
│   ├── svg/
│   │
│   ├── png/
│   │
│   └── external/
│       ├── opening/
│       ├── related_work/
│       └── ...
│
├── experiments/
│   │
│   ├── data/
│   │   ├── latebind/
│   │   ├── c2p/
│   │   └── tls/
│   │
│   ├── scripts/
│   │   ├── common/
│   │   ├── latebind/
│   │   ├── c2p/
│   │   └── tls/
│   │
│   └── plots/
│       ├── latebind/
│       ├── c2p/
│       └── tls/
│
├── deck/
│   ├── outline.json
│   ├── style.md
│   ├── sources.md
│   └── workspace/
│
├── build/
│
└── output/
    ├── pptx/
    ├── pdf/
    └── rendered_slides/
```

不用现在把每个空目录全创建完，但顶层结构最好先固定。

------

# 4. 论文 PDF 建议全部放进去

是的。

尤其下面这些**一定建议保留原文 PDF**：

```text
sources/papers/
├── FRC_EuroPar2018.pdf
├── C2P_MICRO2026.pdf
├── TLS_Cache.pdf
├── MCM_GPU_ISCA2017.pdf
├── SAC_ISCA2023.pdf
└── ...
```

原因不只是让 Codex“读论文”。

更重要的是后面它需要：

### 查原图

比如：

```text
C2P Fig.3
FRC Fig.2
SAC Fig.3
```

### 核对术语

避免把：

```text
candidate pruning
redundant L2 access
remote-shared L1
```

说错。

### 核对我们已有改绘

比如让它：

> 对照 FRC 原图，检查 `figures/drawio/existing/frc/...drawio` 是否存在语义错误。

这非常有价值。

------

# 5. 但论文 PDF 有一个重要原则

把 PDF 当：

> **Evidence / Source of Truth**

而不是：

> “Codex 随便从论文里抓图塞 PPT”。

在 handoff 里我会明确规定：

```text
Do not copy arbitrary paper figures into slides.

For every external figure:
1. determine why it is needed;
2. identify the exact source and figure number;
3. decide whether to:
   - cite directly,
   - crop directly,
   - redraw/adapt,
   - or not use it;
4. record the source.
```

这样以后来源比较干净。

------

# 6. 你已经做好的 drawio 非常重要

既然你说：

> 基于已有工作的改绘图基本都已经画好了，并且有 drawio 可以修改。

那么我们的工作量其实小了很多。

这些一定不要扔进：

```text
external/
```

而应该作为**一级项目资产**：

```text
figures/drawio/existing/
```

比如：

```text
figures/drawio/existing/
│
├── frc/
│   ├── conventional_l2.drawio
│   ├── frc_overview.drawio
│   └── ...
│
├── c2p/
│   ├── c2p_architecture.drawio
│   ├── ata.drawio
│   ├── ring.drawio
│   └── ...
│
└── tls/
    ├── tls_overview.drawio
    └── ...
```

这代表：

> **这些不是让 Codex 重新生成的草图，而是已有人工确认资产。**

Codex 应该：

```text
read
→ inspect
→ reuse
→ modify when necessary
```

而不是：

```text
paper PDF
→ 从头重新画
```

我会在 handoff 中明确写：

> Existing `.drawio` files are preferred over regenerating equivalent figures.

------

# 7. 你已经准备好的数据图脚本也应该成为唯一数据源

这个更重要。

既然你已经参考 C2P 的实验图风格把脚本准备好了，那么建议：

```text
experiments/
├── data/
├── scripts/
└── plots/
```

三者严格分开。

比如：

```text
experiments/
├── data/
│   └── c2p/
│       └── performance.csv
│
├── scripts/
│   └── c2p/
│       └── plot_performance.py
│
└── plots/
    └── c2p/
        ├── performance.pdf
        └── performance.png
```

原则：

> **脚本 + data 是 source，PNG/PDF 是 build artifact。**

以后性能数字变：

```text
data
 ↓
script
 ↓
regenerate plot
 ↓
PPT rebuild
```

绝对不要：

```text
PowerPoint里手工改柱子高度
```

------

# 8. 这样我们的图实际上已经自然分成三种

现在结合你的实际进展，我建议重新定义：

## Type A — Existing editable figures

你已经画好的：

```text
FRC
C2P related work
TLS related work
...
```

位置：

```text
figures/drawio/existing/
```

原则：

> **Reuse first.**

------

## Type B — New original thesis/presentation figures

我们现在真正要做的：

```text
Page 3
Page 5
Page 7
Page 8
Page 9
Page 11

以及之后真正属于你们工作的架构图。
```

位置：

```text
figures/drawio/original/
```

其中第 8 页：

```text
figures/drawio/original/opening/
    p08_unified_memory_path.drawio
```

会成为核心母图。

------

## Type C — Experimental charts

你的脚本自动生成：

```text
experiments/plots/
```

不要用 draw.io。

------

# 9. 外部图片再单独分一类

例如我们刚筛的：

```text
AI and Memory Wall Fig.1
Blackwell 官方图
C2P Fig.3
MCM-GPU Fig.4
```

放：

```text
figures/external/
```

但最好同时放一个：

```text
figures/external/SOURCES.md
```

记录：

```text
Filename:
p02_memory_wall_fig1.png

Source:
Gholami et al., "AI and Memory Wall", IEEE Micro 2024.

Original:
Figure 1

Usage:
Slide 2

Treatment:
Cropped from original paper, no data modification.
```

这样后面论文引用和 PPT source footer 都不会乱。

------

# 10. 我建议再加一个非常有用的 `figure_inventory.md`

例如：

```text
docs/visual/figure_inventory.md
```

里面维护：

| Figure ID | Slide | Type     | Source     | Editable source | Status |
| --------- | ----- | -------- | ---------- | --------------- | ------ |
| F-P03-01  | 3     | Original | Ours       | `...drawio`     | TODO   |
| F-P05-01  | 5     | Original | Ours       | `...drawio`     | TODO   |
| F-P06-01  | 6     | Adapted  | FRC Fig.2a | `...drawio`     | DONE   |
| F-P06-02  | 6     | External | C2P Fig.3  | —               | READY  |
| F-P08-01  | 8     | Original | Ours       | `...drawio`     | TODO   |
| F-W1-03   | 18    | Adapted  | FRC        | `...drawio`     | DONE   |

一旦做到 50 多页，这个文件会非常有价值。

否则后面很容易出现：

> “这张图到底从哪来的？”

------

# 11. 所以我们下一步不是立即让 Codex 开工

我建议先做一个很短的准备步骤：

### 我来生成：

```text
CODEX_HANDOFF.md
```

并同时生成：

```text
docs/storyboard/01_opening_slides_01_11.md
```

前者告诉 Codex：

> **整个项目是什么，以及你必须遵守什么。**

后者告诉它：

> **第 1–11 页具体怎么做。**

然后你把自己的：

```text
论文 PDF
已有 drawio
plot scripts
plot data
参考 PPT
```

按上面的目录放进去。

最终目录至少先达到：

```text
gpu_phd_presentation/
│
├── CODEX_HANDOFF.md
│
├── docs/
│   └── storyboard/
│       └── 01_opening_slides_01_11.md
│
├── sources/
│   ├── papers/
│   └── reference_ppt/
│
├── figures/
│   ├── drawio/
│   │   ├── existing/
│   │   └── original/
│   └── external/
│
├── experiments/
│   ├── data/
│   ├── scripts/
│   └── plots/
│
└── output/
```

就够开始第一轮。

------

## 最终工作流

现在可以非常具体地定成：

```text
我们在 ChatGPT
        ↓
定 storyboard
        ↓
生成 CODEX_HANDOFF.md
        ↓
你把已有资产归档
        ↓
Codex 读取 HANDOFF
        ↓
检查已有 drawio / papers / plots
        ↓
优先设计 Page 8 母图
        ↓
Page 8 审核通过
        ↓
沿同一视觉语言做
Page 3 / 5 / 7 / 9 / 11
        ↓
再进入 Work 1 / Work 2 / Work 3
        ↓
presentation-skill 组 deck
```

所以针对你的两个问题，我的建议可以压缩为：

> **① 用 `CODEX_HANDOFF.md`，不要直接拿聊天记录做主交接。**
>
> **② 建一个独立 PPT 项目目录，把论文 PDF、已有 `.drawio`、实验数据和绘图脚本都放进去；PDF 是证据源，已有 `.drawio` 是优先复用资产，数据脚本是实验图的唯一 source of truth。**

而且由于你已经把**改绘图和实验图脚本基本准备好**，后面 Codex 的重点可以明显收缩到：**统一视觉系统 + 原创逻辑图 + PPT 组装**，这其实是很理想的状态。

下一步我建议我直接把 **`CODEX_HANDOFF.md` + `01_opening_slides_01_11.md` 两个实际文件生成出来**，这样你可以直接放进 Codex 项目目录使用。