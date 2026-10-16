# 2DConvolution有界CPU可行性

结论：**UNRESOLVED_FORMAT_APPLICABILITY；整kernel派生解释证据门槛FAIL/INCOMPLETE，停止本轮扩展。** 没有生成正式输入、准入或运行；Btree资格与此独立。

复用原40940条索引，10个PC各4094条：0120..01a0九个LDG共36846条，0250/STG共4094条。全部P=`fffffffe`、mode1；E未保留。重核每PC首/中/末共30条原行SHA及32KiB以内的前文CTA/warp上下文，不遍历840MB正文或629成员。精确读取字节数、原行内容、offset、SHA、CTA、warp和地址解释均在2D_FEASIBILITY_RECEIPT.json。

两种有精确来源的version3政策都相容：`475a282dd5baabfc481b3be44963e92fc3df34cc` 的源码SHA `d9a7995178e95db6ebf467625036c805ad784d43ece233f6277c6ab217db318f` 打印P、编码E；修复 `756ed33d503704b4faf97bb3a051792f0450d14c` 的源码SHA `4f5aa97ac05c6d01ad9885c0bb51848483b9f1fad4153324dad49ae47a7fb639` 打印P、编码P。2021年fork `9cdd82aae3f95eaba78a9b01cfb5880f8f4f93ee` 的真实Git对象仍证明旧E政策存在。版本或文件日期不能选择本capture合同。精确library/ELF路径及缺失范围已由冻结来源报告界定，本轮未追加归档/ELF/工具链搜索。

应用源码SHA `5e12047cbe8cc8a21658d15df602434ee70ebf0b873d45119974fb49da63a192`，NI=NJ=4096、block32x8，有同一内点条件包围九项stencil load和一个store。所有30个见证的原header坐标对应x=0、i=1/2048/4094。用每PC首条拟合一个固定stencil偏移、后两条作为局部holdout，一个统一first(P)=1偏移假设均匹配。九load的偏移是固定{-1,0,1}邻域，store输出基址从首样本拟合。该检查是**有限样本相容性**：PC与源码项的关联、输出分配基址本身尚非独立来源证据，不能把30条或风险子集当全kernel动态验证。

具体原第58行PC0120：P=`fffffffe`，base=`0x7fdc00000004`，stride4。first(E)=0时lane1=`0x7fdc00000008`；first(E)=1或P编码时lane1=`0x7fdc00000004`。附近PC00c0记录lane0 EXIT，随后P为fffffffe，与早退后E=P的模型相容；仅有打印P仍不能恢复真实E和完整编译控制/谓词语义。不得据此选择历史解释。保留原16376条条件sector/line数量风险，不重算其为已证实性能或结果错误。

最小缺口有两条可另审路径。历史capture路径需要与固定member/session绑定的producer source/build/format receipt；若是E政策，还需要对应动态E锚点。独立源模型路径不强制恢复某个原ELF，但需要有来源、可独立检查的完整source/SASS/GPR/offset轮廓，统一解释全部65536 CTA/524288 warp的动态E、P、early EXIT及所有10个PC的全kernel base/stride，并独立绑定输出基址、预留真正holdout。当前只有源码与有限拟合，没有该轮廓或全kernel证明。

因此本轮没有候选输入精确定义，没有逐行锚点选择、两端点trace或性能筛选。完整2D重建应另获独立任务范围，不能从此次CPU可行性自动升级。原terminal结果、科学pending与全部HOLD不变，LUD未触碰。
