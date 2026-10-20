# C16-Storage-Audit — 原174外发六分片只读审查

审查时间：2026-10-20，Asia/Shanghai。结论：六文件均为 **HOLD**；本轮可授权释放字节 **0**。潜在权重净大小 20,802,101,648 B（19.373467 GiB）；可见分配上界 20,802,138,112 B。没有源删除，实际释放收益为0；整体df同时受其他工作影响，不能据此认领收益。

| 文件 | 大小 B | 真164当前SHA | 结论 |
| --- | ---: | --- | --- |
| P2 / `model-00001-of-00004.safetensors` | 3,945,441,440 | PASS，复用 | HOLD |
| P2 / `model-00002-of-00004.safetensors` | 3,864,726,352 | PASS，复用 | HOLD |
| P2 / `model-00003-of-00004.safetensors` | 3,864,726,424 | PASS，复用 | HOLD |
| P2 / `model-00004-of-00004.safetensors` | 3,556,377,672 | 待Lane T全文核验 | HOLD |
| P3 / `model-00001-of-00002.safetensors` | 3,996,422,976 | 待Lane T全文核验 | HOLD |
| P3 / `model-00002-of-00002.safetensors` | 1,574,406,784 | 待Lane T全文核验 | HOLD |

完整绝对路径、真164路径、每文件SHA256和数字元数据见 [RESTORE_MAPPING.tsv](RESTORE_MAPPING.tsv)，逐文件最小解除条件见 [AUDIT_RECEIPT.json](AUDIT_RECEIPT.json)。HOLD包含缺失必要证明；六个未来保留决定的子状态均为UNKNOWN，没有足够证据把任一文件升级为RELEASE_CANDIDATE。

## 已闭合的事实

- 已从GitHub读取指定Owner JSON与BA TSV；远端分支实际HEAD仍为Owner `8c238970`、BA `061e9fb3`、Lane T `883f4a4b`。原A/G分支HEAD分别为 `59410860` / `73850d93`。精确记录见 [REMOTE_HEADS.json](evidence/REMOTE_HEADS.json)。没有采用其他迁移窗口的同名路径。
- 当前原174为 `huangrulin-174` / `mnt:[4026534768]`，六文件dev=156、inode、nlink=1、0600、0:0、大小、分配块、纳秒mtime/ctime均匹配BA及Owner身份。版本RAW=`a09a35458c702b33eeacc393d103063234e8bc28`，AWQ=`b25037543e9394b818fdfca67ab2a00ecc7dd641`。
- 原174当前 `EXPECTED_HASHES.tsv`、历史交付回执和Owner/BA的六个大小/SHA完全一致；原174留存的两份交付回执与已公布回执逐字节一致。P2、P3状态均为 `TRANSFER_HASH_CLOSED`。这是历史SHA身份链；本轮没有全文读取源权重，**当前源SHA未测**，不能写成当前SHA PASS。见 [IDENTITY_JOIN.json](evidence/IDENTITY_JOIN.json)。
- 当前监督器PID280466、start_ticks597941679仍在线；实际脚本与A固定提交相同，读取 `c16_assets` 原件和immutable receipts。它不自动发布外发包，也不接管下载生命周期。114个可见进程的检查未发现六文件FD、C16打包或传输任务；这只回答当前可见消费者，不能关闭远端/未来队列。
- 126个包内其他文件已记录SHA并保留；模型原件、109状态、监督器、TLS P9、EP-L2 E2及配额/租约均未改变。
- Lane T已证明真164六文件均有匹配大小的候选；RAW1–3有当前全文SHA PASS，后续回执复核元数据未变。本轮直接复用，没有重哈希或复制。RAW4/AWQ1/AWQ2剩余9,127,207,432 B，仍只需在原C16门禁放行后核验，不需要补传19.374 GiB。

## 依赖与权限缺口

1. **A/G保留职责未关闭。** 历史交付成功、V10配对比较闭合均没有授予原174外发副本退役权。未来合同要求精确版本权重，未证明必须使用原174外发路径，也未证明原始外发包从此无职责。需要A/G对本清单六条精确路径的补传、109 provisioning、恢复及保留义务作出明确决定；没有推定整个C16结束。
2. **109现存副本未确证。** 用现有 `gpu109` SSH入口只读检查，返回主机PC / namespace `mnt:[4026531832]`；V8脚本固定的六个 `/data/c16/models/.incoming/...` 路径当前均ENOENT。仅检查这两个模型的根目录名字，没有扫描其他大模型。该结果不等于109没有其他副本，也不等于一定要保留本外发包；需要109/A/G确认当前权威路径或现有补传恢复安排。见 [NODE109_BOUNDED_READONLY.json](evidence/NODE109_BOUNDED_READONLY.json)。
3. **剩余164完整性由Lane T闭合。** 最新公布门禁回执在2026-10-19，SSHFS执行路由174主机IO avg10超过10，因此停读；本窗口没有174-new或native164命令入口，不能把原174今天的低PSI当作Lane T当前放行。RAW4的旧738,197,504 B前缀不是完整SHA，也没有可续算状态，须从0全文计算；不重算RAW1–3。
4. **当前源字节身份未全文核验。** 本轮快审沿用不可变回执与精确元数据，不制造当前SHA。源释放执行方案前仍须在现有IO门禁下补齐原174源SHA证明。计划任务工具也受容器可见性限制：crontab不可用、systemd非PID1，不能声称已排除宿主机或远端计划任务。

## namespace与恢复

原174的 `/root/share/mnt164` 实际落在 `/root/share`、`/dev/md127`、ext4本地Share，**不是真164**。Lane T固定回执中的174-new则是 `huangrulin-sshfs-174` / `mnt:[4026535153]`，同名挂载为 `fuse.sshfs`、`admin-wcx@10.208.130.164:/home/shared`。真164路径必须使用映射表的 `/home/shared/...`，SSHFS显示的1011:1011/0777及秒级时间不能覆盖原174的0:0/0600与纳秒mtime。

[RESTORE.sh](RESTORE.sh) 默认仅打印六条计划，无模型读写。未来获单独恢复授权、6/6证明与现有资源门禁放行后，在原174已获授权的真164 SSHFS桥接上，才可显式执行。脚本核对真实挂载、原174namespace、精确六条路径、目标不存在、大小及48GiB原有保留空间，单流不超过8MiB/s，复制流计算SHA后才无覆盖发布，并恢复uid/gid/mode/mtime。复用保留的目录及126个控制文件；不重建模型原件，不更改权威164文件。ctime/dev/inode仅作历史证据，无法原样重建。未运行恢复写入，不声称恢复实测PASS。

未重复复制、上传、下载或做GPU工作。未来只有在归属授权明确且6/6权威证明齐全后，另行提交六条精确源路径的释放执行方案；批准后才执行，并以原174实际df增量计算收益。

[RELEASE_REQUEST.md](RELEASE_REQUEST.md) 是供用户审阅的条件申请，不是释放授权；[LANE_BA_T_HANDOFF.md](LANE_BA_T_HANDOFF.md) 保持BA与Lane T原有分工。
