# Related work and claim boundary

2026-10-18核查原始论文/作者机构来源。XOR地址映射是已有cache设计手段；本轮不声称DTC首次发明hash、XOR placement或降低冲突的思想。

- González、Valero、Topham、Parcerisa，*Eliminating Cache Conflict Misses Through XOR-Based Placement Functions*（1997）：讨论多种cache组织中的XOR placement。采用[作者机构原文](https://people.ac.upc.edu/jmanel/papers/ics97.pdf)及[爱丁堡大学书目记录](https://www.research.ed.ac.uk/en/publications/eliminating-cache-conflict-misses-through-xor-based-placement-fun/)核对。
- Seznec，*A Case for Two-Way Skewed-Associative Caches*（ISCA 1993），[出版商记录](https://doi.org/10.1145/165123.165152)。它是skewed-associative背景；本轮使用全ways共享的单set函数，保留原组内LRU，不能称已实现多way不同hash的skewed cache。

AE仅实现一个用户预先指定、保留bank低位的row XOR控制，用于检验固定容量和原quota下的Tag冲突变化。它没有自动找hash、地址预知、应用特化、多个候选筛选或新的替换政策。合成stride的正收益和固定反例的负收益都保留；这些结果不能推出GEMM/Gaussian收益。

若未来以C+为基线声称超越传统cache，必须为C+提供对等hash控制，并保留容量、ways、Tag/key宽度、延迟、端口及hash成本的公平比较。本轮不修改C+，不新增论文性能主张，也不替换任何旧论文数据。
