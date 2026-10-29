# 两架构按需读取与单资产恢复流程

本增量补充[采集后处理归档读取SOP](R2_REUSABLE_CAPTURE_POST_ARCHIVE_READ_SOP_V15.md)。发现、NAS访问、Native物化和consumer／科学资格分别验收。[V16实际引用表](READ_RESTORE_ONE_EVIDENCE_REFS_V16.json)保存已完成样本、公共命令和大RESULT的NAS引用，不复制真实scope或大数据。

## 先确定是读取还是物化

公共入口/root/workspace/assets/traces已可发现75常规、75裁剪、RAW7及125个SM70精确输入。按项目的真实binary／argv／input和consumer配置选择asset ID；NAS路径可读不是Native已物化，建立本地副本也不是新consumer接受。

两个公开gateway可先help和metadata inspect。Main／DTC实际证明的接口分别为trace-assets-restore-one-sm70和trace-assets-restore-one-sm89；SM89 ordinary与derived各有inspect。metadata-only请求不继承旧restore授权，真正写入仍需新per-run、per-asset Root0600精确scope及全新target，不覆写或清理现有实验cache。

## SM70 使用已提交member与chunk布局

固定当前注册身份、COMMIT、完整member manifest与range／chunk索引，先核metadata／source／Native写入／关闭重读预算与实际floor。经精确准入后流式核source／chunk／member SHA，写入Native并关闭重开检查SHA，保持确已记录的numeric成员属性；target根是新的Root目录。

实际BlackScholes资产的全部2成员、22319130B已闭合，tar全扫描0B；引擎没有为一个资产恢复去重扫611GB归档或重建125输入全库ledger。Root审计复用真实回执，没有再对正文做一遍文档SHA。

## SM89 使用flat COMMIT与MANIFEST布局

固定当前ordinary／derived catalog、统一注册、原始COMMIT／manifest raw SHA与全部声明成员。验证新目标、源路径、不相容文件／父目录关系和资源范围，再逐文件流式核全SHA、Native写入及关闭重开。SM89不能套SM70 chunk布局，旧C8固定capsule不能充当通用75对恢复能力。

派生资产按真实布局绑定parent COMMIT／manifest、binary和input依赖。必要parent metadata在NAS验证，实际恢复derived不复制parent payload；Gaussian64样本该值为0。legacy资产没有新PARENT文件时，核真实旧字段及引用，不能补造历史文件，也不能默默丢弃parent验证。

SM89未记录历史capture POSIX属性，使用显式新Native uid0／gid0／0444／Root mtime；这与SM70保持已记录numeric属性的证据不同。Gaussian64一对298成员、1592059B已经实际完成，但不意味着所有75对都已物化。

## legacy schema与pointer的边界

| 审查点 | 实际处理与保留条件 |
|---|---|
| COMMIT／manifest变体 | 当前150对象metadata census观察3种COMMIT、11种manifest schema值或None；显式适配已知字段，不把未知格式或缺失当PASS |
| 派生parent旧结构 | 验证原件和现有引用，不造一个历史上没记录的新PARENT文件 |
| pointer时间戳重发 | 仅unix、utc_unix、published_unix、tool_updated_unix四个已列字段容许类型合法、有限时间戳差异；全keyset及非时间语义精确相等 |
| 原始JSON字节 | 不可变target、COMMIT和manifest保持其raw SHA；重编码语义相同也不冒原件hash |
| 属性未记录 | 新安全属性与历史已保留属性分别声明，不从另一架构或capsule推断 |
| 全局激活标志 | false表示无全库写入／批量恢复授权，不能解读成公开NAS或按资产gateway不可访问 |

时间戳规则不能吞掉deadline、scope或身份变化，也不能泛化成忽略所有含time的字段。metadata兼容测试和27项独审与真实按资产restore分别留证；当前公开code／pointer已经完成对应实际样本接受。

## 写入与发布验收

确认完整该资产成员集、真实target及逐项I/O账，完成source与Native关闭重开SHA、真实wait、owner／owned闭合后，才固定实际后端版本和公共pointer。跨项目help／inspect的10条命令支持公共metadata接口范围，不替代source／write／readback的实际字节证明。

所有source保留，旧R5／bulk退休不复活。保持metadata core，不为按需恢复恢复全库正文硬门槛；后续其他资产仍走新精确范围，不从本例借科学／性能资格。最终发布仅使用两份已执行后端原bytes快照及小正索引；大RESULT、真实grant、旧scope和完整数据留NAS。全任务完成仍由Root最终requirements审计与Git读回决定。
