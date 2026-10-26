# 最小诊断计划与执行记录

决策：当前根因判断不需要新的完整应用，也不需要重复已经PASS的CPU模拟器fixture。本轮只执行下述离线验证。测试阅读、历史执行、本轮执行与待授权实验分开。

## 本轮实际执行：有界离线，PASS

本轮用户明确允许有界离线分析和独立诊断脚本。先核查远端资源：load约28，available RAM约238GB；`/root/data`为本地ext4，仅约34GB free、99%使用，另有多个计算进程。未停止或干扰它们。只运行单CPU、nice10、30s超时的小型Python读取，不加载simulator ELF、不碰GPU、不调用科研入口。

脚本：[audit_existing_evidence.py](audit_existing_evidence.py)。结果：[OFFLINE_CHECK_RESULT.json](OFFLINE_CHECK_RESULT.json)。最终验证wall5.852s、user5.778s、sys0.063s，exit0。首次仅聚合检查0.113s也通过；随后为补足raw复核而增加r5重解码（5.857s）；最后加入导入前工具SHA白名单与eligible way求和，复核5.852s通过。不存在自动科学重试。

```bash
timeout 30s nice -n 10 env PYTHONDONTWRITEBYTECODE=1 python3 \
  docs/ep_l2/operations/ep_tag_detach_rootcause_20261026_v1/audit_existing_evidence.py \
  --framework /root/data/ep_tag_rootcause_20261026_v1/worktree \
  --vector-result /root/data/ep_l2_main_vector_r5_20261023_v1/run/results/a6b61f77-2ff6-45ad-897c-df0812d01ae8 \
  --r5-tools /root/data/ep_l2_main_vector_r5_20261023_v1/sources/r5
```

输入只读，每个JSON上限16MiB、hash输入上限32MiB；只写审查目录中的输出。Python禁写外部pycache，未调用原有可写analyze.py/acceptance脚本。

执行内容：

- Vector raw SHA `1f5519151cb381fbc370591d65e7ad78691435d5955ad99fea8dcdf7ffab0f6a`、r5/r4/model terminal SHA逐项绑定接受点；runtime Core1093/main e511精确检查。
- 使用原r5 decoder重新读取整个Vector raw，Feed结果与SHA绑定的R5 terminal逐项相同；normalized全部scope数学复核通过。原固定old212 decoder没有重跑，传入的是已接受且SHA验证的old212终态；这是已有parser的复核，不是新独立parser或新科学接受。
- 独立求和head、16-way class、eligible、reason、route闭合，重建newTag/eligible/reuse真实联合；与既有projection及CSV一致。
- CFD/DWT仅对本地approved accepted projection重新求和和核对r5身份，**没有读取或重解码旧raw**。它们缺少的总联合维持NA。
- 本轮早先尝试用 `/usr/bin/time`，该工具不存在，未启动Python；随后改用bash内建time。本轮本地历史git blob读取触发partial-clone懒加载挂起，已停止读取并转GitHub精确commit。未以未读输出作证。

## 已有真实CPU执行：本轮只阅读证据

