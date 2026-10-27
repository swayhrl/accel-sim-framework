# Padding路由V2、原锁对象保活与198点增量结果

这是e85a23ac源码资格包的独立后续，不改其冻结成员或回执。B五源/47项QA、证书和策略均保持，只有原生CLI接入需兼容另一EP Goal新增的路由。

## 实际工程状态

第一次Main激活preflight安全拒绝：原生N/bin/native已由另一EP Goal从79ad变为89927e，新增EP_PERF_*及EP_FULL_PERF_NATIVE_ENTRY=1。Main没有覆盖、修改或中断这个EP任务，也没有附着padding。V2仅将已验证的1941字节padding prefix尾接当前89927e的完整4568字节；[48项隔离资格](route/CPU_ROUTE_QUALIFICATION.json)包括EP argv/env保持，实际native在资格前后仍89927e。真实部署必须再次核当前SHA，否则继续HOLD。此处V2尚未实际激活。

另发现旧R20 main已离开active stack，而L2 addon仍需原来的锁。已于23:25:09在原PID1498278/start977758783中仅强引用GC可找到的两个原BufferedIO对象：[实际ACK](lease_retention/ACTUAL_ACK.json)。原fd3/4、inode、FLOCK、owner完全不变，无open/dup/重新加锁/模型信号/预算变化。对应[9项隔离资格](lease_retention/CPU_QUALIFICATION.json)真实证明main返回后引用可保持既有文件对象，原对象若已关闭则拒绝，不会重建lease。这使现有唯一owner继续合法工作，不是重启旧Goal。

[独立最终审阅状态](independent_review/FINAL_REVIEW_STATE.json)、[真实只读post-padding facade影子](independent_review/AGING_FINAL_SHADOW.json)和接线构造补齐。E38在最终B665依赖下的资格已在先前e85包中提供。尚待实际padding短点工程验证和aging外层安装；实时资源门不能省略。

## 科学增量：22:59:15固定快照

[完整198点审阅](results_198/REVIEW.md)、[全35程序逐配置表与结构化数据](results_198/report.json)、[新增原因计数器证据](results_198/NEW_RAW_REASONS.json)。198=192新accepted+6合法P0引用；相比checkpoint04的172只扫描26个新增闭合raw，形成30条新增或新可比的配对，证据错误0。缺失字段保持None，原始失败/repair身份没有替代accepted数据。

重要新增DH自身加速（DH_P0/DH_variant）：convolutionSeparable F2561.422263/F1281.187151、2DCONV F2561.078012、ATAX F2561.017823；MVT E384/E768均0.994968，BICG M8为0.967226。全部正负例保留。F256可用20输入GM1.017563，但全部8变体的固定共同10输入GM0.998656；两者人口不同，不能据此晋升统一winner。非P0 CH尚缺，不能计算相对DTC优势改善或声称三负例已被解决。

这些source/CPU/只读影子均不能冒充真正模型试验。Core/FW/binary、DRAM850MHz、L2容量/映射及DTC固定；35普通输入/7未决、旧账本和v0.23保持。Goal仍在执行，不是阶段完成。
