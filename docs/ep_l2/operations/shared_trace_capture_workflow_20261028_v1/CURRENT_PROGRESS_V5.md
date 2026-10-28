# V5：公共56/56与CPU流水恢复

本报告记录2026-10-28本轮实际完成和正在执行的工程范围。整个资产库Goal尚未完成，外部ChatGPT审稿未收到。

## 本轮已完成

- 公共SM89从48常规/48裁剪更新至56/56。新增8对先完成实际POST与精选完整CTA模拟器SMOKE，再将16对象逐成员source/receiver整SHA归档真164，绑定真实父COMMIT，按旧48逐值保留的CAS更新公共目录。
- 新裁剪共111个完整CTA、42,548条记录，按原CUDA线性CTA每40取1。小kernel至少保留一个CTA，实际比例因输入而异，不把全部资产标成2.5%。普通新增48,555,298逻辑字节，裁剪新增387,838。
- 模板沿原consumer82，其余7项沿实际C51，均为SMOKE_NOT_FULL。裁剪保留真实父契约引用，不虚构新的裁剪模型执行。
- 已核全部112公开对象的COMMIT/manifest元数据及声明成员stat。Main与DTC两个真实项目下，对新16对象执行show/path/verify，共96次真实wait0查询。本轮没有再完整回读正文；源KEEP，释放0。
- 常规CURRENT：008a80c0cb6a187b054632d96ced0d8df292ef1fde89e0271d92abc8385233c7；裁剪CURRENT：694aa1bddcd65c9487611520745b8844f88b38f2050d1143afdd9586de46b50f。

## 正在执行，不能计为完成

1. 普通GPU33项仍21已采/12剩余，当前simpleStreams保持运行，最近只读GPU利用率100%。这12项与161专项分别计数。
2. 大型streamcluster V11实际续传。复用1562份闭合Source证据共17,284,403,438B，仍保留本轮逐项当前receiver SHA及最终全receiver验收。FULL最终COMMIT、DERIVED COPY和公共57/57尚未闭合。
3. big3 CPU2后处理已恢复：asyncAPI/cudaCompressible复用已闭完整验证，仅补group；第三Sobol按原validate+group执行。新控制通过独立SSH stdin，不依赖NAS心跳。
4. Gaussian256 A003实际续跑：10,534,208记录/510kernel的完整扫描与观察按原SHA复用，303份已闭group先校当前整SHA再普通复制，只继续剩207组、BIND、最多4个完整CTA的SMOKE。未重采、未重扫全部记录、未重组303份。
5. A003仍受原3600秒窗口约束。当前I/O速率有到期前不能全闭合的风险；不热修改、不打断健康任务。若真实到期，先核owned/租约闭合，按实际部分结果另审有限续跑。
6. exact161正式完成仍7、剩154。新公开8项与161行无QID重合，不能相加。Gaussian两个文件输入、LUD256、scalarProd两size的下批候选已准备，尚未启动新GPU或写边界STOP。
7. captured21的实证差集为11已接受POST、3在big3队列、7尚未进入POST。先为5个小输入准备CPU3流水，两个约844MB的simpleMultiCopy另列，不凭文件大小推记录数。

## 修复与流程约束

### 祖先触限计数不能直接归为自己的OOM

Gaussian A002样本：自身约151MB/硬2GiB，可用61.46GB高于49.24GB需求，全部PSI及自身事件增量为0；失败仅来自无上限祖先的层级memory.events.max增加34/35。新私有CPU门把high/max触及次数作为遥测，仍严格检查实际min(high,max)头寸、物理余量、OOM/kill、压力、节点身份。Root独立14项边界验证通过。健康实例与其他项目registry未改。

### 封包目录与压缩流使用独立变量

首轮8项准备因压缩流变量覆盖目录变量，在checkpoint路径拼接时失败。仅改流变量与新attempt namespace，真实执行17记录变换、checkpoint及原封包函数验证后重试成功。旧失败与部分输出保留；没有为包装错误重跑POST或模型。

### 资格按实际证据范围记录

trace存在、格式验证、精选CTA SMOKE、全输入模型、数值/性能/科学资格分别记录。既有48+48消费者证据审计按每个witness与真实capture/profile绑定，旧c5证据不迁给82/C51，普通模型不自动变成裁剪模型。SM70全库Native正文恢复已按用户要求取消，已接受的611.55GB归档和125输入元数据成果保持。

## 精确证据快照
- [evidence_v5/E042_CPU2_NONOOM_LIMIT_TOUCH_RESOURCE_SOURCE_V9.py](evidence_v5/E042_CPU2_NONOOM_LIMIT_TOUCH_RESOURCE_SOURCE_V9.py) — SHA256 d8e709b53694ad92a33f28177b90b9e6e873d052bb38c0b66658d8e916cfa2d4，4988B。
- [evidence_v5/E043_ROOT14_NONOOM_AND_LIMIT_BOUNDARY_CASES_V9.json](evidence_v5/E043_ROOT14_NONOOM_AND_LIMIT_BOUNDARY_CASES_V9.json) — SHA256 3dbfeea6f31377b74820884f8c7a31367f340f679d04428a24456d678394b00a，2825B。
- [evidence_v5/E044_ROOT_PUBLIC56_ALL112_MAIN_DTC96_ACCEPTANCE.json](evidence_v5/E044_ROOT_PUBLIC56_ALL112_MAIN_DTC96_ACCEPTANCE.json) — SHA256 604e2a1d649141df6257fc1792f660e190e925329481df8ab045cf05fc714ac3，3379B。
- [evidence_v5/E045_MAIN_DTC_ACTUAL96_METADATA_CLI.json](evidence_v5/E045_MAIN_DTC_ACTUAL96_METADATA_CLI.json) — SHA256 12b18dc257c41f87ecba5f1d77e20934fe7bcbd03357bd8f5501abe283f15e41，123160B。
- [evidence_v5/E046_ROOT_G6_A003_COUNT303_REUSE_ADMISSION.json](evidence_v5/E046_ROOT_G6_A003_COUNT303_REUSE_ADMISSION.json) — SHA256 2dc23f967d6e3389067225f7c3d4e653b98c7a627a1116d81edf8c64f700443e，2370B。
- [evidence_v5/E047_ROOT_BIG3_GROUP_REUSE_CHANNEL_ADMISSION.json](evidence_v5/E047_ROOT_BIG3_GROUP_REUSE_CHANNEL_ADMISSION.json) — SHA256 3267caa31162aaa57d11264847a0e4629294edfb40055095ee72e5111b046c80，1920B。
- [evidence_v5/E048_ROOT_SC_SHARED_STDIN_SOURCE1562_ADMISSION.json](evidence_v5/E048_ROOT_SC_SHARED_STDIN_SOURCE1562_ADMISSION.json) — SHA256 15751a950da82f7e19d6e4bb4f2e26d00319f3dd26f5d5453e49bada0c176589，1940B。
