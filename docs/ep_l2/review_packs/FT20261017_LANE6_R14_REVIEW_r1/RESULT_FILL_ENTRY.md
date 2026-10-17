# Next event and executable paper intake

当前正式性能数据0，Fig2–4保持MEASUREMENTS PENDING。没有持续轮询器；本短Goal完成后停止。官方binary与当前科学接受到达时，由用户/协调窗口触发原Lane6新CONTINUE。

本revision的一次入口（不启动模拟或lease）：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/ep_l2/review_packs/FT20261017_LANE6_R14_REVIEW_r1/result_entry.py --repo /workspace/worktrees/accel-sim-ep-l2-ft20261016-lane6-v1 --output /tmp/epl2-lane6-new-event.json
```

输出路径必须全新。入口先读取Lane5准确remote HEAD，再有界fetch该commit且禁止 incidental submodule recursion；原生V2 bind_manifest验证完整identity/run-key、supersession proof，原r4 bridge最终检查remote ref仍相同。任意失败不出数值，不用缓存权威。不实例化registry或修改client/lease。

出现当前合格B16_BANKED/U_WB16配对后，在上述命令追加 `--adapter <exact-new-release-adapter.json>`。adapter沿原r3/r4 schema，必须从Lane5真实发布物绑定：qualification_publication/path、producer_publication/contract_path、native_pairs[].publication_commit/pair_repository_path，必要时result_root。完整例子只可由真实release产生；本轮不填假SHA、binary/key或借旧R0路径。current_acceptance由fresh context注入，不接受手写PASS。未知producer schema须新revision适配/验证，不削弱门槛。

原生consumer会重新检查qualification为Lane5 production-driven、证据文件hash、十一gate、producer/source/binary/mode一致；原RESULTS.csv/PAIR_RECEIPT/specs全身份，实际冻结binary/raw/config字节与trace索引摘要，normal exit、64 slice、exact-once/符号验证及descriptor/MSHR/WAD/lower/response终态退尽。随后匹配指令/口径计算该pair cycles比；发布前再查撤回与ref。No-current或失败行不计均值、不填0。

**本入口的native数值路径只适用1168-slot B16/U_WB16主配对。** 原bridge明确断言1168×64；不能自动支持WBUF8、TVD/RO、Ideal。后者分别要自己的准确预算、feature/oracle、qualification和consumer适配，不修改全局常数绕过。Ideal必须同R1.1 binary baseline，不能跨binary当分子。见FIGURE_READINESS逐panel缺口。

每个合格pair可在新论文revision立刻填Fig2并明示覆盖率；五对全接受才填五点geomean。Fig3使用同pair应用累计窗口与独立审计的native指标，缺列不能推0。Fig4不存在当前合格/完整可执行对照时继续保留图位。新撤回优先于旧PDF或资格证书；保留历史revision并重新生成受影响声明。

已实际运行一次新入口，current rows0、generation2、authority d5317bd25dd0d5debd5abed5d5cf6300e7bd6982，manifest eccaa5bd0f24849dc4ae1c63754785a1cba29eefe23103491013088088ced37a；不是未来R0.1数值正路径验收。
