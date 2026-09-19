# Source anchors

`ldst_unit::memory_cycle()` gates only current `accessq_back()`. `process_memory_access_queue_l1cache()` may pop up to L1D banks per cycle; bypass ICNT may likewise pop multiple queue entries.
