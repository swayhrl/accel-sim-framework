# 已接受机会背景：原始计数与范围

generation47；每条raw SHA与接受row、独立review SHA一致，使用最后一组application累计/FT每slice记录，未把多次kernel边界打印相加。46个有限路径raw全部保留为derived行，含零/负性能点；另5个Ideal端点只列catalog，不用于有限机会推断。raw未输出M0/L2CHAR专用观测时保留null，不能当真实0。

## 同binary四模式（combined fb67448d，H0）

| workload | profile | cycles | pin_block | pool_full | wbuf_full | WB_record_peak | WAD_peak | c7d_wad_full_events | c7d_wad_hazard_events | c7d_missq_full_block | c7d_l2_to_dram_full_block | c7d_dram_scheduler_full_block | c7d_dram_issue_eligible | bank_retry_attempts | bank_wait_cycles |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FWT_7_21 | B16_OFF | 493189 | 0 | 0 | 890294 | 16 | 104 | 0 | 276421 | 12870 | 12779 | 841577 | 1974182 | 405349 | 405349 |
| FWT_7_21 | S64 | 494627 | 0 | 0 | 0 | 35 | 115 | 0 | 302684 | 908665 | 902794 | 845813 | 1978737 | 392301 | 392301 |
| FWT_7_21 | U_CAP16 | 491696 | 0 | 0 | 0 | 16 | 104 | 0 | 279383 | 14107 | 14013 | 839067 | 1973609 | 311688 | 311688 |
| FWT_7_21 | U_OFF | 491662 | 0 | 0 | 0 | 37 | 115 | 0 | 309144 | 974258 | 967911 | 855338 | 1988799 | 316103 | 316103 |
| convolutionSeparable | B16_OFF | 292932 | 0 | 0 | 845097 | 16 | 122 | 0 | 0 | 180063 | 218465 | 2285074 | 5191465 | 1122236 | 1122211 |
| convolutionSeparable | S64 | 293258 | 0 | 0 | 0 | 58 | 128 | 1892 | 0 | 737284 | 846027 | 2279974 | 5185812 | 1105703 | 1105680 |
| convolutionSeparable | U_CAP16 | 292544 | 0 | 0 | 0 | 16 | 126 | 0 | 0 | 194270 | 240798 | 2253887 | 5160955 | 943026 | 943013 |
| convolutionSeparable | U_OFF | 291525 | 0 | 0 | 0 | 55 | 128 | 2706 | 0 | 946179 | 1131759 | 2322087 | 5228345 | 935284 | 935249 |

`wbuf_full`、WAD full/hazard、MissQ full是不同控制边界的计数。bank重试是调用次数，bank_wait是各logical-op等待间隔之和；不同slice/请求重叠，不能相加为独占GPU stall。WAD-full与same-address hazard是独立预检谓词；不能把其和当一个消除后可直接兑现的时间。`c7d_l2_to_dram_full_block`在`!admit && plan.will_send_lower_read && lowerq.full()`时增加，是frontend伴随条件，不是所有MissQ head drain的精确拒绝数，更不是MQ2机会计数。scheduler-full按真实DRAM issue-attempt观测，不是GPU时间分母。

## 原H0五输入（binary23094a9d，不替换原五输入结论）

| workload | profile | cycles | pin_block | pool_full | wbuf_full | WB_record_peak | WAD_peak | c7d_wad_full_events | c7d_wad_hazard_events | c7d_missq_full_block | c7d_l2_to_dram_full_block | c7d_dram_scheduler_full_block | c7d_dram_issue_eligible | bank_retry_attempts | bank_wait_cycles |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sad | B16_BANKED | 110773 | 0 | 0 | 0 | 1 | 11 | 0 | 0 | 0 | 0 | 0 | 4374 | 2255 | 2255 |
| sad | U_WB16 | 110749 | 0 | 0 | 0 | 1 | 10 | 0 | 0 | 0 | 0 | 0 | 4374 | 2233 | 2233 |
| vectorAdd_4M | B16_BANKED | 73696 | 0 | 0 | 440161 | 16 | 95 | 0 | 0 | 1131061 | 1103500 | 975968 | 2076536 | 445678 | 445678 |
| vectorAdd_4M | U_WB16 | 73549 | 0 | 0 | 0 | 35 | 101 | 0 | 0 | 1806747 | 1763609 | 974186 | 2074702 | 367415 | 367415 |
| cfd_097k | B16_BANKED | 79093 | 0 | 0 | 5 | 16 | 69 | 0 | 9841 | 0 | 0 | 101780 | 345211 | 102546 | 102546 |
| cfd_097k | U_WB16 | 79262 | 0 | 0 | 0 | 16 | 67 | 0 | 13400 | 0 | 0 | 102720 | 345995 | 91029 | 91029 |
| convolutionSeparable | B16_BANKED | 292932 | 0 | 0 | 845097 | 16 | 122 | 0 | 0 | 180063 | 218465 | 2285074 | 5191465 | 1122236 | 1122211 |
| convolutionSeparable | U_WB16 | 291525 | 0 | 0 | 0 | 55 | 128 | 2706 | 0 | 946179 | 1131759 | 2322087 | 5228345 | 935284 | 935249 |
| FWT_7_21 | B16_BANKED | 493189 | 0 | 0 | 890294 | 16 | 104 | 0 | 276421 | 12870 | 12779 | 841577 | 1974182 | 405349 | 405349 |
| FWT_7_21 | U_WB16 | 491662 | 0 | 0 | 0 | 37 | 115 | 0 | 309144 | 974258 | 967911 | 855338 | 1988799 | 316103 | 316103 |

这10行pin_block=pool_full=0。全部46行这两项亦为0，但只表示这些实际counter未激活，不证明所有可能frontend等待已完整覆盖。不优先开发pin-aware victim或跨bank任意landing。46行终态created=lower_accept=completed，logical_ops=grants，reserved/read_refs/wb_slots/wb_live=0；终态闭合不排除中间retained-grant空转。

## 既有受控正负例

Conv Q4 B/U为290333/293709，S_EP=0.988505630；WAD256_Q4为292132/289899，S_EP=1.007702683。WAD-full计数55645/54516降为0/0。该metadata控制有实测交互，但不是MQ2/RG1结果、不是任意输入可兑现的critical-path贡献。Conv D4中U bank_wait从1962721降至1791989而cycles由B267521到U268544变慢；少重试/少等待不能替代实测效果。CFD H0负例与所有其它有限背景仍保留在CSV。

`window_availability_summary.csv`汇总169472条原5000-cycle slice-window记录（46行导出）；其中正占用与bank等待共处一个窗口，只是粗粒度共存，不证明相同cycle相同请求的ready/blocked关系。整数平均为0也不证明窗口里队列从未非空。
