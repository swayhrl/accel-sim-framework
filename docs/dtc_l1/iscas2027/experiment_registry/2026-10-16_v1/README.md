# DTC ISCAS2027 experiments: living register

## Latest: V3 and bounded multi-Codex work split

2026-10-16。**[Master matrix V3](MASTER_MATRIX_V3.md)** / [TSV](MASTER_MATRIX_V3.tsv) / **[Multi-Codex plan and task files](multi_codex_v1/README.md)**。

Latest synchronized source:174 `e3dbe3dbf2abb49b923244538d2a3d1828024d4f`, checkpoint20261016T094353Z. Of44 registered rows,5 pass terminal/invariant checks **including2 Hotspot rows on scientific HOLD**,8 running,3 admission-held,28 not started. Full629-body audit confirms fixed-input instruction totals and global-load reference bound32, but discovers90792 Hotspot shared sparse-mask/base-stride interpretation gaps. Original numbers/receipts are preserved; Hotspot semantic promotion and three pending rows stay held. No GM12.

Main A remains original174's active Goal and sole simulation launcher. Prepared helper windows: B on original174 investigates Hotspot provenance; C on original174 resolves a minimal modern128KiB layout proposal; D on109 examines existing SM89 support for SpMV using CPU only. Helpers use separate branches/worktrees and cannot alter the running parser/binary, scheduler, raw data or scientific holds. This commit **does not start any helper or simulator**. The prior terminal-GPU producer work on109 remains completed; LayerNorm trace non-admission remains.

Modern DTC capacity/ports and SpMV SM89 support remain review gates. These proposals do not authorize production protocol/address/support changes. No frozen SG3/logical80 or full pipeline redo. New state snapshots require concrete remote receipts, not logs alone.

## Original register V1 (historical)

Created2026-10-16. [MASTER_MATRIX_V1.tsv](MASTER_MATRIX_V1.tsv), [MASTER_MATRIX_V1.md](MASTER_MATRIX_V1.md), [EXECUTION_PIPELINE.md](EXECUTION_PIPELINE.md), [PAPER_SETUP_REQUIREMENTS.md](PAPER_SETUP_REQUIREMENTS.md), [UPDATE_PROTOCOL.md](UPDATE_PROTOCOL.md). R1 V2 qualification: e1c474f/Core6fba013. Producer109:890fb0be. Capacity decision:e13266, fixed128KiB. These snapshots are preserved, not real-time authorities.

## V2 checkpoint (historical)

[Master status V2](MASTER_MATRIX_V2.md) / [TSV](MASTER_MATRIX_V2.tsv) / [Source checkpoint analysis](CHECKPOINT_20261016T0918Z.md). Source174 `59e1fd9b`: at09:17UTC,44 registered=3 Btree strict terminal PASS,6 running,35 not launched. At that point four modern baseline results had original terminal checks; the later V3 Hotspot scientific hold now limits their use. SpMV SM89 dispatch and LayerNorm trace were not admitted. The source evidence and failures remain unchanged.

## Paper setup

[PAPER_SETUP_APPLIED_V0_6.md](PAPER_SETUP_APPLIED_V0_6.md) records the local IEEEtran setup-table revision. It is not a claim that manuscript source or new performance was uploaded here. Updates to this register are documentation only and must not be used to reset either experiment repository.
