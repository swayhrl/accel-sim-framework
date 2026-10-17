# 未闭合材料与最小后续工作

停止边界：已完成授权的 CPU-only 盘点、来源核对及结构估算。当前 `T1C_RTL_NOT_AVAILABLE`，A 的实际 finite RTL 也未绑定。**没有授权或执行新 RTL、DC、布局布线、模拟器或 GPU 工作。** 不通过改工艺角、忽略 SRAM、缩减端口或修改有限服务合同来制造通过。

|缺口|已检查的具体位置 / 收据|需要用户提供的最小材料|
|---|---|---|
|当前 A/B L1 RTL 身份|Framework 的 T 包与 Core 只有模型；`/workspace/repos/gpu-l2-cache-verilog/rtl/{classic_cache,decouple_cache,decouple_cache_v3}` 均为不匹配 L2；另4个已知 clean clone 的限定索引见 BOUNDED_SEARCH_SCOPE.tsv|真实 L1 RTL 仓库/目录、完整 commit、未提交补丁SHA、top、filelist、include/define、A32×4和B64×8参数、generate后的几何检查；若 B 尚未实现请明确|
|论文原设计到 RTL/DC 的身份链|THESIS_CH4 与 SG0_RTL；没有建立论文与 L2候选69cd5b6的对应|论文当时 IO/OO（可选 C+/Base）source archive/hash、top/参数、对应原始综合目录与日志；只能恢复历史链，不能自动代表 finite L1|
|目标工艺/PVT/电压|未提供当前 L1 的库路径；已知 L2 `scripts/dc_elab_v3.tcl` 只有 `/path/to/target.lib`、`/path/to/link.lib`|原先批准的 process、library名/版本/SHA、PVT、电压、温度、cell selection；不是让本 Goal 选择有利 corner。私有库可只给可核 manifest 和合法可读位置|
|DC身份与约束|同模板的 `/path/to/constraints.sdc`；无真实 compile/report_area/report_timing 流程和 run 收据|DC准确版本、调用命令、脚本/SDC及SHA、clock/uncertainty/IO/generated-clock/reset/exception、tool warning和 unresolved/blackbox 检查|
|真实 SRAM 与完整存储记账|SRAM_MACRO_INVENTORY.tsv：现有 wrapper 不是真实宏；R8_AUDIT / R8_STA 已记录 library/timing views 缺失|每类 Tag/data/ordinary/shared/PIB/RefCnt/generation/waiter 宏：depth/width/banks/ports/mask、读写延时与 collision、Liberty/DB及SHA、LEF/面积、macro映射和实例数；FF实现需明确|
|完整面积与时序报告|五个命名 L2 仓库的固定 report-root 未发现；不等于全机不存在|当前 A/B hierarchical cell+macro area、blackbox面积处理、是否含全部 data及periphery、独立shared计量、matched setup/hold/WNS/TNS、unconstrained endpoints、真实 path reports、mapped netlist/hash；布线结论还需对应RC/physical收据|
|正确性与端口合同|Core 的 generation/slot-generation/waiter/refcount/finite-service 语义可读，但不是 RTL 验证|已有 directed/formal 收据：Tag eviction后仍被引用、最后引用回收、generation wrap/late return、slot reuse、pending late merge、同physical多更新、RAM collision、replacement和4bank quota；必须绑定 source/参数|

没有找到“当前 L1 RTL/DC 所在真实路径”的证据，因此没有替用户猜一个路径；表中占位路径确为模板内容，不是现成库的位置。本次没有遍历 `/home`、其它私有项目、全盘或任意运行目录。工具是否在另一环境可用也未被本审查裁决；引用 R8 的缺失是该既有审计的结论，不是假称本轮重新检查了 license 或安装。

值得后续**单独授权**的最小工作按依赖顺序为：

1. 先补齐当前 A 的 RTL 和已经批准的技术/宏/SDC 身份，核对实际 finite-service 端口与语义。若只有旧 L2/论文 RTL，先做差异规格和实现验证 Goal，不能直接称 A 已实现。B 未实现时单独授权64×8参数化及生成/替换/冲突逻辑的最小变更和等价/定向验证；本 Goal 不写 RTL。
2. 在同一批准工艺、PVT、电压、DC版本、宏端口与时钟约束下，对 A/B 的 Tag-bank read/compare/select/update 边界做配对综合与 STA。报告 SRAM view、hit/miss/victim及同地址冲突路径；局部报告只能闭合局部面积/延时，不能形成 TOTAL_AREA_PASS。
3. 再对完整 OO128 接入物理数据阵列、ordinary、PIB、generation/RefCnt/TagValid/waiter、ready/wakeup/collection/reclaim 做同条件完整面积与时序核对。shared 单列，逻辑和宏面积去重，查缺失实例、unconstrained endpoints 和功能/服务合同差异。IO/C+ 的既有报告若无匹配身份，另行恢复，不能强行加入统一百分比。
4. 若需要 routed Fmax/布线开销，另行授权 place/route/RC 与 macro placement 合同；DC 逻辑面积或 prelayout STA 本身不足以证明该层结论。

以上是后续建议，没有启动任何一项。提交本包后等待科学裁决；现有 HOLD、Lane A、Lane U 与旧冻结实验均不调整。
