# Measured versus adapted coverage

真实CPU：本包C++小程序，无GPU/model API；使用真实系统dynamic linker，未用inhibit-cache。预先冻结ELF/loader/依赖及`/etc/ld.so.cache`的角色、dev/inode、SHA；实际捕获cache出现和unmap。真实fork/clone/exec/exit、长时reader-helper、多轮周期observer、异常退出、timeout与pending清理均走同一个guard和authority入口。

真实事件顺序适配：保持内核产生的父fork事件，暂缓交给guard，让observer/child-stop先出现；随后仍由真实GETEVENTMSG确认。另暂缓真实child首次stop直到parent已reap，检验独立继承快照。这些是受控重排，不是声称自然调度一定产生同样次序。

generation负控：走完整`run_guarded`入口和真实CPU进程生命周期；仅在真实实例退出后注入一条synthetic SIGSTOP及其synthetic新start_ticks，或改变一次身份/image generation。旧guard只替换CPU目录和basename，其分派算法不变，并使用当前Ownership辅助模块；复现不宣称整个旧环境字节一致。适配器在任何针对虚构实例的ptrace或signal系统调用前阻断并留记录。新guard未尝试这类操作。负控遗留的synthetic pending在收据中保留，不是实际存活进程；真实STOP清理由独立内核事件测试验收。

Linux内核强制PID reuse：UNAVAILABLE；真实性能中的PID复用：NOT_ESTABLISHED。不能据CPU PASS认定未来完整应用一定成功；没有新的应用性能、数值正确性、coherence、ISA、RTL或硬件结论。

本包没有运行正式screen dispatcher，未授予新attempt。launch policy拒绝SIMULATION，固定CPU目标源/ELF SHA另行绑定。这不是针对恶意替换CPU ELF的通用安全沙箱。
