用户明确授权：“授权最高60/120 MiB/s，分级提升”。

先应用 Source 30 MiB/s、总数据 I/O 60 MiB/s。取得实际范围进度及资源观察后，可提高至 Source 60 MiB/s、总数据 I/O 120 MiB/s；允许回退至原15/30。单Sender/Receiver、128 MiB原始块、256 MiB暂存、完整SHA、原冻结身份和所有未豁免资源门槛保留。原监督期限及累计计数不重置。

通过原Receiver锁的正常释放边界进行协作重载：仅在当前资产COMMIT、Driver释放锁后取得锁；Driver由原资源门禁正常退出，安装经定向验证的兼容限速代码，释放同一锁文件后由原Supervisor重新准入并续行。不创建第二个Driver、Supervisor或Publisher，不对科研进程发送信号。

已有COMMIT及恢复脚本保持不可变。新限速控制和授权有独立真164回执；改变限速不改变资产对象、成员、range或COMMIT格式。
