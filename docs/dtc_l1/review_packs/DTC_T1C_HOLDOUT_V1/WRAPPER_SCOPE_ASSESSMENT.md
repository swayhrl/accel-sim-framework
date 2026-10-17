# 新EP-L2目录的只读执行权核验

预注册沿用Lane T V2的binary/config/path fingerprint。运行期间独立EP-L2项目改用 /workspace/ep_l2_potential20261017_lane5_results/ 目录；其binary仍为已核23094a9d…，使用EP-L2 FT配置且无DTC选项。原路径前缀校验将其保守标成unknown并设置停止后续派发标记，已原样保留。

此时两个授权attempt都已实际启动：DWT2D已strict PASS，BICG原进程继续。无需改变运行中的coordinator或冻结脚本，也没有新派发、重启、timeout重置或科学参数变化。所有项目的资源占用继续计入原cgroup/host/PSI/disk门槛；无旧锁owner或原A/M/T执行权冲突。

EXTERNAL_PROJECT_IDENTITY_REVIEW.json保存逐PID/start_ticks、binary与实际命令config SHA。最终报告保留原halt标记并解释其范围；任何另一个未核未知项目仍需单独审计，不由此放宽binary/config或资源门槛。此为只读包装归属核验，不是DTC协议或观测器修改。
