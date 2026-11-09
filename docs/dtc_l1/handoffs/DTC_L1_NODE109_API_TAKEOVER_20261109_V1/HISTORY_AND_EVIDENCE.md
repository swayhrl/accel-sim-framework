# 109做过哪些DTC-L1工作：固定GitHub记录调查

## 0. 本报告的证据等级

本报告是2026-11-09对固定GitHub历史文件的调查和前向整理。未登录109、174-new或164，未读取节点活动raw、锁或进程，未重跑native、capture、CPU fixture或模拟器。本包里的路径、GPU/软件版本与归档PASS均保留其原观察日期，不能当作今日现场状态。

已确认两条直接在109执行的DTC工作线：**原生行为/新增算子producer**与**SM89 CPU准入可行性**；另核对了174消费、现代容量审查、早期V100来源和后续存储治理。分支名检索、固定树与历史报告不能覆盖已删分支、未提交文件或所有旧commit，未找到不等于不存在。

## 1. 当前主线及本窗口关系

当前正式运行结果提交为 `7ffcca7f908a21f45ba1a6ebb3b335ff962f97df`；完整工程交接为 `3f0036f2868e20a8d9a4b6244c7c74d940954188`；Main最终科学包为 `b9ff89f00ea8ff889e4189136501c714c5d7e345`；科学接受为 `64cd088b2de575157846f07a21ce09748220f7e2`。[Main完整交接][main-handoff]、[科学接受][acceptance]、[接受后的CONTEXT增量][context-main]。

本轮Oracle固定32输入×OFF/M/L2/L1形成128个自然闭合结果及96个同build实际OFF配对。D是独立raw/strict/归档/恢复审查，M是冻结完整32机会分析，Main是证据连接与复算，科学窗口做固定远端包及小型证据的有界复核。科学接受仅覆盖SM70/V100-derived 64SM固定trace的受控性能反事实，不证明可实现等量收益、等面积收益或严格数学上界。L2的11个精确零和myocyte、srad_v1两个回退保留；原生完整应用数值、capture绑定、coherence、有限机制因果和PPA仍各自独立待资格。[context-main]

**109不是上述32输入的统一producer。** 109→164→174-new是部分资产的历史关系，具体输入来源仍以逐输入spec和固定索引为准。当前109职责只接手历史资料、环境线索和资产维护。Stage I、Stage II及Oracle的已关闭工作不因新窗口重开；英文v0.23母稿冻结，IO/OO来源归赵皓宇博士论文第4章，旧F=null及全部负例保持原状。[main-handoff]

用户已将64cd接收任务交给唯一DTC-L1 Main“DTC-L1交接-1”。本包编制时没有其本机接收完成回执；不能把本报告写成已经更新其D盘CONTEXT。109用独立CONTEXT与MAIN_INTAKE_NOTE回传，Main之后自行消费。

## 2. 直接工作线一：native行为、profile和SASS producer

**固定完成提交：`890fb0be7e681a60419c49ca0a7aa85731d8c164`。** 分支 `hrl/iscas2027-dtc-native-coverage-109-v1`，完成时间2026-10-16 08:50:24 UTC。[producer]、[native-findings]、[source-anchors]

历史专属worktree是 `/home/huangrulin/workspace/worktrees/accel-sim-dtc-native-coverage-109-v1`，campaign根是 `/data/c16/dtc_native_coverage_109_v1`。目录前缀c16来自当时可写存储组织，不改变这项工作的DTC归属。

### 2.1 R0：原固定12应用的资产盘点，没有重采

原12为 `atax, bicg, gesummv, gemm, 2DConvolution, btree, dwt2d, gaussian, hotspot1, lud, nn, mri-q`，其中nn是nearest neighbor。清单记录629个有序成员、9,162,136,500字节；Gaussian和LUD合计604成员。**2026-10-16当时109的原12本地trace root可用数为0。** 这不是629个程序，不证明今日仍缺或已丢失，也不推翻174对同批材料的接受状态。[r0]、[r0-summary]、[consumer]

R0里大量路径属于历史174/container namespace。看到该路径字符串不证明109生产过对应trace。未得到的captured binary、实际输入维度、launch与opcode等字段不能按名字补全。后来的SpMV/LayerNorm是独立新谱系，不能代填原12，更不能代填当前CORE32。

