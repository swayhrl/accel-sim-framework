# 109-STORAGE-API 下一批非 ImageLab 精确回收：完成报告

Goal：`NODE109_API_NEXT_BATCH_RETIREMENT_V1`。客户端执行日期：2026-11-10；109 节点回执时间：`2026-11-09T17:09:46+00:00`。本轮只处理 A→B→C 五组，没有重做 S109 V1–V4 审计，也没有启动或停止科研任务。

## 执行结果

| 组别 | 状态 | 文件 | 逻辑字节 | unlink 文件分配量 | 空缓存子目录移除 |
| --- | --- | ---: | ---: | ---: | ---: |
| A StageA AWQ 权重 | DONE | 1 | 2,686,704,624 | 2,686,709,760 | 0 |
| B R27r2 独立 B1 checkpoint | DONE | 1 | 2,626,691,236 | 2,626,699,264 | 0 |
| C R19 pip HTTP-v2 | DONE | 286 | 3,737,919,097 | 3,738,615,808 | 557 |
| C R17 pip HTTP-v2 | DONE | 198 | 2,449,608,785 | 2,450,063,360 | 393 |
| C VLA pip HTTP-v2 | DONE | 452 | 2,922,307,770 | 2,923,360,256 | 841 |
| **合计** | **DONE** | **938** | **14,423,231,512** | **14,425,448,448** | **1791** |

每个文件都有持久化 INTENT、临删身份复核、非递归 unlink 和持久化 DONE；938 条 INTENT 与 938 条 DONE 和冻结白名单完全一致。独立回查确认 938 个源文件全部不在，三处 `http-v2` 根目录仍在且为空；仅移除清单中已空的子目录。

## 资格、恢复与保护

- A 的原本地普通单硬链接文件身份与 V3 冻结行一致，V2 已对本地与真 164 做过全文 SHA。真 164 AWQ 原 revision 的 `model.safetensors` 当前仍为 2,686,704,624 B；恢复时按清单 SHA `ff45904d41a1fe1ee1d3678d8b04e65d6270d04c05ab38ed3f68d41f121ed6d2` 放回原绝对路径，并复核 config/tokenizer/receipt。StageA `RUNTIME_QUALIFICATION_PARTIAL` 没有改写。
- B 使用自己的真 164 `r27r2.../checkpoints/B1_C1_K2.pt`。独立发布 manifest 和当前两端定向 SHA 均为 `442dbb3af9978488150c5296d4b6e4d23d254511f09f0239f9732813dca6729a`；恢复到本地原绝对路径。没有使用 R26 COMMON 父本或三份已删 COMMON 的回执。
- C 严格按 V3 的 936 个历史普通单硬链接缓存文件 manifest；前后身份稳定。其来源为公开 PyPI HTTP 响应，保留已安装环境版本元数据及本地 direct-url 源。删除后这批离线 HTTP 缓存已失去；未来公开包可用性没有永久保证，本轮未重建环境。
- 当前未见这五组目标的命令行、FD 或 mmap reader，也未见 pip/build 进程；其他用户 FD/maps 有权限盲区，但未见相关命令行进程。现场未发现已授权排队任务指向这些精确对象。检查为本轮时点，不代表未来使用状态。
- StageA BF16 两权重、R26 规范 COMMON、R27 B0 两原始张量均复查仍在。ImageLab、E1、A26、A61/A65/A67、环境、wheelhouse、其他 checkpoint/raw 和此前已 DONE 的 38 文件没有纳入本轮；真 164 和 174 Source 均未修改。

## SSD 空间核算

109 的 `/data/c16` 与 home 共用 `/dev/nvme0n1p2` ext4 根盘。任务控制记录开始时 `available=118,092,693,504` B，worker 结束时 `available=132,523,786,240` B，**实测可用空间增加 14,431,092,736 B（13.440 GiB）**。逻辑文件字节为 14,423,231,512 B，unlink 文件分配量为 14,425,448,448 B；df 差异还含空目录元数据、控制记录及并发写入，不能逐字节全归因于文件。

本批真 164 是经 174-new 的现有 `<ARCHIVE_SERVICE_ACCOUNT>@<TRUE164_PRIVATE_IP>:/home/shared` SSHFS 挂载核实的归档，绝非 174 本地 shadow。完整逐文件身份、INTENT/DONE 时间及缺失回查在同目录 CSV；控制目录各记录 SHA 和 df 前后在 JSON 回执。公开文档只含脱敏路径和小型元数据。
