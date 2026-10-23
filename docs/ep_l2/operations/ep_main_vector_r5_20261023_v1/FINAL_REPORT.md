# Vector r5 原生验证结果

科学接受：EP_NATIVE_VECTOR_R5_DIAGNOSTIC_ACCEPTED。完整应用1次，无自动重试；独立诊断点，非S/F性能配对。

| 项目 | 已接受值 |
|---|---:|
| 模拟周期 | 75039 |
| 完整指令 | 56000000 |
| kernel / slice | 1 / 64 |
| 墙钟秒 | 1216.454 |
| RO事务 | 250118 |
| RO合并请求 | 749882 |
| 已接受RO请求/响应 | 1000000 / 1000000 |
| 实际生产TagFAIL | 0 |
| 实际relieve / detach / detached退休 | 0 / 0 / 0 |
| covered目标set最大RESERVED | 3 / 16 |
| 新Tag需求域最大RESERVED | 3 / 16 |
| covered新Tag需求head-cycle | 915784 |
| 其中all16 RESERVED | 0 |
| structural eligible head-cycle | 687311 |
| 新Tag需求与eligible的实际联合head-cycle | 2385 |

结果分类：TRIGGER_ABSENCE_IN_COVERED_AND_PRODUCTION_DOMAINS。

本点的结论严格限于源绑定的生产FT/RO调用域与已探测head-cycle。TVD等skipped域保持NA，不外推为零压力；存在RO对象、eligible或满VALID/MODIFIED occupancy均不自动构成不可替换Tag压力。head-cycle不是独立请求，物理phase不是requester/victim的kernel因果身份。

若本点为触发缺失，T的真实应用收益声明应收紧。Conv仍未运行，是否追加需下一项单独科学决策，本Goal不自动继续。即使观察到detach，也需同binary受控T-OFF验证才能识别独立性能收益。

实际source为Core1093/main e511；旧main61的S/F、原57/T0、失败/HOLD和已接受配对保持各自身份。没有重新编译或改动有限模型，也不主张SASS数值输出验证或硬件速度收益。全模型闭合、ROC1、64slice、固定212、新r5联合数学、完整真实进程退出已分别通过；具体SHA和证据见同目录JSON。

结果按COPY_ONLY归档真164及独立native Target恢复后，归档回执另行记录。源原件KEEP。


## 2026-10-24 完成、归档与恢复

完整应用一次自然退出，实际15625 CTA、56000000指令、1kernel/64slice、hardware drained；旧212与r5联合数学通过。原生help资格调用另记1次，未加载trace/执行kernel。非启动负控制及已消费请求再入拒绝均没有额外科学fork。

完整结果44普通文件、5目录，原始15679278B；PAX payload15769600B。单receiver、30MiB/s限流、128MiB chunk与暂存边界保留。关闭重开全SHA及两个独立native ext4目标恢复全部通过，uid/gid/mode/mtime_ns与文件集合亦闭合；不把174-new恢复写成native164执行。

源保持KEEP，释放0B。源码原件、旧main61、旧57/T0/失败/HOLD与迁移4次历史保持；当前native注册表仅追加本次请求及审计revision，已关闭且remaining0。本次原始SOURCE_MANIFEST是单项目根的相对路径命名空间，scientific_project由SCIENTIFIC_RESULT_IDENTITY.json明确为EP_L2。

归档SHA256：4042bd52a4dc360a26aeb2fa5d9c17dd30e9399bf5e15e7e14510d1e820be068。
真164：/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_ep_main_vector_r5_v1_results/EP_NATIVE_TAGPRESSURE_VECTOR_HOLDOUT_V1/33af7b058c2bcf331f57d8a801a814380e924dc9556b4bb063d95dd99443793e。

精确取回入口、全SHA、两个native Target及复原命令见RECOVERY_POINTER.json、TRUE164_ARCHIVE_RECEIPT.json、FINAL_VALIDATION.json。独立恢复验证只使用新bundle里的归档数据与校验工具，不要求旧174执行软件。

## 下一项科学决策

Vector的250118个RO事务与687311次structural-eligible head-cycle暴露，仍未达到不可替换Tag压力；真正的“新Tag需求且eligible”联合为2385次，也没有实际TagFAIL。这进一步支持收紧当前T应用收益的论文表述，不能把RO准入或eligible当作detach收益。TVDskip375000次的raw维度仍NA。

保留T的功能正确性/条件性机制解释，不声称真实workload独立性能收益。Conv保持未启动；是否值得追加Conv，或将下一轮资源优先用于W/V同背景控制与端到端吞吐，应另作明确科学决策。本Goal不启动后续条件。唯一当前研究待办继续维护在ep_main_native_takeover_20261023_v1/NEXT_SCIENTIFIC_DECISION.md。

母稿仍按用户既定EN-v22边界处理，未编辑母稿、未推广EN-v24、未伪造未提供稿件的表号映射。
