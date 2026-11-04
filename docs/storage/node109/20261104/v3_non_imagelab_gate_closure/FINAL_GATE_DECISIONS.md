# Node109 非 ImageLab 三类 HOLD 有限闭合 — V3

基线：V2 冻结 HEAD `0915c630a740dc863505ce86012440be322117cb`。本轮没有删除、移动或修改 109 Source，没有处理 ImageLab，也没有运行科研实验或修改科研台账。仅对 R27 三份文件与真 164 的 R26 规范父本作定向全文 SHA；StageA 复用 V2 的双端 SHA，只刷新三份权重身份。

| 对象 | 当前物理回收量 | V3 决策 | 依据与未闭合门槛 |
| --- | ---: | --- | --- |
| StageA 三份 `.safetensors` 权重 | 8.250 GiB（8858648576 B） | `HOLD_SCIENTIFIC_OWNER` | V2 双端 SHA 已通过，V3 inode/mtime/大小未变；四份 copyback 为 PASS，但总状态仍为 `RUNTIME_QUALIFICATION_PARTIAL`。尚无科研 owner 对续行、109 即时读取和按需恢复的明确答复。保留其余 21 文件、收据、配置、tokenizer、目录与科学控制记录。 |
| AWMA 三处 `pip/http-v2` | 8.493 GiB（9119387648 B） | `READY_FOR_USER_RETIREMENT_APPROVAL` | 936 个单硬链接文件、无软链接；468 份元数据均属于公开 PyPI 包或 Simple 索引；156 份索引中所有下载 URL 指向公开文件站。现有环境与缓存 inode 分离，6 个本地直装来源仍在，当前未见 pip/构建进程或精确缓存 FD/mmap。删除前仍须复核文件集合和读取者。 |
| R27 三份 `COMMON_POST_BOOTSTRAP.pt` | 7.339 GiB（7880097792 B） | `HOLD_SCIENTIFIC_OWNER` | 三份当前 Source、真 164 R26 规范父本的全文 SHA 均为 `09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55`；R26 发布清单 SHA 符合历史凭据，R27 三份发布记录指向该父本。用户已认可按需恢复策略，但明确说这**不是**科研 owner 的删除资格批准；Lane U174 使用意见待到。R26 父本及 R27 其他 checkpoint/raw/结果不动。 |

因此当前**可请求最终删除授权的精确集合**只有[三处 pip HTTP 缓存](NEXT_APPROVAL_READY_WHITELIST.csv)，预计释放 8.493 GiB；这不是 unlink 授权，也不是已经实现的 `df` 增量。两类科研资产共 15.589 GiB 仍 HOLD。V2 的 24 文件 StageA 草案已修订为仅 3 个权重候选，详见 `STAGEA_WEIGHT_ONLY_CANDIDATES.csv`。

恢复方式：缓存从公开 PyPI 重取，已安装环境和本地直装包来源保持；StageA 如获 owner 同意，从真 164 的精确 revision 恢复三个权重至原路径并核 SHA；R27 如获 owner 同意，从真 164 R26 规范父本逐个恢复到三个原路径并核 SHA。没有在本轮实际执行恢复复制。

读者边界：当前未见精确路径的活动进程或 FD/mmap，但 StageA 快照有 415 个 FD、107 个 maps 视图不可读；缓存快照有 416 / 105 个。不能声称全用户绝对闲置。缓存 READY 是**请求用户授权的资格**，实际操作前必须再次确认没有匹配读取者且清单未漂移；一旦命中则转 HOLD。StageA 与 R27 的 owner 资格没有借空 FD 推断。

公开仓库用占位符替换私有账号/主机；精确相对 revision、源 inode、SHA 与清单摘要保留，私有原始证据 SHA 记录在 JSON。完成本轮发布后 STOP，等待 ChatGPT 审核下一步清理范围。
