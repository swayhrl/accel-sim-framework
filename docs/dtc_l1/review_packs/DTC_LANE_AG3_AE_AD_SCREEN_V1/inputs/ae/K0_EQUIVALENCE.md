# Hash-OFF equivalence to fixed X2

这里K0指新增**hash开关OFF**；既有K1失效是另一独立机制，不能把hash ON/OFF改名为原失效K1/K0。

**PASS_BOUNDED_CPU_FRONTEND_EQUIVALENCE**。相同CPU test源分别对固定X2 header/parser与AE header/parser独立编译；共两次GCC11.4调用，两个单translation-unit独立ELF，身份与argv见`SOURCE_AND_TOOLCHAIN.json`、`CPU_COMMAND_RECEIPTS.json`。

4个geometry × 7类输入中，新omitted和新显式0分别与固定X2对照逐byte比较：**56组完整逐请求输出相同**。内容包括set、Tag entry槽位/完整行地址/LRU、physical/generation/ready/Ref、RR、PIB、grant/conflict、map-loss及请求顺序。另4组旧geometry S=1/2/6/12在OFF仍与X2完全相同，没有把ON限制泄露到OFF。

专门LRU见证先填满组，`will_new_miss(first)`明确提升first的recency，再插入新行；victim为原第二老行。新OFF与旧X2一致，ON也遵循同一recency政策；未引入只读peek或其它替换语义改动。

生产parser同一注册helper测试omitted=0、显式0=0、显式1=1并echo，未知选项拒绝。shader config注册/传递由静态delta审查确认；没有完整shader配置对象/动态库构建。四个原生产文件可精确恢复X2字节，所有原逻辑变化均受新增flag约束。

范围限制：这是CPU frontend每请求行为及源码等价性，**不是完整模拟器周期、ordinary实际流量、全部ISA或应用数值等价性**。两个ELF是CPU单元测试，不是新Core simulator binary，也不链接libcudart。没有启动任何full/canary/native应用或GPU。此前论文结果保持原身份，不据本轮将旧结果迁移成hash结果。
