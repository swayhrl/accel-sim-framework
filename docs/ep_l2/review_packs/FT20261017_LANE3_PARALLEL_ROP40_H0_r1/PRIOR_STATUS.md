# Lane 3 r16 — A2/A3分别修复，源码绑定C++反例实际闭合

状态 `A2_A3_SOURCE_BOUND_CPP_VERIFIED_PRODUCTION19_PENDING`。用户授权一次新的短时CONTINUE Goal，完整读取协调92de53a63616f9fcc53f2058ad975c3c8f90b13c及此前r15源码反例/复现说明；原项目、分支和r14 native ownership修复保留。

准确Core候选 **30c2920a3754bdaae09511f93d91873959c09f15**；A2独立修复 **47fa210cec52643e969ad3118eef63c58d5aef0f**，A3独立修复 **85e625e78df08124e53e9d8a9e500ee117d7ff96**。Framework有界runner源码以SOURCE_IDENTITY记录的ea2a38c46完整SHA为准。源码仍在Lane3隔离branch；未合并Lane1主线/公共R2，也未rebase成已资格版本。

实际C++11/UBSan执行：4次顺序小编译、18次进程调用。C8/C16下，旧3f源码A2分别exit21、A3分别exit22；只修A2时A2 PASS/A3仍exit22；只修A3时A2仍exit21/A3 PASS；两项均修复时全部PASS。共8次明确非零反例、10次零退出（含最终2次controls），旧失败日志/二进制完整保留。比较用A2/A3测试函数体在四个variant中哈希一致；最终control仅额外扩展generation复用/错误physical-cycle拒绝。

A2使用role延后转换协议：last fill只更新Tag可见sector，Payload仍RO且pinned；最后requester真实commit、无未完成sector后才unpin并转RESIDENT。A3复用已有reply.transaction保留denied候选，selected仅表示真实Bank grant；跨ICNT背压重新获取RAM read，commit后清身份，且既有RO pending优先于后来出现的native response，避免再把授权park住。公共Bank arbiter/ABI、metadata字段数、D512、payload容量和Bank数均未改；RO-OFF响应tail与r14所有权/host guard源码不变。

最终controls实际检查：1op/bank/physical-cycle、同Bank旧RO/后WB/下一RO顺序公平、3cycle ICNT full、grant后未enqueue必须重读、partial fill、request exact-once、descriptor与pending token归零、pin保持至retirement、Payload/Tag stale generation拒绝与真实slot复用、错误physical cycle不消费grant。测试使用真实store/transactions/store-port/MSHR实现和原样提取的runtime/scheduler方法；时钟/Tag/native-ready/packet外壳为明确facade，不是完整cache/partition/DRAM生产模拟。不能把这些实际小C++执行称为19项生产PASS。

资源：四次中央Lane3 lease均1CPU/2GiB且已RELEASED；编译耗时2.72/2.73/2.84/2.73秒，峰值<=290816KiB。未调用正式build入口、未启动sim/应用/扫描/waiter，未改变50GiB workspace、64GiB RAM及共享配额；额外保留Lane1至少4CPU/8GiB envelope。首次过严courtesy预检因Lane1 lease让行，0编译/0 lease；之后在合法剩余额度内完成小测试。实际results解析到Share，后续variant也严格检查Share40GiB+2GiB；baseline只有workspace/registry前检，Share46996332544B是紧随其后的实测，未冒充baseline前检读数。所有真实receipt/限额/输出盘身份保留。

已消费Lane1生产088146/e424的发布事实；它只有common U_WB producer资格上下文，不含已资格RO。Lane5的A1独立资格HOLD保持；RO不阻塞其主线。五个冻结whole-commandlist oracle无读取body、改写、trace重抓或重新认证；旧R0/R1撤回及旧213个Lane3 pack文件保留。

新pack `docs/ep_l2/review_packs/FT20261017_LANE3_REVIEW_R16_A2_A3_r1` 含分项A2/A3 RECEIPT、实际四组合矩阵、旧失败日志、源码/方法/依赖/binary SHA、独立补丁及公共delta审查。gpu-cache.h/arbiter无公共delta；仅RO生命周期及RO-gated response调度变更供Lane1评估。完整19项、真正cache/partition A2/A3时序、官方最终R2集成和Lane5独立科学资格仍NOT_RUN/PENDING；无RO正式binary/性能结果。短Goal在push/readback后结束，等待下一正式事件CONTINUE。
