# A2：r2 SGEMM main61 有限S/F配置与资格覆盖提案

任务：`A2-SGEMM-MAIN61-CONFIG-PROPOSAL-r1`，批次`EPL2_WORKLOAD_PREPARATION_BATCH_r2`。本包只完成A2新增配置/差异/覆盖映射；不重复候选、opcode、W/V、epoch全审查。最终准备状态以`PROPOSAL.json`和`RECEIPT.json`为准；不是E资格、启动spec、队列或运行授权。

## 选择准确生产者与cohort

- Core **d010911e3174a3764791183cd108fe4664ba8731**；Framework **9dd1ee57a83d83b56b7874bc7c716185ab52c8f7**；vendor **f90c430c3a1ce8f08c09942a5a1c3a797bb2295b**。
- main61：`/workspace/build/ep-l2-ms20261020-a-wad-pending-r41/accel-sim.out`，SHA256 **61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5**。
- archive：`/workspace/build/ep-l2-ms20261020-a-wad-pending-r40/libgpgpusim.a`，SHA256 **3c6ce15b88ae16c17c30718618aedc769495168d6e3d0c371270ba95b7b0aca8**。
- 本轮已物理核对上述两SHA，Core工作树干净；不更换当前93a9 capacity binary、不构建/执行main61，也不触碰E正在进行的运行。
- SGEMM采用独立冻结trace探索cohort，登记`E2_EXP_SGEMM_MEDIUM_20261020_r1 / REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE`保持。它不是原七输入第八格，不替换Btree，不混入原MAIN或新capacity统计分母。

输入：准确medium commandlist，2次HtoD＋1kernel，1658916864条active-lane指令；保存全输入hash **694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb**。body **1b0739908e3aef52cedea68962172ccac55f0c2d4c651623cb8fb0655475db06** /2216170035B，commandlist **0a0d21711ff3f3de1604fc0a243d5be2df5155147bb09bc4533bd017b62f5913** /92B。保存证明与准确入口引用于`PROPOSAL.json`；本轮没有重扫、重哈希或复制大trace。E在任何以后获批使用前仍执行其原身份门禁。

## 配置资产和准确差异

有序使用`CONFIGS/base-0.config`、`base-1.config`、`base-2.config`，然后是所选profile；三份base均逐字节复用原main61正式有限H0配置。历史空白/注释不更改，以保留SHA；其中旧注释不是本包新的科学结论。

`CONFIGS/S.config`逐字节复用无输入专属证书的传统S overlay；149项解析后选项与原main61已合格S完全相同。`CONFIGS/F_MECHANISM_UNSEALED.config`保留原完整F机制选项，仅剥离FWT的5项输入专属oracle绑定；没有借用FWT/Conv证书，没有填假路径，也没有将T/M关闭。此UNSEALED文件不应作为完整F启动。若C本轮候选已经发布，真正封入的F/config与字节来源另见`C_CANDIDATE_BINDING.json`及PROPOSAL最终字段。

|选项|S|F|
|---|---:|---:|
|`-gpgpu_ep_l2_ft_mode`|1|2|
|`-gpgpu_ep_l2_tvd_clean`|0|1|
|`-gpgpu_ep_l2_tvd_dirty`|0|1|
|`-gpgpu_ep_l2_ro_tag_detach`|0|1|
|`-gpgpu_ep_l2_ro_line_mshr_bypass`|0|1|

除这5个机制选项及F自身5项已发布候选metadata路径/哈希/scope外，不允许其它S/F差异。完整选项与共享不变量见`OPTION_DIFF_AND_INVARIANTS.json`，不是E runtime-config hash/run key。

保持payload **1168**、Tag **1024**、lineMSHR **128**、descriptor **512**、每址 **32**、WAD **128**、legacyWB参数 **16**、4banks×每物理周期1op、128B line/32B sector。F共享payload允许真实借位，不把legacyWB16误称固定16槽物理上限。有限诊断/free-service/ideal/meta、COPY_FREE、L2_DATA_FREE、STATIC_WB64、fixed-victim、MQ2/RG1全部维持原关闭值。L1/时钟/DRAM/ROP、kernel launch与既有H0一致，无模拟cycle/指令截断。

**main61没有大容量总开关选项**，因此不附加`-gpgpu_ep_l2_diag_l2_large_capacity 0`或1；使用原有限profile已经准确表达选定机制。不能把93a9配置的master0或新data-free/大容量ON资格复制过来。

