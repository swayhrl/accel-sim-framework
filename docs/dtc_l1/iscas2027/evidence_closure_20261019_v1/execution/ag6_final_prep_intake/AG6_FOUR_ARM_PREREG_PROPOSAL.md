# AG6 V2 four-arm science proposal — non-executable

本提案不含新UUID、启动命令、dispatcher或执行锁。V2上限为4次新实际启动，BA唯一派发；旧AG6六点准备为历史，不能自动改用，也不能从BA32补AG6失败格。

| Order | Arm | AE bankrow XOR | AD progressive | Qualified imported comparator |
|---|---|---|---|---|
| 0 | AE_GEMM | 1 | 0 | AG3 UUID `8b6006aa-610e-41cf-82f0-135f80e449cf`, 1,071,405 cycles |
| 1 | AE_Gaussian | 1 | 0 | AG4 UUID `87daf914-1730-4012-8053-7cb3c9536636`, 3,278,356 cycles |
| 2 | AD_GEMM | 0 | 1 | 同一GEMM comparator |
| 3 | AD_Gaussian | 0 | 1 | 同一Gaussian comparator |

两份`BASE_REUSE_*.json`均按严格分离的原始strict、历史executor范围和新复用资格裁决。PASS仅适用于原精确身份，不是历史executor追认或当前launch资格。任一条件变化/不足即UNRESOLVED，不允许仅ON数字除以未合格BASE。

完整四点数据提案在`AG6_FOUR_ARM_SCIENCE_PROPOSAL.json`：原完整trace list、所有原command/memcpy、CTA/instructions、ROI、实际ELF/lib路径及SHA、270项effective options、配置SHA、原Core/Framework来源。所有新UUID均为`UNASSIGNED_BA_ONLY`；旧BASE UUID只作为引用，绝不新执行。

固定Core `c8090115bd57512b1b23fca7d925301fa620c751`，编译Framework `8e43c75a5e2eb60a8466084602b7df8117111e89`，同一实际ELF与lib。K0，OO128，Tag64sets×8ways开发stress，640×128B物理80KiB、PIB128、ordinary16KiB、shared96KiB、4 banks、lower32768、clock及全部finite create/inject/refill/waiter/collect/WB/retire/Ref/generation/sector/ledger/fence不变。

AE仅将`-gpgpu_dtc_l1_tag_hash_bankrow`从0置1，固定bank-preserving XOR，bank号/端口不变；AD仅将`-gpgpu_dtc_l1_progressive_wakeup`从0置1，4 waiter/cycle及消费者自身ready/notification语义不变。禁止组合、AC/AC2/AF、K1/K2、modern、其它输入/Tag/hash调优。无RTL面积/时序/频率或load数值正确性外推。

统计必须逐输入/逐arm保留整数cycles，`speedup = imported same-input BASE / accepted ON`，另给ON/BASE。full strict必须含全输入自然exit0、全部options、公共traffic与finite/ref/credit/sector闭合；失败留UNAVAILABLE。不得以host wall推GPU性能。

| 字段类 | 类型及比较边界 |
|---|---|
| new / valid / pending、lower create/inject、Ref/credit | 原共同计数/守恒；相同定义才直接比较。 |
| physical/PIB积分、ready→collect/WB/retire | 最终累计snapshot，64SM相同总体；不相加510个累计快照。阶段累计不证明实际重叠，未直接测量即UNAVAILABLE。 |
| waiter通知/自身ready/broadcast-done | AD ON专有诊断单列；OFF未打印为UNAVAILABLE，不作不同条件均值因果差分。 |
| hash set/bank冲突 | 只报告真正打印的分布；aggregate不是bank/set分布，缺项UNAVAILABLE。 |
| L2 / DRAM | L2实际接受32B sectors；DRAM实际issued atoms×32B、读写分开；不把原未初始化n_ref当有效事件。 |
| K1-only、private generation/sector/value、native/ISA/coherence | 既有未输出或未资格范围保持UNAVAILABLE，不补零。 |

统计字典绑定原AG4 `METRIC_DICTIONARY.tsv`完整SHA。两输入仅发现集，不是独立验证/GM12，不改旧44行或稿件。

BA发射前必须独立发布实际四UUID/inputs/config/Core/ELF/libs/loader/cache、集成source SHA、changed-path资格、R2/authority/FLOCK、timeout7200秒和fail-stop及比较定义，commit/push/fetch-back核HEAD/tree/blob/clean。默认一worker；最多两个AG6+BA合计活跃sim需事前完整资格及资源审计，未闭合不得并发。

任何实际启动（包括失败）消耗对应AG6上限；hard identity/mapping/resource/authority/strict失败停止新派发并按冻结规则收好自身已启动root，保留全部负结果、timeout及并发中已启动两点；不隐藏retry、替换或第五次。完整strict的性能负结果保留且可继续。

四点均完整合格后BA按原政策写新`SELECTION_V2`，不改旧selection：每输入speedup≥0.98、两输入GM≥1.02，最大GM，0.5%相对tie偏AE。缺格/失败不提升，保持provisional O。之后BA32工作仍用自身独立预算与资格，不自动继承本四点数字。
