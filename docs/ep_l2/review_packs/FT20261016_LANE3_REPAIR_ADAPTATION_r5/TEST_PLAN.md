# Staged production tests — all new C++ cases NOT_RUN

The source extends the r4 executable/harness rather than rerunning old frozen binaries.

- Existing cache, D512, reverse-sector, dirty-WB, native-pin and epoch cases remain. Add repeated actual host prefill of sectors 0/1, stable shared handle/version-zero warm hit, zero timed bank grants during prefill, and rejection of prefill both during and after the whole-commandlist epoch. Direct cache fixtures set physical GPU time before bank callbacks.
- Four actual partition modes with offset0 remain staged. Add offset4096 × C8/C16 × four detach/bypass modes (eight cases), using real force_l2_tag_update, partial-sector reads, normal lower returns, one-entry ICNT backpressure and exact-once requester closure. Count per-bank grant deltas in each physical cycle and require max<=1, zero violations and final drain.
- Re-run source-scoped r4 native all-OFF directed regression and RO independent module references only after shared admission. Old log PASS is not copied onto r5 source.
- Before any formal application: consume official Lane 1 R0.1, freeze new source/binary/config identities, pass Lane 5 physical_bank_clock and memcpy_payload_identity plus separate detach/bypass/combination gates. Lane 5 assigns any run keys/quota. Do not rebuild the old R0/R1 or r4 immutable binaries.

The five executed Python tests validate only configuration-receipt identity/scope, immutable output and explicit pending/current scientific acceptance requirements. Sixteen source-pattern checks are separately labeled STATIC_PASS_NOT_COMPILE_OR_RUNTIME_PASS. Neither substitutes for the staged C++ tests or application independent qualification.
