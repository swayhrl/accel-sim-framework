# 接班操作、节点资产与安全边界

## 1. 环境与Git

本地用户环境：Windows，D:\repo，PowerShell。科研主节点109：
```text
ssh huangrulin@10.156.120.109
cd /home/huangrulin/workspace
```

仓库共享对象库：/home/huangrulin/workspace/accel-sim-framework。
该主worktree在交接检查时位于其它C16协调分支，**不要在这里checkout/reset/stash/清理**。新任务使用独立worktree/branch。

推荐只读启动（以下在SSH后的Linux shell中运行）：
```bash
repo=/home/huangrulin/workspace/accel-sim-framework
git -C "$repo" fetch origin hrl/aiarch-new-window-handoff-109-20261109-v1
handoff_sha=$(git -C "$repo" rev-parse FETCH_HEAD)
git -C "$repo" rev-parse "$handoff_sha^{tree}"
git -C "$repo" show "$handoff_sha:docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1/README.md"

git -C "$repo" fetch origin hrl/ai-workload-research-coordination
coord_sha=$(git -C "$repo" rev-parse FETCH_HEAD)
git -C "$repo" rev-parse "$coord_sha^{tree}"
git -C "$repo" show "$coord_sha:docs/ai_workload_research/CURRENT_STATE.md"

git -C "$repo" fetch origin hrl/aiarch-q1-scientific-completion-109-v1
git -C "$repo" rev-parse FETCH_HEAD
git -C "$repo" rev-parse FETCH_HEAD^{tree}
```
Q1应核5787826ca21f7af958e6e1c1f828d62fd58a1ec4 / a070243a93fee5594dd88d515f08e228677ebf75。handoff与协调若有新提交，先保存实际identity和diff；不要把本包记录的HEAD当永远最新。

新审查worktree示例（先确保名字未用）：
```bash
git -C "$repo" worktree add -b hrl/aiarch-handoff-independent-review-109-v1  /home/huangrulin/workspace/worktrees/accel-sim-aiarch-handoff-independent-review-109-v1  "$handoff_sha"
```
不要merge历史执行HEAD。显式git add限定本任务路径；不用git add . / -A，不force push，不修改第三方runtime。网络认证必要时沿用已有gh auth git-credential helper；不要输出token/credentials或私有环境变量。

本地AGENTS.md标题为VM/TLB，明确适用于hrl/vm-core-v0及其VM/TLB后代；不能将其分阶段仿真任务误作为AI-ARCH当前Goal。新worktree仍应读所有实际适用的AGENTS和任务协议；若scope发生实质冲突，按具体授权处理，不能直接忽略。AI-ARCH主要协调规则为docs/ai_workload_research/COORDINATION_PROTOCOL.md。

## 2. 最新Q1完整工作区与数据

```text
执行worktree：
/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109

分支：
hrl/aiarch-q1-scientific-completion-109-v1

OUT：
/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1

TOOL：
/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109/util/ai_workload_research/q1_3dgs_completion

W2：
OUT/windows/W2
```

三份真实完整状态：
- OUT/.private/STATES/C_D，next15140；
- OUT/.private/STATES/C_V，next15240；
- OUT/windows/W2/.private/STATES/C_FINAL，next15301。

均由本次仅做存在性+MANIFEST路径核查确认仍在；完整SHA与科学资格以固定PUBLIC/PRIVATE索引、STATE_INDEPENDENT_INSPECTION.json及实际GPU恢复收据为准。交接没有再次完整hash19.5GB。原.raw/STATE_*_MANIFEST.json是保存时公共收据；sidecar和owner在状态目录同级。不要修改、补造、移动、删除这些既有状态。

主要私有raw：
OUT/.private/JOBS/PRODUCE_LATE；
OUT/windows/W2/.private/JOBS/<job>/；
每个job有REQUEST、WORKER_IDENTITY、RESTORE_INITIAL、RESULT、REGIONS、TRANSFERS、GPU_EVENT_SPANS、TERMINAL_READY/ACK等（具体依实际模式）。
Resource journal原字节在各.private/RESOURCE_SAMPLES.original.jsonl，Git中有lossless .gz与identity。大chunk不在Git。PRIVATE_RAW_INDEX.json固定全路径、长度、SHA，共约19.5GB retained private payload。

