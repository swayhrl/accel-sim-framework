# K0 CPU 默认OFF等价

Y2绑定行为Core `c0a5e2c31e407c57e3a4af3ce529c921e8059a05`，冻结Core `6fba0136f8465b59fe5858a950fa39efb265f654`。V1 `b673d046b38f61159b5db67a477d58d1afa4662f`仍是正确的历史FAIL_CLOSED，未覆盖、未重跑原Goal。本包不把旧STOP Core当K1。

生产注册名为`-gpgpu_dtc_l1_invalidate_on_source_event`，`OPT_BOOL`，默认`0`。`options_cpu_probe.cc`链接Y2独立构建的新`libcudart.so`，调用真实`gpgpu_sim_config::reg_options()`和生产parser/print。使用限定的`LD_LIBRARY_PATH`，并实际检查`ldd`绑定；不以系统CUDA同名库代替。

|生产解析输入|mode / 新flag / finite_service|结果|
|---|---|---|
|省略全部选项|0 / 0 / 0|退出0|
|OO + finite=1，省略新flag|3 / 0 / 1|退出0|
|OO + finite=1，新flag=0|3 / 0 / 1|退出0|
|OO + finite=1，新flag=1|3 / 1 / 1|退出0|
|OO + finite=0，新flag=1|3 / 1 / 0|退出0|
|未知选项负例|生产Unknown Option拒绝|退出1|

`k0_default`、`k0_explicit_off`在CPU夹具中通过**真实生产新flag注册/解析**设置OFF，运行逐字提取的新source idle条件、cluster/SM传递及LDST分支。四个CPU SM上下文均有可查询retained Tag；ordinary请求发生后OO映射不变，source observer请求数0。`k0_frozen`执行从冻结Git对象提取的原LDST ordinary invalidate函数体，只有方法名改为`frozen_invalidate`以共存。三者观察状态严格相等。

另有同一份Y2独立回归脚本，分别编译到新/冻结common header，14个命名用例各跑一次，共28次，逐项比较状态和退出码。覆盖IO/OO、pending/victim、finite late merge、slot/generation重用、sector扩展的旧行为；MODERN的这些K0回归不提升其K1资格。期望写在`inputs/k0_regression.json`，结果在`EXPECTED_VS_OBSERVED.json`。使用V1测试文本作为Y2新输入的明确副本；未执行V1 runner，未改V1产物。

K0源码差异已披露：新增flag/observer及K1-only ordinary派生观察接口；source参数标签贯穿原调用链；finite occupancy observation改用独立采样edge。OFF保持原ordinary invalidate/cycle分支；`gpu-cache.cc/.h`与冻结blob完全相同。本CPU证据没有把两个二进制SHA差异视为行为差异，也没有声称完整输入、所有配置或完整LDST对象集成的时间等价。

判定：**PASS_K0_CPU_SCOPE**，不是完整Gaussian/GEMM配对收据。完整输入尚未运行。若后续Core变更或AA审查发现OFF不再同义，须在同一新Core上用完整相同输入重跑K0/K1严格配对，固定build/binary、有效配置、输入内容/顺序和parser身份，不能用旧结果替代。本Lane没有完整模拟派发权。
