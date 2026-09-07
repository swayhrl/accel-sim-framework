# C4：已提交版本的受限真实 Llama 回放

状态：`PASS — SPECULATIVE_CANDIDATE`。这不是正式 M4B 结果。

最终受限回放固定为 decode1 compute-only 的前 3 个连续 kernel，所有运行在低优先级
独立 scratch 下完成。Framework `5dd4501a51720a959129860b72988a6961b07477`，
Core `c21137bcb86010215c008292f272aacefac175d3`，二进制 SHA-256
`6a40636e76b33f7f3622e175144379febf8d018b9e3e93d1e62d7c8383fb74fd`，本地 runtime
SHA-256 `20d1c446391c2f6da4f764ab3904b2b236f7571ad8511f4bf0c68a5607297b7e`。

| 配置 | 退出 | 关键观察 |
| --- | --- | --- |
| standard paper | 0 | L2 mode 0；末段累积 L2 34 access / 2 hit / 32 miss |
| sub-entry | 0 | L2 mode 1；末段同为 34 / 2 / 32，候选未改变该段前端语义 |
| sub-entry + Weight Segment | 0 | 1,539 次 Segment launch，512 hit、1,027 miss、512 次 L2 suppression；末段 L2 18 / 2 / 16 |
| ideal diagnostic | 0 | 诊断配置正常完成 |

四个 profile 的 `m4c_telemetry_frontend_(instruction|transaction)` KERNEL 记录均为
75 行，且 SHA-256 相同：
`0df818636951396dd2297f261038351e309f4616ad0c7ede9b04d6e77a89839e`。这为本次受限
输入上的 data/store/atomic 前端 exact-once 保持提供运行时交叉检查；它不替代全 ROI
验证。

运行 manifest 分别位于 scratch：paper
`3dfcf2932576027d2a2a4abcabc2e45155c24aee1e60ec3f8aeecb1b0dfb447e`、sub-entry
`5fedd19e0e9b3f7c12c53a8bca0432f5243f64550f15a5170d7ac8612d414fc9`、segment
`83b3bdb80db5c351196a87495d4da04c66a9b052da1c45a06c0b7bd4feef9035`、ideal
`637b8f5568869cbe1b7e88f3fc0555e791e4bd663041cf419edae4a3d87a1c80`。每个 log 已导出
为 provenance-bound telemetry TSV。