根RESOURCE_RECEIPT.json是W1原始RESOURCE_STOP；W2原收据为windows/W2/RESOURCE_RECEIPT.json，NATIVE_Q1_MATRIX_COMPLETE。整体终态是根RECEIPT.json的NATIVE_Q1_LATE_PIPELINE_COMPLETE。不要看到W1文件就误判最新Goal未完成。

历史Q1 worktree均在同一worktrees父目录：
accel-sim-aiarch-q1-3dgs-continuation-contract-109-v1；
accel-sim-aiarch-q1-3dgs-late-pipeline-native-109-v1；
accel-sim-aiarch-q1-3dgs-late-pipeline-r1-109；
accel-sim-aiarch-q1-cpu-hardening-109；
accel-sim-aiarch-q1-r2-109。
旧C_E/C_R_E在V1 OUT/.private/STATES，分别next5/8，不能与最新C_D/C_V混称late。

## 3. 合法原资产与环境

GS-Scale原资产：
/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014
- software_sources/gsscale/examples/simple_trainer_hybrid_optimized.py
- software_sources/gsscale/cpu_adam/cpu_adam.cpython-310-x86_64-linux-gnu.so
- scene及scene/images_4_png（1678张接受的预处理图像）
- venv/bin/python（Python3.10.12、Torch2.2.0+cu121、IPEX2.2.0、NumPy1.26.4、psutil6.0.0）

运行旧GS Python通常需：
LD_LIBRARY_PATH=/data/c16/env/cpython-3.10.12/lib。
未加时加载libpython失败不是环境已损坏，不因此重装。

监督器Python：
/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python。
它在Q1只提供psutil/NVML绑定；这不表示GS使用vLLM模型runtime。

原trainer SHA：
17e70b6466f7e33a24d1610aa7deb69316cd177dc2c212cd8b717b9884f4808a
CPUAdam C++ SHA：
f3f32bc04f61749baf57d1bd877b24379597e50cf4a94d04fdde80a11c19ce9f
CPUAdam binary SHA：
c451fda99327e5969da9f0476ef3f4915815dc9ff314c22cce002e5551379a55
renderer实际私有so记录在BINARY_IDENTITY.json。接受的AlexNet evaluator已在private Torch cache，不重新下载权重或重建旧环境。

只有读取Git/json和轻量CPU审查时，不运行Torch模型、JIT、CUDA或NVML初始化。CPU分析可用原已安装NumPy；不能随意执行旧worker/supervisor：它们会读固定OUT/CFG并启动GPU或写原目录。

CPU复算正式统计可仅使用标准库csv/statistics读取固定FORMAL_SAMPLES.tsv；按phase/policy分组5个closed_window_wall_seconds算median及MAD，检查valid=True、actual_steps=51，保留全部20行。

## 4. GPU共享协议：历史身份不等于今天白名单

唯一共同锁：
/data/c16/locks/c16_gpu_campaign.lock
实现fcntl.flock(LOCK_EX|LOCK_NB)，非lockf。单owner覆盖CUDA初始化、模型、子进程、同步/terminal握手、context清理至放锁/预约释放。不等待冲突锁，不kill/暂停/调优其它项目。

实际Image-Lab状态入口历史为http://127.0.0.1:8188/gpu-sharing/status。
当前工具shared_gate.py/shared_lease.py包含challenge/no-store/age校验、loaded modules/functions hash、实例身份、nonce、kernel holder、reservation、quiescence与异常状态验证。任何新执行都重新验这些实际条件，不能凭静态JSON、空队列、0%利用率或小显存批准。

