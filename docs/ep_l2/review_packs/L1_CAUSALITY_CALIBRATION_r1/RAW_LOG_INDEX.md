# Raw Log Index

All runs retain `raw.log.gz`, `run_status.json`, `effective_config.json`,
`target_summary.csv`, `target_l1.csv`, `target_dram.csv`, and
`target_window.csv` beneath their stated result roots.

- D256 META-HR: `/workspace/results/ep_l2_l1_causality_d256/META-HR/`
- D256 BANK-HR: `/workspace/results/ep_l2_l1_causality_d256/BANK-HR/`
- D512 META-HR: `/workspace/results/ep_l2_l1_causality_d512_speculative/D512-META-HR/`
- D512 BANK-HR: `/workspace/results/ep_l2_l1_causality_d512_speculative/D512-BANK-HR/`

Each directory contains the seven selected workloads: vectorAdd_4M, scan,
spmv, convolutionSeparable, btree, sad, and FWT_7_21.

