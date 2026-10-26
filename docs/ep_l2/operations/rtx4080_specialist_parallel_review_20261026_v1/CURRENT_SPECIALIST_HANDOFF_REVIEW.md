# EP-MAIN资产专项并行交接与外部审阅快照

快照时间：2026-10-26 14:43（北京时间）。本快照供Root提交远端审阅；它没有执行新GPU任务、模拟、部署、清理或更改科学资格。

## 当前主线

- 当前RTX批仍在处理 streamcluster 的完整作业，原dispatcher PID1376608 / start_ticks973408720与实读一致。不能因为GPU暂时空闲绕过它的作业租约。
- Root已实际arm一个有限SDK4.2默认50,000元素Vector微窗口。controller PID1410582 / start_ticks974840061存活；状态为 WAIT_ORIGINAL_WHOLE_JOB_COMMIT_AND_NATURAL_STOP。这表示控制器已启动并等待边界，不表示新的GPU采集已启动。
- 微窗口必须等当前作业COMMIT、接收端回读、catalog闭合和原dispatcher自然STOP；窗口结束并独立确认清理后，接续精确33项原身份队列，保留原绝对72小时截止时间。窗口上限900秒，单采集进程180秒；轮询1GiB上限不是文件系统硬配额。
- SM70 V12R2已保留失败，driver末尾为 Source EOF before complete verification，未发布整批COMMIT。identity Lane正在准备V13最小修复；此快照不把EOF的唯一原因归结为buffering、NAS或Source损坏，也不声称V13已经获批或重启。
- CALL.REL/RET的有限CPU研究在另一个临时Lane进行，目前没有广泛ISA放行。

## 本轮专项整理与已完成适配

161条旧专项队列记录已冻结为161个声明身份、118个binary SHA。旧reason不是当前根因计数；原MAP标签中64行在已有v3静态映射后已暴露真实特殊指令域。历史失败保留，未通过改标签制造完成。

mapper Lane精确处理其中87条历史映射/静态枚举记录，覆盖67个binary SHA。实际完成67个二进制的新静态提取/映射，另对2个二进制验证readelf十六进制FUNC Size最小修复。最终为：

| 精确87行的当前静态分派 | 行数 | 唯一binary |
|---|---:|---:|
| 已映射、仍需特殊指令域资格 | 65 | 45 |
| ordinary静态候选，仍GPU_REQUIRED | 13 | 13 |
| 映射严格HOLD | 9 | 9 |

新候选按序保留每次cuobjdump创建的同名cubin，并对listing、提取顺序、保存文件集合及每像完整ELF输出闭合。v1保留冻结v3的PLR/JSON/ELF-owner两核心函数；v2只另补十六进制符号大小。未知owner、越界、缺非NOP PC、跨像同function/PC歧义及普通域不支持指令继续拒绝。v1的17例、v2的19例CPU正负测试通过。

13个静态候选进一步收窄：仅原MVT、SYR2K、SYRK、GEMM四个source/binary身份形成可执行准备包；FDTD-v4单列为显式修复变体，不能算原FDTD-v3被修复。原v3失败、GESUMMV未初始化B、四项未完成read-before-write证明的输出缓冲以及两项Rodinia随机输入继续HOLD。输入资格明确是确定性source初始化策略，不是实际输入字节快照。

这份新worker包维持producer55、validatorf9、POST5d、采集flags、数值策略、原CPU2后处理及现有锁。Root exact grant在任何attempt目录、租约或GPU查询之前检查。Root独立完整diff审阅及109 CPU复放12项集成测试均通过，接受范围仅静态准备；真实MVT GPU grant仍未安装。

## 身份比较器的Root结论

Root独立复放22项fixtures及3条真实已存在可用路由，接受私有比较器用于只读Goal审计。三条可用路由不等于原历史attempt、实际输入、producer profile或科学身份等价；未重写旧失败、未部署公共overlay，未重新全读trace/input payload，也不自动给予consumer或硬件资格。

## 外部审阅边界

请分别审阅：静态all-image证明、确定性source策略、SDK微窗口边界控制、运行时producer闭合，以及consumer/science资格。前四者不能互相替代。整库公共125输入入口激活和完整目标恢复验收仍是原Goal的后续工作，本轮专项包不等于整个Goal完成。

所有新源码、日志、提取/SASS和回执位于真164。mapper私有中间物约331MB；未新增Native trace payload。Source KEEP，释放0；没有改现有科学registry或预算。证据索引记录原路径、原SHA与脱敏快照SHA，JSON递归排除token/nonce/secret字段；Git是否提交、远端HEAD由Root后续核实，本文不预先声称推送完成。
