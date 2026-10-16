# Round A64｜A61 IGB-small GraphSAGE G1数字资格STOP独立科学审查

**日期：2026-10-16；审查者：ChatGPT／AI-ARCH Discovery。状态：INDEPENDENT_REVIEW_ACCEPTED_WITH_SCOPE。**

## 0. 权威、执行边界和裁决

- 唯一被审执行来源：swayhrl/accel-sim-framework，A61执行分支 hrl/aiarch-a61-igb-small-gnn-native-109-v1，final commit 37120f98186b83a946f4812755523f5d73245491，Git tree d13b446ca4824cb3ad7ffae25b5ce91c023b75a1。
- 通过GitHub连接器独立核对Goal HEAD 9be1d85b0ce105026e7fc4206a0380a98ffb4d1e → final恰好ahead 1，final → execution branch HEAD identical。final commit列出60个新增Git文件，git-data tree与报告一致。独立读取FINAL_REPORT、GATES、失败JSON、原日志、执行源码、GraphBolt数据/数字canary、GPU ledger及其它部分raw；本审查没有在控制端逐个重算全部60文件SHA256，后者属于109已报告的执行发布收据。
- **接受A61 DATA_OR_NUMERIC_NO_GO / STOP；确切门为COMPILED_UPDATE_QUALIFICATION_JOINT_PREDICATE_FAILED。** 不是编译器bug确认，也不是GNN供数/硬件性能负结果；不能替原报告将失败改PASS。
- 本次审查纯GitHub只读与协调记录，没有连接109/174-new/164、启动GPU锁/重启Codex、修改任何A61执行结果或资产。

## 1. 可信的资格结果及界限

| 项 | 已接受 | 严格界限 |
|---|---|---|
| G0 | 唯一官方IGB-small归档MD5、SHA256、原始真特征/标签/有向边、安全解包、合法学术本地使用范围和环境闭包PASS | 非泛法律保证；不是OGB替代镜像 |
| G1 FULL_RESIDENT_GPU | 原1024 FP32特征＋完整CSC均驻GPU，B1024一个自然batch的前向/梯度/首次Adam PASS；Torch reserved 8,698,986,496B，约8.10GiB | 不证明完整32批持续容量/训练性能；不等于全驻留更快 |
| G1 PINNED_CACHE_ON | 真实图/特征GPU cache存在，fallback和采样语义、模型eager数字PASS；cache replay有真实命中 | 首批/正确性replay命中率不是正式稳态，不能推断PCIe/DRAM流量或等待 |
| G1 编译训练步 | 函数返回，前置finite和loss门未触发；更新复合条件FAIL | 没有保存第二名字、逐参数差值和编译梯度，原因UNKNOWN |
| OFF／G2／等待诊断 | 0正式训练步、所有6组正式点NOT_RUN | 没有完整自然step wall、供数瓶颈或硬件headroom结论 |

单自然seed节点ID相同不保证各arm的GraphBolt邻域逐边相同。原报告明确FULL、PINNED、replay的input IDs与sample edge SHA不同：足以接受每条路径自身合法的功能门，不足以将这三次执行当作逐bit相同输入的数值/时间配对。

资源按原始gpu_ledger与收据：锁累计64.680326s，采样task RSS约9.47GiB、NVML显存约8.39GiB；总下载约4.06GiB、新盘约9.86GiB；用户报告子进程退出、锁释放。采样显存不是数学峰值保证，但有Torch allocator精确记录。

## 2. 从执行源码独立核对失败谓词

准确源码：tools/aiarch_a61/native.py，SHA256 d511fe347e963e10b724613de077fe4a542386a15e0d3496e05868fe9ab04c18。对PINNED_ON的自然mb先执行numeric_oracle得到eager训练更新；随后新建model2/opt2，调用torch.compile(train_step,dynamic=True)，返回后使用一个短路assert：

    for (n,p),(n2,z) in zip(model.named_parameters(),model2.named_parameters()):
        assert n==n2 and torch.allclose(p.detach(),z.detach(),atol=1e-6,rtol=1e-4), ...

**这是两个不同失败原因的复合谓词。** 错误字符串报告的layers.0.lin_r.weight只是第一个reference参数名。第二名字、实际delta、失败元素和编译侧gradient都未保存，不能由此证明真正的参数值错误，更不能说已定位torch.compile精度缺陷。

从源码看，编译的是train_step函数，并非将model2替换成OptimizedModule；两边原始model对象都由同一GraphSAGE类创建，因此直接由模块包装前缀引起名称不一致的假说较弱。但缺当时的逐项记录，不排除比较器/模型变更或生存期问题。也不能将名称匹配当作已经实测的事实。

原numeric_oracle在16个seed的FP64参考上已证明eager forward/gradient/首次Adam解析式；这不是对编译路径的gradient独立参考。第一次Adam在gradient近0位置可能放大微小gradient差异（post-stop数学注记已指出），但这是分析性假说，不是本次测到的更新差。

源码没有记录两个初始模型的逐参数SHA，也没有同一冻结输入下的eager/eager对照。GraphBolt自然异步采样的历史失败mb未以可完全重建的逐边raw保存；新实验无法声明与旧失败样本逐bit配对。旧失败只在原范围内保留，不用新PASS追溯抹掉。

## 3. 下一科研动作

**仅推荐一个有界的新数值可归因canary，优先CPU静态预检，再占109短GPU锁。** 它是科学数值门，不属于可默默降级的普通工程fix。建议一个新独立branch/Goal（A65），必须由用户把启动指令交给对应Codex才真正执行；不得重启或修改旧A61。

核心三路：对同一个新采样但内部冻结的自然B1024 minibatch（原GraphBolt缓存/图/feature/标签、模型精度与数学合同不变）创建bitwise一致初始状态、完全独立optimizer的eagerA/eagerB/compiledC。先记录名称/dtype/shape/初态和输入SHA；再记录loss、梯度、更新后参数的逐参数差值、不一致位置/相对阈值和异常值，分别判名称门与数值门。eager/eager证明该执行条件的比较下限；compiledC使用原train_step dynamic=True，不通过改变逻辑或容差寻找PASS。禁止新增其他工作量、GPU profiling、正式step wall。

建议新累计硬边界：原GPU非阻塞独占共享锁≤180s，下载0，新盘≤128MiB，RAM≤12GiB，VRAM≤12GiB，CPU≤4，总≤3次实际optimizer更新＋仅用于工程中断的一次保留重试。所有assets从原A61私有位置只读使用，任何缺失科学payload、锁竞争、预算越界均STOP，不搬数据去164、不触碰AWMA/C16。

结果分流：若eager/eager已失败→先分类非确定性/模型或样本突变；若eager/eager通过而compiled不通过→保留真实编译路径差异且逐阶段定位，不自动归罪编译器；若全通过→新canary只支持新冻结输入下数值资格，不能将旧A61 FAIL改写为PASS，下一轮才独立考虑正式三arm训练wall；若名称/比较器失败而值一致→标测量门缺陷并保留旧报告原样。任何数值阈值调整/核心版本切换/真实数据变化必须独立科学复审。

科学路线仍为A61原题：先强软件＋完整训练step wall，尤其保留已经可行的FULL_RESIDENT_GPU最强参照。仅PINNED_ON优于OFF不等于硬件机会。未取得完整wall之前，不发GPU Cache硬件Goal。A62/A63稀疏训练候选继续只读储备，不能用来覆盖A61。

**终态：A61合法STOP独立接受；A65只建议/待用户派发；当前无新增109 GPU任务。**