## C fallback绑定边界

必须来自C真正发布的SGEMM自有候选：`SAFE_FALLBACK_NO_CERTIFIED_LINES`、`NO_READONLY_CERTIFICATION`、`whole_commandlist`、准确SGEMM commandlist/input身份，以及header-only空ranges。T/M仍为1；certified-by-policy覆盖为0，**实际RO集合仍UNKNOWN**，不报告“实测SGEMM零RO”，不以fallback构造Tag detach正例。

Core d010 `ep-l2-ro-runtime.inc:34–71`检查geometry、ranges/manifest SHA、domain、epoch/scope；`:403–407`检查实际commandlist SHA；`ep-l2-ro-oracle.h:25–46`要求正确header及fallback零ranges。C的候选只是准备metadata，不是科学证书已被E接受。

若最终尚无已发布C候选，F保持UNSEALED，`SGEMM-CANDIDATE-FALLBACK-BINDING`明确MISSING并交D/E2；不把占位符叫READY、不无限等待。若已绑定，也只标`PREPARED_NOT_E_QUALIFIED_NOT_ADOPTED`，后续仍由E独立审查和采用。

## 复用18门，保留真正输入缺口

`QUALIFICATION_COVERAGE_MAP.json`逐项固定18份既有main61门metadata的Git commit/path/SHA：原all-OFF、bank/P1、finiteWB、memcpy/payload、mode合法性、requester/stale/sector/WB/resource闭合及7项RO/V/WAD/共享资源组合门。引用的是E已接受的同一**d010/61aad**生产身份和既有case映射，不把之前未合格的红版本或额外joint fixture升级。现存fallback case`new_combined_fallback`也在同source mode/lifecycle映射中。

E可按原delta处置复用这些通用机制证据，不应因新增SGEMM重跑17项/OFF或重建生产main。它们不等于SGEMM输入资格。最小剩余项为：

1. E对SGEMM既有探索登记、准确完整输入字节/grammar/非原子属性与本次所选main61的源适用性、当前身份作独立绑定。
2. E独立审查本输入C候选fallback与固定F/T/M、全部S/F配置/auxiliary/profile标签，生成自己的资格与run/config/parser身份；本包不复制FWT/Conv资格id作为SGEMM资格。
3. 原main61 terminal parser静态路径对S/F及实际manifest/scope作检查，不要求F一律为`TRACE_MODEL_CLOSED_WORLD`；`NO_READONLY_CERTIFICATION`仍需E准确封口。见`TERMINAL_BINDING_PROPOSAL.json`，本轮未调用parser做synthetic/native PASS。
4. 如果覆盖映射后仍有具体未闭合的输入专属义务或真实缺陷，由E提出最小有界检查/A2按原producer流程处理；本包不自动建议额外native或生产修改。
5. 未来经资格和用户明确批准后，才可由唯一E控制器提2端同main61完整S/F（拟议2次、2×384MiB端点上限，另计collector/metadata/资格余量；walltime UNKNOWN）。本批0次，没有实际预留或启动。

未来实际终验需准确native OS exit0、无cap/fatal、完整1kernel/1658916864指令、64slice结构/实际T/M/P1/config、commandlist epoch闭合、sector/data/exact-once与完全drain，不能以raw进度或数值缺件掩盖原终验门禁。

## FWT与范围勘误保留

原main61 FWT Q **1d3af457edec4aa6cd175a8c11bbbe4f9c6d6159f95789294850e2f2fd74c2c9**仍为其准确19kernel/S/F模型范围的INDEPENDENTLY_QUALIFIED，18门PASS；本轮只引用，不重做其恢复准备。旧E011/E012仍INCOMPLETE。原source/capture/numeric payload缺件限制复采和数值应用结论，不自动撤销已有冻结trace Q，也不引入统一新的数值门或豁免新SGEMM资格。

Btree/SpMV/Scan HOLD、额外joint FAIL/未执行替代、F_MINUS_W和完整fixed64 dirty+RO边界都保持。新93a9完整F仍须单独资格；本次主动选main61不会将新93a9混入旧MAIN分母。

本轮只有小Git metadata/config核查及所选旧main/archive SHA，没有模拟/native、主binary构建、机制/生产源码修改、E registry/CLIENT/lease修改、Goal/控制器或后台poller。最终交付refs与远端回读随本包发布。
