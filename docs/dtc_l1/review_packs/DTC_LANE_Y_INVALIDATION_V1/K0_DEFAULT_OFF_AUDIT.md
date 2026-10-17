# K0 默认OFF审计

结论：`K0_NEW_OPTION_UNIMPLEMENTED`。不能把冻结行为的CPU回归称为新K0路径PASS。原174容器，独立Lane Y worktree与构建；完整模拟派发数为0。

只读锚点：Lane X Core `f8b34dd7a738caddf4f23dd417e34c0b63c206d9`；冻结Core `6fba0136f8465b59fe5858a950fa39efb265f654`。`SOURCE_AUDIT.json`独立比较Git对象：唯一变更是`docs/dtc_l1/LANE_X_OPTIN_INVALIDATION_V1_SCIENTIFIC_STOP.md`；所有非docs文件无差异。代码身份相同不等于两个构建产物SHA相同，更不是一次完整输入运行。

本Lane从发布Core建立detached独立只读源码worktree，CMake Release完整构建`libcudart.so`，并编译四个现有CPU测试。库/二进制/配置/编译命令SHA及每条命令退出码在`BUILD_AND_COMMAND_RECEIPTS.json`。另外把同一份独立探针分别绑定发布Core头文件与冻结Core Git对象导出的头文件，14个命名用例各跑一次，28次的观察状态/退出码严格配对一致。它们覆盖已有IO/OO生命周期及sector扩展，不包含尚不存在的K1 hook。

`options_cpu_probe.cc`链接本Lane新编译的真实Core库，调用真实`gpgpu_sim_config::reg_options()`、生产option parser和print；只创建配置上下文，不调用GPU init、kernel加载、模拟线程或cycle。显式限定`LD_LIBRARY_PATH`并核对`ldd`实际解析到本Lane库，避免系统CUDA同名`libcudart.so`替代。`EXPECTED_AND_OBSERVED.json.options`记录有效echo：

|输入|有效mode / finite_service / flush_l1|退出码|
|---|---|---|
|无参数|0 / 0 / 0|0|
|mode=2，flush_l1=1|2 / 0 / 1|0|
|mode=3，flush_l1=1，finite_service=1|3 / 1 / 1|0|
|未知负例选项|Unknown Option|1|
|`-gpgpu_dtc_l1_invalidate_on_source_event 0`|Unknown Option|1|
|`-gpgpu_dtc_l1_invalidate_on_source_event 1`|Unknown Option|1|

既有`finite_service`与`flush_l1`的默认0不是新失效开关。显式新选项OFF也无法进入可运行K0路径。无参数解析成功只证明当前发布版本的真实默认配置，不能冒充新K0。

对Lane AA的建议：当前不得启动K1。若后续Lane X实现无法证明OFF与冻结模型同义，Lane AA应在同一新Core上对K0/K1重跑**完整、相同输入**作严格配对；逐项固定Core/build/binary、完整有效配置、输入内容与顺序、parser和运行身份。旧A/T/U或冻结结果可保留为历史对照，不能替代新K0。即使未来CPU配对通过，也须单列未覆盖的完整运行差异与qualification。本Lane不派发这些模拟。