### 2.2 R1/R2：共15个原生条件

12个诊断条件分别为独立链ILP 1/4/8、地址stride 1/32/257、共享消费者g1/g4/g32，以及hit32k/chain32k/chain128m。另有SpMV主输入、LayerNorm主输入和唯一native敏感性输入。因此是 **15个case/条件，不是15个不同应用**。[prereg]、[timing]、[profile]

每个条件有7个独立进程batch×10次未profile的CUDA-event样本，之前有3次相同算子warmup。NCU使用application replay，cache-control/clock-control均none，ROI是完整kernel/operator；新增算子另有nsys核对。event、nsys区间和NCU duration口径分别保留，不能混用。诊断的固定grid为304、block为128、每线程1024次标量uint32逻辑load；维度间footprint、coalescing及依赖可共同变化，不能据此声称已经隔离硬件MSHR、PIB、Ref或单独fanout因果。[prereg]、[native-findings]

| 条件 | 实际实现与输入 | 已证事实及限制 |
|---|---|---|
| SpMV主输入 | Parboil `4e0fc54866546efa44fe93af57c9cef62f6c8eb9`；原JDS prefetch kernel字节不改；small/1138_bus.mtx＋vector.bin，FP32，int32索引；1138维、4448 padded JDS entries | 1138个输出通过原源码比较谓词；grid36/block32、33寄存器、无shared/local。36 CTA对当时76SM明显underfill。warm NCU DRAM读为0；event中位数4.096μs是该固定条件的原生测量。不能作为大规模流式SpMV、严格通用数值界或DTC硬件收益。 |
| LayerNorm主输入 | 已安装PyTorch2.5.1+cu124 `F.layer_norm`；FP32 `(1024,1024)`，width1024、seed109、eps1e-5、weight1/bias0 | 对FP64 CPU population-variance参考逐元素比较通过，rtol2e-5/atol2e-6。完整单个vectorized LayerNorm kernel含内部归约。grid1024/block(32,4,1)、43寄存器、24B dynamic shared；warm NCU DRAM读0。 |
| LayerNorm敏感性输入 | 同一实现，唯一变化为 `(8192,1024)` | native/profile已完成，DRAM读31,584,000B；没有捕获该输入的SASS，不能由主输入代填cubin/trace资格。 |

上述数值与资源见[SpMV身份][spmv-id]、[binary/framework/input身份][binary-id]、[新增family表][families]。SpMV的原始比较谓词本身较宽；原结果保留max-abs误差和源码阈值，不把“PASS”扩展成未定义的精度承诺。native固定GPU上的正确性只支持这些具体case，不推广到CORE32全部应用或Oracle的数值正确性。

### 2.3 历史环境和capture修复

当时设备是RTX4080/SM89；driver580.178.04、CUDA12.8 compiler/disassembler、NCU2025.1.1；PyTorch环境为 `/data/c16/env/c16-py310`。tracer借用独立AWMA worktree内既有NVBit1.7.5/Accel-Sim tracer5；来源 `7f38c063fa853525680effd8454d4899c7895ff5`。实际工具是：

`/home/huangrulin/workspace/worktrees/accel-sim-awma-simcompat-v1/util/tracer_nvbit/tracer_tool/tracer_tool.so`

其历史SHA256为 `14891b344554ff221423f51e970e1d0c92ab78c9375d9f993dafbfd8420af3db`；postprocessor SHA256为 `c7691bb9e3d37fe1da491f9f182cfbbe8c657687ecc1fb4992a7fd8dc86270a2`。共享工具资产不是AWMA科学资格的移交。[source-anchors]、[capture]

历史capture先出现native exit0但无trace、缺cuGetExportTable、缺disassembler等失败，随后显式绑定既有libcuda.so.1和CUDA12.8 nvdisasm成功。失败尝试保留；没有重建tracer或升级全局工具链。旧README里的“锁空闲”“GPU仅桌面进程”“Timing will acquire”等只描述当时，不能作为今天的状态或执行许可。[producer]、[trace-gaps]

### 2.4 真正生产的trace，以及后续有效结论

