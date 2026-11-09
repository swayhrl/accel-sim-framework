# 给Main／科学窗口的174-new导航更新提案

这是独立接班提案，尚未修改`hrl/ai-workload-research-coordination`或Main的本机`CONTEXT.md`。请在Main当前109 Goal收口及科学窗口审查后，按届时最新状态选择性采用。

## 可登记的节点事实

1. `174-AI-ARCH` 已在受信`hrl-174-new`确认`root@10.208.130.174:2239`、hostname`huangrulin-sshfs-174`、namespace`mnt:[4026535153]`和主仓库`/root/workspace/accel-sim-framework`。15个历史AI-ARCH任务工作树实际存在，HEAD与固定执行commit一致，检查时均无工作树改动；15个生产者报告在节点物化，五项后期receipt可读。详细身份与状态见本轮`NODE_TASK_ASSET_INDEX.json`。
2. A70-N、A73-H、A75-D、A77-S的私有`FINAL_READBACK.json`仍在；本轮结果分支保存四份原样小文件副本及路径/字节/SHA绑定。A70-P临时目录为空，readback未找到；固定Git报告和receipt保持可用。
3. A4-N文字缺损已由现场字节再次确认：全ASCII、2,334个`?`、固定SHA一致。有界搜索未见真实可读V2。导航应保持`PARTIAL_DOCUMENT_INTEGRITY`，只引用A5受限独审，不能把文档传输哈希通过改写成完整文本接受。
4. A77-S源审资格仍是`MODEL_AUTHORITY_NO_GO / PAIRING_NOT_ESTABLISHED`，0准入资源轴/0pilot。只登记AWMA已发表framework/config/binary身份；实际外部performance core和与自然强native的配对未闭合。不能从源码路径存在推出模拟器准入或GPU硬件性能负例。
5. 工作流bootstrap固定GitHub记录可读，手动模板有范围可复用；旧CLI Skill自动发现未验证，174节点当前未定位该commit对象/工作树。无需把它列成174科研实验。

## 应保留的当前主线保护

用户确认Main=`AI-ARCH交接-1`正在执行`AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1`。其启动HEAD、资源准入、进度和formal数待Main实际回报；不从旧导航快照推断停止，也不由174窗口查询109或新增验收门。Q1原执行authority保持`5787826ca21f7af958e6e1c1f828d62fd58a1ec4`。174本轮没有新native/GPU/模拟器结果，无新硬件候选晋升。

## 建议导航落点

将本结果分支的固定`TAKEOVER_REPORT.md`与`NODE_TASK_ASSET_INDEX.json`加入AI-ARCH导航的“174-new历史与节点资料”入口，并注明本轮`CPU_ONLY_TAKEOVER / A4-N_PARTIAL_TEXT_GAP / STOP`。A21旧资产缺口应继续受109后续Q1事实更新；A45-S旧CAGRA建议与A58旧GNN提案均不恢复。科学判断仍以各原执行commit、独审和更晚同范围authority为准。本提案不请求合并旧执行分支、不重启任何旧Goal。
