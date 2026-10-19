# Preserved CPU engineering failures

原始记录均在新raw根，索引见`RAW_FILES_SHA256.tsv`。

- `authority-first.*`：最初12项真实CPU生命周期和4项纯身份负控通过；此后增加父先退出等覆盖，没有把最初范围宣称完整。
- `authority-second.stderr`：两个CPU测试套件同时申请自身独占锁，另一套被拒绝。改为顺序执行；没有放宽锁。
- `authority-third.stderr`：新父先退出重排适配器未区分嵌套git wait调用，栈定位报`KeyError('pid')`。修正测试适配器定位真实guard帧，原失败保留；生产归属规则未放宽。
- `authority-fourth.stderr`及该次OBSERVER：外部EP-L2新增离线锁缺少精确绑定，authority按原规则STOP。只读审查当前源码及独立Lane D授权后，在新包增加精确身份绑定并测试所有变异拒绝。未修改旧AG4绑定或收据。
- `authority-fifth.*`：最终14项生命周期及4项纯负控全部通过。
- `dispatch-first.*`/`dispatch-second.*`/`dispatch-final.*`：旧生产分派复现与新guard负控；后续扩展普通子进程、线程及root，最终6项通过。旧不安全ptrace操作由适配器在内核前拦截，没有向虚构/外部实例发信号。
- `mapping-final.stderr`及`mapping-first-result.json`：CPU回归子Python继承OSS `PYTHONHOME`，系统Python未能初始化。测试子命令加`-E`隔离Python环境变量，`mapping-second.*`全部8项通过；没有修改mapping解析器。

这些都是首次新性能之前的独立CPU工程迭代。本轮没有性能启动，未消耗或恢复任何性能预算；旧AG4模拟开始后的STOP没有被撤销。

根目录`closure-final.stderr`另保留终态收集器对新出现的DTC closure CPU脚本按未知执行权拒绝的收据。收集器随后改为将当前authority STOP原样发布，而非要求它PASS才能保存已完成的CPU资格；生产observer、未知控制器拒绝及所有资格条件未改变。这不授予外部脚本任何执行权。
