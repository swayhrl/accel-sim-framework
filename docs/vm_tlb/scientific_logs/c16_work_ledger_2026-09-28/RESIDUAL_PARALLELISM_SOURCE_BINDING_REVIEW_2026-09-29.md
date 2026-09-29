# C16 residual-parallelism：2026-09-29来源审查增量

本文件追加本轮ChatGPT审查结果，不修改任何实验source、binary、raw或已接受历史结果。它在状态上优先于总账EXP18原先的`PREP+PRODUCER_ACCEPTED_PENDING_INDEPENDENT_CONSUMER`：最新producer的数值与基本执行表可读，但source identity记录尚有不一致，正式接受须先闭合该问题。

## 1. 本轮实际核验范围

Repository：`swayhrl/accel-sim-framework`。

| Lane | branch | commit | tree |
|---|---|---|---|
| 8 / 174-new | `hrl/c16-grouped-residual-parallelism-prep-174new-v1` | `493250b11302344c1f445465da8c58e6275545bd` | `f8893515af454aaff442f3598912dbf89bb22608` |
| 7 / 109 | `hrl/c16-grouped-residual-parallelism-native-109-v1` | `ab84399012c89fce2c21fabac8d6f9fa8688d164` | `dd7b4a5dfa7082c54057584177c2b864f197e88e` |
| 6 / 174-new | `hrl/c16-grouped-residual-parallelism-consumer-174new-v1` | `911bca13be88ba14ecdf2698b2f3499659644811` | `2367b5d501f940fc7bfe8af64e69d1f265151a84` |

三组branch与commit回读均identical，tree用Git commit对象确认。Lane6的FINAL_DECISION仍然是scaffold/waiting，不是正式consumer结果。

实际读取了prep early/final gate；producer的SOURCE_AND_GATE、BUILD_RECEIPT、CPU_CONTRACT_TEST、CORRECTNESS、LAUNCH_AUDIT、METRIC_SELECTION、GPU_LOCK_RECEIPT、全部12条NCU kernel rows、计时summary、计时raw的结构和部分行。本轮未SSH核实109实物、未重算400条timing的bootstrap、未复跑GPU或模拟、未读取Lane4 partial。

## 2. 新发现：3种SHA值、4处字段为65字符

### 2.1 base source

`SOURCE_AND_GATE.json: base_source.sha256`记录：

```text
974980f34d7269c9a33ccd642d9dc9bc8700f58e9afc633d65634dedd9c5fc5a6
```

Lane8 `EARLY_GATE.json: bindings.old_source_sha256`记录：

```text
974980f34d7269c9a33ccd642d9dc9bc8700f58e9afc63d65634dedd9c5fc5a6
```

前者65位，后者64位。

### 2.2 patch artifact

`SOURCE_AND_GATE.json: gate.patch_artifact_sha256`记录：

```text
445191bee12aae39530a16cf24519565105de0ecc0d424da200c30c23ed44b348
```

Lane8 `bindings.patch_artifact_sha256`记录：

```text
445191bee12aae39530a16cf24519565105de0ecc0d424da20c30c23ed44b348
```

前者65位，后者64位。

### 2.3 patched generator

`SOURCE_AND_GATE.json: gate.patched_generator_sha256`与`BUILD_RECEIPT.json: patched_generator_sha256`均记录：

```text
b7541f5a96ae001f78cb8eb8b61ec923cff40c9cadaa05dd06144dc6777f675cf
```

Lane8 `bindings.patched_generator_sha256`记录：

```text
b7541f5a96ae001f78cb8eb8b61ec923cff40c9cadaa05d06144dc6777f675cf
```

前者65位，后者64位。

Lane8 early gate commit `f6bad36a0ee49e718df268421e96593c94756b77`与final commit中的EARLY_GATE为同一blob `d0165c98648389d3eef9ac1781a0f50f7bd8c03c`。这不是final gate改写造成的差异。

目前只能证明记录不一致，不能据此断言实际执行source错误，也不能把重复字符直接删去当作来源证明。Pack SHA256SUMS验证JSON字节，不等于验证JSON内部引用的source/binary身份。

## 3. 可保留的数值观察，暂不最终接受

固定K4096/N12288、M1/16/32/64、GROUP_FULL_M、split1/8，weight-side共24.9375MiB。

| M | split8 module ms | split1 module ms | g1=1-T1/T8 |
|---:|---:|---:|---:|
| 1 | 0.032976 | 0.074752 | -126.686% |
| 16 | 0.040976 | 0.076800 | -87.427% |
| 32 | 0.067584 | 0.086016 | -27.273% |
| 64 | 0.119808 | 0.113904 | +4.928% |

前三行等价于split8相对split1缩时55.89%、46.65%、21.43%；百分比的分母不能混用。M32仍然有split8收益，不能说只在M1/M16有效。

NCU八个GEMM的所选TEX read-side L2 lookup miss均为0；这不等于所有L2访问都命中、DRAM为0或L2延迟免费。M64 profile中split8 GEMM仍略快，但reduction消耗其收益；NCU profile内部时间不能与native CUDA-event时间混算精确分解。

CTA/76SM、launch waves/SM、active-warps是不同指标；384CTA不是设备已经饱和的证明。M1/M16同时改变有效行、input/output和reduction工作，不能将收益差全部唯一归因partial-tile。

## 4. 下一步只做CPU收尾

### Lane7 / node109

继续原producer branch，保持原commit可访问。禁止CUDA初始化、GPU锁、重编译、重跑timing/NCU。

先对现存原source、`GROUP_FULL_M_SOURCE.patch.gz`、patched generator、原build log和已运行binary做普通文件hash及构建来源核对。binary记录为：

```text
/data/c16/grouped_residual_parallelism_v1/build/lib/awq_residual_parallelism_ext.cpython-310-x86_64-linux-gnu.so
SHA256 f98ac68a1e923c61c0351f1a688b899878a7d2eb72f7bbef6152e3bef7143693
source root /data/c16/grouped_residual_parallelism_v1/source
```

若实物与冻结gate/构建链闭合，只追加metadata correction，保存旧错值/实测值/依据，自动读取immutable gate，加入64hex与exact-value cross-file断言，重封pack并push/fetch-back/clean。不要amend原科学commit，不变更raw、binary、output或科学结果。

若实物无法闭合，保持科学接受gate关闭并报告具体缺口；不得把expected改成现值或无授权重跑。

### Lane6 / 174-new

复用`911bca13...` scaffold；source correction gate通过后绑定原producer+更正commit，证明raw未变化，从400samples和12条NCU rows独立重算。complete ABBA bootstrap seed20260929、1000次；报告M64区间和统一分母，保留指标范围与时序解释限制。

若结果确认，当前剩余现象可定位为有限样本内的低CTA供给、有效tile工作与归约权衡，不再发展新cache-aware split机制。不增加M/K/N/split/GROUP_M，也不抓SASS或启动模拟。

## 5. 主线不变

Lane4原M1 B16长跑保持，不停止、不重启、不改binary/config/worktree/scope、不读partial；M1F full timing仍须等待Lane4完整terminal项目级gate。最新native支线关闭与否不代替跨token驻留主线。

完整本地交接文件：
`C16_AI_WORKLOAD_HANDOFF_CONTEXT_2026-09-29_MAINLINE_PRESERVED_NATIVE_CLOSEOUT_PENDING.md`

该文件在本次对话附件提供，包含主线、已完成探索、文献、节点、精确SHA及新窗口启动提示词。本文是远端追加的审查与接续入口，不声称已执行上述修复或consumer。
