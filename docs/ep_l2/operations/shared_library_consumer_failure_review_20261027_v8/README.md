# 共享资产库 V8 退出完整性验收与历史失败核对

统一 Goal 保持 active，完整覆盖 SM70 的冻结125输入、RTX4080补齐与161行实际适配。当前共享目录仍为41常规和41裁剪；公共入口全范围恢复及兼容性验收尚未完成。

## 本轮实际闭合

### 真实解码器退出完整性

Root 完整阅读紧凑线程状态、格式层和解码适配器三份源，并从85份精确原件建立独立副本，重新运行179项解码、457项退出完整性、21项压缩资源和8项小资源检查，全部通过，原件末检未变。另做20项真实原生解码反例和正例：五配置均拒绝原先缺少EXIT线程的流；合法分歧退出可继续执行仍存活线程；三维8CTA、raw2、33线程尾warp完整覆盖通过，全部自有C++子进程自然退出0。

因此，精确V3只获得私有R6 CPU组件接线准入。它要求每个物理线程在EOF前退出，拒绝复活和重复退出；不更改原C++ decoder及配置，不把metadata分类当作完整SASS、硬件时序、数值或科研资格。Session不修改caller的RLIMIT；XZ内存不足是资源HOLD，不是ISA不支持。

准入回执为 ROOT_CONSUMER_V3_CPU_COMPONENT_ADMISSION_V1.json，SHA 939d0e7dcd514d4a1c4b3424645df9b5086cae2a375d8f4ddd3d404fdbfb3455。独立四组复放 SHA 0185ae8e14ccb467ea6dca471a8de48a884cc68e782f24808fd48636423e8624；Root新增20例 SHA 05d31e7ec66577af80b52f2ea7b737ca68bb0a910cdc29de073e5b5740084533。

### 历史失败与成功后继

242行历史QUEUE仍保留4条FAILED_RETAINED，不改失败历史。独立对照109原job、原失败留存和已提交归档后，其中3条输入范围已有合格普通及完整CTA裁剪后继，无需重复GPU采集。

| 原失败 | 已有成功后继 | 精确核对 |
|---|---|---|
| PolyBench 3MM A001 | 3MM A002_CPU_RESUME | 原job与归档TASK整个对象相等，manifest/COMMIT/CURRENT及裁剪parent join一致 |
| Parboil stencil c3e987 A001 | A002_CPU_ADOPT_V2 | 原job与归档TASK整个对象相等，原binary/argv/input及常规裁剪join一致 |
| FIRST_VECTOR55_IMPORT_V1 | CUDA_SAMPLES_DB3EEA_VECTORADD_4M_ADA7_55C6_V1 | 原失败留存EXECUTION、SOURCE_FULL_RECORD_VALIDATION、native.stdout与已提交成员逐字节相同；原capture rawSHA与成功manifest成员相同 |

Vector的核对不依赖现在可变的import脚本推测历史身份。旧留存部分本身没有因此得到资格；实际复用的是既有成功COMMIT。3MM/stencil两项的成员元数据已重新绑定至已提交manifest。剩余实际失败输入为SDK42 simpleTemplates 4d7f84996ec9，其binary SHA 24e15a483e3d1d8ec70dcdd6f8c601189148ee476db93e47c06e1162c1b55e47，仍需Epoch动态适配；其他simpleTemplates资产不能替代。

V2核对回执 SHA 0153ea8b55e3d8a28f0fd866fccf195aaaf20908587897ec6aa5c870d53a6253。历史失败数4与尚未补齐的失败输入数1必须分开统计；另外33个普通待采、161专项和已安排SDK/reduction窗口不因本核对减少。

### 后续普通验证器CPU并行

Root审阅完整adapter、shared_io、loader、原f9 validator和mother精确diff，并独立运行基础、29项矩阵、6项真实CLI测试。固定f9/f4校验函数语义保留；跨kernel共享context/stream/stats约束和声明顺序聚合保留；两个worker共用读速率预算并继承同一whole-job LOCAL_IO引用。

这仅是未来CPU组件资格，未更改当前streamcluster进程、任务队列或GPU入口。独立回执 SHA 0f405e95072a72e8e98cab6e86be274bd82cd16b44e9da4876d4bb5be572a030。正式新批次还需精确Root准入、同一grant原字节解析与fresh deadline复核、总内存/IO预算及自然边界；V2正在私有准备。单个巨大kernel不会因按kernel分工而获得双倍并行。

## 准入前发现的真实缺口

旧Epoch4独立CPU审查发现，昂贵metadata读取前保存的旧时间值可能让已过期runtime被接受。真实延迟2.276秒的反例返回时已过期1.292秒，且没有超过原5秒握手timeout。另有完整49-record闭包反例证明receiver只核握手bool、未完整join身份或原runtime字节；这些结果不表示实际live握手或外层固定manifest已被绕过。grouped trace完整重开有序记录检查能正确拒绝损坏流，未被削弱。

V5已补共享OFD和持锁生命周期、raw admission保存、fresh Popen时限检查，并完成109真ext4有限fixture；最后新增的完整握手join仍待全正反例重放，15次idle与首次30秒admission的完整正向也未闭合。因此V5冻结为HOLD，绝非GPU-ready。有限V6正在准备：慢静态/idle阶段完成后由唯一issuer首次发出短admission，不给过期grant续期；尚未生产部署或发行新GPU批准。现有健康SDK/reduction控制器不热换。

## 正式恢复流程仍需完成

R6候选把真实Native slot闭合读回的literal bytes直接交给persistent五配置解码器，以Native SHA和consumer EOF双证明决定验收及resume。缺consumer proof的旧Native ledger不能冒充完成。已存在public view仍链接原literal commandlist同字节文件；另列absolute-path元数据，不能伪称builder已经重写commandlist。fraction范围差异须精确derivation与排除证据，不能借别名覆盖。

候选已实际核对125输入、22,769唯一对象、25,149成员、972,603,859,656B角色图；这些是metadata核对，不是实际全体Native body恢复。完整proof缓存/五profile状态/真实C++进程的资源压力和父先退cleanup反例正在有限CPU资格中，最终新CodeID尚未Root验收。V3密集合成解码探针每配置20,001记录约0.65至0.69秒，五配置顺序约3.71秒；这是工具容量观察，不是实际125完成时间或GPU科研性能。正式并行度须以精确CPU/RAM/32全局窗口、64MiB slot、256MiB对象上限及原绝对deadline共同准入。

## 当前长任务与完成条件

本轮实际核对SM70监督1424444、driver1424449、唯一恢复1431348，RTX1376608、SDK1410582及reduction1501892/1501891的精确PID/start_ticks仍匹配。SM70仍缺目标COMMIT及同run EXACT_BATCH_COMPLETE；rchar增长和.writing文件不能支持阶段或完成率结论。109原validator849258/start_ticks361246237仍在执行，未热替换。

最终仍需SM70真实归档闭合、125输入全范围Native/consumer/跨项目验收、所有可行4080缺口与实际161专项适配、公共工具及适用模拟器兼容性、完整例外与最终远端回执。源KEEP、源释放0，科学历史/预算/资格不变。外部ChatGPT审稿尚未收到；整个Goal不标complete。

本目录SNAPSHOT_MANIFEST保存本轮精确小型源与回执SHA；大payload和运行日志继续存真164。此前V7保留原样。