测试源码：[Core1093 test_detach_diagnostic.cc](https://github.com/swayhrl/gpgpu-sim/blob/1093d2629e3d6a9130ba25b9dd119b6f3e16c092/tests/ep_l2/test_detach_diagnostic.cc)。修正native fixture的第11行include路径不同，其余行对应；它修正GPU partition/stats ownership，不改变生产机制。

|控制|源码行|已有真实执行支持|不能扩大的结论|
|---|---|---|---|
|PRESSURE_ELIGIBLE|212–215|r5 corrected exit0，18replies/18lower、143cycles、drain1；detach后同line新handle，旧返回不把新payload置ready|只证明测试情形，不证明全部协议交错|
|RESPONSE_BACKPRESSURE|207–210|r4 actual exit0，detach1=retired1；真实ICNT队列满，旧detached返回仍live、pins1、sector0 ready；consumer恢复后drain|不是多sector乱序完整组合证明|
|PRESSURE_STICKY_REUSE|195–199|成功merge置reuse后，即使部分waiter退休也detach0|证明guard生效，不证明guard可去掉|
|PREVIEW_REPEAT|241–258|32次preview/snapshot，r4 ledger/r5 covered/joint rows不增；有最终semantic witness|未直接逐次比较全部模型canonical状态|
|TAGPRESSURE_CAPTURE_JOINT|222–236|真实16pending/16eligible；same-line HIT_RESERVED vs新TagFAIL，32快照不增数|合成压力不是应用性能机会|
|NATIVE_REQUESTER_RO_VICTIM|217–221|ALL_OFF/R4_ONLY/R5_ON三变体actual exit0，均120cycles、18replies、18lower、576bytes、drain1|Frontend拒绝而direct access能relieve再directory deny；不能把direct路径当Frontend接受|
|DETACH_THEN_LATER_DENIAL|259–263及相关subcontrol|历史测试展示detach后capacity拒绝|不证明常规preview会放行所有这种请求|

历史r4：Framework `7c2f830175f40e16651eab4a3cd3a7af73e9927b` 的
`docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1/native_r4_independent/INDEPENDENT_NATIVE_REVIEW.json`，
SHA256 `5e84c0784d635e7e6284f855bbfe4f63898818b4799894b3b0ef0ac6e6505c7a`。48次invocation、16类reference/OFF/ON，全部实际exit0。旧fixture有额外未打印owner导致GLOBAL非全closed，权威报告仅作有限fixture，不当应用资格。

历史r5 corrected：同一Framework提交，`approved_r5_joint_r1/native/COMPLETE_INDEPENDENT_NATIVE_SOURCE_SEMANTIC_REVIEW.json`（相对同review pack根），SHA256 `b3214410e77ddb18f5dcc1f7f8a9b91284089cac94456fd485ef4ff931bbfa8f`。15次唯一实际invocation全exit0，8个R5_ON、10独立epochs、42frames；FIXTURE_ONLY.patch保留，生产main/archive不变。这些是历史producer/native fixture结果，不升级为native epoch2完整应用接受。

NATIVE_REQUESTER_R5_ON raw：SHA `8b3cb970642bab3f6b106c0850ce61a52eb6b622cf395d7796fc351eafd06370`、42581B；三变体semantic digest均 `10550917095251637561`。RESPONSE_BACKPRESSURE_on raw：SHA `4ac70d0df11a9862a7ece1f6b1793c497a0ae95ac56b97bedd4a0373ec494634`、25627B。本轮阅读receipts，未宣称重新读取这些旧raw。

分项sector/bank证据：Core1093 `tests/ep_l2/test_payload_sector_lifetime.cc:33–48` 验证一个sector返回不清除另一个pending；`test_ro_bank_progress.cc` 的A2/A3/controls使用真实transactions/store/scheduler，但clock/Tag/packet facade边界保留。分项证明不自动组合。

## 可选追加CPU验证：NOT_EXECUTED

只为补正确性覆盖，不为把detach凑成非零。现有根因决定不依赖它们。

1. **单一组合case**：初始请求一次带两个sector，避免merge置reuse；16同setpending→17th新Tag触发detach→旧payload分sector乱序返回，期间ICNT满→同line新请求获得不同handle。逐步断言旧/新generation、required/issued/pending/ready、pin、descriptor、exact-once response和最终drain。一个sector返回时另一sector仍pending；旧返回从不改新Tag。
2. **preview状态强化**：同一physical cycle，canonical snapshot覆盖Tag/generation、事务/reuse、payload/masks/pins、descriptor、bank及queues；32次preview前后完全相等。复用现有fixture，不创建完整应用。

本轮未编写或执行这两个case。若后续确需执行，先核验现存fixture ELF/source/archive与当前权限；在独立目录单进程nice运行，建议30s wall、2GiB地址空间、16MiB输出上限。若需要重建大型simulator或无法确认身份，保留未执行；这些限额是计划，不是已经准入的命令。不得调用epoch2完整应用入口或GPU采集。

## 需要新的科学授权：NOT_SCHEDULED

真实压力窗口、Conv r5完整端点或同binary T-ON/OFF性能对，均需精确spec/cohort、fresh budget、native资格和资源准入；当前remaining0，不继承旧额度。本轮没有提出“立刻运行一项”的请求，因为没有一个已有证据支持的真实压力窗口。只有先识别满足实际TagFAIL且可改变判断的候选，再考虑有界科学验证。放松reuse或开放nonRO路径另外属于机制改版，见 [证明清单](CLAIM_BOUNDARY_AND_NEXT_DECISION.md)。
