# 供 EP-L2 Main 消费：DTC Native 承诺变化回执

固定 EP 来源：`79582eac99a308671ccd8542d52b2b62a53e5587`。DTC owner 于 2026-11-09 16:17:44 UTC 按共享 Native `REGISTRY_UPDATE.lock` 和 epoch/SHA 事务，正式将五条已归档恢复请求的结果增长与恢复窗口承诺降到每条 268,435,456 B metadata 界：NON_TAG_REMAINING28 释放 4,294,967,296 B；PHYS768_FIRST4 释放 536,870,912 B；CODESIGN16_LAYOUT_R1 释放 2,415,919,104 B；PHYSICAL_PIB16 释放 2,415,919,104 B；STAGE_IIA_FIRST16 释放 2,415,919,104 B。**合计释放准入承诺 12,079,595,520 B，实际物理磁盘释放 0 B。** DTC 十项新保证合计 **8,380,228,658 B**，其余五项占额未变；所有 Source KEEP、负例、消费记录与其他 owner 字段未变。

registry SHA `c884c5afec814b6a8ab45bbc40c5d6eda4d275f9bca43a51ac8733c294efd3c8` → `99d308561466e45470456121c3a24dd51ace29ab6e9f7718283f0960cd493592`；current epoch SHA `61880c3c289e3fed982a4ced8514d2bb9981b3e747a00febed4994961b2c2665` → `4b81fa564096db462d58cb2a1717f3c5e1f9e6adadea488c132af923fbb12024`，epoch=2、预算 89→89。owner 事务 intent SHA `6f03c570c9395a3b18c6698a3a89c47af7ce03db41e4aa18d02a319a36b9e1d5`，COMMITTED 回执 SHA `3e8486af8b108c1d0c8393b54aa67153536b7c4c1a42df1b5eac56ccb2ffbf9f`；Native 原路 `/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/dtc_owner_closeout_v1/`。其他 67 条 request 和 registry 顶层字段均逐字段不变。

16:20:25 UTC **只读** EP 适配器回读新 SHA，GEMM/Stencil 的 foreign remaining writes 分别为 **8,650,761,266 / 8,717,870,130 B**，无 metadata error、EP 消费 0。含原两族 carrier 与有效 **5 GiB** 底线的无 claim 共同诊断需求为 **14,357,111,858 B**；同期 Native 可用 **18,526,584,832 B**，账面裕量 **4,169,472,974 B**。这只是瞬时账面诊断，**不代表 GEMM EXT0/1/2 或 Stencil EXT0/2 已获逐点准入**；RAM 和 Native 资源均须 EP 按原合同重新采样。DTC 未启动 EP 模型，也未创建 dispatcher。

仍保留 V100 72 未消费预算相关保证、MLP 一个未决 generation、Oracle initial8 的 13 条原池 claims，以及五条 metadata 界。十项具体金额、SHA 与证明见同包 `OWNER_CLOSEOUT_LEDGER.json`、`REPORT.md`、`LIVE_EVIDENCE.json`。由用户转交本回执；DTC 不修改 EP-L2 `CONTEXT.md`。
