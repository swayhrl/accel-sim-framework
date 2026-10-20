# 既有候选：来源、规模、成本和证明边界

审查对象完全来自D原INPUT_SELECTION.json：SpMV是原先第一备选；Scan/SGEMM是已记录的未选候选。没有下载、重新捕获、生成新规模或读取候选新S/F收益。三者完整命令、逐body已发布SHA/大小与当前文件可达性见EXISTING_CANDIDATE_MANIFESTS.json。

| 候选 | 冻结规模与完整命令范围 | 预计执行成本的可用代理 | 独立验证价值（不是预期加速） |
|---|---|---|---|
| SpMV | Parboil Dubcova3 large；6条HtoD＋1kernel；34,529,277B body；历史声明21,131,849条活跃线程指令 | 三者最小的trace/I/O与指令代理；新native模拟walltime UNKNOWN；本次实际语法失败，禁止因小就选用 | 稀疏间接访问，旧B0 descriptor拒绝361635、每地址cap8598；可对照请求跟踪压力，但并非新128/512预算下的测量 |
| Scan | CUDA SDK scan NO_ARGS；初始HtoD 27,262,976B＋33kernel同一个应用；5,329,077,632B body；历史声明1,963,460,720条指令 | 最大的body读取/多kernel成本；不得拆33kernel凑独立应用；新native模拟walltime UNKNOWN | 旧B0 tag拒绝222849、descriptor拒绝60513316、WAD拒绝2318944；不同于btree低压力上下文，但当前输入失败不能入新科学结果 |
| SGEMM | Parboil medium；两HtoD分别4,063,232B和4,190,208B＋1kernel；2,216,170,035B body；历史声明1,658,916,864条指令 | body约原btree的2.74倍，声明指令约3.73倍；这些不是宿主机时间预测，新native模拟walltime UNKNOWN | 稠密计算/复用背景的低传统跟踪压力对照；旧B0 tag/line/descriptor拒绝均0、每地址cap1409，真实V复用与新R机会仍UNKNOWN |

旧B0 runtime/Core/预算与新最终方案不同，旧重试数既不等于独立请求，也不构成新机制收益；历史指令在完整当前校验结束之前只作为已有声明值。具体新检查结果单列CANDIDATE_AUDIT.json和总报告。

输入来源：SpMV/SGEMM来自parboil.current.small8.stage/parboil/11.0冻结trace；11.0只是目录标签，缺少原run.sh与原应用source revision，不能当已确认编译器版本。Scan保留run.sh字面捕获命令，声明CUDA_VERSION=9.1，但原应用/trace producer完整revision仍UNKNOWN。不得据目录反推未知版本，也不因缺少run.sh就伪称trace资产不存在。

若某候选通过完整原字节/native语法/非原子检查，能主张的可复现范围是**该准确trace＋完整kernelslist.g＋A/E最终冻结binary/config的trace replay**。不代表可以从原源码重新捕获同输入、数值SASS/算法输出正确或已获E运行资格。logical matrix维度未获来源证明的部分保持UNKNOWN，不从HtoD字节数猜维度。

只读覆盖另行限定：三备选目前没有可沿用的独立C/E完整epoch只读证书，UNKNOWN不能填成测得0；更不能拷贝Conv证书。若E采用一个合法候选，固定F的T/M保持原政策，未认证line按已独立验证的空覆盖/普通路径回退，不为触发R而改输入。只读证书、输入语法和运行数据正确性各自记录，不互相替代。

E还需独立决定：输入适用性/完整身份、当前生产源路径所需验证、同最终S/F配置与固定策略、真实资源和剩余40累计预算。D本轮不执行模拟来估计walltime，不发screen、不注册或启动应用。
