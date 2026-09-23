# Context persistence audit

Both trace filenames are consumed by one `accel_sim_framework` instance and one `gpgpu_sim` object in order: warmup kernel uid=1, then measurement kernel uid=2.

- L1D: naturally invalidated when all threads complete because the frozen base config has `-gpgpu_flush_l1_cache 1`.
- L2: preserved; the frozen config does not enable L2 flushing.
- shared TLB/PWC/controller: preserved in the single `translation_controller` constructed with the simulator and not recreated at kernel cleanup.
- memory contents and mapping: preserved in the same simulator process/context.
- per-kernel shader execution state: naturally re-bound for uid=2.

The L1 invalidation is reported scope. No simulator semantics were changed to force persistence.
