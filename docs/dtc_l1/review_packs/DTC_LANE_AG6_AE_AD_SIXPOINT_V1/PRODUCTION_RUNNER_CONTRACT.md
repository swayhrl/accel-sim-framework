# AG6 execution contract — executable registration pending

授权仅6个新实际启动、单worker，顺序与`USER_AUTHORIZATION.json`一致；两个新BASE完成且严格校准后才开放任何ON。每点只一次、timeout7200秒、无retry/替换/第七次/canary。保守RUN_START预留与实际fork分别计数，任何不确定启动都不能复用预留；CPU fixture目录和synthetic预算负控从性能台账排除。

Core与实际ELF不重新编译；编译Framework源为`8e43c75a5e2eb60a8466084602b7df8117111e89`，Core固定`c8090115bd57512b1b23fca7d925301fa620c751`。使用原AG3只读实际ELF/库，SHA与build-id必须重新严格确认，不能以功能相似重编译替代。

K0、PAPER_OO、OO128、Tag64×8、640×128B物理80KiB、PIB128、ordinary16KiB、shared96KiB、4 banks、lower cap32768、clock与全部finite/ref/credit/sector/generation/ledger/fence服务不变。BASE全OFF；四ON点每次只AE或只AD。AE固定bank-preserving XOR；AD保留4waiter/cycle与独立消费者ready。禁止组合、其它输入/机制/参数或K1复跑。64×8仍是开发stress配置，不提升论文主配置。

当前无EXECUTABLE_PREREGISTRATION和PREREG_PUBLICATION_READBACK。CPU发布不替代这两个条件，`--dispatch`不能通过publication gate。注册器先要求source-bound CPU、完整输入、当前runtime角色和两BASE门槛资格，后生成6个新UUID，所有执行文件/SHA/命令/ROI/options/资源/失败规则必须commit/push/fetch-back HEAD/tree/blob/clean。

原R2资源逻辑字节不变，详见`RESOURCE_CONTRACT.md`。每点真实launch前审计所有项目与FLOCK；不接管、kill、pause或删除其它项目的进程/锁/文件。当前磁盘门槛失败时只有只读CPU准备，不能读完整trace body或真实dispatch。CPU preliminary与正式性能admission不混淆。

guard只信当前未reap且由父ptrace事件证实的实例。退出同时撤销归属/image；stop/resume核start_ticks/tracer/Tgid与image generation；继承快照绑定父/子ticks。PENDING不是PASS，确认窗口2秒，未证实不能resume/信号；未知exec/maps、cache角色/hash/设备/inode/TOCTOU仍拒绝。每次exec捕获真实早期cache出现及unmap，不以晚采样绕过。

严格停止后保留原始所有失败与负结果，顺序剩余格不得补跑。报告只用本批同输入BASE/ON整数cycles之比；ON专有字段是诊断，OFF缺字段UNAVAILABLE；不能用host wall推GPU性能、累计阶段和推实际重叠或条件均值作因果差分。两输入是发现集，不是独立验证/GM12；不声明数值load/native/coherence/ISA或RTL时序/面积正确性。
