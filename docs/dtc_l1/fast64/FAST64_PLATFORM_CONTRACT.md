# DTC FAST64 Platform Contract

Status: **CANDIDATE FROZEN — MUST PASS FAST64.1 BEFORE PRIMARY USE**

## 1. Platform-shell origin

FAST64 reuses only the stable, trace-driven 64-SM shell concepts already
validated by the C2P reproduction infrastructure. It does **not** reuse C2P's
cache mechanism or C2P's 64-KiB/32-way L1 as the DTC baseline.

The shell candidate is:

- 64 simulator endpoints;
- one SM per endpoint (`64 x 1`);
- 1.41-GHz core/ICNT/L2 and 850-MHz DRAM domains;
- GTO scheduling;
- 20 memory partitions;
- two sub-partitions per memory channel;
- the deterministic non-IPOLY 20-partition mapping already used by the stable
  C2P paper-table shell;
- the stable C2P-shell L2 geometry/path timing unless FAST64.1 proves an
  incompatibility with DTC's unrelated contracts.

## 2. DTC mechanism-preserving cache/resource contract

The following values come from the DTC mechanism contract, not from C2P:

| quantity | FAST64_BASE | FAST64_IO | FAST64_OO |
| --- | ---: | ---: | ---: |
| logical L1/tag capacity | 16 KiB | 16 KiB | 16 KiB |
| line size | 128 B | 128 B | 128 B |
| logical associativity | 4-way | 4-way | 4-way |
| conventional data capacity | 16 KiB | n/a | n/a |
| physical DTC pool | n/a | 80 KiB / 640 lines | 80 KiB / 640 lines |
| PIB | 8 | 256 | 128 |
| traditional MSHR capacity | 32 | not a DTC capacity | not a DTC capacity |
| tag banks | 4 | 4 | 4 |
| tag service | 1 req/bank/cycle, max 4 | same | same |
| physical allocation width | n/a | 4/cycle | 4/cycle |
| lower issue width | source/frozen | 1/SM/cycle | 1/SM/cycle |
| L1 write ratio | 0 | 0 | 0 |
| observer runtime-stat cadence | 500000 | 500000 | 500000 |

The FAST64 bring-up must prove from resolved configurations and source that
unrelated GPU parameters are identical across Base/IO/OO.

## 3. Lower-outstanding capacity

Candidate primary cap:

`FAST64_LOWER_CAP = 8192 = 64 SM * 128 credits/SM`.

This value is **not formal merely because of proportional scaling**.
FAST64.1/FAST64.2 must prove that it is not an artificial performance
bottleneck for representative DTC traffic.

Qualification compares the candidate against a clearly non-binding high cap
(e.g. 1,048,576) using at least two representative workloads/modes.

The candidate is accepted only when, for each comparison:

- final cycles are equal;
- final instructions are equal;
- parser-visible scientific counters are equal;
- lower-cap-full stalls are zero under 8192;
- lower/accounting terminal state is identical.

If 8192 binds, increase to the smallest common value demonstrated non-binding
across the qualification cases. Never choose a cap based on which value gives
the best DTC speedup.

## 4. Observer identity

FAST64 uses the independently validated stats-light A1 observer:

`-gpgpu_runtime_stat 500000`

Observer overlay SHA from existing M5 evidence:

`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`

No future FAST64 Base/IO/OO triplet may mix A0 and A1 observer identities.

## 5. Platform-diff requirements

FAST64.1 must materialize complete resolved configs for Base/IO/OO and produce
a machine-readable diff. Every differing line must be classified as exactly
one of:

- `DTC_MODE_REQUIRED`;
- `PIB_REQUIRED`;
- `PHYSICAL_POOL_REQUIRED`;
- `DTC_INTERNAL_REQUIRED`;
- `ERROR_UNRELATED_DIFFERENCE`.

Any `ERROR_UNRELATED_DIFFERENCE` is HARD failure until resolved.

## 6. Forbidden substitutions

FAST64 must not silently import from C2P:

- 64-KiB/32-way private L1;
- C2P Snapshot Matrix or peer-L1 logic;
- C2P/ATA/CCD/RING latency paths;
- C2P cache-search queues;
- workload-specific C2P tuning knobs.

C2P contributes only a validated platform shell, existing trace payloads, and
runtime/infrastructure experience.
