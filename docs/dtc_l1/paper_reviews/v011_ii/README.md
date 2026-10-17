# DTC v0.11-II：第二节动机重写与论证TODO

日期：2026-10-17。底稿为本对话的英文v0.11-I（Introduction专项修改后版本）。本目录是论文文本增量，不是新的实验、完整LaTeX源包或已编译PDF。

## 本轮交付与状态

- `motivation.tex`：用于替换原`sections/motivation.tex`，标题保留Allocation and Retention Trade-off。
- `introduction_with_todos.tex`：沿用v0.11-I引言文字，只在第4段及贡献段后加TODO锚点。
- `author_todos.tex`：可选的显示开关；作者稿默认显示短ID和标签，阅读版可以隐藏，登记表中的OPEN不因此关闭。
- `TODO_REGISTER.md`：每项问题已有证据、缺口、关闭条件、禁止推论、后续对应章节。

**当前未合入本地完整源包，也未编译。** 本轮container与Python执行工具持续ServerError，不能读取本地ZIP、执行LaTeX、渲染或产生新的可验证sandbox文件。因此仅把经过文本审阅的替换稿和标记存入独立GitHub写作分支。不要把本目录称作已经保持4+1页、通过版式检查或可直接投稿的新PDF。

本轮通过Files读到了v0.11-I PDF第1–2页、引言修改说明和v0.10可检索源码。v0.11-I修改说明确认第二节仍为v0.10原文；源码镜像中该`sections/motivation.tex`的旧SHA256是`72482e3afe6287b5247f474fb4c11af4e0e5132db9e3b1fbb4a0aa420e2e6ab6`。后续实际合入时应再核原ZIP文件身份，不默认为本轮已做逐字节本地比对。

## 为什么要重写第二节

原第二节按Lookup coverage、Consumer storage、Release timing介绍三个概念。它们都重要，但上一轮引言已建立对应关系。再次定义IO/OO，不能增加读者对设计取舍的理解。

本轮按“已观察到什么/结构上可以推出什么 → 它要求比较哪一种设计选择”的顺序改写。前后章节的职责是：引言提出问题；第二节说明为什么容量、查询和完成需要分别研究；第三节给出精确状态和动作；第四节报告方法、完整结果和解释。

### 对照参考论文的写作逻辑

这部分是对用户提供原文的结构分析，不是公认模板，也不把他人的数据当DTC证据。

- DL-MSHR §3.1–3.2先区分primary与secondary miss需求，再说明固定entry/slot分配为什么不能适应两类需求。资源单位与所提分配机制一一对应。DTC也应把等待项、可查询映射与物理保留行分开，不能只写“更多资源带来更多并发”。
- MiCache §3.1–3.2先展示动态MSHR需求，再联合观察cache命中与MSHR占用，据此提出共享存储。我们能借鉴“观察先于设计推论”的顺序，但不能移植其互补关系为DTC已验证性质。

本节没有增加上述两篇的主论文引用或改动原BibTeX。它们是作者写作参考。正式第二节使用原`dtc-artifact`和`zhao2024`引用键。

## 三段分别完成什么

### P1：等待容量与缓存容量不是一种干预

引用原BICG控制：增加PIB到128项仍保留16KiB数据和32MSHR；PIB-full消失，但周期增加5.43%。另一项80KiB传统cache保留8PIB/32MSHR而相对16KiB快3.002倍。

这一段只说明PIB容量不足不能独自解释该例，不宣称提高命中率是全部原因。原WAIT128的cap/inactive配置差异及其非绑定受理范围仍在IV方法/证据中保留；本文没有把这些运行重写为字面上完全只差一个参数。

`CMP-01`标记更强的传统/DTC性能解释尚未闭合。现有M已经有更细的计量，但不足以给出唯一、可加的瓶颈分解。

### P2：有物理数据，不等于后来请求可以查到

采用明确的假设例子：两个已接纳指令共享一条物理行；PIB存索引和依赖而非结果向量；映射替换之后，原消费者继续持索引，新lookup却不能找到该分配。随后给出当前640行/128Tag的配置事实，解释80KiB保留和16KiB查询覆盖的不同职责。

这是结构说明，不是伪造的native请求序列，也不是已经测得的位数/面积节省。`COV-01`等T1受理后检验扩大Tag是否真有收益；`HW-01`提醒metadata-only等待仍有pool、索引、依赖、端口及回收成本。

### P3：数据已就绪，不等于等待项已释放

引入原BICG同128PIB/640行控制：ready-to-collection为3557.95/1.16 core cycles。明确单位为退休cacheable warp指令的均值，起点是全部引用接纳且数据就绪之后。等待期间PIB仍占用，IO还可能保持release-list行。因此匹配等待深度后还要研究完成与回收策略。

这里使用的是正文已有的ready-to-collection，不是摘要的fully-ready-to-completion，也不是端到端memory latency。`ORG-01`提醒GEMM T0仍需独立验收；BICG配对和未来T0均不能单独回答OO/C+差额。

## 你指出的引言第4段，怎样标记

引言中的“We ask when this organization is preferable ...”后放三个标记：COV-01（逻辑Tag覆盖的实际收益及代价）、CMP-01（相对传统cache的性能解释）、HW-01（有限服务的实现与PPA）。贡献段另标NOV-01，避免把逻辑写顺误认为独立创新性已经证明。

这些TODO不反过来否定已有结构事实，也不要求“改出正收益”才能关闭。补证不支持更强主张时，应缩小主张并记录依据。

## 后续合入方式（本轮未执行）

只在论文工作树中操作，不在Lane T/A执行工作树中合入。备份并核对v0.11-I源包；用本目录`motivation.tex`替换`sections/motivation.tex`，用`introduction_with_todos.tex`替换`sections/introduction.tex`。

需要开关时，将`author_todos.tex`复制到论文根目录，并在main.tex的导言区加载：

```latex
\input{author_todos}
% 默认显示TODO。纯阅读版可加下一行；它不表示问题已关闭。
% \dtcshowtodosfalse
```

两份替换文件自身也提供默认可见的fallback标记。即使未加载开关文件，也不应因缺少TODO宏而中断。原H1/Pending项及submission检查继续保留。

更新版本标识后须重新编译、核对引用及所有页。第二节增加了动机文字和TODO标记，本轮未证明页数仍为4+1。按内容去重和浮动体组织处理，不缩字号/页边距。

本轮不修改第三至六节、图表数据、参考文献、原44行或任何运行参数。EDIT-01登记第二节与IV既有BICG叙述的去重任务，待审IV时再处理，不在本轮默默删除原结果。

## 实验证据范围

- 最终固定性能与same-depth：Framework `f5c37d6edcce832a72cb0830021bffa78df6cc13`。
- Lane M用于标记未决问题：`d723784a8b897566b63113f95972f7a8d12a01ce`。
- Lane T：本轮未查询新候选结果、未发Goal、未修改分支或执行状态；其结果只在受理后关闭相关TODO。