历史验收信息仅用于回查：
- GPU RTX4080，UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59；
- Image-Lab source761ab4f22690f6305b7f903e15a99cc685382a1b；
- 审计4bcee3fe8d0f82a891d67818cd02d8c580dbe6fb；
- 当时ComfyUI PID3518111、UID1004、start_ticks442348560；
- restricted profile，禁用若干H3/Ollama路径；
- 历史Windows收据路径D:/repo/image-lab-gpu-sharing-v2.1/，存在性/时效不能假设；
- 旧cache/gpu-validation.lock不等于共同锁，不能拿它替代；
- 历史普通compute PID3246996不是可放行的固定白名单。

允许VERIFIED_GATED_RESIDENT_CONTEXT仅当实际代码已加载、全部GPU入口被锁门控、当前无GPU执行且child/drain闭合。桌面共存及逐进程activity遥测缺口必须记录；不等于绝对无干扰。不要重部署Image-Lab或重复canary；身份变化若缺生产验收，先停止GPU准入，向资源所有者核实。

admin配置路径与SHA已在历史EXECUTION_BINDING.json中，凭据只在既有API请求内使用，不复制到交接、日志、Git或聊天。

## 5. 资源：历史授权与物理保护分开

原Q1 V1/R1/R2资源上限8h Goal、3h持锁、14GiB显存、40GiB sampled RSS、48GiB charged、64GiB新增盘、free32GiB、训练≤16logical/监督≤2logical。旧单窗口规则亦保留在各版STOP中。

后来用户明确允许109接续并解除该执行原预算。最新Goal实际配置24h/23h运维看门狗、训练8–21/监督22–23、Host MemAvailable≥10GiB、free≥32GiB、charged guard参考节点MemTotal约62.4GiB、NVML15GiB、Torch allocator仍13GiB，checkpoint上限由当时内存/盘余量约45.3GiB决定。RSS大哨兵值仅解除逻辑sumRSS预算，不能解释成节点有1TB内存。具体以RESOURCE_CONTRACT和各cfg为准，不拿历史snapshot当新空闲承诺。

实际两窗口GPU累计4537.190s（75m37s），峰值NVML3778MiB、sampled RSS23.367GiB；session charged峰值27.255/16.915GiB。容量未触及旧数字，但顺序窗口与监控协议在新授权下修正；不能因此说旧单窗口合同其实通过。

新窗口接班文档本身不扩大权限。对未来新科学Goal，明确资源所有者当前窗口和实际CPU/内存/cgroup/盘/GPU可用性；保持物理安全，不用“解除限制”绕过未知竞争、身份、数据许可或数值规则。没有授权不启动GPU、下载、安装、全局时钟/功率/权限调整。

## 6. 跨项目与工具使用

不访问164，不恢复174 simulator。C16、AWMA、EP-L2、DTC-L1、VM/TLB是独立项目，仅读固定公开证据，不看它们活动GPU raw、不清旧cache/模型。主repo有大量其它worktree，不等于允许接管。

Linux远端可能无rg；文件搜索优先rg，若确无则用git ls-tree/固定路径/少量Python查询，不做全盘扫描。Windows调用远端Python可用PowerShell here-string经ssh stdin；中文可能受本机编码影响，生成UTF-8内容时用明确编码/Unicode escape，最后检查U+FFFD。csv输出用LF，避免CRLF使git diff --check报尾空白。JSON.stringify不是shell escaping。

同Goal普通路径/API/日志/receipt错误有界修复；实质模型、precision、quality、强后端或共享资源合同变化单独明确。任何时刻只一个GPU dispatcher；CPU子任务也共享真实资源，别让多窗口同时写CURRENT_STATE/manifest。

## 7. 结束验收

每次实质交付：精确commit/tree、显式路径staging、相关测试及diff --check、push/fetch-back、remote ref/commit/tree与文件blob/字节核验、worktree clean。大raw留private加完整SHA，不通过把raw改名为PASS使任务结束。观察时段不完整、无法校准时钟、退出码未记录必须如实保留。

本包只核身份、文件入口与状态存在性；不启动任何锁、模型、GPU或后台Goal。后续审查应新建自己的工作区，禁止原样运行本包里任何历史执行命令。
