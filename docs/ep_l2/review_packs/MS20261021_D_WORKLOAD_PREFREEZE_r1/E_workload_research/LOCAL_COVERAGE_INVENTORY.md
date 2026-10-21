# 本地覆盖盘点（只读）

当前正式MAIN为 **5个独立应用、5对S/F**；新capacity实验仍是同一五输入，已接受2/5对，**不会把workload数增加到10**。原七输入目标中FWT未闭合、Btree仍HOLD。当前45次实际启动的历史不修改。

五应用共21个动态kernel launch/端，不能称21个独立workload或21个独立静态kernel。每应用目前只有一个输入规模；Conv行/列、DWT十阶段、CFD五次调用属于应用内部，不是独立输入样本。五应用可支撑这些应用和机制的有限结论，对普遍GPU收益的主张覆盖较窄；不以“达到某个固定数量”替代代表性与负对照。

| 应用/输入 | kernels/端 | 完整指令 | 当前MAIN | 新capacity | 本地完整文件 |
|---|---:|---:|---|---|---|
| FWT_7_21 / _logK_7__logD_21 | 19 | 791609344 | INCOMPLETE_NO_ACCEPTED_MAIN_PAIR | 0 accepted pair | True |
| btree / file___data_mil_txt_command___data_command_txt | 2 | 444467849 | INPUT_SCOPE_HOLD | 0 accepted pair | True |
| convolutionSeparable / __size_3072 | 2 | 714547200 | CURRENT_ACCEPTED_MAIN_SF | 0 accepted pair | True |
| dwt2d / __data_rgb_bmp__d_1024x1024__f__5__l_3 | 10 | 148684429 | CURRENT_ACCEPTED_MAIN_SF | 0 accepted pair | True |
| cfd_097k / __data_fvcorr_domn_097K | 5 | 143129372 | CURRENT_ACCEPTED_MAIN_SF | 1 accepted pair | True |
| sad / _i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin | 3 | 157583646 | CURRENT_ACCEPTED_MAIN_SF | 0 accepted pair | True |
| vectorAdd_4M / __size_4000000 | 1 | 56000000 | CURRENT_ACCEPTED_MAIN_SF | 1 accepted pair | True |

新capacity已接受CFD、Vector；其余精确运行态见JSON快照，终态仍须独立验收。Vector MAIN已经由新F资源重试补齐，旧E014 exit−15 RESOURCE_LIMIT保留；不可沿用旧“只有四主对”状态。FWT E011/E012仍INCOMPLETE，真实退出码缺失；监护修复不能追认exit0。Btree物理文件存在和旧oracle审核不等于解除输入语义HOLD。

## 下一步仅资格准备，未获启动授权

1. **FWT_7_21 original complete input S/F restoration qualification review**：Predeclared before new F outcomes; multi-stage transform and saved W/butterfly reuse hypotheses complement current five。Existing exact main61 S/F qualification and complete non-atomic input can be reviewed/reused only for matching old runtime; new-runtime FWT scope not yet E-qualified。若以后单独批准完整配对需2次，按两端384MiB预留768MiB；成本：Existingmain61 feasibility: S80–110min,F85–120min; old incomplete elapsed5041/5395s are not accepted completion times; current resource load/new-runtime cost unknown。边界：OriginalE011/E012 INCOMPLETE remains charged; durable exit fix covers known monitor persistence defect but does not infer old exit0 or missing external143 sender. Present user count/time removal authorizes only current five capacity inputs, not FWT/retry.

2. **SGEMM medium input qualification review only**：D selected on complete grammar/non-atomic closure plus dense-compute diversity; no new F speedup inspected。D full original-byte/native-grammar/non-atomic input proof PASS, E source/profile/fullinput/oracle-fallback qualification NOT granted. Source revision/capture run script/toolchain gaps remain UNKNOWN。若以后单独批准完整配对需2次，按两端384MiB预留768MiB；成本：1,658,916,864 lane instructions/2,216,170,035 trace-body bytes; current native walltime unknown. Static D review837.48s already complete; do not repeat full scan unnecessarily。边界：Requires explicit independent exploration registration and launch authorization. No automatic Btree replacement or RO-certificate inheritance.

3. **Btree exact held input witness/provenance review only**：Predeclared irregular traversal/read-heavy negative pressure control, selected before F performance。Complete2 bodies physically present, but explicit E nonzero-mask/full32 address semantics input_scope_HOLD; old offline RO artifact review does not remove it。若以后单独批准完整配对需2次，按两端384MiB预留768MiB；成本：444,467,849 instructions/809,709,439 body bytes; current qualified walltime unknown。边界：Not a low-cost ready-to-run candidate. Do not edit trace records or weaken parser semantics; full source/input scientific review and explicit authorization required.

4. **SpMV Dubcova3 rejected-record source/provenance triage only**：Original predeclared first fallback with34.5MB body and21.1m instructions, independent of observed F speedup。HOLD: actualIADD3 record missing one source register; cannot reuse old cycles as qualification or silently repair trace。若以后单独批准完整配对需2次，按两端384MiB预留768MiB；成本：Small saved body is a cost proxy only; current full native runtime unknown。边界：Research only; unless authentic complete input and semantics supplied, no launch. Scan is lower priority: separate nonzero shared-address tail failure,33kernels/5.329GB and1.963b instructions.

8–10个独立应用可作为下一阶段覆盖工作目标，不能为凑数提升HOLD、重复计kernel或无授权扩展本轮五输入。BFS/Hotspot/histogram/PolyBench只因外部类别名称存在而提出不足以进入本地可执行清单；本次未发现其E/D/C/B完整来源及资格闭合的已审文件，故不猜测trace可用或atomic/RED合法性。

现成新增候选中，没有一项已经取得E完整runtime/profile/input科学资格可直接低成本启动。最接近复用的是原FWT main61资格，但需要新的恢复授权；SGEMM是D完成全输入语法与非atomic证明的唯一新增候选，仍不是E合格端点。Scan明确有输入格式失败，暂不推荐投入完整资格。

完整绝对路径、注册/接收SHA、saved trace SHA及本次stat大小/设备/inode均在JSON。只重算小metadata SHA，没有重读大trace或全盘扫描。
