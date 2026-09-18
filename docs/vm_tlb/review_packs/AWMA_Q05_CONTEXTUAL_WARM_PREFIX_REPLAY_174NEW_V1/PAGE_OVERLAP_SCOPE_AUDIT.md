# Translation-relevant page-overlap scope audit

The replayer enters VM only from `ldst_unit::memory_cycle()` for global, local, and param-local spaces. `contextual_page_overlap.py` mirrors trace-driven opcode space resolution, including generic LD/ST first-active-address classification using each trace header's shmem/local bases. It excludes shared, constant (`LDC`/`ULDC`), texture/surface, addressless controls, and zero-width implicit records.

The resulting tables are trace-address page overlap (4 KiB and 64 KiB), not hardware or simulator-TLB residency. They deliberately remain separate from the simulator `{asid,vpn,page_size}` domain.
