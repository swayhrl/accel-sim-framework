问题：
目前正在使用codex进行一些体系结构方向的论文复现和实现，主要是在gpgpu-sim和accel-sim上工作，领域主要是gpu相关的访存研究，比如cache和tlb相关的工作，需要调研一下有没有什么比如合适的skill可以提升效率，给我讲讲，并且讲讲怎么部署？

回答：

有，而且对你这种 **GPGPU-Sim / Accel-Sim + GPU cache/TLB + 论文复现** 的工作，Skill 很适合。但我这轮检索后的结论是：

**不要指望找到一个现成的“GPU Architecture / Accel-Sim 专用 Skill”直接解决问题。**目前公开生态里更成熟的是通用软件工程 Skill；真正能显著提升你效率的，是把你反复做的“论文 → 模拟器 → 实验 → 回归 → 数据分析”流程做成一组自己的 domain skills。

另外有一个很重要的现状：Codex 现在的 Skill 已经是正式的一等扩展机制，`SKILL.md + scripts + references` 即可；Codex 会按需加载 Skill，而不是把所有说明一直塞进上下文。repo-local Skill 推荐放在 `.agents/skills/`，用户级 Skill 放在 `~/.agents/skills/`。Codex CLI 和 IDE extension 都支持 standalone skills。([OpenAI Developers](https://developers.openai.com/codex/skills))

------

# 一、对你最有价值的，不是一个 Skill，而是这一套

我建议最终形成：

```text
accel-sim-framework/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── gpu-paper-to-sim/
│       │   ├── SKILL.md
│       │   └── references/
│       │
│       ├── gpu-codepath-map/
│       │   └── SKILL.md
│       │
│       ├── accel-sim-experiment/
│       │   ├── SKILL.md
│       │   └── scripts/
│       │       ├── capture_manifest.py
│       │       ├── run_smoke.sh
│       │       └── compare_stats.py
│       │
│       ├── gpu-cache-tlb-debug/
│       │   └── SKILL.md
│       │
│       └── sim-regression-analysis/
│           ├── SKILL.md
│           └── scripts/
│               └── analyze_regression.py
│
├── .codex/
│   ├── config.toml
│   └── hooks/
│
└── ...
```

这几个东西各司其职：

| 机制          | 放什么                                                       |
| ------------- | ------------------------------------------------------------ |
| `AGENTS.md`   | **永远成立的仓库规则**：怎么 build、不能随便改什么、baseline 规则、实验目录规则 |
| Skill         | **有条件触发的工作流**：比如“复现论文”“分析 cache regression” |
| `scripts/`    | 确定性工作：跑 benchmark、抓 stats、比较结果、记录 commit    |
| `references/` | GPGPU-Sim/Accel-Sim 代码路径知识、cache/TLB 结构说明         |
| Hooks         | 真正要强制执行的约束                                         |
| Subagents     | 并行读论文、追代码路径、分析日志                             |
| MCP/Plugin    | GitHub、论文数据库等外部数据                                 |

这个边界很重要。官方也明确把 `AGENTS.md` 定位为项目级持久指导，把 Skill 定位为可复用任务流程。([OpenAI Developers](https://developers.openai.com/codex/guides/agents-md))

------

# 二、目前现成 Skill 里，最值得你装的是 Superpowers 的一部分

我查了当前 Codex 插件目录和 OpenAI 的插件仓库，**Superpowers** 现在是一个可安装的 Codex plugin，包含一整套开发 workflow。([GitHub](https://github.com/openai/plugins/blob/main/plugins/superpowers/README.md?utm_source=chatgpt.com))

但我不建议你把它所有规则全盘照搬。

对体系结构模拟器最有价值的是四个。

### 1. `systematic-debugging`

这个非常适合 GPGPU-Sim。

它要求：

```text
异常
 ↓
稳定复现
 ↓
最近改了什么
 ↓
追数据流/控制流
 ↓
提出一个假设
 ↓
做最小实验验证
 ↓
确认 root cause
 ↓
再改代码
```

而不是：

```text
IPC 掉了
→ 猜可能是 MSHR
→ 改
→ 不行
→ 猜 interconnect
→ 再改
→ ...
```

它明确要求先 root-cause investigation，再做最小验证实验。([GitHub](https://github.com/openai/plugins/blob/main/plugins/superpowers/skills/systematic-debugging/SKILL.md?utm_source=chatgpt.com))

**我认为这是现成 Skill 里与你工作匹配度最高的。**

尤其适合：

- IPC 突然变化；
- cache miss 数异常；
- MSHR / reservation fail 异常；
- TLB miss latency 不对；
- deadlock；
- 某 benchmark 性能暴涨/暴跌；
- baseline 和修改版统计不一致。

------

### 2. `verification-before-completion`

体系结构研究很容易出现：

> 编译过了，所以修改应该是对的。

或者：

> 一个 benchmark 提升了，所以机制有效。

这种 Skill 可以强制 Codex 在声称“完成”前验证：

```text
compile
→ smoke
→ baseline
→ proposed
→ stats sanity
→ regression
→ diff
→ 才允许 close
```

建议借鉴这种思想，但自己做一个 `sim-regression-analysis` Skill。

------

### 3. `using-git-worktrees`

这个和体系结构研究也非常匹配。

例如：

```text
baseline/
idea-l1/
idea-l2/
idea-tlb/
paper-repro/
```

几个 worktree 可以同时保持不同 simulator 状态。

Superpowers 已经有专门的 worktree workflow，并且会先检测是不是已经处于 linked worktree，避免重复创建。([GitHub](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md?plain=1&utm_source=chatgpt.com))

------

### 4. `requesting-code-review`

体系结构代码很适合让另一个 agent 做：

```text
Architecture correctness review
State machine review
Performance-path review
Statistics/config review
```

Superpowers 的做法是把 diff 和明确 requirement 单独给 reviewer subagent，而不是让 reviewer 吃掉整个主线程上下文。([GitHub](https://github.com/openai/plugins/blob/main/plugins/superpowers/skills/requesting-code-review/SKILL.md?utm_source=chatgpt.com))

这对复杂的 `gpu-cache.cc`、`shader.cc`、memory partition、TLB path 很有价值。

------

# 三、但 Superpowers 里有一部分，我反而不建议直接套在你的研究上

例如强制 TDD。

软件工程中的：

```text
write failing unit test
→ implement
→ pass
```

不总适用于微体系结构模拟器。

很多时候你的“test”实际是：

```text
microbenchmark
trace
cycle count
cache stat
assertion
synthetic workload
```

所以我建议：

**保留 systematic-debugging + verification + worktree + review。**

而不要机械要求：

> 所有 cache/TLB 改动必须先写 C++ unit test。

你应该把它改造成 **architecture validation first**：

```text
mechanism invariant
→ targeted microbenchmark
→ stats sanity
→ baseline reproduction
→ performance experiment
```

------

# 四、真正值得你自己做的第一个 Skill：`gpu-paper-to-sim`

这是我认为收益最大的一个。

你目前大量工作其实都是：

```text
读论文
 ↓
搞懂 motivation
 ↓
搞懂 mechanism
 ↓
判断 Accel-Sim 能不能实现
 ↓
找 simulator 对应位置
 ↓
列修改点
 ↓
实现
 ↓
实验
```

每篇论文都重复一遍。

完全可以 Skill 化。

## 它应该强制 Codex 输出五张映射表

例如你给：

> 复现某个 L1 cooperative cache 机制。

Skill 自动走：

```text
Paper mechanism
      ↓
Architecture state
      ↓
Simulator object
      ↓
Code path
      ↓
Config/statistics
```

最后形成：

| Paper concept   | Hardware state  | Simulator object | File/function | Implementation |
| --------------- | --------------- | ---------------- | ------------- | -------------- |
| remote L1 probe | directory/tag   | cache object     | xxx.cc        | add lookup     |
| sharing scope   | SM cluster      | cluster config   | xxx.cc        | new knob       |
| replacement     | cache metadata  | tag array        | xxx.cc        | policy         |
| latency         | interconnect    | ICNT             | xxx.cc        | latency model  |
| traffic         | request packets | mem_fetch        | xxx.cc        | stats          |

这样 Codex 就不应该上来直接改代码。

------

## 我会把它写成类似这样

```yaml
---
name: gpu-paper-to-sim
description: >
  Map GPU architecture papers to GPGPU-Sim or Accel-Sim implementations.
  Use for cache, TLB, virtual memory, interconnect, memory hierarchy,
  prefetching, scheduling, multi-GPU, or related architecture paper
  reproduction and implementation tasks.
---
```

核心规则：

```text
1. Do not edit simulator code immediately.

2. First extract:
   - problem
   - baseline architecture
   - mechanism
   - new state
   - request/data flow
   - timing assumptions
   - hardware overhead
   - evaluation methodology

3. Build a simulator mapping:
   paper mechanism
      -> simulator component
      -> class
      -> function
      -> config
      -> stats

4. Identify semantic risks:
   - functional behavior
   - timing behavior
   - resource contention
   - replacement behavior
   - ordering
   - backpressure

5. Produce an implementation plan.

6. Only then modify code.

7. After modification:
   build
   -> smoke test
   -> targeted workload
   -> baseline comparison
   -> regression
```

这样以后你说：

```text
$gpu-paper-to-sim
复现这篇 TLS-Cache，先帮我把 RL1 设计映射到当前 simulator。
```

Codex 就会自动按这个工作流执行。

Codex 本身支持显式 `$skill-name` 调用，也可以根据 `description` 自动匹配。([OpenAI Developers](https://developers.openai.com/codex/skills))

------

# 五、第二个最重要：`gpu-codepath-map`

GPGPU-Sim 最大的问题之一是：

**代码路径长，而且很多结构名字和论文概念不是一一对应。**

例如一次 L1 miss 可能一路涉及：

```text
warp instruction
 ↓
ldst_unit
 ↓
memory coalescing
 ↓
L1 cache
 ↓
mem_fetch
 ↓
interconnect
 ↓
memory partition
 ↓
L2
 ↓
DRAM
```

TLB 又是：

```text
memory instruction
 ↓
translation lookup
 ↓
L1 TLB
 ↓
L2 TLB
 ↓
page walk / fault model
 ↓
memory request
```

所以做一个只读 Skill：

```text
gpu-codepath-map
```

输入：

> 找出一次 global load 从 SM 到 L2 的完整调用链。

输出强制要求：

```text
function
file
caller
callee
state changed
queue entered
queue exited
stat updated
latency added
```

还可以自动生成：

```text
docs/codepath/
    global_load.md
    l1_miss.md
    l2_miss.md
    tlb_miss.md
    page_walk.md
    dram_request.md
```

以后 Codex 就不需要每次从零 grep。

------

# 六、第三个：`accel-sim-experiment`

这个 Skill 能直接节省大量实验时间。

Accel-Sim 本身已经提供：

- `short-tests.sh`
- `run_simulations.py`
- `monitor_func_test.py`
- `get_stats.py`

官方 README 也明确推荐用 job launch manager 来管理实验，而不是直接手动调用 `accel-sim.out`。([GitHub](https://github.com/accel-sim/accel-sim-framework?utm_source=chatgpt.com))

所以不要重新造一套 runner。

你的 Skill 应该**包住它们**。

例如：

```text
$accel-sim-experiment baseline-vs-new
```

Skill 自动：

```text
1. Capture git HEAD
2. Capture git status
3. Capture config hash
4. Capture trace path/version
5. Build
6. Smoke test
7. Run baseline
8. Run proposal
9. get_stats.py
10. normalize
11. compare
12. generate manifest
```

实验目录：

```text
experiments/
└── tls-cache-v1/
    ├── manifest.json
    ├── baseline/
    │   └── stats.csv
    ├── proposal/
    │   └── stats.csv
    └── compare.csv
```

其中 `manifest.json` 至少记录：

```json
{
  "git_commit": "...",
  "branch": "...",
  "dirty": false,
  "gpu_config": "...",
  "config_hash": "...",
  "trace_set": "...",
  "benchmark_set": "...",
  "command": "...",
  "baseline_commit": "..."
}
```

这对论文复现特别重要。

------

# 七、第四个：`gpu-cache-tlb-debug`

这个应该是你的领域知识 Skill。

把常见 bug 模式固化进去。

## Cache

检查：

```text
tag lookup
hit/miss
MSHR
reservation fail
fill
writeback
eviction
dirty
replacement
cache line state
request merge
backpressure
latency
statistics
```

## TLB

检查：

```text
virtual address
page size
TLB index
tag
hit/miss
MSHR
walk request
walk latency
page fault
migration
translation fill
shootdown
statistics
```

每次出现异常时，Codex 不应该只看发生错误的那一行，而应该沿请求生命周期追。

这和 `systematic-debugging` 组合起来非常好：

```text
systematic-debugging
        +
gpu-cache-tlb-debug
```

一个提供调试方法，一个提供 GPU domain knowledge。

------

# 八、第五个：`sim-regression-analysis`

这个 Skill 负责回答一个很关键的问题：

> 为什么性能变了？

而不是只告诉你：

> IPC 从 1.52 变成了 1.39。

它应该按因果链分析：

```text
IPC
 ↑
stall distribution
 ↑
memory latency
 ↑
cache/TLB behavior
 ↑
queue occupancy / MSHR
 ↑
interconnect / DRAM
```

比如自动检查：

```text
IPC
L1 hit rate
L2 hit rate
L1 MPKI
L2 MPKI
TLB hit rate
page walk
MSHR reservation fail
DRAM reads
DRAM writes
ICNT packets
memory latency
warp stalls
```

然后输出：

```text
Observed:
L1 hit +8%

But:
MSHR reservation fail +35%
ICNT traffic +18%
average miss latency +22%

Therefore:
higher L1 hit rate did not translate into IPC because ...
```

这比简单 CSV diff 有价值得多。

------

# 九、Skill 里的代码知识不要全写进 SKILL.md

Codex 现在采用 progressive disclosure：

开始只看到：

```text
skill name
description
path
```

真正命中 Skill 后才读完整 `SKILL.md`。([OpenAI Developers](https://developers.openai.com/codex/skills))

所以最好：

```text
gpu-cache-tlb-debug/
├── SKILL.md
└── references/
    ├── gpgpu-sim-cache.md
    ├── gpgpu-sim-tlb.md
    ├── accel-sim-trace.md
    ├── memory-partition.md
    ├── interconnect.md
    └── stats.md
```

`SKILL.md` 只写：

```text
如果问题涉及 L1/L2：
read references/gpgpu-sim-cache.md

如果涉及 TLB：
read references/gpgpu-sim-tlb.md
```

这样不会每个对话都吃掉大量 context。

------

# 十、部署方式：如果你主要用 VSCode Codex，我推荐 repo-local

这点尤其重要。

**当前官方文档明确说明：Codex IDE extension 不支持 Plugins；Codex CLI 有 `/plugins` browser。**

但是 **standalone skills 是支持 IDE extension 的。** ([OpenAI Developers](https://developers.openai.com/codex/plugins))

所以你现在在 VSCode remote server 上做 Accel-Sim，最佳方案不是折腾 plugin marketplace，而是：

```bash
cd /workspace/accel-sim-framework

mkdir -p .agents/skills/gpu-paper-to-sim
mkdir -p .agents/skills/gpu-codepath-map
mkdir -p .agents/skills/accel-sim-experiment/scripts
mkdir -p .agents/skills/gpu-cache-tlb-debug/references
mkdir -p .agents/skills/sim-regression-analysis/scripts
```

然后：

```text
.acceler-sim-framework
└── .agents
    └── skills
```

随 repo 一起版本控制。

Codex 会从当前工作目录一路向 repo root 查找 `.agents/skills`。([OpenAI Developers](https://developers.openai.com/codex/skills))

------

# 十一、怎么测试有没有加载成功

在 Codex CLI / IDE 中：

```text
/skills
```

或者：

```text
$
```

查看可用 Skills。

然后显式：

```text
$gpu-paper-to-sim
```

例如：

```text
$gpu-paper-to-sim

分析当前提供的论文。
先不要修改代码。

把论文中的 cache 机制映射到当前 Accel-Sim/GPGPU-Sim，
给出请求路径、需要增加的状态、配置、statistics 和修改位置。
```

官方支持 `/skills` 和 `$skill` 两种方式。修改 Skill 后通常会自动检测；如果没出现，重启 Codex session。([OpenAI Developers](https://developers.openai.com/codex/skills))

------

# 十二、跨多个 GPGPU-Sim/Accel-Sim repo 的 Skill 放全局

如果你有：

```text
accel-sim-framework/
gpgpu-sim_distribution/
paper-A-repro/
paper-B-repro/
```

建议：

```text
~/gpu-codex-skills/
├── gpu-paper-to-sim/
├── gpu-codepath-map/
├── gpu-cache-tlb-debug/
└── sim-regression-analysis/
```

然后：

```bash
mkdir -p ~/.agents/skills

ln -s ~/gpu-codex-skills/gpu-paper-to-sim \
      ~/.agents/skills/gpu-paper-to-sim

ln -s ~/gpu-codex-skills/gpu-codepath-map \
      ~/.agents/skills/gpu-codepath-map

ln -s ~/gpu-codex-skills/gpu-cache-tlb-debug \
      ~/.agents/skills/gpu-cache-tlb-debug
```

官方明确支持 `~/.agents/skills`，也支持 symlink Skill 目录。([OpenAI Developers](https://developers.openai.com/codex/skills))

我尤其推荐这种方法，因为你可能会同时开很多 worktree。

------

# 十三、现成 Superpowers 怎么部署

如果用 **Codex CLI**：

```text
codex

/plugins
```

然后找到：

```text
Superpowers
```

安装，重新开 session。

当前 Codex CLI 的 `/plugins` 就是官方插件浏览器。([OpenAI Developers](https://developers.openai.com/codex/plugins))

如果你主要使用 **VSCode Codex extension**，我反而建议直接取其中几个 Skill 使用，而不是整个 plugin。

例如：

```bash
mkdir -p ~/tools
cd ~/tools

gh repo clone obra/superpowers
```

然后：

```bash
ln -s ~/tools/superpowers/skills/systematic-debugging \
      ~/.agents/skills/systematic-debugging

ln -s ~/tools/superpowers/skills/verification-before-completion \
      ~/.agents/skills/verification-before-completion

ln -s ~/tools/superpowers/skills/using-git-worktrees \
      ~/.agents/skills/using-git-worktrees

ln -s ~/tools/superpowers/skills/requesting-code-review \
      ~/.agents/skills/requesting-code-review
```

Superpowers 当前公开版本采用 MIT License。([GitHub](https://github.com/openai/plugins/blob/main/plugins/superpowers/README.md?utm_source=chatgpt.com))

------

# 十四、`AGENTS.md` 反而要比 Skill 更先做好

我会在 Accel-Sim 根目录至少写：

```markdown
# Repository policy

## Architecture work

Before modifying simulator behavior:

1. Identify the request/data path.
2. Identify architectural state affected.
3. Identify timing/resource effects.
4. Identify statistics needed for validation.
5. Record the baseline behavior.

Do not mix unrelated architecture changes.

## Validation

For simulator changes:

1. Build.
2. Run targeted smoke test.
3. Reproduce baseline.
4. Run the modified mechanism.
5. Compare architectural statistics.
6. Run regression tests before completion.

## Experiments

Every experiment must record:

- git commit
- dirty state
- configuration
- trace/workload
- launch command
- statistics output

Do not compare results produced from different configurations or traces
unless the difference is intentional and documented.

## Accel-Sim

Prefer the repository's existing job-launching infrastructure over
inventing a new experiment runner.
```

这些属于**永远应该遵守的规则**，所以比放进 Skill 更合适。

Codex 每次开始工作都会先读取 `AGENTS.md`，而且支持从 root 到子目录逐级覆盖。([OpenAI Developers](https://developers.openai.com/codex/guides/agents-md))

------

# 十五、Subagent 对你的工作其实也非常有价值

官方现在特别推荐 subagent 用于：

- exploration；
- tests；
- triage；
- summarization；
- log analysis；

而且明确提示：**read-heavy 工作很适合并行，多个 agent 同时改代码则容易冲突。** ([OpenAI Developers](https://developers.openai.com/codex/subagents))

这几乎正好对应论文复现。

例如：

```text
Main agent
    │
    ├── Agent 1：只读论文
    │      └─ mechanism / assumptions / evaluation
    │
    ├── Agent 2：只读 simulator
    │      └─ L1/L2/cache call path
    │
    ├── Agent 3：只读 simulator
    │      └─ TLB / VM / address translation path
    │
    └── Agent 4：只读 config/stats
           └─ config knobs / counters / experiment support

                   ↓

             Main agent
                   ↓
        Paper → simulator mapping
                   ↓
             implementation
```

这种方式非常适合：

> “看看 C2P-Cache 这个机制在 Accel-Sim 里应该改哪里。”

而不要让四个 agent 同时改 `gpu-cache.cc`。

------

# 十六、甚至可以把这个并行模式直接写进 Skill

例如 `gpu-paper-to-sim`：

```text
If subagents are available:

Spawn read-only workers for independent investigation:

1. Paper mechanism analysis.
2. Cache/TLB/memory code-path analysis.
3. Configuration and statistics analysis.
4. Related implementation and regression-test analysis.

Do not allow multiple subagents to edit simulator code in parallel.

Wait for the read-only analyses and synthesize them before implementation.
```

这样以后每次论文复现都会自动并行。

------

# 十七、Hooks 是下一阶段非常值得加的东西

Codex 现在支持：

```text
SessionStart
UserPromptSubmit
PreToolUse
PostToolUse
SubagentStart
PreCompact
PostCompact
Stop
...
```

而 `PreToolUse/PostToolUse` 可以针对 Bash、`apply_patch`、MCP 等触发。([OpenAI Developers](https://developers.openai.com/codex/hooks))

对你很适合做：

### PreToolUse

发现：

```bash
run_simulations.py -B all...
```

先检查：

```text
baseline 是否存在
git 是否 dirty
实验 manifest 是否建立
```

### PostToolUse

发现运行：

```text
make
short-tests.sh
run_simulations.py
get_stats.py
```

自动记录：

```text
command
exit status
git HEAD
timestamp
output path
```

这样实验记录就不是靠 Codex “记得做”，而是工具层面强制。

------

# 十八、论文检索方面，我不建议过度依赖 Skill 本身

我查当前 plugin 目录时也看到了科学研究类插件，例如 SciSpace、Sider Scholar、Consensus 这一类。

但对你做体系结构，我认为它们只是辅助。

你的核心资料仍然是：

```text
ISCA
MICRO
HPCA
ASPLOS
SC
PACT
ISPASS
arXiv
作者主页
GitHub artifact
```

真正有价值的是做一个：

```text
gpu-literature-audit
```

Skill，规定 Codex 每次研究 idea 必须查：

```text
same mechanism
same optimization target
same hardware structure
same simulator modification
same benchmark phenomenon
```

特别是最后这一项。

例如你想到：

> 动态把 L1 bank 从 local 调给 remote。

不能只搜：

```text
dynamic L1 cache partitioning
```

还应该拆成：

```text
GPU cache way partitioning
GPU cache bank partitioning
local/remote cache allocation
adaptive shared/private cache
NUMA GPU cache
multi-GPU remote data caching
cache resizing GPU
CTA-aware cache allocation
```

这种**检索方法本身**很适合 Skill 化。

------

# 十九、我对你当前环境的部署优先级

如果现在开始做，我不会一下部署十几个 Skill。

第一阶段只上：

```text
1. AGENTS.md
2. gpu-paper-to-sim
3. accel-sim-experiment
4. systematic-debugging
5. verification-before-completion
```

然后形成：

```text
             paper
               │
               ▼
      $gpu-paper-to-sim
               │
               ▼
        architecture map
               │
               ▼
         implementation
               │
         bug ──┴── no bug
          │
          ▼
$systematic-debugging
          │
          ▼
 $accel-sim-experiment
          │
          ▼
 baseline / proposal
          │
          ▼
$verification-before-completion
```

这五样已经能明显改变工作方式。

------

# 二十、我最推荐你最终做到的状态

以后你在 Codex 里可以直接这样说：

```text
$gpu-paper-to-sim

这是 C2P-Cache 的论文。

目标是在当前 Accel-Sim branch 上做最小可验证复现。

先不要改代码。

并行完成：
1. 论文机制拆解；
2. 当前 L1/cache 请求路径；
3. 需要增加的状态；
4. config 和 stats；
5. baseline 实验设计。

最后给出 paper → architecture → code → experiment 的映射。
```

然后：

```text
按刚才方案实现第一个最小版本。
```

最后：

```text
$accel-sim-experiment

对 baseline 和当前版本跑同一组 traces，
收集 cache / memory / IPC 相关指标，
生成 comparison。
```

出了问题：

```text
$systematic-debugging

不要直接修。
从第一次出现 divergence 的请求开始追。
```

这比单纯在每次 prompt 里重新告诉 Codex：

> “这是体系结构研究，请仔细看看，不要乱改，先分析……”

要稳定得多。

**如果只让我选一个最值得现在开始写的自定义 Skill，我会先做 `gpu-paper-to-sim`；第二个马上做 `accel-sim-experiment`。** 这两个分别解决你现在最耗人工的“论文到代码”和“代码到可信实验”两个环节。Accel-Sim 自己已经有成熟的 trace、simulation launcher 和 stats 工具，因此 Skill 的重点应该是**组织和约束这些已有能力，而不是重新造 simulator runner**。([GitHub](https://github.com/accel-sim/accel-sim-framework?utm_source=chatgpt.com))

如果后续基于你现在实际使用的 Accel-Sim 仓库来落地，我建议直接把这套东西做成 **5 个可以拷进 `.agents/skills/` 就能用的完整 `SKILL.md` + `references` + 实验脚本骨架**，并专门针对 GPGPU-Sim 的 cache、TLB、memory partition、interconnect 代码路径来写，而不是泛化的软件开发模板。