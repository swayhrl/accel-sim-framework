# FWT与SGEMM medium输入准备

输入包状态为 **MISSING**，工程审查材料已齐，可交 **E2 REVIEW**；两者都没有获得本轮启动或运行PASS。本交付仅整理现成输入和小型来源原件，没有恢复旧环境Goal、改变正式执行地点或建立控制器。

|输入|完整trace正文|记录范围|完整活跃lane指令|包内入口|
|---|---:|---|---:|---|
|FWT_7_21|1,785,749,388 B|2条HtoD＋19次kernel|791,609,344|[MANIFEST](FWT_7_21/MANIFEST.json)、[完整顺序](FWT_7_21/COMMANDS.json)、[逐kernel表](FWT_7_21/KERNELS.csv)|
|SGEMM medium|2,216,170,035 B|2条HtoD＋1次kernel|1,658,916,864|[MANIFEST](SGEMM_medium/MANIFEST.json)、[完整顺序](SGEMM_medium/COMMANDS.json)、[逐kernel表](SGEMM_medium/KERNELS.csv)|

每包保留逐文件已发布SHA、当前stat大小、完整kernelslist原字节、逐kernel名称/网格/block/寄存器/共享内存/完整记录统计，及SHA/统计原始证据指针。19次kernel是同一个FWT应用内部的动态调用，不增加独立workload数。

## 身份与来源

FWT native trace composite为 `f3695b85379fb762faaf9830bda449e0a5f1e4d3e351774cf33d90850059b460`；SGEMM为 `694ce08c82354963d0a24f45b13020c9a98d21e60b511166812d6176b4f486cb`。这两者由原完整body SHA和命令清单重组校验，未重扫大正文。SGEMM旧ROUND1树hash `2074532f…`采用不同定义，不与native composite混为一个身份；正文SHA一致。

读取起点：E `66b28ad7c6811e1e15370d4a24e97fff693319c5`，D `f93add1ef2e22e5f8b04e1dce7de5b7ddfd15a80`。准确每个来源的路径、SHA、Git HEAD及是否匹配已提交blob在[SOURCE_BINDINGS.json](SOURCE_BINDINGS.json)。E的其他未提交回读文件未改动。

找到本地gpu-app-collection源码，版本 `dad09cb0487845edc7524ded814c6cde9f0ef6a1`。它只能作为**明确版本的参考实现**，不能冒充当年采集的应用commit。所有参考构建命令均未执行。

## FWT：来源存在，但原scaled源码与数值输出缺失

原 `run.sh`完整保留在manifest：声明 `CUDA_VERSION=9.1`、`CUDA_VISIBLE_DEVICES=4`，调用原capture binary的 `-logK 7 -logD 21`，经 `traceall.so` 和post-traces-processing生成列表。GPU index4不证明GPU型号/UUID；`binary version=70`只说明代码目标，不能补成某个具体GPU型号。原FWT header没有NVBit/tracer版本，故仍UNKNOWN。

Framework YAML将这组参数归入 `sdk-4.2-scaled`。当前本地CUDA11示例却将 `log2Kernel=7`、`log2Data=23`写死，未解析logK/logD；不能用它重建logD21后称为同一输入，也未改源码或参数来凑匹配。原scaled SDK源码/patch、捕获binary SHA、构建日志及编译参数仍缺。manifest中给出的CUDA11单目标make只供理解参考源码的构建接口，`reference_build_input_compatible=false`，不是本冻结输入的可执行构建方案。

完整记录顺序为HtoD512 B、HtoD8,388,608 B，随后kernel1至19。记录中没有DtoH、memset或初始化payload；不能凭清单补写这些API。现存参考实现有`srand(2007)`、dyadicConvolutionCPU及相对L2范数<1e-6检查，但原采集源码未绑定，所以这些只能是算法/oracle参考，不能证明原trace的种子、值或输出。

已有全epoch只读资格模型覆盖全部19kernel：131,072条line及41,943,040次读lane-line引用属于SAME_LINE_STORE，认证RO lines为0。这是地址分类证据，既不是数值输出oracle，也不是runtime detach收益。完整非原子/原字节证明已复用。

旧E011/E012回执仍是 **INCOMPLETE**，未补造exit0、未退回次数，也不采用raw cycle比作为正式性能。E若决定以后恢复，只能按精确producer/input/profile审核适用性并单独批准新端点；旧main61资格不自动覆盖新capacity版本。

## SGEMM medium：已有独立探索登记，仍不可启动

