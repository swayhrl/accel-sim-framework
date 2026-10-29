# V15 四份R2研究资产已完成公共交付

更新时点：2026-10-29T22:12:20.393987+08:00。四份保原工作集的repeat-only输入已完成原native QA、完整采集、F9／GROUP、限定ENTRY、裁剪、全SHA归档和公共发布。严格目录75份常规、75份裁剪，独立RAW7另列；统一发现也已实际切到75／RAW7，Root已验收Main／DTC14条读取命令。整个Goal仍未完成：最后审计发现旧R5按需物化入口依赖已退休authority和不存在的全对象ledger，新的单资产restore-one正在准备；全库Native正文回读保持取消。外部ChatGPT审稿未收到。

[完整证据引用表](FINAL_R2_PUBLIC75_EVIDENCE_REFS_V15.json)以全3对PUBLIC75总入口和aligned先前发布接受为主，绑定各层实际小proof，不复制scope、job原件或trace正文。

## 四份新资产的数据与裁剪

| 精确R2程序 | 完整kernel／GROUP | F9 records | 实际裁剪CTA | 实际裁剪records |
|---|---:|---:|---:|---:|
| alignedTypes | 24 | 60755776 | 48 | 1898880 |
| transpose | 24 | 18874368 | 2472 | 474624 |
| scan | 66 | 182048256 | 8366 | 4571088 |
| convolutionSeparable | 6 | 67903488 | 2076 | 1700106 |
| 合计完整数据 | 120 | 329581888 | — | — |

裁剪保留完整CTA并绑定实际parent；比例按每个实例计算，aligned为48／1536即3.125%，stride40不能一律写成2.5%。COPY已完成全成员receiver SHA及parent绑定，随后采用同NAS发布并保留所有旧目录行。旧私有路径消失是已记录的发布迁移，不能据此报数据丢失。

Root独立检查最终全部150对象metadata及成员stat；aligned发布对应Main／DTC12条实际命令，剩余三对对应36条，总48条均实际wait0并闭合。读路径与资格限于其真实精确版本，不跨binary、input或consumer迁移。

## 模型资格仍限单CTA入口

四项均是ENTRY_COMPLETE_CTA_RUNTIME_STARTUP_RETIREMENT_ONLY。aligned选8424条records、退休305408 source加auxiliary lane uops；scan为344／12544，transpose184／7168，卷积1188／56320，分别沿各RESULT口径。它们证明精确完整源CTA可进入模型并退休，不证明全feature、whole-input功能、所有配置、通用ISA或原生性能。裁剪继承parent ENTRY标签，不假称裁剪又跑过模型。

aligned原28CTA feature模型的2GiB OOM及未覆盖的60／63 witnesses仍保留。scan／卷积旧GROUP因ancestor资源事件结束，V5只复用原F9及54／5个已闭GROUP，补12／1个缺口；旧失败未洗成成功。保原空间和repeat2也不等于保住长期cache、稳态和计时统计。

## 资产范围与保留缺口

原33项按24对常规裁剪、7项RAW例外和2项默认不完整输入延期分别登记；这与新R2四对的身份及75／75对象数不是同一统计单位。完整RAW7已归档并可由两个项目读取，POST／裁剪及consumer缺口保持。两个工程small scan pilot的native QA和采集已完成，POST仍是明确gap；研究路线已采用保原工作集的R2，不把pilot写成已处理，也不杜撰用户点名豁免。

canonical专项仍8完成、153延期。SM70公共125输入已完成NAS访问，全Native正文回读已取消；巨默认RAW重POST和全161适配不再由旧Goal UI文字恢复硬门槛。源KEEP、释放0，科学资格、预算、242条历史与失败原件保持。

## 统一发现与剩余恢复入口

统一快照已发布并独立接受，SHA为51d1a45d1adde6b2b2c3e751d949879758f3a4e1d8508e3409961558008f41ee。旧125输入、242条历史、typed161完整图和原142个对象整行保留，另加入8个R2对象、RAW7及有效33项处置。历史as-of阶段图保持原样，当前处置看current_delivery_exceptions_and_additions。[统一目录及恢复边界](FINAL_UNIFIED75_AND_RESTORE_BOUNDARY_V15.json)。

metadata_only和full_library_activation:false不表示公共库不可读，也不授予全库写入或恢复资格。当前EP29／DTC35的64条trace入口均解析到164，说明Native消费者可读NAS；它们不能冒充Native物化验收。

旧R5默认materialize-small门控尚不可用。新恢复路径只面向Root明确选择的单资产、目标、字节预算与完整SHA；正在准备源码，尚未安装或实际恢复，不将其写成PASS。该修复不会重新启用全125正文回读，也不触碰既有实验缓存。旧C8与合成恢复证据仅按原范围保留。

本提交保存当前SOP、范围／缺口表、小证据与实际执行源码。精确远端HEAD、tree及文件读回由提交后的独立NAS回执记录；报告内容本身不构成Git发布或外审通过证明。V13及之前各版本保留其原时点。
