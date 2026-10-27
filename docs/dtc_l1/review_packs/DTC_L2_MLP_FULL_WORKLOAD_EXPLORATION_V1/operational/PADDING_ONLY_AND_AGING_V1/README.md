# DTC-MAIN：预测余量缩减与大任务等待保护，源代码资格包

**发布时尚未生产安装；不把CPU/mock资格称为真实模型完成。** 本包供Main进行先发布回读、再登记、再唯一owner接入。所有SIGSTOP/长暂停方案继续HOLD；本方案没有任何模型暂停/信号/重启。

预激活状态：2026-10-27T23:07:42.178767+08:00，本轮新accepted 197+合法旧P0引用6，实际live 66，未启动80，历史旧任务live 0。完整扫描/组合/CH匹配尚未完成，Goal继续。

## 范围与资格

- [Padding实现与API](padding/README.txt)、[完整47项资格](padding/CPU_QUALIFICATION.json)：组件20、owner12、实际冻结原生前缀代码路径13、旧accepted只读回归2。原生前缀中的Popen/系统/authority等在隔离CPU fixture里mock，未启动真正模型；真实headroom仍可能HOLD。
- [33行不可变资源证书](certificate/A_ONLY_ELIGIBILITY_CERTIFICATE_V1.json)、[独立证据审计](independent_review/E_CERTIFICATE_AUDIT.json)。同input/binding/Core/FW/binary/design及所有非目标选项，允许仅initial9单因素内target-field-masked传递，绝不称全配置完全相同；组合/扩边无折扣。原peak不下降，只将1.20×peak+256MiB padding改成1.10×peak+128MiB，原floor768MiB、结构128MiB、当前RSS10%增长包络和RSS/AS硬限不改。128MiB为经验余量，非绝对结构上界。当前RSS超过certified同design峰值则优惠0；候选仍原provider/current canonical最大值全额保留。unknown/foreign/claims/cross-design/failed-only无折扣。
- [原生CLI候选与41项路由资格](route/REVIEW.md)：真实入口仍N/bin/experiment→N/bin/native，只有显式newREQ opt-in分支，旧4212-byte body完整原样尾接。未编辑冻结R/tools。三份INTENT/LAUNCH/PID附加绑定、不可变fresh准入证据和原strict AND新增strict在模型结果目录闭合，旧点不变。
- [75/25大任务等待保护](aging/POLICY_REVIEW.md)、[最终B665依赖下同38项资格](aging/CPU_QUALIFICATION_FINAL_B665.json)。只一个等待目标，保留原完整预测/实际资源门和4 pre-exec；真实自然完成且strict/archive/restore接受后，释放估计被实际正slack增量夹界，75%保护、25%回填。own-drain仅未来可行性估计，绝不当当前物理余量。真正claim/unknown已承载全额时virtual R=0，避免双重预留；绝不重提spent身份。
- [独立最终审阅](independent_review/REVIEW.md)与[必须的post-padding facade接线](independent_review/AGING_INSTALL_CONSTRUCTION.py.txt)。E外层必须拿B.overlay.resources的真实有效视图及原forecast，不能直接读取B threadlocal未激活时的base view；E状态全pending只advance一次，原B chooser继续独立裁决。

## 激活与可复现性

Main应先核真实GitHub回读及qualified_sources/policy/certificate/QA完全相同，再用原e.update_authority事务只加本request operational record，budgets/remaining/consumed/specs不变，peer/history保持。先一个**现有已登记未spent**短点作为真实工程验证，完整strict+额外sidecar+归档/native restore通过后再扩大scope。这个阶段门不是模型启动总数上限。真实资源不足则等待，不能合成headroom或抢先消耗身份。

[协调者部署器](coordinator/prepare_padding_install_v1.py)、[原生路由/唯一owner附着器](coordinator/apply_padding_router_owner_v1.py)、[报告附加验收后置审计](coordinator/verify_padding_report_v2.py)随包。当前代码没有执行这些部署器。后续ACK/实际pilot另记，不回写本冻结发布包。

## 历史单独统计

[旧3个恢复任务的实际终结回执](historical_only/HISTORICAL_RECOVERY3_TERMINALS_V1.json)：streamcluster DM、SYRK CH/DH均returncode -15，stop reason为旧expected_growth/MEMORY_HEADROOM，不是自然完成、不是本轮accepted。Main仅只读核对，未发送信号、未修改或重启旧任务，不将其结果晋升。

本轮固定35普通输入、7未决保持，Core9eedb313/FW02775fd7/binary02a28936、DRAM850MHz、L2容量/映射、DTC架构均不变，英文v0.23不改。预计实际并行度仍由动态物理内存、cgroup/CPU/磁盘压力决定，不承诺看到空闲内存就能启动所有点。
