# 最新增量：OLMoE多输入采集交付与独立分析安排

日期：2026-09-28。本增量晚于LATEST_UPDATE.md中的Lane8几何审查与Lane7尚在采集的状态；不改写原始实验。与原70条总账、EXP06合并后，本次新增EXP07，合计72条逻辑工作记录，不是72次独立试验。

## 1. 交付状态

109/Lane7完成OLMoE多输入路由采集。远端branch `hrl/c16-olmoe-routing-provenance-multiround-109-v1`，scientific commit `35bc117a961ad55114f9d75752beb29f6acadc59`，final commit `27b923db5922e2f986d2f9e815050bdbad0c3bd2`，tree `782a2b2b43d7cd96579f7b10d095de314f492945`。相对前一项split-K结果`0e88faa...`前进2 commits；已核远端分支与final commit一致。

六session各64步，一次model load及一次GPU锁；四个捕获session×16层×64步=4096条routing记录。T0/T1/T2输出token序列一致，只支持该TEXT控制范围内未观察到hook改变输出，不证明所有输入或所有内部状态完全不变。

实际runtime为Python3.12.3、torch2.7.1+cu126、transformers4.55.0、BF16、SDPA、DynamicCache；完整runner已归档。本轮Git源码审查显示每session独立prefill、step间复用KV并检查长度每次加1、greedy与EOS处理明确。

164持久化：
- 科学RUN_ID `C16R_olmoe-routing-provenance-multiround-v1_20260928T092536Z_c91846a955f5`；
- durable RUN_ID `C16R_olmoe-1b-7b-0125-instruct_routing-provenance-multiround_prefill2048-decode64_passive-hooks_all-layers_20260928T092536Z_c91846a955f5`；
- manifest SHA `07ce90441cecfc29d2669c306084913e8b704234cd4e065c403a01fc4487ac9b`；
- catalog SHA `0007fd2f1ed22449ae683bb4644acf914dd921b51854e8a5566eb731d6f3784e`；
- ACK SHA `1f2740893326c192d645ac050a82b648e97f6bd9db1004b903e7f8d9b2d37901`。

正式原始数据按durable RUN_ID读取；初次未被接收的partial已隔离，不能作为第二个实验或替代raw。

## 2. 当前数据实际支持到哪里

| 输入 | Layer1主要routing lag | lag11观察 | 当前解释 |
|---|---:|---|---|
| TEXT | 22 | Jaccard0.938784，shuffle p950.300479；16层均超线 | 强11步/22步重复结构；22是11的倍数，不是独立发现 |
| CODE | 16 | 未超lag11参照 | 显著的描述性峰在另一间隔，与模板token结构相符 |
| STRUCTURED | 14 | 未超lag11参照 | 描述性峰随输入改变 |
| PROSE | 1 | Jaccard0.171341，p950.164213；仅高约0.00713；3层超线且0层以11为主峰 | 弱超线不应等同于TEXT的强周期，不足以直接证明共同固定周期 |

表中数值来自producer已提交结果，尚未由本轮ChatGPT从164 raw独立重算。原始prompt的最大lag也必须结合equality rate：PROSE full-prompt最高仅约0.0284，不能因存在最大值就称PROSE本身有明显周期。

旧V34 Layer1前32步：unordered top-k32/32、ordered30/32、output token32/32；router input/logits SHA均未相等。可以说原专家集合与输出序列在明确的新runner中得到复现，不能说原内部状态或旧runner逐bit复现。

## 3. 不直接接受producer较强标题的原因

原协调文件明确p05/p95只是描述性置换区间。当前analysis.py将“TEXT Layer1 lag11过p95，且任一替代输入Layer1 lag11也过p95”直接映射成跨输入分类。机器条件成立与证明共同强周期是两回事。

本轮保留producer JSON不改写，项目层只接受其为已交付、可进入独立消费的采集结果；“不同输入族都稳定出现相同11步周期”暂不作为已接受科学结论。

不能把原本固定Layer1/lag11的主比较说成从2048项事后挑选；但额外16层×32lag×4输入的完整谱是2048个相关观察点，逐点超p95和“有几层过线”均需说明选择范围、相关性与效应大小。不同层不等于独立生成重复。

## 4. 一轮174-new独立consumer

为174-new复用Lane6准备了一个连续CPU任务：核全部raw/身份/生成连续性，独立重算原指标与原分类，再做明确标为结果可见后补充的效应强度、同序列前后稳定性、多项筛查及input-token条件化检查。不重新运行GPU，不将附加检查包装成预注册成功标准。

coordination：
- branch `hrl/c16-olmoe-multiround-consumer-174new-v1-coordination`；
- commit `fa0564f7025d62c4d466ce879a0566c404b8f4cb`；
- file `docs/vm_tlb/chatgpt_handoff/c16/olmoe_multiround_consumer_v1/LANE6_174NEW_INDEPENDENT_CONSUMER.md`。

状态：handoff已发布、待用户下发；不能写成consumer已运行。

109/Lane7本项结束并释放锁。下一项split-K访存状态任务此前用户明确未下发；本次不代为启动。它与174-new独立consumer没有GPU资源冲突，可以在用户下发后并行。Lane4不动，Lane8另一个KV/backend任务不被本consumer占用。

## 5. 来源S44与审查深度

所有路径相对于`swayhrl/accel-sim-framework@27b923db5922e2f986d2f9e815050bdbad0c3bd2`。
- `docs/vm_tlb/review_packs/C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1/FINAL_DECISION.json`，blob `91b1ff20050974df823f89e75b3f21ecdb500447`；
- 同目录`SOURCE_AUTHORITY.json`，blob `8a01cac30bdb1fef5125357dd52a6bcabc14c930`；
- 同目录`GENERATION_CONTRACT.json`，blob `c75c683f3b45cb1bd4fd89d0b477e08f6a33b8b9`；
- 同目录`RAW_LOG_INDEX.tsv`，blob `08cf730660be971b8ba6cd6c62744f5ec4f5d0bb`；
- 同目录`NEXT_174_CONSUMER_CONTRACT.md`，blob `5135f510977d65af56775813dd43fdb2e8243dfe`；
- `util/vm_tlb/c16/olmoe_routing_provenance_runner.py`，blob `3ffb0f0051edc3d7ba5c0cd2f2185ce6ab80cbb6`；
- 已读`olmoe_routing_provenance_analyze.py`的置换、分类及历史对照代码；
- 原coordination `378df585...`中原采集handoff第9、10节。

ChatGPT核的是远端提交、来源、关键代码与回执，没有SSH访问节点、没有重算4096条raw、没有声称重做所有SHA校验。后续独立consumer完成后再追加最终接受范围。本增量不授权新GPU采集、缓存机制或模拟器长跑。
