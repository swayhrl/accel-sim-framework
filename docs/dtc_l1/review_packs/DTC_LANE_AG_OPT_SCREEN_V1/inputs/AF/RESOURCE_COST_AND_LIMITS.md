# Resource cost / hardware and scientific limits

AF只引入请求中的一个opt-in布尔开关。ON限定PAPER_OO；OFF不扫描候选且不递增局部机会/触发计数。原Tag-bank、allocation、lower issue、refill/waiter、collection及retire配额不变；不改Ref粒度、K1、write可见性、ordinary cache、sector策略或全局pool容量。

候选搜索只在无free + valid live原LRU的miss上发生。检查当前set的W个way及physical metadata，按最小LRU选择安全候选；防御性扫描相同identity的finite return队列Q，host最坏工作O(W×Q)，原RR free搜索O(P)仍存在。触发后沿原release/allocate路径；新增simulated-cycle延迟为0，明确属于候选时间模型假设。4/8-way例子最多检查4/8个way，不表示真实多端口状态读取、Ref/ready/owner同时可见、优先选择、扇出和释放同步免费。

GCC当前CPU ABI的实测：`sizeof(config)` X2/AF均56字节（bool使用既有padding）；`sizeof(oo_frontend)`由488增至496字节，差8字节来自候选局部64-bit trigger counter。每个64SM frontend合计host计数状态增加512字节。这是C++对象大小，不是RTL最小bit数、面积或功耗；没有新增每line Ref/owner状态，并不证明原metadata已有足够读取端口。

真实硬件晋升必须审查：Tag-way与physical Ref/ready/valid索引读取端口、是否需要候选ready/Ref0摘要（若新增则另合同）、最老安全选择网络/比较器、同cycle K1/lookup/return/retire的顺序与互斥、SRAM宏/扇出/布线/频率、重命名generation和回收握手成本。若需要多cycle扫描、摘要维护、额外队列或延迟/宽度参数，保留为请求，不自动加入AF V1。

CPU build最多2个并行编译任务；CTest串行，负测child运行时parent等待。完整Core shared library已CPU编译，未构建或运行trace executable；没有GPU/native workload、kernel launch、full simulator执行。GNU time记录构建wall1:46.51、user172.29s、system23.81s、最大单child RSS610304KiB；这个RSS不是两个编译器的合计峰值。准确资源/ELF SHA见 `RESOURCE_AND_BINARY_IDENTITY.json`，大build与原始CPU日志只在AF独立root。

CPU判定：17个synthetic见证与9/9 CTests PASS；生产option parser验证省略/0/1，default-OFF的4组CPU API轨迹与固定X2逐字节相同。新WB拒绝用例是受控“未调用retire”的header witness，结合未改动的真实LDST WB gate源码，不是完整operand collector端到端资格；candidate queue full用源代码定位分离，没有注入真实LDST满队列。未覆盖项标PARTIAL而非制造PASS。

首轮parser CTest因继承库路径选中CUDA vendor libcudart而失败；未运行任何kernel，原失败日志和SHA已保留。测试环境改为绑定AF自己构建的Core库后9/9通过；生产机制未因该修复变化。旧7个CTest源码未改。当前成果不证明真实输入窗口频率、加速、数值load/coherence或真实PPA，仍为条件优化候选。