| 对象 | producer已交付 | 现在应继承的状态 |
|---|---|---|
| SpMV主输入 | 4个完整spmv_jds：3 warmup＋1 final；header cubin89/tracer5；每个36 CTA/36 warp/2927条warp-instruction record；无skipped-CALL | native有效，producer格式/覆盖检查PASS；174 consumer拒绝仿真准入；后续109 CPU审查为NO_GO/HOLD。不能停留在原表的PENDING_174_OPCODE_TRACE_CONTRACT。 |
| LayerNorm主输入 | 6个完整kernel：2 affine初始化＋3 warmup＋1 final；每个LN为1024 CTA/4096 warp/2,324,480条记录 | 实际cubin是86，运行设备是89；存在29条静态CALL.REL.NOINC被tracer忽略的warning。SASS NOT_ADMITTED。完整grid、数值PASS、exit0不弥补语义缺口。 |
| LayerNorm敏感性输入 | 没有capture | NATIVE_SENSITIVITY_ONLY / NOT_CAPTURED。 |

[capture]、[trace-audit]、[trace-gaps]、[consumer]、[sm89-decision]

ACTIVE_FROM_START保留初始化及前序kernel，但异步HtoD、memset、allocator/driver活动和精确初始cache状态仍不完整。warm native与cold final-kernel replay不是天然严格配对。这批材料不能用来直接填充现代DTC性能行。[trace-gaps]

## 3. 174消费结论：属于consumer工作，不算109新增采集

174复用109的15个native条件，独立核验285个payload成员及174,081,218个索引字节。首次consumer把额外的PAYLOAD_FILES.json索引误当为另一个payload而失败；之后在新namespace更正包装理解，未替换科学payload，首次失败仍保留。历史verified目录为 `/workspace/dtc-service-closure-174-v1/producer109-890fb0be/payload-verified-v2`。[consumer]

冻结Framework18a68dcc的canonical-runtime canary保留原4成员list/字节，打印 `unsupported binary version: 89`，exit0且没有完成instructions/cycles，被terminal与independent collector拒绝。该attempt不是性能0、speedup1或accepted行。把89映射为86、改header或由opcode root重名推断Ada时序，都改变了准入合同。[consumer]

此段只继承历史consumer结论；首轮109接手不重开canary，也不跨到174-new读取当前Main控制面。

## 4. 直接工作线二：SM89 CPU准入可行性

**固定完成提交：`d58e75ce32845a281692f19aeb4057b4c9822a3f`。** 分支 `hrl/iscas2027-dtc-sm89-admission-109-v1`，2026-10-16 10:32:25 UTC完成。[sm89]、[sm89-decision]

历史worktree为 `/home/huangrulin/workspace/worktrees/accel-sim-dtc-sm89-admission-109-v1`，CPU source/build/raw/assets根为 `/data/c16/dtc_sm89_admission_feasibility_109_v1`。这轮未申请GPU锁，没有native、GPU、LayerNorm修复或完整simulator启动。

实际完成的CPU证据包括：

1. 检查194个local worktree和5类decoder文件。AWMA/C16里的89入口是Ampere classifier的别名/映射，并不提供独立Ada ISA、资源和时序证明。
2. 对原4份SpMV压缩trace做冻结parser CPU解析，11,708条warp records可解析；完整scope为353,256 active-thread instructions。独立decoder对照已捕获PC/mask/opcode/寄存器/宽度/地址等字段。
3. 23个完整opcode拼写、16个root；FFMA.FTZ完整拼写相对既有C16审查为新增。root存在不等于完整语义支持。
4. 检出64条动态高半寄存器依赖缺失边：64位常量load记录base，而后继消费R17/R3；每个成员16条。常量地址、uniform/predicate依赖及宽地址就绪仍有缺口。
5. 4个negative fixtures与20个literal dispatcher控制流probe通过，但它们不是完整simulator build或性能canary。`candidate_fail_closed.patch`只把unsupported分支改为失败退出，未应用，也没有增加SM89支持。

[sm89-source]、[sm89-tests]、[sm89-pairs]、[sm89-validation]

有效结论是 **`NO_GO_FOR_DROP_IN_SM89_ADMISSION`，scientific promotion HOLD**。新窗口不执行历史 `run_cpu.sh`、不重复扫描194个worktree、不尝试“只补89编号”，也不以新会话为由重做既有CPU验证。

## 5. 两个归档与一个整树问题必须分开

### 5.1 Native指定归档：已有历史目的端完整性PASS

历史路径：

