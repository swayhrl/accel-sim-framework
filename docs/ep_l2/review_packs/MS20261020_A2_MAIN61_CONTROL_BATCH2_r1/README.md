# 第二批：main61 RO因子、去V与局部诊断

本批入口`BATCH.json`包含Conv/CFD/DWT各六项具体overlay和`SPEC_CANDIDATE.json`，合计18项；第一批另含各工作负载W_ONLY/F_MINUS_R，共24份准备候选。第一批已先发布并交E2，不等待本批。全部候选source/main身份冻结，0构建、0原生测试、0完整应用启动，未修改E中央registry。

生产绑定：Core `d010911e3174a3764791183cd108fe4664ba8731`；Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`；main SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`。正式producer入口仍为`MS20261020_A2_FORMAL_WAD_PRODUCER_RELEASE_r1/RELEASE.json`，本批不是新producer或新科研campaign。

## 分层状态

表中工程控制PASS仅指本次实际执行的静态有序config解析、固定资源/几何、非研究参数与资产hash检查。历史工程原生PASS保留其原main67/773身份；E现有main61资格只登记S/F，不能自动推广。

| A profile / E别名 | W/V/T/M | source-supported | 当前静态工程控制 | 现有原生证据与最小资格缺口 |
| --- | --- | --- | --- | --- |
| W_ONLY / 同名（第一批） | 1/0/0/0 | 是 | PASS | 当前d010 A1 mode2、bank retry、legacy rollback可供E映射；仍需新profile资格 |
| F_MINUS_R / 同名（第一批） | 1/1/0/0 | 是 | PASS | 当前d010完整dirty/clean/capacity/drain证据可供E映射；仍需新profile资格 |
| F_MINUS_V / 同名 | 1/0/1/1 | 是 | PASS | 保持W及完整RO，关闭clean/dirty TVD；审查旧773 `ro_native_dram_warm_R_without_V`的source等价性，必要时仅重链接该fixture并补一项 |
| WV_M_ONLY / **WV_M** | 1/1/0/1 | 是 | PASS | 审查旧773 tag/line压力下T0M1两项及当前d010 dirty/shared证据；缺口时现有d010 ELF执行两项，无需编译 |
| WV_T_ONLY / **WV_T** | 1/1/1/0 | 是 | PASS | 审查旧773 tag/line压力下T1M0两项；要求Tag脱离及有限LineMSHR128行为；缺口时现有d010 ELF执行两项 |
| S_COPY_FREE / 同名 | 0/0/0/0 | 是 | PASS | 旧67 copy-only原生local及ROP7工程PASS可供等价性审查；不能豁免response/fill/lowerWB/frontend服务；必要时只重链接小fixture |
| S_L2_DATA_FREE / 同名 | 0/0/0/0 | 是 | PASS | 旧67 local/ROP7工程PASS；保持copy latch、容量、队列与固定延迟，要求physical data grants=0；必要时只重链接小fixture |
| F_L2_DATA_FREE / 同名 | 1/1/1/1 | 是 | PASS | 旧773 F_data_free工程PASS；必须由E明确发布`full_data_free_finite_residual_service`专属PASS门，缺口时现有d010 ELF补一项 |

**以上8项的“E精确native/profile资格”均尚未具备。** 可复用的是已有证据和输入资格基础，不是未登记profile的执行授权。`QUALIFICATION_GAPS_AND_TEST_REQUIREMENTS.json`逐项列出当前d010原生回执映射、历史原生证据、最小缺口及可选命令。先做证据/source等价性审查；覆盖足够则不补测试，不重复17项原生套件。可选命令没有执行，也没有形成E队列；相关fixture若需要重新链接，只使用现有对象、冻结d010 archive和原七个库，不重建完整模拟器。

## 输入与配置复用

| 工作负载 | 已接受端点S / F | 完整输入指令数 | 输入内容SHA256 |
| --- | --- | --- | --- |
| Conv | E010 / E009 | 714547200 | `620f80f945d8ddbcef639e7e374fd2cb7122f8b07f239c82ccd32a2c4d90e79f` |
| CFD 097k | E015 / E016 | 143129372 | `6d5eb92fbe5391b3811dc08fcaaacb891ec8a69639512b99f68d224b6a921e66` |
| DWT | E017 / E018 | 148684429 | `5df26bc18e344ec381ce8cae8acd93a0e8b2266d5def861dd575a7061a303fc9` |

