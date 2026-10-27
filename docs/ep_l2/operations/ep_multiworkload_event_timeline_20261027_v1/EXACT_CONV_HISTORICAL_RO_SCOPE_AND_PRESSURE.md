# Exact Conv3072 historical RO scope and pressure

**PROVEN：并非RO资格为零，也并非旧F未触发RO事务。** 对本次strong identity438eefd...的完整两kernel输入，既有whole-commandlist/128B/canonical-VA证书覆盖294,912行；旧main61 F E009实际RO admit1,251,551、事务371,495、merge880,056、detach0。静态证书与实际RO准入两项均为正。不能把当前冻结S未带RO资格解释成输入没有可认证RO。

精确匹配：旧F input_audit和D/C证书引用的kernel1 SHA9678e314.../4,072,647,057B、kernel2 SHA1c4c91bd.../2,772,248,484B与当前V2逐成员相同；完整104B commandlist SHAab229081...也相同（保留68B系数初始化、37,748,736B输入初始化和两个有序kernel）。旧EP复合hash620f80...与新strong438eefd...是不同身份编码，靠完整成员/命令匹配关联，不把两个hash直接当相同。

原manifest SHA1cb3bc004fa7824e2e9eb3b1da991b8114fb588eae8e87cf92e124996b7bd425，ranges SHAa8dfd6d20ef62f959bd7908abf76b58434039ae63e611059c490a8c5c177e80e；本地副本为GitHub原字节，67B CSV的CRLF保留。范围0x7f7590000000..0x7f75923fff80（inclusive行基址）恰294,912×128=37,748,736B；覆盖11,698,176个read-lane引用，另294,912条同线store行排除。epoch是whole_commandlist，不是逐kernel替代；后续HtoD排除为空，初始复制需在epoch激活前drain。证书仍依赖可见完整agents、无外部写者/隐藏VA别名/MMIO、前epoch写回和copy drain等模型假设，不证明数值SASS或物理别名不存在。

旧F E009是Core d010/Framework9dd/main61 SHA61aad385...，E2通过显式离线decoder终态重验接受同一旧raw，原失败回执保留，没有重启。精确GitHub7c2f830...的完整587,728B状态文件重新核SHA=f7abf59d...与takeover索引相同。64slice只汇总一次：oracle candidates1,386,184、acceptedRO1,251,551、transactions371,495、merges880,056、responses1,251,551、lowersectors1,179,774、detach0；admit=transaction+merge。旧F E009、T-OFF E025和M-OFF E026均291469cycles，说明旧谱系控制差值0，不说明RO事务0。旧16way的Tag-set-full观察为0；不补写r5/current生产计数。

当前Main/B已证的32set8way/Core78f正式S有previewTagRF42,717及联合pressure_frontend_denied42,717，actualft_access probeFAIL0是preview.line_available=false提前拒绝；这是现实Tag-full需求，T仍N_A。历史64set16way F不能与当前S配对，也不能把RO覆盖比例乘42,717推断eligible共现。当前相同set/时间的认证RO owner、missing-sector、reuse_seen、真实relief联合及F后续收益全部UNKNOWN；F本身会改变事务、MSHR/TVD和Tag寿命背景。

**决定边界：Conv是有现有正证书及历史RO生产准入的下一轮资格审查候选，优先于把问题归为无压力；不在本任务将冻结S改F、执行CPUloader、申请或启动新模型。** 新Core/新cohort的manifest/ranges精确重绑、真实loader与协议资格及任何F启动仍需Main独立流程和授权。本次仅小证书/报告/元数据，0Trace正文/DB/旧raw扫描、0模型/loader/预算/共享写。

来源：D原证书精确commit ca1ca06bd3e9384298b18bba5dbd68a8d9d8295b，path docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d/ro_input_evidence/convolutionSeparable_r1/{manifest.json,certified_ranges.csv}；C复核ef6d9127eb4882229efc561d832a5985780cea60，path docs/ep_l2/codex_handoff/mechanism_study_2026_10_19_v1/c/input_review_convolution_r1/D_ORACLE_REVIEW.json，SHA47ae3eaa...；旧F状态7c2f830175f40e16651eab4a3cd3a7af73e9927b/path docs/ep_l2/review_packs/MS20261020_E2_MAIN61_TERMINAL_COMPAT_r1/F_REVALIDATED_RUN_STATUS.json，Gitblobce42c3aa...。完整SHA、链接和逐成员列表见JSON/证据索引。