`/root/share/mnt164/huangrulin/dtc_native_behavior_workload_coverage_109_v1/20261016_v1/dtc_native_coverage_109_v1_20261016.tar.gz`

归档85,512,354B，SHA256 `af5c6ec76179f881f689f486829c025055764bd9e564e598c0dc18560865f984`。285个payload文件合计174,081,218B；索引SHA256 `8b6f25483a78af6b8b13571b2656793e48e04acaa1593e6809e63f0ebe51bf5e`。2026-10-16T08:47:31Z左右，独立目的端流式tar/逐成员SHA验证PASS，历史route为109→hrl174new→mounted164。[native-archive]、[native-index]

这是**指定归档及285成员**的证据，不是今天重新验证，也不是全工作树归档承诺。该路径在历史174-new/root挂载namespace出现，不要求它在109原样可见；同一164后端的多个挂载alias也不是多个独立副本。

### 5.2 SM89 CPU归档：已知证据只到109本地

`/data/c16/dtc_sm89_admission_feasibility_109_v1/DTC_SM89_ADMISSION_FEASIBILITY_109_V1_CPU_RAW.tar.gz`

576,292B，45个verified raw/source/build成员，SHA256 `95f3e6d6e3a986bdc7d9d2468374275e2e008b81cbd88d0ec026315117a6f28f`；raw-index SHA256 `6cfc9205bd197e362f76c8ccabf82b752e404f60ead0ce43be839a59db83d7d7`。已有本地archive与逐成员验证PASS；所读来源**没有证明它已进入true164**。[cpu-archive]、[cpu-index]

### 5.3 11月4日整树盘点：TARGET_UNVERIFIED

固定 `b290790401e248a19427c26c0dde51e6b55ded67` 的两张存储表仍记录 `/data/c16/dtc_native_coverage_109_v1`：allocated439,816,192B、logical437,757,580B，状态TARGET_UNVERIFIED，true164_path为空。原因是缺完整Nov04 source-to-target成员映射，整树恢复未测，cleanup_prerequisite_met=NO；证明时间为2026-11-04T02:26:07Z。[storage-inventory]、[storage-map]

**两份记录不矛盾：10月验收的是固定285成员包，11月审的是整个工作目录。** 当前不能判定额外工作文件是否都归档、哪些为重复/派生，不能按两个不同日期/范围的字节总量相减得出“未归档字节数”。存储表project=C16只是存储分类，不移交其他C16资产。

同次retirement白名单没有DTC路径；这只说明该次名单没列它，不证明之后从未移动/删除。跨项目使用报告也提醒“DTC在174执行不等于完全不依赖109”，但没有建立DTC对StageA/Qwen3/R26/R27等共享候选的精确依赖，也未取得正式owner答复。该报告中的DTC48运行快照已过时，不能恢复旧运行状态。[retirement]、[cross-project]

**第一轮现场最有价值的工作**是：确认两处DTC专属root和worktree的当前存在性，复用现有成员索引，把285成员与当前路径作元数据层映射，单列额外文件/未知项，记录CPU小归档的现存位置和是否有后续持久化回执。无需重hash285个payload、解压恢复或重新归档。

## 6. 不应误接管的相邻工作

### 6.1 早期M5/Paper-10：AutoDL V100

固定 `a9cdb3328a346cbc9a76b7ffadae3725b4209ab5` 明确producer为AutoDL V100/CC7.0，CUDA11.8、sm70、NVBit1.8；SIM_HOST负责回传/replay和科学Git记录。不能把这些SM70输入一概归为109 RTX4080生产。[autodl]、[m5-pipeline]

其中早期SpMV为 `parboil_spmv_medium_bcsstk18`，50 invocations/50 raw/50 grouped traces。归档spmv.tar.zst为53,292,499B，SHA256 `5d7d92ca08d6a3c2b8f5e4b7085428dcaa1ec5bdae330816132113eefb3f0852`，状态ARCHIVE_PASS/COPYBACK_SHA_PASS/LOCAL_IMMUTABLE_PASS。它与109的small1138_bus、4次capture是独立身份；两者仅共用一部分上游源码，不能合并输入、binary、trace或性能。[m5-spmv]

如果109现场有M5副本，记为外部producer材料的本地副本，不重写其producer为109。所读M4/graphics报告也没有建立109 GPU执行归属；保留来源未证状态。