追溯到E的原件：`E2_EXP_SGEMM_MEDIUM_20261020_r1`已经存在，状态为 **REGISTERED_EXPLORATORY_HOLD_NOT_LAUNCHABLE**。因此“没有任何登记”是旧摘要表述；当前真正缺口是来源/数值/RO-fallback/producer资格与新启动授权。[冻结登记原件](saved_evidence/E_SGEMM_REGISTRATION.json)明确保留Btree HOLD及原七输入，不能按更早D提案静默替换Btree。

Framework YAML保存参考调用：

```text
parboil-sgemm -i ./data/medium/input/matrix1.txt,./data/medium/input/matrix2t.txt,./data/medium/input/matrix2t.txt -o matrix3.txt
```

重复的matrix2t参数按原文保留：参考main要求三个名字，实际从第0项读A、第2项读转置B。冻结kernel为`mysgemmNT`，grid(8,66,1)、block(16,8,1)、shared512 B、42寄存器。完整D审查已有51,847,488条warp记录、1,658,916,864条活跃lane指令，global/shared atomic记录均0。没有重复进行这次约837.48秒的完整审查。

现存参考构建接口为Parboil的 `python2 ./parboil compile sgemm cuda`，平台从CUDA_INSTALL_PATH选nvcc；实际捕获构建命令、flags和binary身份仍UNKNOWN。**不要直接执行**collection的`make parboil`或`source src/setup_environment`作为本次准备：前者调用make data并构建整套suite，后者可能下载、安装及编译旧SDK。本次两者均未执行。

采集header在已存完整审查中记载NVBit1.4、tracer3、binary70；这些是版本标签，不是工具commit或binary SHA。`11.0`目录名不是nvcc版本证明。原run.sh、实际GPU/driver/CUDA build、tracer/postprocessor身份和原采集session/archive绑定仍缺。

输入矩阵及预期matrix3在所查确切源/data路径不存在，Parboil datasets symlink目标也不可达；没有扫描共享盘寻找或下载全套数据。逻辑矩阵维度保持UNKNOWN，不从HtoD字节数或grid推导。参考比较器要求相同float数量，每项满足绝对误差<0.01或相对参考值误差<1%，再到EOF；真实参考输出文件及其SHA缺失。参考main只声明computeGold，没有调用，因此不能声称已有CPU数值PASS。

SGEMM自身RO证书仍UNKNOWN，不拷贝Conv证书、不填成测得0。C/A2/E2需要独立证书或明确审查过的空覆盖普通路径回退；D的语法/非原子证明不是E资格。

## 精确补件与后续职责

[MISSING.json](MISSING.json)逐项列出owner、缺失范围、原件追溯所得及可关闭缺口的证据。

|范围|FWT需补|SGEMM需补|
|---|---|---|
|源码再采集|原scaled源码commit/patch、capture binary与build log|原capture源码commit、binary与build log|
|采集来源|GPU/driver/CUDA build、NVBit/tracer/postprocessor精确身份|同前，并缺原run.sh/capture命令及session/archive绑定|
|数值复现|原初始化payload或绑定生成器、捕获数值参考输出|原matrix1/matrix2t及维度/SHA、matrix3参考输出/SHA|
|RO/runtime|旧地址模型0覆盖保留；新运行版本由A2/E2审核|C证书或E审核普通回退；完整producer/profile/input资格|
|启动|E单独决定恢复授权；旧INCOMPLETE保留|已有探索HOLD登记；仍缺新科学范围和启动批准|

F/D/B/C/A2/E2按现有链条消费材料，不迁移正式运行地点。正式执行仍为原174、E2唯一调度；不改任何控制器、台账、当前producer或失败trace。Btree/SpMV/Scan HOLD、原七输入与原统计分母均不变。

若以后另行批准，每对是2次真实完整启动、每端384MiB/每对768MiB结果硬预留；FWT的S80–110min/F85–120min仅E保存的旧版本先验，不是已接受完成耗时，新版本耗时UNKNOWN。SGEMM的真实walltime UNKNOWN；静态检查837.48秒不是native执行预测。10GiB新增/24GiB总结果与物理保护的说明引用E研究快照，不构成当前空余额或资源租约。任何大搬运、构建、数据获取或新模拟均先经E准入。

本次操作：小型元数据/源码读取、确切文件stat、小清单SHA与已存body SHA复用；仅额外读取一次FWT kernel1的2048 B header前缀补查版本字段，未扫描正文。**零大trace扫描/重hash、零构建/native/GPU采集/完整应用、零大下载/搬运、零中央状态修改**。[DELIVERY.json](DELIVERY.json)记录工程边界；[prepare_inputs.py](prepare_inputs.py)可复核包生成，明确拒绝打开trace正文。
