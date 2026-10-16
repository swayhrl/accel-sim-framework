# NEXT_DECISION

**建议接受本轮可行性结论，现代保持 native/modern baseline-only；不启动现代 DTC 主结果。** 原128KiB固定总数据/shared预算保持，原64-SM授权主线独立继续。没有需要本窗口代做的队列操作。

具体原因已经闭合：现有代码双对象计容，R1独立服务缺少物理组织；候选A可给出单epoch无重叠布局，但代价是明确的多端口存储、新分区/清退约束、普通端口显式限流和候选域限制；原100KiB shared与fixed80在数学上不兼容。支持全域的动态池备选B已有96行反例。工程范围超过单次配置修补，不能为现代性能图自动展开。

如果后续仍要求实施，先决定下面三个可审查事项；它们是新的资源/支持域合同，当前用户和 `GOAL_C_MODERN_CAPACITY.md`、固定决定e13266ba均未授权自动选择。此文件记录待决事项，不发起任何实现或仿真。

| 决定 | 明确选项及影响 | 本报告建议 |
|---|---|---|
| 结果范围 | 保留baseline-only；或另行批准A只适用于显式S≤32的DTC候选集合（完整平台baseline仍保留64/100，不能称DTC全域支持）；若必须DTC也支持100则需B的独立机制课题 | 本轮baseline-only；不默删输入或自动fallback |
| 端口成本 | A按DTC四个20KiB bank各4R1W、48KiB尾部32个word bank各2RW+1W单独计价；若要求共用较少端口，则需新仲裁/collection时序合同 | A还需补普通访问/fill显式cycle配额并重新配对baseline；只作为有限服务成本候选，不声称实测4080或等面积 |
| epoch/执行域 | 必须定义原kernel边界及并发情况下的分区所有权、drain和缓存状态处理；是否允许明确限制执行域也要单独批准 | 在此之前不准入任何DTC性能行，不自动串行化或清空缓存 |

只批准容量算式不足以通过上述事项。即使以后批准A，也先做 [LEGAL_DOMAIN.md](LEGAL_DOMAIN.md) 的局部验证，格式/SM89、共享服务、baseline配对和A的启动authority仍独立有效。不能将原4080 baseline-only counterfactual当作native DTC性能验证。

工作量边界：A至少涉及Core `shader.cc/.h`、`gpu-cache.cc/.h`、`gpu-sim.cc`的配置、最大几何、每SM分区和清退接线，以及Framework的显式spec/严格collector和定向测试；现有状态可复用，但涉及未实现的epoch状态处理。B还需重订pool/Tag/progress并修复已复现反例。不给未经实现验证的工期承诺；任何后续实施应是独立Goal与source identity，本轮到可决策报告为止。