### 6.2 现代RTX4080容量/服务审查：174负责，现代DTC仍HOLD

固定 `d6f0a3300972d7b1d9638b8f4b1338c25912a1b3` 是174 modern-layout方向。冻结普通128KiB再另加80KiB DTC会形成208KiB data/shared预算；不能悄悄与128KiB baseline比较后声称同成本。固定128KiB方向仍需普通cache/store/atomic、shared合法域、端口与drain等服务合同，CPU容量算术不是实现准入。[modern-readme]、[modern-next]、[modern-contract]

现代DTC性能行仍为0/HOLD。共享AWMA RTX4080 platform/tracer可以是历史依赖，但不把AWMA/C16资格自动转移到DTC。109接手资产不接管174结构实现；1024Tag/physical640的NO_FREE_LINE安全HOLD另行保留。

## 7. 新窗口必须保留的三层字段

| 维度 | 示例 | 不允许的推断 |
|---|---|---|
| 今日存在性 | PRESENT_METADATA_ONLY、MISSING_AT_OBSERVED_PATH、INACCESSIBLE_PERMISSION、UNKNOWN_NOT_INSPECTED | 没找到旧绝对路径≠不可恢复丢失；目录可见≠完整性PASS。 |
| 完整性证据 | INHERITED_SHA_RECEIPT、CURRENT_SMALL_FILE_SHA_MATCH、PAYLOAD_NOT_REHASHED | 继承10月SHA回执≠今天重hash；285成员PASS≠整树PASS。 |
| 科学使用资格 | HISTORICAL_NATIVE_VALID、PRODUCER_FORMAT_PASS、SIM_NOT_ADMITTED、MODERN_DTC_HOLD | 数值PASS/exit0/格式PASS≠ISA、时序或DTC性能准入。 |

历史raw、失败、负例、索引及SOURCE_KEEP持续保留。新窗口只能前向追加今日观察和未决项，不改写原封包状态，不为界面RUNNING/blocked/旧NOT_YET启动owner、改registry或reset预算。

## 8. 来源和检索记录

`SOURCE_INDEX.json`记录58份已读取固定来源的Git blob、bytes和SHA256。初始31份producer/SM89来源中，29份的bytes/SHA与原PACK_MANIFEST一致，另2份是清单自身；后补读取的native/CPU两个成员索引也与原清单一致。这些成员索引只作为只读映射来源，没有读取其raw payload。`evidence/TOOL_ENTRYPOINTS.index.json`只列固定Git tree中的18个历史脚本入口，没有执行脚本。

检索关注DTC/ISCAS/109/native/SM89/现代容量、M4/M5/trace与109存储治理分支及相关固定提交。默认分支搜索空结果不作为不存在证据。新窗口允许在两个已知DTC专属root、worktree及它们直接指向的小型文档中补查未提交历史；其他项目仅记录明确引用，不扩大为全盘审计。

