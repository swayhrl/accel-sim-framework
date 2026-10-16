# Btree 有界来源核查

结论：**UNRESOLVED_FORMAT_APPLICABILITY**。已验证历史producer合同、6000条原始full32记录及保留二进制候选的排除证据，但没有绑定本次采集实际采用的producer。原terminal PASS保持，科学适用性仍待审；不生成新正式输入。

## 新增可验证证据

复用104476条风险索引，按原字节偏移稀疏读取全部6000条 Btree 风险行，每条原行SHA与旧索引一致。它们均为 `findRangeK/1c40/LDG.E.SYS`、4B、P仅1个活动lane、mode0携带32个地址字。没有再次顺序读取Btree正文或其余成员。见 [INDEX_AND_SOURCE_MODEL_RECEIPT.json](INDEX_AND_SOURCE_MODEL_RECEIPT.json)。

历史producer `0e2fddcdef37fc59ad786553892b75567a5f2cdb` 的源码SHA `8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a`：打印P=E&predicate，按E序列化地址；base_stride失败后退为mode0列表。其可验证源码与原launcher的旧traceall路径、无version字段header和mode0/mode1混合形态相容。**这是来源家族相容性，不是实际采集构建绑定。**

若采用上述E-list合同，32个字唯一对应32个物理lane，5792条活动地址与冻结parser不同，208条相同；已逐条与索引地址交叉核对。若采用已检查的P-only列表合同，单P只应输出1个字，与这6000条的32字形态全部不符。这一数量排除直接来自原始字节及具体serializer源码，不依赖地址“像不像合法指针”。它不排除未提供来源的自定义producer/格式修改，不能自动给固定capture选定合同。

同一保留包还提供可验证的2021年fork源码：commit `9cdd82aae3f95eaba78a9b01cfb5880f8f4f93ee`、Git blob `d8028fee05e288aa1d76ec6833d647a5b908691c`，源码SHA `61955513bd801178565851fceebef89a489e118df40c4861c34b7366716b7e31`。已从包内Git对象核对工作树源码完全一致。它虽然也按E编码，却声明version3，并在全局TOOL_COMPRESS开启时只输出mode1或mode2、关闭时只输出mode0。其已检查代码不能在同一固定开关下生成原成员观察到的混合mode0/mode1，因此不能拿它替代旧traceall来源。比较见 [PRODUCER_POLICY_COMPARISON.json](PRODUCER_POLICY_COMPARISON.json)。

## 保留ELF候选排除

从同包45,793,177字节的 `validation.tgz` 只提取三个Btree名称的候选，CPU使用cuobjdump11.8反汇编，未执行ELF或GPU代码。`b+tree-rodinia-3.1`、`btree_k1`、`btree_k2` 的SASS相同；sm70 `findRangeK` 的PC1c40是 `@!P0 BRA 0xe80`，而原trace记录 `LDG.E.SYS`、dstR11/srcR4、width4。三者都不能用来解释原风险PC。ELF/包/SASS SHA及原始反汇编行见 [PRECOMPILED_CANDIDATES.json](PRECOMPILED_CANDIDATES.json)、[BTREE_PRECOMPILED_COMPARISON.json](BTREE_PRECOMPILED_COMPARISON.json)。没有以别的架构或相同程序名冒充匹配二进制。

历史应用源码的 `kernel_gpu_cuda_2.cu` 与GPU-app-collection commit `40e0052cebd3f98006190ed09e78f4981ef1a41b` 的字节一致（SHA `7b2da2312b0b7c38f6c83a5cb8a8ae5394be155f7d7dc6373a1d2b7b72267daa`）。源码存在按key谓词选lane后读取indices的操作；但拒绝的ELF使其不能绑定到PC1c40，不能靠源码位置直接恢复动态访问或输入数据。

## 地址解释、影响及最小缺口

保留原反例：第1成员第691行，P=`10000000`，lane28冻结消费 `0x7f8eed50bc04`，历史E-list关联则为原word28 `0x7f8ef0d10f88`。两者都来自原列表，不是新造地址。5792条条件差异涉及可缓存global load的sector/line身份，单条访问数量仍1；可能影响cache命中、合并和下游等待，不预测性能方向。

需要的最小来源可以是与固定成员绑定的producer构建/格式收据、带lane/E标识的原始未压缩记录及包装链，或其他能唯一确定该列表合同的采集证据；**不限定必须恢复某个指定ELF hash**。当前launcher所指精确library/ELF路径不存在，保留外层包和已检查validation子包没有对应tracer library；此否定证据的搜索范围已记录，不是全机器或所有嵌套包不存在的宣称。

本项在这里停止扩展。后续如选择E-list解释作新派生研究，需先审查输入定义，再由独立候选/准入流程处理这个单成员单PC；本轮没有生成该输入、改写旧结果或改变Lane A状态。
