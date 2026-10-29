# V16 两架构按资产恢复与公共读取已验收

最终私有稿时点：2026-10-30T00:44:34.201323+08:00。V15已真实Git发布至514b024b113ac41fd61d509ee75b138714c6f238，统一发现51d1、严格75常规／75裁剪、独立RAW7及SM70公共125输入NAS访问均有Root接受。新增SM70与SM89按资产恢复后端现均已实际验证并公开入口；这是功能和限定范围接受，整个Goal仍由Root完成最终requirements审计及Git读回后再判断，本文不提前宣布全任务成功。

[实际小proof引用表](READ_RESTORE_ONE_EVIDENCE_REFS_V16.json)绑定source／Native SHA、I/O、公开pointer和两项目命令。原V16候选稿保持原时点，本稿只追加真实完成状态；旧source-only／pending字段不改写成历史已成功。

## 已执行的三个完整资产

| 架构与精确资产 | 完整成员 | payload字节 | source／Native写入／Native关闭重读各自字节 | metadata实际字节 |
|---|---:|---:|---:|---:|
| SM70 BlackScholes e99c1422 | 2 | 22319130 | 各22319130 | 13561846 |
| SM89 Gaussian64 ordinary | 163 | 1195761 | 各1195761 | 4850740 |
| SM89 Gaussian64 derived | 135 | 396298 | 各396298 | 4927616 |

SM70已恢复全部两个声明成员，包括22319003B的kernel-1.traceg和127B的kernelslist.g；不是只做小索引样本。SM89合计298成员、1592059B，ordinary与derived分别使用新Root精确scope及新Native target、AS512MiB，真实wait0和owned闭合，source／member与Native关闭重开SHA均匹配。派生parent payload读取／复制为0，parent COMMIT／manifest及所需NAS依赖引用保留。

SM70保持已记录的numeric成员属性，新target根仍是新目录。SM89属性明确为新Root uid0／gid0／只读0444／Root mtime，未声称历史capture属性已知或已保留。一个SM70资产与一对SM89样本都不能标成125输入或75对全库物化；只验证了各自后端声明范围及这些实际样本。

## 两个公共gateway

- SM70：/root/workspace/assets/traces/tools/trace-assets-restore-one-sm70，实际代码8b5538991c9f8f7dab7c9e253da805793efb4f20499e7927ba85b4c74c500cc8，20168B。
- SM89：/root/workspace/assets/traces/tools/trace-assets-restore-one-sm89，实际代码d2c640b0e8f38e2f507ce70218c2d590fbbeaeb3357212b878f2c5914c510788，24348B。

CURRENT_SM70_RESTORE_ONE.json和CURRENT_SM89_RESTORE_ONE.json分别绑定代码版本和实际接受。Main／DTC对SM70各执行help、inspect共4条；对SM89各执行help、ordinary inspect、derived inspect共6条，合计10条实际wait0、owner闭合、body读取0。inspect和真实restore是不同证据，不能互相替代。

global activation=false保留无全库写入／批量restore授权的含义，不等于公共资产不可访问。EP／DTC64路径解析到NAS不冒充Native ext4物化。旧bulk、R5以及固定C8工程capsule不作为新通用恢复的替代权限或覆盖证据。

## 历史metadata兼容保持原件

SM89实际源码独审27项检查，并读取当前150对象约7.57MB metadata census，覆盖观察到的3种COMMIT与11种manifest schema值或None。对legacy缺失的可选字段和parent关系作显式验证，不补造历史PARENT文件、不重编码原manifest后伪称原SHA。只有声明过的4个时间戳字段可按typed finite语义比较；全keyset、其余语义及不可变target rawSHA仍严格绑定。

这些metadata覆盖事实不等于150对象已全恢复。实际ordinary／derived样本、旧C8固定capsule和SM70 chunk布局分别说明，不能跨架构或layout授予资格。

## 保持的范围与最后发布步骤

严格75／75、RAW7与SM70125不因新增本地副本增加；canonical8／153延期、原33的24对常规裁剪／7项RAW例外／2项大默认延期、大RAW重POST和两个工程pilot POST gap保持。保原工作集R2替代pilot的研究路线，但不把pilot写成已处理或用户点名豁免。全Native SM70正文回读继续取消，旧Goal UI不复活该门槛。

全部资产工程body进程均已闭合，本稿没有新GPU、模拟或科学／性能资格。源KEEP、释放0，原预算、科学例外和历史保持；外部ChatGPT审稿未收到。Root仍应执行最终requirements清单审计，把本稿与两份实际后端原bytes快照统一提交Git并读回，之后才作Goal完成判断。

## 最终范围总账与证据判定

[当前范围／数量瘦投影](FINAL_DELIVERY_SCOPE_SUMMARY_V16.json)、[Root逐要求预提交审计](EVIDENCE_V16/ROOT_PRE_GIT_REQUIREMENTS_AUDIT.json)和[有效用户范围修订](EVIDENCE_V16/EFFECTIVE_USER_SCOPE.json)把旧Goal UI中已取消的全库正文回读与161硬门槛排除，保留其余工程要求。真实完整台账在公共catalog/CURRENT_DELIVERY_SCOPE_LEDGER.json，源527710B原件及SHA另有引用，未把全表塞进Git。

SM70路径记录为100无fraction标签和25fraction/trim路径，不把无标签当完整应用采集证书。SM89对象按显示归并为CUDA SDK/Samples96、Rodinia32、Parboil18、PolyBench/GPU4；这是150个普通/裁剪对象而非150个程序或完整测试集覆盖。8个R2原始投影缺程序/套件标签，最终台账由冻结任务显式补充display metadata，原ASSET及51d1快照不变；上游suite修订未知不从CUDA编译器版本推断。

保护工具复核发现DTC bin/native由其他已登记研究路线演进至46c69a，旧其余三个pin保持；不能写成4/4旧pin未变。本资产工程没有修改该科学router，也不回滚外部已授权变更或据此增加科学预算。实际原件和Root最终审计保存在NAS；本文不以自己的存在替代提交后的精确Git ref/tree/file读回。
