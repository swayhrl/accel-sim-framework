# Round-1 Wave-1 execution contract

Round-1 is an **application-level** L2CHARV1 campaign. A result covers the
whole replay from first to final kernel launch; it is not labelled as a
per-kernel resource share.

`util/l2_char/run_round1_campaign.py` is the campaign runner. It reads the
reviewed 52-row roster and uses the recorded `trace_tree_sha256` instead of
rescanning the 159 physical trace roots.

## Ordered cohorts

| Selection | Entries | Purpose | Start condition |
|---|---:|---|---|
| `wave1a` | 27 | `PRIMARY_FULL/RUN`, historical `<1h` | Start now. |
| `wave1b` | 4 | Primary entries with a historical 1--4h scheduler prior | After Wave-1A qualification review. |
| `wave1c` | 3 | Primary entries with no historical runtime | After Wave-1A qualification review. |
| `ubench` | 6 | Sanity/reference only; excluded from workload-heterogeneity aggregates | After the primary quality gate. |
| `secondary` | 11 | V100 bounded/special and trimmed diagnostics | Natural-drain qualification only. |

Every job has an 8-hour limit. The only valid terminal state is
`COMPLETE_VALID`: normal simulator exit, successful production parse, and
passing terminal invariants. Other terminal states remain explicit:
`TIMEOUT_8H`, `SIM_ERROR`, `INVARIANT_FAIL`, `PARSE_FAIL`, or `OOM`.

## Fixed production contract

Every run records the paired core/framework SHA, QV100 base and trace config
SHA256, and observation-overlay SHA256. The runner rejects an overlay unless
instrumentation is on with a 5,000-L2-cycle window, set/window data enabled,
and every directed issue/ReturnQ hold hook set to zero.

The scheduler admits at most the requested number of jobs and starts no new
job when `MemAvailable < 96 GiB` (configurable). It writes current peak RSS,
wall time, any matching RSS prior, trace-tree SHA256, terminal cycles and
instructions, and a complete status to `run_status.json`.

## Wave-1A command

```bash
python3 util/l2_char/run_round1_campaign.py \
  --wave wave1a --jobs 10 --mem-available-min-gib 96
```

Canonical outputs are under
`docs/l2_char_v1/round1_results/<suite>/<workload>/<input>/`: `raw.log`,
parsed CSVs, manifest, parser diagnostics, and `run_status.json`. Once a wave
is reviewed, the canonical source outputs stay there and a compressed review
pack is added under `docs/l2_char_v1/review_packs/`.

After a wave drains, generate the evidence table before deciding whether to
start the next cohort:

```bash
python3 util/l2_char/summarize_round1_qualification.py \
  --wave wave1a \
  --out docs/l2_char_v1/round1_results/wave1a_qualification.tsv
```

It reports terminal L2 accesses/misses, performance, output shape, resource
pressure/blocking, RSS, and an explicit `UNREVIEWED_COMPLETE` state. It does
not apply an arbitrary scientific inclusion threshold.
