# 论文实验观察账本（不是AWMA结果）

记录单位：论文版本×实验组×workload/输入×配置×指标/分母。

## 文件

- `ROUND02_DATA.json`：6配置、34条workload（LATPC24、Valkyrie10）、17条明确数值/定性观察。
- `ROUND03_DATA.json`：12上下文、40条workload（MPW12、Avatar主套件20、ML8）、40条观察；columns+rows用于减少重复字段，按列名解码。

累计74条workload记录/57条观察，不是独立程序数、实测实验数或全部图表数据集。

## 证据规则

只转录原表、正文明确数字及图上明确标注。没有估读柱高。作者均值不复制到每个workload；input只给footprint时不补造shape；null表示未披露或未核实，零须有原文依据。

同名benchmark跨suite/输入/架构不自动合并。MB/KB保留原单位。IPC倍数、cycle reduction、等待比例、动态能量不可相加。

Round03特别区分：MPW的L1页表是leaf；Avatar的MPMI是每百万指令，LATPC的MPKI是每千指令；VIPT并行不是VIVT过滤；动机理想CAM不是真实端口成本；推测准确率/coverage/可压缩率/Fast Translation比例的分母不同，不可相乘当联合概率。

原文矛盾或协议缺项保留定位，不静默调和。观察只帮助选择问题与对照，不替代AWMA配置、校准或执行授权。