[main-handoff]: https://github.com/swayhrl/accel-sim-framework/blob/3f0036f2868e20a8d9a4b6244c7c74d940954188/docs/dtc_l1/handoffs/DTC_MAIN_FULL_HANDOFF_20261109_V1/HANDOFF.md
[acceptance]: https://github.com/swayhrl/accel-sim-framework/blob/64cd088b2de575157846f07a21ce09748220f7e2/docs/dtc_l1/review_packs/CORE32_ORACLE_SCIENTIFIC_ACCEPTANCE_20261109_V1/README.md
[context-main]: https://github.com/swayhrl/accel-sim-framework/blob/64cd088b2de575157846f07a21ce09748220f7e2/docs/dtc_l1/review_packs/CORE32_ORACLE_SCIENTIFIC_ACCEPTANCE_20261109_V1/CONTEXT_INCREMENT.md
[producer]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/README.md
[native-findings]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/NATIVE_FINDINGS.md
[source-anchors]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/SOURCE_ANCHORS.md
[r0]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/R0_FIXED_COHORT.tsv
[r0-summary]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/R0_SUMMARY.json
[prereg]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/PREREGISTRATION.json
[timing]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/TIMING_SUMMARY.tsv
[profile]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/PROFILE_METRICS.tsv
[spmv-id]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/SPMV_SOURCE_INPUT_IDENTITY.json
[binary-id]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/BINARY_FRAMEWORK_INPUT_IDENTITY.json
[families]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/R0_ADDED_FAMILY_PATHS.tsv
[capture]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/CAPTURE_ENV_READY_RECEIPT.json
[trace-audit]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/TRACE_AUDIT.json
[trace-gaps]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/TRACE_DELIVERY_AND_GAPS.md
[consumer]: https://github.com/swayhrl/accel-sim-framework/blob/b9ff89f00ea8ff889e4189136501c714c5d7e345/docs/dtc_l1/iscas2027/service_closure_174_v1/PRODUCER109_CONSUMER_REVIEW_V1.md
[sm89]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/README.md
[sm89-decision]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/NEXT_DECISION.md
[sm89-source]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/SOURCE_COMPARISON.md
[sm89-tests]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/CPU_TEST_RECEIPTS.json
[sm89-pairs]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/PAIR_DEPENDENCY_WITNESSES.json
[sm89-validation]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/VALIDATION_SUMMARY.md
[native-archive]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/DURABLE_STORE_RECEIPT.json
[native-index]: https://github.com/swayhrl/accel-sim-framework/blob/890fb0be7e681a60419c49ca0a7aa85731d8c164/docs/dtc_l1/review_packs/DTC_NATIVE_COVERAGE_109_V1/RAW_PAYLOAD_INDEX.json
[cpu-archive]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/CPU_ARCHIVE_RECEIPT.json
[cpu-index]: https://github.com/swayhrl/accel-sim-framework/blob/d58e75ce32845a281692f19aeb4057b4c9822a3f/docs/dtc_l1/review_packs/DTC_SM89_ADMISSION_FEASIBILITY_V1/RAW_LOG_INDEX.json
[storage-inventory]: https://github.com/swayhrl/accel-sim-framework/blob/b290790401e248a19427c26c0dde51e6b55ded67/docs/storage/node109/20261104/ASSET_INVENTORY.csv
[storage-map]: https://github.com/swayhrl/accel-sim-framework/blob/b290790401e248a19427c26c0dde51e6b55ded67/docs/storage/node109/20261104/SOURCE_TO_TRUE164_ARCHIVE_MATRIX.csv
[retirement]: https://github.com/swayhrl/accel-sim-framework/blob/b290790401e248a19427c26c0dde51e6b55ded67/docs/storage/node109/20261104/fast_retirement_v1/FROZEN_WHITELIST_AND_DONE.csv
[cross-project]: https://github.com/swayhrl/accel-sim-framework/blob/8700af7cd3e0cd530f8efa8dfe5333ebdd9f1d1e/docs/storage/node109/20261104/cross_project_usage_review/FINAL_CROSS_PROJECT_USAGE_REPORT.md
[autodl]: https://github.com/swayhrl/accel-sim-framework/blob/a9cdb3328a346cbc9a76b7ffadae3725b4209ab5/docs/dtc_l1/m5/AUTODL_V100_CAPTURE_HOST_HANDOFF.md
[m5-pipeline]: https://github.com/swayhrl/accel-sim-framework/blob/a9cdb3328a346cbc9a76b7ffadae3725b4209ab5/docs/dtc_l1/m5/handoffs/M5_0BT_CAPTURE_REPLAY_PIPELINE.md
[m5-spmv]: https://github.com/swayhrl/accel-sim-framework/blob/a9cdb3328a346cbc9a76b7ffadae3725b4209ab5/docs/dtc_l1/m5/handoffs/M5_0BT_SPMV_CAPTURE_CLOSEOUT.md
[modern-readme]: https://github.com/swayhrl/accel-sim-framework/blob/d6f0a3300972d7b1d9638b8f4b1338c25912a1b3/docs/dtc_l1/review_packs/DTC_MODERN_LAYOUT_PROPOSAL_V1/README.md
[modern-next]: https://github.com/swayhrl/accel-sim-framework/blob/d6f0a3300972d7b1d9638b8f4b1338c25912a1b3/docs/dtc_l1/review_packs/DTC_MODERN_LAYOUT_PROPOSAL_V1/NEXT_DECISION.md
[modern-contract]: https://github.com/swayhrl/accel-sim-framework/blob/b9ff89f00ea8ff889e4189136501c714c5d7e345/docs/dtc_l1/iscas2027/service_closure_174_v1/MODERN_CAPACITY_CONTRACT_REVIEW.md
