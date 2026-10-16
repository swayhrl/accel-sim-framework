# 固定Btree条件E-list合同

唯一候选定义：原kernel-1/findRangeK/PC1c40/LDG.E.SYS/4B的固定6000条mode0记录，每条P只有一个活动lane i，列表恰有32个地址word。按历史producer `0e2fddcdef37fc59ad786553892b75567a5f2cdb` 的ascending E-lane serializer解释，E必须全32位，该活动lane地址为原 `raw_word[i]`。候选保留P和全部指令字段，仅将地址列表序列化为现有parser可读的一个word。全部6000条统一应用，包含208条地址相同的记录；未根据地址大小、性能或收益挑选。

历史producer源码位置 `/workspace/dtc-hotspot-format-174-v1/evidence/march.cu`，SHA `8dcb5ad444a6cb6a3cfb1271308e27b8395ee16afae0135703b3ac3820b09d4a`。其104-107行保存 `__ballot(1)` / `__ballot(pred)`；662行打印交集P，681行选择E作为地址mask，695-727行检查stride，727-736行不满足stride时按lane0..31列出E中地址。来源规则有可核代码和Git版本，不证明该capture实际使用该构建。冻结来源收据副本见prior_evidence。

原始字节直接支持：单P、32word、原行SHA/偏移、原PC/opcode/GPR/width、每个raw地址word、6000/5792/208计数。条件模型支持：把raw[i]关联到物理lane i及其程序地址语义。没有源码profile重建、地址预测、native输出或历史ELF等价证明。三个旧ELF候选在sm70 PC1c40是BRA，不能用来补造对应的LDG身份。

具体见证：原第691行，P=`10000000`，lane28；原frozen消费word0=`0x7f8eed50bc04`，新合同取原word28=`0x7f8ef0d10f88`。原行SHA `1a796138e666ecfb5b7ae812ad5a9f275b0c1225ed501d96c60d6976c51eedf8`。两个值均来自原trace字节。新合同改变5792条可缓存global load的地址/sector/line身份；每条仍只有一个4B活动lane、一个sector、一个line。不预测命中率或性能方向。

G0固定原list SHA `26315d4ae044e91094d54134ec94e25d70fd4eda8c0fe01767bc2a9437d73467`、原kernel-1 SHA `80c00c479a79c4a0c470de34c0b5b4421eb8e737e6cbb3a4046304b1f555395e`、原kernel-2 SHA `3c67f85abf952be8a0d109497baabaf97a53d15d4f40e9d1ba2d74ddb1fdc481`，以及风险索引gzip SHA `2266153d542547398f7ec807eb92a3be1c68678b2bab888bd50011d5220c15b7`。逐条重新读取6000原行，不依赖旧表单独声称通过。

G1候选kernel-1大小405,160,748字节，SHA `6295eb13625bbc8f25a712917b1b92a02ffcd2e1faba542e555f7845a1288722`。仅在白名单行保留从行首至第一个地址前的精确字节前缀，加上被选中的原地址token和换行；其他行逐字节不变。list和kernel-2另存独立普通文件，无指向原输入的可写hardlink/symlink。新输入目录 `/workspace/dtc-btree-format-stability-cpu-174-v1/candidate`，文件0444、目录0555；身份以SHA绑定。

G2独立Python decoder完整对读原/新成员，核原始行SHA、精确允许变换、所有其他字节、CTA/warp范围与声明指令数、EXIT边界、GPR/PC/mask/opcode、同步和完整list。C++ driver链接完整未改生产parser，调用其list/kernel/threadblock接口消费完整两个kernel。所有memory records采用统一schema：35个little-endian u64，依次PC、P、opcode解析的width、lane0..31地址；inactive lane写0。指令hash采用driver/decoder中明确的UTF-8 canonical line，包含CTA序号、warp、PC、P、opcode、typed GPR、width及非memory immediate。两实现没有共享地址解码函数。

旧mode0多余地址可能被parser尾部读入未使用的 `imm` 字段；新列表去掉多余word后该未使用值可能变化。目标opcode LDG在实际trace_driven.cc不消费imm，地址来自memadd_info。BAR/DEPBAR等消费imm的记录及其全部字节不变；非memory immediate纳入完整指令hash。不能据此声称所有未使用结构体字段完全相同。

Core支持域见CORE_COMPATIBILITY.json：两个既有Core均保持原commit/源SHA/binary；全输入只涉及常规global load/store、宽4/8B、mode0/1，对齐、单lane不跨sector/line。实际运行的服务/排空证明为NOT_RUN，不从CPU静态兼容性推断terminal PASS。原Btree pending与历史结果保持。
