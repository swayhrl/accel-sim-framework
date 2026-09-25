# Observatory attribution

Status: **AUTOMATIC ANALYSIS / NO ROOT_CAUSE CLAIM**

Level1 was collected for every development point. Level2 was added for the
two same-cycle regressions, T2 and A1.

- T0/T1: L1 launches fall by
  2,732,281/
  6,638,820;
  `translation_not_ready` and L2 service pressure also fall. This direction is
  consistent with the +5.390%/+2.758% responses.
- A2: physical service falls and dependency-scoreboard events decrease while
  the response is +1.698%; the matched grouping-only arm is exactly OFF.
- T2/A1: both suppress physical service and have zero coalescer head-block
  cycles, so their -1.026%/-1.132% responses do not reproduce old C1 waiting.
  Level1/Level2 show changed cache-reservation, coalescing-stall, scheduler and
  p99-tail distributions. This is consistent with downstream ordering/pressure
  perturbation, but the current evidence does not establish a root cause.
- The +1-cycle sensitivity reverses T2 to a positive response and leaves A2
  within 0.3% of OFF, confirming that response sign can be schedule-sensitive;
  it does not eliminate the service-suppression mediator.

Machine-readable totals, 512-cycle windows and bounded progress checkpoints
are in `OBSERVATORY_LEVEL1.tsv`, `OBSERVATORY_LEVEL2.tsv` and
`OBSERVATORY_PROGRESS.tsv`.
