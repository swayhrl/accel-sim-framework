# Baseline and telemetry neutrality

## Evidence already closed

- The feature defaults OFF and the accepted baseline `tag_array::probe` body remains the OFF path.
- New metadata helpers return without mutation when the functional feature is disabled.
- 1,998 randomized LRU/FIFO selector cases reproduce the baseline invalid/recency result with the feature OFF.
- Quota zero follows the baseline selector and never protects a fill.
- Diagnostic enable is absent from victim-selection inputs. Matched diagnostic OFF/ON configs produce identical interval lookup and quota allocation.
- Full Core compilation passes. The accepted `vm_core_m1_test` regression passes.

## Still required before final readiness

The frozen quota-full/no-local-protected state must first receive an authorized semantic resolution. After that change, run the small non-C16 simulator fixture for:

1. clean accepted Core;
2. instrumented Core, feature OFF;
3. feature ON with diagnostics OFF;
4. feature ON with diagnostics ON.

For the applicable matched pairs, compare allocation/victim sequence, cycles, instructions, cache counters, request ordering, termination and output. No real C16 replay is authorized.
