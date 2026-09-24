# Non-memory visibility canary

Canary: accepted `DECODE_FLASH_PRIMARY_2_STEP16` (`splitkv-combine`), V1 10/80.

The final observer binary exactly preserves the accepted signature:

- cycles: `10480`
- instructions: `72908`
- CTAs: `2`
- unique memory UIDs: `1099`

Level 3 reports:

- scheduler dependency/scoreboard classifications: `34927`
- scheduler barrier classifications: `2898`
- scheduler eligible-but-structural classifications: `31`
- all LDST stall-enum observations: `4835`
- mean DRAM scheduler queue occupancy: `0.047365`
- L1D reservation failures: `0`

The automatic label is:

`PRIMARY_OBSERVED_LOCATION=NOT_MEMORY_DOMINATED:SCHEDULER_DEPENDENCY_SCOREBOARD`

with `MEMORY_PIPELINE_STALLS` secondary.  This validates that the observatory
does not force every workload into a memory diagnosis and can surface an
existing scheduler-side predicate.

This is a location result, not a root-cause claim.  `Scoreboard::checkCollision`
does not preserve the producer domain of a blocked operand, so the observer
cannot determine whether those dependencies originate from compute latency,
memory latency, or a mixture.  That distinction remains `UNRESOLVED` and would
require a controlled experiment or added source provenance beyond V1 scope.
