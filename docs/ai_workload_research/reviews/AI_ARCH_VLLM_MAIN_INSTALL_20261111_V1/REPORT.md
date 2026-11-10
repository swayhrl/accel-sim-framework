# AI-ARCH｜109 Qwen3.5-4B 独立 vLLM main 环境安装回执

日期：2026-11-11（109 本地时间）。范围：安装和 CPU 侧检查。承接固定资产资格报告 `8e836c7bb0b0428fe2c04630ef21ddf6b9d3269f`；固定模型 `Qwen/Qwen3.5-4B@851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`。模型卡 `sources/Qwen_README.md` 的 vLLM 段要求 main，并给出 `--language-model-only` 纯文本模式。

## 结论

**`INSTALL_COMPLETE_CPU_CHECKED / GPU_RUNTIME_UNTESTED`。** 109 上新建隔离环境 `/data/c16/envs/aiarch-vllm-main-ca3c154d-v1`，安装 vLLM nightly `0.34.0rc1.dev167+gca3c154d2` 及完整解析依赖。wheel 的固定路径含源码提交 `ca3c154d26749c2b59d9d99050d2bd631d2c63f7`；安装后的 `direct_url.json` 与该路径一致。未覆盖共享 `/data/c16/envs/c16-vllm-v0.30.0-sm89-v1`，其 vLLM 仍为 `0.30.0`。

安装使用官方模型卡所示的 vLLM nightly 索引和 `uv --torch-backend=auto`，以固定 wheel URL 指定主包。依赖解析结果：`uv==0.13.7`、`torch==2.14.0+cu132`、`transformers==5.22.2`、`triton==3.8.0`，完整 201 行环境冻结清单见 `freeze.txt`；其 SHA-256 为 `04f8c8017e53433a54d0e92df9492c9557836c449dfbfaf19c5287088274b240`。`pip check` 输出 `No broken requirements found.`。安装命令和离线检查脚本一并归档。安装源包括 PyPI、uv 自动选定的 PyTorch CUDA wheel 索引和固定 vLLM nightly URL；没有额外镜像替换。

## CPU 侧证据

| 检查 | 结果 |
| --- | --- |
| vLLM/PyTorch 导入及版本 | PASS；`verify.json`。检查进程 `torch.cuda.is_initialized() == false`，环境隐藏 CUDA 设备。 |
| 固定配置的架构入口 | PASS（静态）；固定 `config.json` 指向 `Qwen3_5ForConditionalGeneration`，本安装的 registry 有对应入口，也有 `Qwen3_5ForCausalLM`。 |
| 纯文本入口 | PASS（静态/CLI）；`vllm serve --help=all` 在 `VLLM_TARGET_DEVICE=cpu`、`CUDA_VISIBLE_DEVICES=-1` 下退出 0，列出 `--language-model-only`；配置源码含该字段，Qwen3.5 类声明多模态裁剪支持。此 CLI 仅显示帮助，没有启动服务。 |
| 依赖 | PASS；`pip check` 无缺失或冲突。 |
| 原共享环境 | 保留；原 vLLM `0.30.0`。 |

默认 CUDA 平台配合 `CUDA_VISIBLE_DEVICES=-1` 运行 CLI 帮助时，在 NVML 设备索引查询处以 `NVMLError_InvalidArgument` 退出。改为 `VLLM_TARGET_DEVICE=cpu` 后帮助命令退出 0；这是纯 CPU 入口检查所需的环境设置，不是 GPU 服务成功。CPU 帮助的 stderr 还报告未找到 `vllm._C_AVX2`，CUDA wheel 未在本轮用于 CPU 推理。这些诊断原样留在 109 私有安装目录。

## 边界和后续门

109 驱动 `580.178.04` 的 `nvidia-smi` 报告 CUDA `13.0`，本次 `uv --torch-backend=auto` 解析出 `cu132`。安装和 CPU 检查不能证明该组合在 SM89 的实际算子、GDN prefill、FlashAttention、vision 裁剪、模型加载、完整生成、数值、质量或容量通过；驱动与 wheel 的实际动态兼容也仍待验证。**`RUNTIME_VERSION_GATE_OPEN` 缩小为“main 安装已固定，GPU 原生动态验收未完成”。** 当前仍为 `NO_GPU_PROBE_READY`，不把静态入口升格为科学结果。

本轮没有初始化 CUDA、加载固定 checkpoint、运行 Runner/服务、训练、Profiler 或 GPU 实验；没有更改固定权重/会话和协调分支。未来如要动态验收，需另立明确 GPU Goal、当前 109-AI-ARCH 资源窗口，并遵守 Image-Lab 共同 flock、预约、loaded gate 和实时身份准入。失败时保留原负结果，不以降精度或换模型绕过。

私有安装与日志：`/data/c16/aiarch_vllm_main_install_20261111_v1/`。公开 Git 只收小型脚本、冻结清单、CPU 回执和本报告；不收 wheel、缓存、模型权重或原始会话。
