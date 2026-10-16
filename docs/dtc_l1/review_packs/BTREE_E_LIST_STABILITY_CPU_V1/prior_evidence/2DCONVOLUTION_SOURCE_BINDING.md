# 2DConvolution 有界producer绑定核查

结论：**UNRESOLVED_FORMAT_APPLICABILITY**。已从真实保留Git对象验证一个2021年仍使用旧E-mask约定的version3 producer，进一步排除了“version3或包日期说明已修复”的推断；没有证据把它或修复后的producer绑定到当前固定trace。原terminal PASS保持，科学适用性待审。

## 可验证producer来源

| 来源 | 精确源码身份 | 地址合同 |
|---|---|---|
| 上游 `475a282dd5baabfc481b3be44963e92fc3df34cc` | SHA `d9a7995178e95db6ebf467625036c805ad784d43ece233f6277c6ab217db318f` | version3；打印P，编码E |
| 上游修复 `756ed33d503704b4faf97bb3a051792f0450d14c` | SHA `4f5aa97ac05c6d01ad9885c0bb51848483b9f1fad4153324dad49ae47a7fb639` | version3；打印P，编码P |
| AccelWattch fork `9cdd82aae3f95eaba78a9b01cfb5880f8f4f93ee` | Git blob `d8028fee05e288aa1d76ec6833d647a5b908691c`；SHA `61955513bd801178565851fceebef89a489e118df40c4861c34b7366716b7e31` | version3；打印P，编码E |

第三项是本轮新增证据。包内Git HEAD是2021-09-02；从其Git pack及9个loose objects解析该commit，实际源码与包内工作树完全一致。该文件最近一次提交为2021-07-23的 `0835a716347106383ad51701e550943f4a75300b`。它不是只凭文件名或mtime猜出的旧副本。见 [ARCHIVED_GIT_SOURCE_PROOF.json](ARCHIVED_GIT_SOURCE_PROOF.json)。但这个Git证明只绑定**包内源码**，不证明当前trace由该源码编译的library采集。

该版本的instrumentation保存 `__ballot(1)` 与 `__ballot(pred)`，采集各执行lane地址；receiver打印两mask交集，却使用E作地址压缩/列表mask。包内postprocessor只移除CTA/warp前缀、分组并复制剩余指令字符串，不重新编码地址，因此分组不能补回缺失E或自动把旧合同变成P合同。源码文件、偏移和SHA都在 [ARCHIVE_ASSET_RECEIPT.json](ARCHIVE_ASSET_RECEIPT.json) 中。

## 当前输入的证据边界

原header的NVBit1.4/version3、CUDA11.0 launcher和外部tracer_tool.so路径，与多种producer实现相容。该精确library与应用ELF路径当前不存在；没有采集session的build/source receipt。保留的45项validation包成员名中没有2DConvolution目标；没有遍历无关ELF的符号。本轮没有搜索其他大trace包或重建工具链。不能把“2021年包内存在旧合同”反过来当作当前输入一定用了旧合同。

应用源码 `2DConvolution.cu` 与历史GPU-app-collection commit `40e0052cebd3f98006190ed09e78f4981ef1a41b` 字节一致，SHA `5e12047cbe8cc8a21658d15df602434ee70ebf0b873d45119974fb49da63a192`；NI/NJ=4096、block32x8与既有几何相容。这仍不是原ELF、predicate或producer绑定，没有据此生成新source-profile输入。

复用原104476条索引中的40940条2DConvolution记录及旧10-PC表，不重读其840MB正文。PC0120..01a0的9项LDG.E.SYS各4094条，共36846条cacheable global load；PC0250/STG.E.SYS有4094条。精确PC、原行SHA和地址备选仍由旧索引绑定。

## 地址解释与最小缺口

原第58行PC0120：P=`fffffffe`、base=`0x7fdc00000004`、stride4。旧E合同若first(E)=0，lane1为 `0x7fdc00000008`；若first(E)=1，则为 `0x7fdc00000004`；修复后P合同把base绑定first(P)，对应后者。两套检查过的version3源码不能仅由这条压缩记录或版本字符串区分。

仍保留此前条件性的16376条sector/line数量风险（其中12282条cacheable load、4094条store），不把几何投影当作已测性能或选择合同的依据。最小补充是绑定当前成员/采集session的producer格式或source/build证据；若能绑定P-mask合同，可排除本项旧E锚点机制。若绑定E-mask合同，还需10个PC的动态执行锚点证据。源码存在、打包日期和terminal PASS都不能替代该绑定。

本轮有界范围到此结束，状态为UNRESOLVED；不选择E或P、不更改科学输入/支持域，不生成正式派生输入或配对结果。必要的下一轮取证可交独立窗口，不在这里继续扩展编译器/JIT搜索。
