# vectorAdd-DH 资源失败只读诊断

点：`E2-AEV100-e7bb67e63e3c3847-DH`；UUID：`b15d3469-ed1b-4979-b7fa-9ba864c8630e`。原失败仍为 `STOP_UNACCEPTED`，accepted cycles 为 null，未重跑。

该点不是因自身RSS达到上限或被内核OOM killer终止；旧外层守护把5个在场模型未来可能增长到16GiB的差额全部预留，在共享cgroup原始memory.current波动后仅差28.09375MiB越线，主动向原模型发送SIGTERM。确认的是资源预算策略触发；当时缓存/其它共享占用的具体组成未记录，不能断言缓存是唯一根因。

失败时间为北京时间 **2026-10-25 13:56:44.286358**，原运行约20.70分钟。已完整读取125个外层资源采样、125个原BA资源决定、130条认证进度及535,074字节解压raw。全部125个原RAM判定按冻结source逐条重放一致。

| 失败样本项目 | 精确值 | GiB |
|---|---:|---:|
| host MemAvailable | 297,489,358,848 bytes | 277.058556 |
| host所需64GiB+未来预留 | 147,433,979,904 bytes | 137.308594 |
| cgroup max | 274,877,906,944 bytes | 256 |
| cgroup current | 144,653,254,656 bytes | 134.718842 |
| cgroup实际余量 | 130,224,652,288 bytes | 121.281158 |
| 未来模型增长预留 | 78,714,503,168 bytes | 73.308594 |
| 48GiB+未来预留门槛 | 130,254,110,720 bytes | 121.308594 |
| **仅差的预算缺口** | **29,458,432 bytes** | **28.09375 MiB** |
| 本点峰值RSS | 599,785,472 bytes | 0.558594 |
| 本点硬上限 | 17,179,869,184 bytes | 16 |

原判定为 `host_available >= 64GiB + future_RAM` 且 `cgroup_max-current >= 48GiB + future_RAM`。只有第二项失败。上一采样余量316,706,816字节，最后10秒变成−29,458,432字节；本点末段RSS没有增加。外层source随后设置 `MEMORY_HEADROOM` 并 `killpg(SIGTERM)`；trace精确记录发送者frontend PID1192124，接收模型PID1192249，`SI_USER`，launcher returncode −15。

当时在场的五项预算如下。每点16GiB为原冻结硬上限；表中RSS是各自最接近失败时间的10秒**进程树**采样，非同一时刻的逐模型VmRSS，不可冒充原预算的精确逐项输入。

| 程序/配置 | 每点硬上限GiB | 最近RSS GiB | 与失败采样偏移秒 |
|---|---:|---:|---:|
| BICG CM | 16 | 2.253906 | +0.243701 |
| BICG DH | 16 | 1.339844 | +0.214823 |
| BICG DM | 16 | 1.578125 | -2.457119 |
| nw DM | 16 | 0.488281 | +1.439180 |
| vectorAdd DH | 16 | 0.558594 | +0.000000 |

五项硬上限合计80GiB，由原聚合未来预留反算的模型RSS总量为6.691406GiB。最后10秒共享cgroup current增加1,109,528,576字节，模型未来预留减少763,363,328字节，净预算余量下降346,165,248字节。这个共享池变化可证，其内存组成和所有者不能由现有历史计数反推。

125次BA采样的cgroup `low/high/max/oom/oom_kill/oom_group_kill` 全为0；host `oom_kill`累计366不变。cgroup swap始终15,400,960字节；host pswpin=3,742,045页、pswpout=11,010,455页，均无增长；own major fault delta全0。host/cgroup memory PSI avg10/60/300全为0.00；host memory PSI some/full累计仅增加88,890/88,753微秒，cgroup some/full增加0/1微秒。125个BA决定均为CONTINUE。结合明确的用户态SIGTERM，可排除本点kernel OOM kill及swap抖动直接触发；共享IO PSI只是当时背景，不能据此归因本次内存预算停止。

磁盘检查通过，原free 23,467,507,712 bytes，高于所需 12,107,496,346 bytes。完整raw没有OOM、bad_alloc、断言崩溃或实际deadlock签名；唯一deadlock文本命中只是配置开关。末条进度SIMULATE完成72,625,760/84,000,768条指令（约86.458%），end=NONE；没有完整自然结束，不能接受cycles。

R7增加clean inactive file cache credit，但仍使用full-hard未来预留。本次只需29,458,432字节credit就可跨过该门槛；按先扣8GiB的公式，clean/inactive交集至少需8,619,393,024字节。**当时未保存memory.stat六项，不能声称缓存占比已查明，也不能证明R7当时一定会通过。**

R12/R12B将旧前端运行期外层RAM判定改为新鲜实际余量，保留原字典/旧判定及override证据；新V4以4GiB作初始准入预留，hard cap仍16GiB。仅用本次已录host/cgroup计数、即使cache credit=0，actual-only规则也会通过。这只验证规则反事实；该vectorAdd点已结束且不在R12目标中，**没有重跑通过的证据**。

最小下一步是保留本次失败，对已有125样本继续作离线对照，并从后续正常队列记录完整fresh cache/OOM/swap/PSI/逐项预算；不自动重试。若未来另行批准重测，必须用新实验身份、独立预算及完整strict/archive自然结束验证，原账本不覆盖。

证据SHA与完整逐项快照见 `DIAGNOSIS.json` / `EXTRACTED_EVIDENCE.json` / `MANIFEST.json`。原raw gzip SHA256为 `4cd9640338b4590424a510a953409a1a76ae1eb3c1aee7fa11cfce43cd7c52b6`；解压SHA256为 `7c7bfa90d681d55aae0e432119eb93db22fce8c0adc47eff55c6abbb9cba68b1`。本诊断没有启动模拟、改变active/pinned source、中央registry、原分类或历史账本。
