# Btree科学适用性：确认HOLD，分开记录两种不一致

E权威为69301fe9d336af4a9638099461f6823b0c1252ba。Btree原登记D_V1_btree和原trace不变。

## 实际复现及结论

原kernel-1.traceg第691行，mask=0x10000000，唯一活跃lane=28；list_all有32个地址字段。原生Framework9dd1ee57的trace_parser.cc第192–199行遍历lane，只有活跃lane才从流读取下一个地址，因此lane28取得第0列0x00007f8eed50bc04，而固定32列解释的第28列是0x00007f8ef0d10f88。二者不同。第223行尝试读一个imm，不会将另外31列按lane-index重排；普通LDG没有这种重排补偿。

核对D实际使用的冻结C oracle aabc7d80/763cbcdf解析同一原始记录，结果同样是第0列。**此记录上，离线oracle与native的已消费地址相同**，不能报告成“oracle取lane28而native取第0列”。真正未闭合的是32列输入的语义与原生紧凑active-lane语法；二者同样忽略多余地址不能证明输入正确。C oracle没有完整尾字段检查，故此前整epoch/哈希/3条只读候选证明不足以使Btree成为可用native输入。

D只做有界原始记录读取和准确源码函数解码，没有执行C++、解析器二进制、模拟器或GPU。源/记录SHA、实际函数返回值及比较见BTREE_MAPPING_COMPARISON.json。E已有严格非零mask尾字段检查拒绝该输入，D保持HOLD。原候选3-line manifest和原始日志均保留，只撤去其“可用于native输入资格”的推论。

## 需要A/E（必要时C）独立处理的边界

1. A确认实际生产解析器及地址传播链的source映射，E确认输入HOLD范围；不能仅凭模拟结束/旧性能结果解除。
2. 若要保留原Btree用于科学运行，需要原trace producer/捕获版本的明确紧凑地址或32-lane格式证据。D不推测某一列才是真值，也不删31字段、改mask、拼接/重写trace或生成新捕获。
3. 如果A选择改变生产解析器支持另一输入编码，这是新的runtime源码、binary与原生输入语义资格；另行源码审查、准确新身份和E受影响资格，不能继承旧二进制PASS。本轮D不实施或请求立即重编译。
4. 如果提议派生修复输入，先由A/E/协调者说明生成规则、来源/可逆记录、全字节新hash、oracle重建与新登记；在授权和语义闭合前不执行。不得覆盖原trace。
5. C oracle输出与E native输入证明应分开，后续C可按所属范围补尾字段拒绝；D不修改A/C生产源码。当前应用由E证据叠加HOLD屏蔽，不去改写旧证书制造“已修复”状态。

本HOLD仅影响Btree。DWT2D已有10kernel输入语法/非原子/原字节及零mask证明保留；该证明不是完整S/F性能接受。原五输入不重复扫描，EN-v18、E台账和40累计上限均未修改。
