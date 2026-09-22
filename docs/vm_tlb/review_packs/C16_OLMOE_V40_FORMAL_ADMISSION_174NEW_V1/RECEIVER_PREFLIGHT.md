# Receiver / node164 preflight

`status: PASS_FOR_PREPARATION_ONLY`

- receiver: `huangrulin-sshfs-174`, user `root`
- execution branch: `hrl/c16-olmoe-v40-formal-admission-174new-v1`
- base handoff: `4e52e288064b902ba1850a45eb7bb74e04080953`
- node164 root: `/root/share/mnt164/huangrulin/c16_ai_workload`
- mount: writable SSHFS from node164; C16 root, `captures/inbox`, `raw`, `catalog`,
  `quarantine`, and receipts layouts are readable
- capacity: 70T available at check time
- Python: 3.10.12; Pipeline V1 data-plane sources compile
- transport: `origin` fetch of the coordination branch succeeded
- concurrent formal admission: none observed (`pgrep` inspection)

No accepted raw, catalog entry, or inbox bundle was modified by this preflight.
`FORMAL_ADMISSION_CONCURRENCY=1` remains a runtime admission precondition.
