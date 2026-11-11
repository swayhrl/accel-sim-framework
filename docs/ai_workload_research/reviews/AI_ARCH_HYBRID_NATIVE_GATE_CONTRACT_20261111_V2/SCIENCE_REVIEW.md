# AI-ARCH-5｜Draft PR #2 科学合同审查与V2修订理由

**裁决：REVISE，不接受V1原文直接派发GPU；V2仅为固定待授权设计。** 固定PR原head `d750e4a7d3477f93198f419b7682756ab661c88f`。V2合同见同目录 `REVISED_CONTRACT.md`。原V1保持历史不覆盖、PR保持Draft。此审查没有批准任何GPU窗口。

### ① 对象语义：有限接受
四个自然WildChat user对与Qwen自生成assistant组成的是**Qwen反事实自续对话**，不是自然Qwen生产会话。原WildChat GPT回答不能进入模型，也不是质量gold。第二轮user可能依赖GPT独有内容。V1只作消息结构/无redacted/toxic筛选，无法识别这种依赖或未标注PII。因此V2增加GPU前的固定四条私有源内容/权利/依赖审查；任一不适用则不运行、不换样本。原四条hash选样主要用于发现技术可行性，不能称为代表性质量样本。

### ② 参数与运行时：有条件接受，补充硬资源与PTX门
BF16、TP1、LM-only、max-model-len8192、max-num-seqs1、0.85服务配额、四会话×两次、每次256输出token和30分钟单锁窗口，作为**技术资格上界**可保留。但0.85不是实际设备安全界，需 own GPU≤14GiB、Host/charged/disk及当次资源owner时段许可。输出截断不是“质量坏”，也不能算技术完整PASS。

NVIDIA CUDA 13.x支持driver≥R580的**有限**minor兼容；CUDA 13.2对应完整发行驱动R595，PTX JIT/新driver API可能在R580失败。109的 `580.178.04` + `torch cu132`不是仅凭版本即必败，也**绝非静态PASS**。只有获准GPU窗口内先基本CUDA同步、实际SM89 Triton/PTX/GDN后端、再完整模型装载的逐门fail-closed验收，才能在有界范围内获得动态资格；失败不升级驱动、不换wheel、不自动降级或再申请第二锁窗口。

主要外部核对来源：
- <https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html>
- <https://docs.nvidia.com/cuda/archive/13.2.0/cuda-toolkit-release-notes/index.html>
- <https://docs.vllm.ai/en/latest/cli/bench/throughput/>（gpu_memory_utilization为单实例的配置）
- <https://docs.vllm.ai/en/stable/features/reasoning_outputs/>（请求级enable_thinking与parser边界）

### ③ 四条独立质量门：V1不充分，V2已定义
V1的单人/单项accept-reject-indeterminate未规定独立性、原GPT依赖、评审盲法、分歧、截断处理和“质量PASS”的推断范围。V2定义G0源适配与隐私门，G3技术完成门及G4至少两名有权限的独立盲评者、四维逐项结果、分歧第三方仲裁；不具备合法评审者则保留QUALITY_GATE_OPEN。全部四条通过，也只能登记 `LOCAL_4_SESSION_CONTEXTUAL_ACCEPT`，不进入后续机制研究。

### 仍需授权
本提交只修改科学设计，不是新的GPU Goal。109-AI-ARCH保持 `NO_GPU_PROBE_READY / STOP`，直到用户明确派发固定V2且当次资源owner同意。不得以更新PR、成功push或本审查评论解释成允许CUDA初始化。
