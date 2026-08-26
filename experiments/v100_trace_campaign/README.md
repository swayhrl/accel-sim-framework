# TLS + C2P V100 trace campaign

This directory is the reproducible hardware-trace campaign for the workloads
missing from the TLS Cache and C2P Cache papers.  It deliberately does not
attempt to create the original FRC traces: those are AMD OpenCL/Multi2Sim
workloads, while this campaign emits NVIDIA Volta SASS traces for Accel-Sim.

The campaign has 14 logical cases:

* TLS: Mars SimilarityScore and SHOC FFT, Sort, GEMM, Stencil2D, Reduction.
* C2P: ISPASS BFS, LIB, LPS, RAY and Pannotia color_max, fw_block, mis,
  pagerank.

`manifest.json` is the execution manifest.  `inputs.json` records every input
and its provenance.  The exact paper inputs are not disclosed by either paper,
so all first-pass choices are deliberately marked `candidate`.  A full trace is
refused unless `--allow-candidate` is explicitly given.  When authors reply,
replace each candidate with the supplied parameter/data hash and change the
status to `frozen`. If authors have not replied by the campaign date, the
explicit `freeze` step below instead records a *frozen reconstruction* decision
that remains distinct from paper-confirmed inputs.

## Intended AutoDL host

Use one V100 32 GB instance, CUDA 11.8, and an expandable data disk.  The
observed AutoDL allocation of 6 CPU cores / 25 GB RAM is sufficient for serial
capture, but Stencil2D post-processing is CPU-bound; reserve at least 120 GiB
of free remote disk and continuously offload completed archives.  The trace
format is Volta (`sm_70`), which matches the QV100 simulation configuration;
do not replace it with an A100/4090 merely for native speed.

The host needs `git`, `curl`, `unzip`, `make`, `g++`, `zstd`, `rsync`, Python
3, CUDA 11.8, and a working NVIDIA driver.  Start from the TLS worktree if
possible, because its toolchain lock pins CUDA 11.8 and NVBit 1.7.6.  The
scripts work from any Accel-Sim worktree passed as `--framework-root`.

## One-time setup on AutoDL

From an SSH/tmux shell, after cloning the TLS worktree and copying this
`v100_trace_campaign` directory beside it (the campaign directory need not be
inside the framework worktree):

```bash
export FRAMEWORK_ROOT=/root/autodl-tmp/accel-sim-tls-cache
export CAMPAIGN_ROOT=/root/autodl-tmp/v100_trace_campaign
export WORK_ROOT=/root/autodl-tmp/tls-c2p-v100
cd "$FRAMEWORK_ROOT"

bash "$CAMPAIGN_ROOT/scripts/preflight_host.sh" \
  --framework-root "$PWD" --work-root "$WORK_ROOT"
bash "$CAMPAIGN_ROOT/scripts/build_workloads.sh" \
  --work-root "$WORK_ROOT"
bash "$CAMPAIGN_ROOT/scripts/stage_inputs.sh" \
  --work-root "$WORK_ROOT"
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" validate \
  --framework-root "$PWD" --work-root "$WORK_ROOT"
```

`build_workloads.sh` fetches pinned public sources and compiles only the 14
target applications for `sm_70`. `stage_inputs.sh` preferentially consumes the
campaign's `WORK_ROOT/input-seed/` mirror, then a locally extracted upstream
data directory, and only then requests the upstream helper. It copies only the
C2P candidate files into the campaign input directory and emits a generated
SHA256 lock file. Review and commit/archive that generated lock before a full
run.

## Safe execution order

```bash
# GPU/driver/tracer smoke test. Must pass before burning time on a workload.
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" smoke \
  --framework-root "$PWD" --work-root "$WORK_ROOT"

# Native correctness and metadata-only kernel discovery for all candidates.
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" run \
  --phase native --case all --framework-root "$PWD" --work-root "$WORK_ROOT" \
  --allow-candidate
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" run \
  --phase discovery --case all --framework-root "$PWD" --work-root "$WORK_ROOT" \
  --allow-candidate

# Inspect pilot output and choose/freeze actual inputs. If proceeding with the
# documented reconstruction candidates, create an auditable, hash-bound freeze.
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" freeze \
  --framework-root "$PWD" --work-root "$WORK_ROOT" --case all \
  --rationale 'Paper inputs are undisclosed; reviewed V100 discovery output and approved pinned public reconstruction inputs.'

# Then trace one case. A frozen reconstruction needs no --allow-candidate.
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" run \
  --phase trace --case tls-shoc-fft --framework-root "$PWD" --work-root "$WORK_ROOT" \
  --minimum-free-gib 200

# After approving the pilot volume/runtime, trace the remaining selected cases.
python3 "$CAMPAIGN_ROOT/scripts/campaign.py" run \
  --phase trace --case all --framework-root "$PWD" --work-root "$WORK_ROOT" \
  --minimum-free-gib 200
```

The `trace` phase is serial, resumable, records provenance per case, runs
post-processing, verifies every kernel path named in `kernelslist.g` is present,
nonempty, and (for xz files) has the correct stream signature, then deletes
only raw `.trace`/`.trace.xz` files and creates `archives/<case>.tar.zst` plus
SHA256. It never removes an existing verified archive. A background disk guard
terminates a case before the free-space threshold is crossed. The post-processor
waits for its final xz child before this check, preventing a zero-byte last
trace from being archived.

To copy completed archives to persistent storage automatically, set an already
configured rclone remote before invoking `run`:

```bash
export TRACE_ARCHIVE_REMOTE='myremote:accel-sim-v100-2026'
```

The runner calls `rclone copy --checksum` after every successful archive.  If
no remote is configured, use AutoDL AutoPanel or `rsync` manually before
shutting down the instance.

In a second `tmux` pane, keep the live campaign state visible with:

```bash
bash "$CAMPAIGN_ROOT/scripts/monitor_campaign.sh" --work-root "$WORK_ROOT" --watch 30
```

## Important limits

* `--allow-candidate` is intentional and must remain visible in the run log;
  such traces are reconstruction candidates, not proven paper inputs. The
  `freeze` command binds an approved reconstruction decision to both the exact
  manifest and SHA256 input lock, and includes it in every provenance record.
* `fw_block` is pinned to the small `256_16384.gr` candidate.  The known
  `512_65536.gr` input is excluded until a measured pilot says it is practical.
* Do not run multiple NVBit full-trace jobs on the same V100 concurrently.
* Keep `runs/<case>/provenance.json`, `stats.csv`, `kernelslist.g`, and the
  archive SHA256.  They are the minimum hand-off artefacts for later simulation.
