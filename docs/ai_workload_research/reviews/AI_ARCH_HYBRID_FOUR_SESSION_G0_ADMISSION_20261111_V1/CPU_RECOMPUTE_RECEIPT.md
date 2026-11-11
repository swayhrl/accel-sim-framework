# CPU 复算收据

- 固定 V2：commit `d058d4faf2d93e31976888808a608c4a8fa46714`；tree `fd6085fe75179143a764ed8aa050ef10a37112eb`。
- 代码：同目录 `g0_cpu_check.py`；在 109 独立工作树运行。完整命令使用本地 DuckDB 工具目录 `PYTHONPATH=/data/c16/aiarch_hybrid_asset_qualification_20261110_v1/tools` 和 `/data/c16/envs/aiarch-vllm-main-ca3c154d-v1/bin/python`，输入固定本地资产，输出本目录的 JSON 与私有 0700 目录。
- 环境：Python 3.12.3、DuckDB 1.4.1、Transformers 5.22.2、`Qwen3_5Tokenizer`。tokenizer.json SHA-256 `5f9e4d4901a92b997e463c1f46055088b6cca5ca61a6522d1b9f64c4bb81cb42`；tokenizer_config.json SHA-256 `316230d6a809701f4db5ea8f8fc862bc3a6f3229c937c174e674ff3ca0a64ac8`。
- 数据文件 SHA-256 `2023b66a16cf095fcd3686e10259dc089eca95f739fa1c863b07af56029f9f00`；231,061,961 字节。候选/探索/保留数 27,628/22,079/5,549；四条选择承诺 `a5f4cfb551054561d6353d096143679bb8603c7ab0a2831d5f409ea86feee701`。首轮与旧 GPT 诊断 token 计数均与原 V1 固定列表逐项一致。
- 脚本只读取 Parquet、tokenizer 文件及四条必要消息；没有 CUDA 调用、完整模型加载、网络下载或 GPU 工作。初次本地运行暴露 chat template 返回类型差异，已改用 `return_dict=True` 后重新完整复算；最终输出以本次成功结果为准。原失败不涉及数据或 GPU。
- 私有审阅文件 `review_cases.json` 只在 109 的 `/data/c16/aiarch_hybrid_four_session_g0_private_20261111_v1`，目录 0700、文件 0600，未发布 Git。
