# r5 四输入与18门适用性候选

本目录仅供root逐门审签，不是新Q、运行准入或native PASS。实际production身份固定Core1093/main e511/archive7b590；旧r4 Q只作为结构与历史模型前提的引用。

独立检查：12个完整模型源码文件（FT、RO事务、TVD、oracle/store、L2 admission、GPU clock等）从9243到1093字节不变；RO runtime整个模型类前缀字节不变。gpu-cache.h确有17行被动const getter新增，因此不声称整个header字节不变；diag preview也新增snapshot host字段。新增observer边界仍须真实source/native/parser/math证据闭合。

每输入保留完整trace身份、原selection、原kernel/command范围、native非原子证明、whole-commandlist RO证书和原assumptions。只重新核小config/oracle/metadata及source blob，没有重读trace正文或hash大型binary/archive。原inspector须在启动及终验fresh核全部真实输入身份。

|workload|完整指令|kernel|旧runtime hash → 新runtime hash|

|---|---:|---:|---|

|cfd_097k|143129372|5|951f7ad289ae → 4cf86a8a4e70|

|dwt2d|148684429|10|6a1db5bac84f → e06135b92c84|

|vectorAdd_4M|56000000|1|39d5f27a2e25 → c2ab92dfc528|

|convolutionSeparable|714547200|2|9eed8d3ce2fc → 7ff3f887d669|

新runtime hash由已审tagpressure_runtime_identity.py调用原content_hash/asset_manifest精确公式导出：唯一变化是EPL2_TAGPRESSURE_DIAG=1；config和oracle等模型资产内容不变，不能继续使用旧hash。完整精确值在各输入RUNTIME_IDENTITY_REBIND.json。

72份逐门plan逐项给出：不变模型前提、旧native实际case/标签与范围、1093 source bridge、完整input/oracle ref，以及仍待共同新r5 delta证据。原17模型native不重复执行；历史48原生仅支持不变模型前提。另4个既有212 observer gate和4个新增r5 gate均保持PENDING，不能拿旧observer资格、新native仅两ON子集或native exit0替代。

保持边界：Conv完整legacy masked-row证明仅其原输入有效；DWT原aggregate FAILED（Btree）不改，只复用已完成的DWT normalization行；Btree仍HOLD。所有captured full-application numeric payload/result仍UNKNOWN，无新S/allOFF应用资格、无新pair、无额外C联合fixture提升。

818项检查指小制品SHA/源字节/配置派生与元数据一致性；没有运行测试、native、build或应用。真实15个修复native的完整独立release/math尚待root最终证据注入。资源不足可合法HOLD未启动端，不能弱化5+2、端384MiB或整640MiB metadata预测；本目录不进行任何资产清理、迁移或中央写入。
