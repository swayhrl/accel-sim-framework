# EP-L2 ChatGPT Handoff — Current State

Updated: 2026-08-30

This is a coordination summary for the EP-L2 research workflow. If it conflicts with a newer reviewed closeout, stop and report the conflict instead of guessing.

## Frozen C6c anchors

```text
Core      0cde333340792cffed869cbbc7e7dc88667c6b8b
Framework 0a0c0fc3e1ffb6ca346090e59e94d2128e5adc0e
```

C7d is developed in isolated worktrees/branches derived from these anchors. Do not modify or reuse the live C6c smoke/prefill worktrees from C7d.

## C6c status

Pre-C6c B0-Banked forced every logical bank operation through an unconditional staging/retry cycle. The old ~50% `bank_conflicts` rate and old Banked performance data are non-evidentiary.

C6c corrected the behavior:

```text
idle bank + no older pending/granted op
    -> first ready op grants immediately this cycle

older pending/granted op exists
    -> preserve oldest-ready priority

later same-bank op in an already-used cycle
    -> true contention / retry
```

C6c telemetry:

```text
bank_logical_ops
bank_attempts
bank_grants
bank_retry_attempts
bank_true_conflict_ops
bank_true_conflict_events
bank_wait_cycles
```

Observed smoke evidence:

```text
spmv:
  Legacy cycles = 23,453
  Banked cycles = 23,453
  logical ops/grants = 422,502 / 422,502
  true conflicts = 0
  wait cycles = 0

cfd_097k:
  Legacy cycles = 79,555
  Banked cycles = 81,443
  logical ops/grants = 1,093,466 / 1,093,466
  true conflicts = 16,166
  wait cycles = 16,166
```

Long C6c smoke/prefill runs may finish as diagnostic evidence. If C7d changes the Core SHA, do not silently promote those runs into the final formal Target-Baseline dataset.

## Frozen Target Baseline

Per L2 slice:

```text
128 B line, 4 x 32 B sectors
Resident Tag: 64 sets x 16 ways = 1024 entries
Resident payload quota: 1024
Bypass payload quota: 128
B0-Legacy: separate resident/bypass 1R1W RAMs
B0-Banked: 1152 entries, 4 x 288 banks, payload_id % 4,
           static 1024 resident + 128 bypass ownership
Line MSHR: 128
Shared persistent request descriptors: 256
Per-address descriptor cap: 32
WAD: 128
ICNT->L2: 64
L2->DRAM: 128
DRAM->L2: 64/slice
L2->ICNT: 64
FR-FCFS scheduler: 128/channel
DRAM ReturnQ: 192/channel
Primary DRAM clock: 850 MHz
Primary L1: 64 KiB, 4 sets x 128 ways x 128 B, 4 banks, 20 cycles
```

No Unified borrowing, RO no-MSHR, replaceable RO pending, TVD functionality, or graphics borrowing belongs in the Target Baseline.

## Useful Round-2 evidence

```text
btree merge 2 -> 4 -> 8 improves strongly; 8 -> 16 saturates
MissQ 32 -> 64 gives little/no general benefit
L2->DRAM 64 -> 128 gives little/no general benefit
FR-FCFS depth strongly affects vectorAdd, saturates near 128 for spmv,
and is non-monotonic for cfd
```

Do not interpret FR-FCFS queue-size sensitivity as pure buffer-capacity sensitivity.

## Why C7d exists

Current `EPL2B0V1` is useful but still has incomplete or ambiguous blocker semantics. After C7d, the next clean `13 workloads x 2 baselines @850 MHz` campaign should be the only full Target-Baseline characterization rerun needed.

C7d is instrumentation-only and must not change simulated architecture behavior or timing.

C7d should make the final campaign accurately distinguish:

```text
Tag/set allocation pressure
LINE_MSHR_FULL
DESCRIPTOR_POOL_FULL
PER_ADDRESS_CAP
WAD full vs same-address hazard
payload service vs capacity
real bank contention
L1 bottlenecks
MissQ vs L2->DRAM vs DRAM scheduler vs ReturnQ vs DRAM bandwidth
sustained vs bursty pressure
```

## Final 26-run role

After C7d freezes new final SHAs:

```text
13 frozen workloads x {B0-Legacy, B0-Banked} @850 MHz
= 26 formal runs
```

That campaign should answer the Target-Baseline bottleneck questions once.

## Opportunity study is separate

The final 26-run cannot quantify RO/TVD/Unified opportunity by itself. Those require timing-neutral shadow state.

After Target-Baseline freeze:

```text
RO oracle + RO shadow
TVD shadow
Payload-role complementarity shadow
kernel/epoch snapshots
```

Opportunity runs should primarily use B0-Banked because proposed Unified uses the same 4-bank physical organization.

## Execution order

```text
C6c smoke/prefill diagnostic work
          +
C7d instrumentation completeness
          |
          v
C7d closeout + timing-neutrality review
          |
          v
freeze final Target-Baseline SHAs
          |
          v
one clean 26-run @850 MHz
          |
          v
Target-Baseline analysis / closeout
          |
          v
small 1 GHz subset if still justified
          |
          v
opportunity branch: RO / TVD / complementarity shadow
```