每份候选从对应已接受S或F的实际有序config生成，保留原base-0/base-1/base-2、环境、DRAM、ROP、cache/L1、完整trace、终止契约和input proof。24份候选的`comparison_invariants_sha256`均与对应已接受F端点完全一致；这是实际静态检查结果，详见`STATIC_VALIDATION_RECEIPT.json`。能否复用现有端点作为消融比较锚点仍由E审查当前资格、parser和完整exit/drain；本次不推导性能比。

RO的12份候选直接保留对应输入已接受F的whole-commandlist certificate，核验manifest/ranges SHA及commandlist SHA，不换成任意只读声明或最佳子集。关闭RO的候选移除证书参数。E仍按原政策刷新完整trace内容校验，本次没有扫描全部trace body。原输入采集/源码修订缺口及trace-model闭世界范围仍保留，不宣称数值SASS输出正确性。

`WV_M_ONLY/WV_T_ONLY`是A正式profile名，当前E terminal adapter只接受`WV_M/WV_T`。候选spec已使用E别名，W/V/T/M语义不变；不得只改profile文字却保留错误feature vector或T/M flags。全部保留observer=1、D512、per-address32、LineMSHR128、WAD/TVD128、payload1168、4bank/P1、WBUF16与所有旧ideal/legacy开关为0。

## 兼容性与因果解释

- W_ONLY与F_MINUS_R均为W=1；不是S或OFF替代物。V与RO不互相依赖，F_MINUS_V保留T/M与真实native lower path；T/M可分别开启，WV_M仍保留Tag约束，WV_T仍受有限native LineMSHR约束。
- COPY_FREE仅允许静态S，不能与V/RO/W或DATA_FREE叠加。它只豁免copy read/write的payload服务，保留非copy服务与原copy状态/latch。S_COPY_FREE对S可用于判断copy服务成本，不是关闭writeback生命周期。
- L2_DATA_FREE可用于S或完整F，只豁免数据bank服务。Tag/descriptor/WAD、metadata lookup、固定接口/ROP延迟、response/lower队列及完整drain仍有限。诊断端点必须保留`diagnostic=true`与`hardware_P1_throughput_eligible=0`；不能将豁免服务当硬件P1吞吐提升。
- F_MINUS_R与F的比较观察整体RO贡献；W_ONLY与F_MINUS_R观察在W底座上增加V的贡献；F_MINUS_V与F观察在WR底座上增加V的贡献。WV_T、WV_M、F_MINUS_R、F组成同输入证书的T/M四格，不能据一个profile的收益宣称交互项。S/F和三个局部诊断分别作为成本定位，不把overlapping wait计数直接相加成GPU stall。

## E2最短实施顺序与预算边界

第一批先审Conv W_ONLY/F_MINUS_R；第二批优先审Conv F_MINUS_V与WV_T/WV_M，复用现有精确输入证书及源分支证据。局部诊断可独立走资格审查，不必等待其他profile。若已有工程PASS足够，经E明确source等价性和证据范围处置即可复用；否则按机器清单补最小native项。最后由E发布新的profile资格、重新绑定spec资格ID、parser、input proof与source/main，独立执行原中央准入。

Conv这8项均有原32条件；CFD/DWT的16项控制是配置候选，当前矩阵没有对应消融条件，需要E/D在原32分配内明确工作负载替换，且遵守冻结/截止。**24份候选不是24次启动授权。** 不增加40次上限、不重置T0，不扩大已耗尽的contingency，不修改中央matrix/registry，不退款FWT INCOMPLETE历史启动。

F_MINUS_W和完整fixed64 dirty+RO继续不支持，不开发、不用S或clean-only64替代。旧B/C联合失败与未资格状态不因本次配置检查改变。`FIRST_BATCH_METADATA_CORRECTION.json`记录汇总指令数类型修正，以及草案中继承的S/F audit、旧contingency理由/ready状态和条件ID的清理；实际profile.config字节没有变化。候选spec现绑定对应控制bucket与条件ID，第一批原发布提交保留，E使用最新批次文件。
