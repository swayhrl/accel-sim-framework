# Bounded CPU cases

**137项通过，C++编译2次，无完整Core构建/模拟/native应用/GPU运行。** `inputs/FIXED_CASE_PLAN.json`在编译前锁定，仅一个hash候选；编译/执行argv、退出码和原始文件SHA见`CPU_COMMAND_RECEIPTS.json`，期望/观察见`CPU_CASES.json`。原始输出共2,976,952字节，留在AE external目录。

|组别|运行数|断言|
|---|---:|---|
|4 geometry × 7类 × X2 OFF / AE omitted / AE0 / AE1|112|实际production frontend/header/parser；逐请求状态、独立索引/LRU模型、bank quota、late merge与K1 old owner|
|旧geometry S=1/2/6/12 × X2/AE OFF|8|OFF保持旧索引/退出码，4组逐byte等价|
|生产注册helper/真实parser|4|omitted0、显式0、显式1有效并echo；未知选项exit1|
|ON geometry/mode/finite拒绝|13|S=0/1/2/6/12；B=1/2/8；finite0；LEGACY/BASE/IO/MODERN，指定STOP诊断+SIGABRT(-6)|

每个mapping进程校验12,352个固定地址（line0..4095 × offset0/1/127，加固定seed64个57-bit line），独立Python oracle核全样本的FNV摘要和4096B stride set序列；不是全2^64地址穷举。对所有合法S的bank和范围性质另由位域公式证明。任意调用点一致性由中央helper和静态delta恢复审核保证，实际lookup/eviction/victim由逐请求Tag槽位对照补足。

冲突用例在同cycle给四bank各一次grant及同bank重复，实际grant4/reject4；另用原可配置global quota=1的窄配置，验证首grant/第二bank拒绝/下cycle可用。这里只是Tag服务API测试，不把多bank grants称为多个reference提交；原whole-line LDST每次调用提交一reference源体不变。

固定trace每种只三pass，无应用trace：

|S/ways|4096B stride miss OFF→ON（96请求）|neutral miss OFF→ON（96请求）|固定反例miss OFF→ON|
|---|---|---|---|
|32/4|96→32|32→32|5→15（15请求，负收益）|
|32/8|96→32|32→32|9→9（27请求，持平）|
|64/4|96→32|32→32|5→15（15请求，负收益）|
|64/8|96→32|32→32|9→27（27请求，负收益）|

4096B stride每bank下old unique sets：S32为1、S64为2；ON分别8和16；bank仍相同。反例是预定`L=4k+k*S, k=0..ways`，没有在看到结果后更换地址或公式。其S32/8无损而另三项更差的完整结果均保留，不以优化算法继续筛选。

LRU定向用固定有界line0..65535扫描取同组ways+1条，先填满、will_new_miss探测first、再插入；旧second被evict，probe副作用未整理。late/K1用六个旧consumer、return metadata先处理4个waiter、第7个late pending merge、E隐藏目录、同址新physical、旧Ref逐个退休到最后回收；终态wakeups8、pending hits6、miss2、retired8、Ref/allocated0、map-loss sum/count8/2。

每请求Python oracle还核组内first-invalid/min-LRU、probe+access recency顺序、miss/hit/eviction和map-loss；错误期望字段会被比较逻辑拒绝。13个非法配置必须命中指定诊断，非任意崩溃即可通过。编译stderr保留：既有parser ignored-qualifier warning和测试源紧凑格式的indentation warning，无编译错误；未为消除非功能warning再触发第三次编译。
