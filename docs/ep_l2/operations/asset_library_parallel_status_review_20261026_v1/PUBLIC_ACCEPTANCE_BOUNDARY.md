# 公共验收的实际代码边界（尚未执行生产）

## 代码定位

冻结副本：[verification_stages.py](code/public_suite_not_activated/verification_stages.py) 的cross、restore、finish；[runtime.py](code/public_suite_not_activated/runtime.py) 的validate_cross_reports、restore_object、materialize_object。原CODE_MANIFEST同时提交，副本未改字节。

## 三个cwd的检查不重复全库fresh SHA

cross逐cwd调用list、verify --all。validate_cross_reports明确要求：

- PASS_BOUND_METADATA_ACCESS_NOT_FRESH_SHA_V3；
- fresh_all_SHA_this_call为false；
- 全125资产/精确成员集合与绑定一致；
- 每成员full_sha_recomputed、fresh_body_sha_verified均为false。

三个cwd分别完整materialize一个≤32MiB小输入；父进程再重开全SHA。另独立核全部公共视图和commandlist字节、顺序、SHA。不能把这部分称为三次完整trace正文重读，也不能反过来把它称为全量Native恢复已经完成。

## 独立全逻辑对象Native窗口验收

restore遍历全部22,769个bindings，以window_max=64MiB对每个对象调用restore_object。该函数完整读Source、累计Source SHA，写Native窗口，关闭后完整回读并累计Native SHA；要求完整EOF及两者SHA等于对象SHA。所有对象完成后，finish_receipt核对972,603,859,656逻辑字节及22,769对象。

Native窗口并非“只抽前64MiB”。它按offset连续覆盖整对象；若某对象数百GB，也必须覆盖其所有窗口。全部输入的重复成员按对象去重，一套精确context约束的已完成回执可以复用，返回值明确不是本次fresh重读。

证明经物理/逻辑双SHA和gzip CRC绑定到公共CAS与fsync ledger，才能按工具规定清掉自身临时窗口。Source原件、近期缓存及其它项目文件没有清理授权继承。

此阶段证明所有逻辑字节曾经过Native窗口写入与关闭回读；不证明整对象或整套输入曾同时完整驻留在本地，也不证明所有大文件的原数值uid/gid/mtime已在Native重建。源绑定元数据的校验和小完整物化另有适用范围。

## 尚未跨过的门槛

当前生产验收尚未启动。V12R2仅完成精确NAS-only归档续跑的Root准入；其COMMIT与EXACT_BATCH_COMPLETE尚缺。旧公共模板不能未经重新绑定就自动继承新engine SHA、Source inode别名资格和新完成回执。

需独立Root确认最终Source2闭合、12项或更新后的实际源码pins、public catalog/overlay、protected-after及新spec，再进行安装和激活。当前Goal UI仍暂停，报告不能声称全库验收完成或自动恢复Goal。

## 复用与工期应怎样审

已有归档Source和Target全SHA可以作为绑定历史证据，三个cwd的metadata访问检查已经按此复用。窗口恢复则是新Native Target的实际字节路径，现有NAS归档SHA不能伪装成本地写入回读证明。

若希望进一步缩短工期，先明确究竟改变哪项证明、哪些对象已有相同catalog/binding/profile/context的有效Native回执，以及替代证据是否覆盖同一目标。应保留逐项fresh/非fresh区分，更新冻结spec与Root批准后再执行，不能事后把抽样或历史NAS证明改名为全量Native验收。

按约30MiB/s的聚合计量预算，读Source、写Native、回读Native三类I/O合计约2.92TB，理论下限约25.8小时。这个三倍不是三个项目cwd重复刷三遍全库；元数据、有限窗口关闭、SHA、压力降速会增加耗时。此前26–78小时估计尚不是经全规模生产实测的保证。
