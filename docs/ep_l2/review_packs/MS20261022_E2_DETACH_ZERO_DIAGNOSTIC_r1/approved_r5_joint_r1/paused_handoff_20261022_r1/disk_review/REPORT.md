# 有界空间核查：不能将约160MB下降归因于已查r5工件

首次独立df为7,808,626,688B；相对root报告激活时7,968,653,312B下降160,026,624B，低于Vector当前7,931,630,504B门槛123,003,816B。没有全范围历史inode基线，无法完整证明变化来源，结论保持UNKNOWN。

已stat本轮r5 /tmp目录和build共1349个entry；已查近期Git bucket共1162个entry，近期63个loose object实际344,064B，pack无晚于激活cutoff的新ctime。r5 build实际266,600,448B，主要是正式main、archive和原native ELF，均早于cutoff；main已nlink3共享，不能再次按88MB重复算回收。此轮/tmp r5目录与顶层文件合计上界约12.2MiB（未跨组inode去重），主要是小型分析/候选证据，不能解释约160MB下降，也不足补上约123MB缺口。

/proc检查109进程、962个fd及2.54MB maps元数据：没有E2 deleted-open fd；其它项目两bash共享20,480B已删除脚本inode及VSCode4,096B脚本，与E2无释放授权。VSCode旧映射仅可见路径，实际allocated总量未知，不干预这些进程。未读取raw/trace/binary正文、未大文件hash、未全盘du。

本轮**已证明可安全释放候选为0B**。/tmp工程冗余必须另行证明精确发布副本、无直接路径依赖和活动reader后才可考虑；本次不执行删除或迁移。正式main/archive/native（含失败fixture）、全部付费结果与旧FAIL/HOLD、shared Git对象和旧tmp_pack均保留。按照用户最新指示，盘点收尾，等待root发布暂停状态；174-new迁移未获授权。
