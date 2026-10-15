# A59 后续｜ogbn-products 许可权威 CPU-only 核查（109 / Lane M）

**裁决：AUTHORITY_PARTIAL_OGB_APPLICABILITY_UNRESOLVED。保留原 A59 的 DATA_LICENSE_NO_GO / STOP，不启动训练。** 本轮取得了原始作者论文的学术使用声明，也排除了两个容易误用的替代许可；尚未获得将可读正式条款明确绑定到官方 ogbn-products 的权威记录。这个结论不表示使用违法、许可被撤销，或所有来源都不存在许可。

用户明确同意本次109独立CPU-only核查。新分支 `hrl/aiarch-a59-license-authority-cpu-109-v1`，固定父提交 `0e52f088d21e0a88ff471cdf5ad76a7a539cf616`；新 worktree/output，原A59工作区和证据只读。预算1worker/RAM256MiB/元数据16MiB/新增盘32MiB/20分钟。没有访问GPU、共享GPU锁、训练、科学图数据或依赖安装。

## 新增证据与适用性

| 证据 | 实际核查结果 | 能证明什么 |
|---|---|---|
| OGB 固定官方文档 | commit `f4c21f16796589fdf18dee00b206e01915cfa564`、blob `e4feb4017b0eb5e6ed12dc976f8d6eb4d104cf67`；仍将 ogbn-products 指向同一 Amazon license.txt | 确认精确数据集与所引用许可入口；入口本轮403 |
| 原始作者论文 | 原文PDF完整9307397B，SHA256 `4019c64f9f8437d41321bd4018d898c956ae189198baf5edd7501b7fb29c8723`；本地第2页左栏文字核验 | 明确存在上游学术使用声明，不再只是二手转述 |
| OGB issue #499 | 2025-03-14提交；当前open、评论0；作者关联 `NONE` | 官方项目已有相同断链报告；未见维护者确认替代许可 |
| AWS 官方多语言评论许可 | Git blob `11c0e89cc1cf218c6528b9b1d7eca7013eb35cc4`，真实文本读到 | 明确限定 Multilingual Amazon Reviews Corpus，不能转用到当前产品图 |
| issue提议的 Amazon Software License | 官方页面实际读到软件定义、许可附着条件和3.3条款 | 未找到将该许可附着到ogbn-products的记录；不据此认定替代许可成立 |
| Internet Archive及官方历史路径 | CDX/快照/available API超时；特定AWS PDS文档路径404且该路径历史查询空 | 本轮未恢复精确历史文本；不是全网不存在的证明 |

原始作者的确切10词引文是：

> We have made this dataset available for academic use

来源：[McAuley等原始论文，第2页](https://snap.stanford.edu/data/amazon/productGraph/sigir_draft.pdf)。完整PDF通过初始有界前缀及一次成功的条件Range恢复，ETag、Content-Range和完整字节数核对一致。一次中间TLS超时计入同一轮；原始前缀、失败和修复收据保留，没有将前缀SHA冒充完整文件SHA。最初双栏文字抽取出现混列，已用左栏裁切独立修复并断言引文，再形成最终资格记录。

OGB指向XMLRepository和Cluster-GCN；原A59只读XMLRepository快照中Amazon-3M引用McAuley的2015论文，Cluster-GCN官方README也说明Amazon2M的数据生成来源。这条链支持“相关上游数据由作者公开供学术使用”的事实。它尚未补齐官方ogbn-products全部派生内容的具体适用条款，也没有恢复OGB当前所引用的Amazon许可正文；本轮不把这一差别自行改成科学门PASS。

[OGB #499](https://github.com/snap-stanford/ogb/issues/499)的替代链接来自提问者建议，不是维护者许可决定。[Amazon Software License](https://aws.amazon.com/asl/)具有其自身适用条件，不能因名称含Amazon就推定它覆盖本图。另一方面，[AWS官方多语言评论许可](https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt)虽可读，其命名对象与当前任务不同，也未被借用。没有用代码MIT/Apache许可替代数据许可，没有更换图或科学任务。

## 资源与边界

109实际HTTP正文下载 **10833231B**；已计控制端官方源获取及中转 **43828B**，另计 **2MiB控制端检索/传输保守预留**，合计账户 **12974211B**，低于16MiB。论文是文献元数据证据，不是训练输入；图数据、依赖、安装均0。保守预留不是精确实测流量。

CPU固定在核心0、OpenMP/BLAS1；监督采样任务父子RSS峰 **60227584B**（约57.44MiB）。各Python地址空间硬限256MiB，监督提前阈值240MiB。RSS为有边界的采样值，不声称系统绝对峰值。源PDF重建时保留前缀、尾段和完整文件，新盘峰仍在32MiB内；归档前当前自有盘 **23224320B**。最终文件/Git增量及时间在远端回读收据再次核验。

原A59 HEAD仍为固定父提交且工作区clean；相关只读文件SHA记录在资源收据中。无旧资产写入，无系统设置修改，没有向第三方发消息。原A59 GPU步骤保持NOT_RUN。

## 唯一下一步与停止决定

本轮自动检索到此收口，不自动创建新的许可Goal或GPU实验。若继续，应由科学协调审查本轮上游学术使用证据，并取得针对 **官方ogbn-products具体派生内容** 的维护者/权利人适用性说明；可直接使用本目录 `REVIEW_REQUEST_DRAFT.md` 的单一问题草稿。草稿未发送，也不表示已取得新许可。

即使后续审查确认数据准入，A59的二进制ABI、强缓存正确性、数值和训练wall仍未验证，不能由本轮文字证据替代。需要按另行明确授权的连续执行范围推进，维持原科学条件和累计资源账。

## 发布

仅推送本独立CPU核查分支，不修改/合并原A59或协调分支。完整论文/HTML等快照保留在私有输出；Git仅含小型权威/适用性判断、原始API/资源收据、SHA与脚本。提交前检查所有SHA/JSON/脚本语法，push后核exact commit/tree/blob/SHA、clean及预算后STOP。
