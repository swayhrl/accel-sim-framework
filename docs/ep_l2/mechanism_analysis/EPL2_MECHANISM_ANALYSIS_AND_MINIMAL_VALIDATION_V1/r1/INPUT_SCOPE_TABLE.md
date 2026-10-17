# 输入和计时范围（现成材料，未重抓trace）

| 输入 | Suite/版本证据 | Literal程序参数/大小证据 | 捕获kernel文件数 | 缺项 |
|---|---|---|---:|---|
| sad | 当前manifest路径suite标签；capture脚本未定位 | `literal命令/输入大小未披露` | 3 | 不由host memcpy50688B推断算法输入规模 |
| vectorAdd_4M | CUDA-SDK目录；run.sh CUDA_VERSION9.1 | `vectorAdd --size 4000000` | 1 | 准确SDK commit未披露 |
| cfd_097k | Rodinia3.1来自可执行文件名；目录9.1与脚本CUDA_VERSION10.1分别披露 | `cfd-rodinia-3.1 ./data/fvcorr.domn.097K` | 5 | mesh文件内容/准确单元数、原source默认迭代数未披露 |
| convolutionSeparable | CUDA-SDK目录；run.sh CUDA_VERSION9.1 | `convolutionSeparable --size 3072` | 2 | 实际维度语义/源码默认循环未独立核验 |
| FWT_7_21 | CUDA-SDK目录；run.sh CUDA_VERSION9.1 | `fastWalshTransform -logK 7 -logD 21` | 19 | 不把log参数臆造为默认source迭代数 |

完整run.sh原文、commandlist、trace manifest和已接受内容身份在derived/INPUT_SCOPE.json；本次只读现成小文件，没有执行capture脚本（原脚本中的rm等命令也未执行）。

cycles来自native full-application终态gpu_tot_sim_cycle，包含模拟的launch与设备退尽；host trace解析/墙钟不在此计时内。修复后host prefill的Tag偏移不等于物理GPUcycle。kernel-shared delta及64slice/窗口计数不相加为独占执行时间。完整commandlist不自动等于完整源码默认循环。
