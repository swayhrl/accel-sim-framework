# A67 CPU-only 证据复核记录

2026-10-16；Codex Lane M/node109。类别：同一Lane独立于原分析器的CPU重算；不冒充另一科研协调窗口的外部独立审查。

对象commit `c425819d1f41e0cbd3053315cd5590697e808a3c`，tree `5ae9be2bf51ba959b9588a8111ae28bf6f03af84`。本次不运行原native/analyze/supervisor，不导入Torch/NumPy/DGL，不触及GPU锁。

- 90个Git blob（含原Goal）、88条SHA清单及执行source身份匹配；7项原A61科学定义AST一致。
- 六个12-step窗口与调度一致；原order.npy正式前缀SHA一致；72formal+12warmup+1canary=85，逐参数Adam step及loss/shape记录相互吻合。
- 标准库解析原NPZ，将665619个元素按`initial-.003*g/(abs(g)+1e-8)`独立计算，全部满足原update门atol1e-6/rtol1e-4；max abs4.09879625e-9。FP64重算与原FP32逐操作解析式的舍入顺序不同，不要求max误差相同。
- 原forward/gradient仅审查记录与原封不动的oracle，未重新数值生成；未完整归档的采样子图数组不能由hash逆推。
- 六个wall/throughput及离散度复算一致。将已有pin/context/warmup/wall作算术加和未翻转方向，但不是冷启动E2E测量。
- 独立解析41个NVML原CSV及PID/start_ticks/PGID/SID：33次OWN_LIVE分类，其余空；窗口边界和最终退出闭合。纯CPU另验10归属和7解析用例通过。快照不排除任意短采样间隙任务；未实际复现A65退出竞态，也未将旧监督重标PASS。
- 原执行资源源账在合同内。旧输入/运行库全量SHA与不可变性沿用原pre/post审计，本次未重读其全部GB级payload。

判断：接受`SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE`的限定范围解释，没有新硬件证据。每臂只有2短窗口、FULL CV约23.6%、邻域不逐边配对、准备另账、无物理流量/关键路径/收敛/compiled资格；这些限制持续有效。

详见[A67_CPU_VERIFICATION.json](A67_CPU_VERIFICATION.json)。核验进程affinity[0,2]、512MiB地址空间上限，RSS峰35880KiB，CPU0.355s；这不是整个阅读/整理过程的总耗时。GPU/锁/新训练/数据与依赖下载0。

原复核文本SHA256及核验器/输入包SHA保存在[ORIGINAL_ARTIFACTS](ORIGINAL_ARTIFACTS.json)。原A67证据继续由精确Git commit提供，不重复复制大raw。