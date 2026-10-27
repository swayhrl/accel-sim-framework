# 科学增量V4：只读快照

采集UTC 2026-10-27T21:59:28.917840+00:00（CST05:59:28），原冻结35输入/350点。以E/V3 UTC20:54:53的271 accepted为锚，当前279=273新执行strict+archive/native restore与6已核验reference。仅新8个accepted raw进行闭合/扫描，旧271 raw不重扫；8条raw及新IO链无证据错误。旧191配对的UUID、RESULT SHA、cycles、输入/配置身份全部不变。

## 关键新证据

DH配对191→207，增加16。新增DH-P0 scalarProd/scan/srad_v1解锁3/3/8个配对；另cutcp E384与myocyte Q128各1。新增GESUMMV M16/F256仍缺同design DH-P0，不能计算speedup。所有新增配对核对同输入binding、Core/Framework/binary、完整冻结输入计数以及除L2/FRFCFS两个允许项之外全部effective options；固定DRAM850MHz与10MiB容量。

- cutcp: E384 1.000000x
- myocyte: Q128 1.000000x
- scalarProd: E384 1.000000x, F128 0.998952x, F256 1.004467x
- scan: M8 0.994288x, F128 1.156693x, F256 1.283635x
- srad_v1: E384 1.000000x, E768 1.000000x, M8 0.997719x, M16 0.997719x, Q64 1.000000x, Q128 1.000000x, F128 1.000000x, F256 1.000000x

scan F128/F256为1.156693x/1.283635x，但DRAM_read_atoms只变化-0.007222%/-0.000995%。收益不能归结为显著DRAM读量下降；调度/排队与F+191 partition共享credit同时变化，现证据不分离因果。scan M8回退，srad M8/M16轻微回退；负结果保留。

## 人口口径

| Profile | 当前可配对人口 | 可配对人口GM | 正/平/负 | 全8共同人口25的GM |
|---|---:|---:|---:|---:|
| E384 | 27/35 | 1.000769 | 3/18/6 | 1.000830 |
| E768 | 25/35 | 1.000830 | 3/16/6 | 1.000830 |
| F128 | 27/35 | 1.013648 | 6/15/6 | 1.008899 |
| F256 | 27/35 | 1.022996 | 7/15/5 | 1.014493 |
| M16 | 25/35 | 1.001233 | 5/16/4 | 1.001233 |
| M8 | 26/35 | 1.000346 | 5/15/6 | 1.000589 |
| Q128 | 25/35 | 0.996412 | 4/15/6 | 0.996412 |
| Q64 | 25/35 | 0.997321 | 4/15/6 | 0.997321 |

全8共同人口由23扩大至25。每个profile在原锚相同人口上的GM均与锚精确相同；全部旧191对没有任何cycles或speedup改变。因此上述GM相对旧报告的变化是新人口/新配对加入，不能当作旧工作负载性能被重新改善。suite分层与available/common两套人口、全部输入列表和新配对counter变化在SCIENTIFIC_INCREMENT.json/SUPPLEMENT.json中保留。

DH-P0 accepted28/35，CH-P0 33/35；DH-P0仍阻塞7项：3MM (RUNNING_CONFIRMED, 1 accepted variants); GEMM (RUNNING_CONFIRMED, 6 accepted variants); GESUMMV (RUNNING_CONFIRMED, 4 accepted variants); SYRK (PENDING, 0 accepted variants); hybridsort (RUNNING_CONFIRMED, 0 accepted variants); lavamd (RUNNING_CONFIRMED, 0 accepted variants); sgemm (PENDING, 0 accepted variants)。这些输入另有11个已accepted变体等待分母。CH-P0尚缺：SYRK, lavamd。

没有任何profile达到full35 accepted。nonP0 CH尚未开展/缺失，不能计算相对DTC收益或正式挑选uniform配置。旧scan M16 typed工程negative保留、accepted_cycles=null，不纳GM；未来R2完全不计本快照。missing不填0/1，不按程序挑最优profile凑GM。raw reservation原因是重试/拒绝次数，非唯一请求数或耗时；last-printed avg latency非全输入加权均值。完整declared trace计数通过不等于原应用数值输出正确性已证明；英文v0.23母版不变。

## 审计边界

本次只写A/results_increment_v4，不改E目录、生产、历史分类或预算，不模拟。主报告/新raw evidence/完整analysis可使用.gz发布；旧锚raw证据按不可变RESULT/UUID链接复用。individual file snapshot不是覆盖全部正在运行任务的单次事务，采集后自然完成的新点不混入本时间截断。
