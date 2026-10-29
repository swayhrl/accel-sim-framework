# 给 EP MAIN 的 Lane O V1R2 交接

可将下面内容直接发给Main。Lane O没有代发消息，也没有登记或启动新模型。

> Lane O已完成W/V/M/T只读分析及审查修订，文档在`hrl/ep-l2-lane-o-workload-memory-characterization-20261028-v1`分支，路径`docs/ep_l2/operations/ep_lane_o_workload_memory_characterization_20261028_v1`。请以V1R2的MEASUREMENT_CONTRACT.md、NI_MATRIX.md、PILOT_GAPS.json为采集接口依据。
>
> 请先复用已验收小汇总，不重复跑性能矩阵或扫描Trace。四个候选为Scan、Conv、FWT、Vector6M：S观察基线需求；合法F/WV观察实际Victim、RO及Tag联合。FWT现有是S/WV，勿直接替成未资格化RO-F。
>
> 新统计须区分真实ingress、queue_enter、first_head、admission；现有head计数不能冒充入口重访。旧MS与FT requester不天然同类，Lane O已撤下未证实的精确受阻百分比，保留原始独立数/重复数。若Main已有absorbed/请求类别小投影，请给精确路径/身份；没有则保持未知，不为此另开raw/Trace扫描。
>
> 请先回读缺口表，确认当前可采用的Core/ELF基点、已有统计/NI能够覆盖哪些格、哪些指标仍确实缺失。仅确需新增时，在独立候选工程分支准备默认OFF的计数器及CPU控制；先给逐路径NI、实际状态/输出成本、精确模式/输入和拟议点数。一个S OFF/ON不能覆盖全部F/WV hook，点数不能固定假设为4+1。
>
> 当前没有新增完整仿真预算，也没有合并生产Core的授权。正式补采由EP-MAIN统一报精确规格/预算、准入和调度；不干预现有实验，不延迟DRAM或缩Tag追求非零。只取Lane O文档，不把整个科研分支或待写Core候选自动合并到Main。

Main最小回包：`source_base`、`reusable_artifacts_by_metric`、`remaining_gaps`、`NI_coverage_and_missing_controls`、`candidate_scope_and_cost`；未确定项写UNKNOWN，不用补跑来填表。
