# 历史缺口的精确输入级说明

此增量为公共SM70资产库补齐99条历史负面路径观察的失败原因。125项冻结完整输入、全部对象和成员指纹、代码及科研资格均不改变。

| 历史失败原因 | 路径观察数 |
|---|---:|
| 未找到命令清单 | 85 |
| 命令清单没有kernel条目 | 6 |
| 声明的kernel成员缺失 | 4 |
| 声明成员存在但字节数为0 | 4 |
| 合计 | 99 |

99不是独立workload数；同一路径可能分别在174和174-new观察。四条缺成员观察合计202条缺失成员引用；四条零字节成员观察对应四个带host的身份键，不能简单当作四个不同物理文件。CORR与COVAR的trim-local目录虽然missing_members为0，仍各包含零字节文件，因此未纳入125项完整输入。

原issues所有99条记录及archive_input_issues逐值保留，新增failure_annotations与逐成员历史stat。Root逐条解析原始metadata对象，所有观察都有具体失败原因；它们与125项完整输入的442个精确(host,path)别名无重叠。同程序或同版本的其它输入ID仅作参考，不能凭程序名把这些失败输入改成已恢复。

历史TRACE_MEMBER_OBJECT_METADATA原始gzip与原scan_assets/build_report源码已按原字节存入公共NAS SHA目录，gzip完整CRC和逻辑SHA已核对。公共解释不再要求读取私有EP目录。所有新证据都是既有元数据派生，未新读取trace正文、trace stat或扫描旧174。

真164元数据准备入口：

/root/share/mnt164/huangrulin/traces/receipts/sm70_public_bootstrap_preparation_20261025_v1/COMMIT_V4.json

COMMIT_V4 SHA256为997688771dbfa4a7b7d29ee1087cfc6c9cd218e9d77c9906d5f233af3a64d097。最新未激活模板为proofs/sha256/d197720c3c981dc5a5b1772886cb3fa1fbb16790d621af68baeea92f77b43ab0，和V3模板的唯一差异是issues_ref。正文读取授权仍false，protected_after_ref仍null，Source2真实关闭校验/COMMIT及后续全量验收继续待完成。

该增量不授予科研资格，不删除任何Source原始trace，不修改现有复制进程、科学预算或历史。
