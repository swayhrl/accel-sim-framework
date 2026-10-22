# convolutionSeparable：r4 F observer 独立诊断接受

E055_64617d96 为 CURRENT_ACCEPTED_DIAGNOSTIC_POINT，完整714547200条指令、291469周期、2个kernel、4条命令、64slice。真实native wait0/exit0，原中央COMPLETE_VALID及另一次只读raw/终态核对均通过。不是S/F配对。

实际RO事务371495，合并880056，成功detach 0；覆盖head原始Tag失败0，实际commit原始Tag失败0，relieve调用0。不同计数域不强制相等，不从跳过探测推断全局Tag充足。

- Zero detach in this new source/condition only; inspect conditional stage distributions rather than infer globally sufficient Tags. {"detach_success": 0}
- No all-reserved raw Tag outcome at covered/probed frontend heads. Upstream-skipped paths are unobserved, not global Tag sufficiency. {"raw_reservation_fail": 0, "observed_heads": 9307288, "probe_skipped": 1719574}

根因结论：EXACT_POINT_CAUSE_CLOSED，Actual productionTag probe never returned RESERVATION_FAIL; the source-required branch calling RO relieve was never entered, so detach was never attempted. RO transaction presence is separately measured; skippedfrontend rawpressure remainsNA andglobalTagabundance is notclaimed.

逐slice/物理kernel阶段、212项分布和checked/unobserved门见INDEPENDENT_TERMINAL_AND_CAUSE_REVIEW.json。物理阶段不是请求/被驱逐对象的因果kernel，跨阶段detach/retire差为NA，不作为独立存量。保留全部负结果与未知项，不回填旧main61日志。

原sameinput F公共cycles相等：True；公共RO字段相等：True。仅作复现描述，不形成跨binary S/F性能结论。原结果位置：/workspace/ep_l2_ms20261019_e_results/E055_64617d96。
