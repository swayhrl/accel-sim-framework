# 174 V4 publication review status

Status: `NOT_CLOSED / EVIDENCE_INSUFFICIENT_FOR_PUBLICATION`

Date: 2026-09-20

Mode: `ZERO SCIENCE REVIEW`. No simulation, replay, new scientific data, or
TLB/PTW/cache mechanism work occurred in this recovery/review path.

## Remote publication state

The V4 exec ref remains intentionally unchanged:

```text
hrl/awma-174-hitpath-v4-provenance-closeout-exec
c8657cf637c5b54a0f40135248ff1eabcfd66696
```

That commit tree does not contain the required final V4 report, latency matrix,
target-delta table, coverage table, envelope, receipts, raw index, or closure
SHA256SUMS. It must not be described as a completed provenance closure.

## Node164 recovery

The stale sshfs endpoint was safely detached. The mount was subsequently
restored externally and is readable at:

```text
/root/share/mnt164/huangrulin
```

The exact durable V4 root is:

```text
/root/share/mnt164/huangrulin/awma_runtime_activation_forensics_hitpath_v4
```

`NODE164_MOUNT_RECOVERY_RECEIPT.json` is included in this commit and binds the
mount source, the exact durable root, and the raw completeness check.

## Immutable evidence result

The qualification log is complete:

```text
P34_REPAIRED_10_80_QUALIFICATION
run.log SHA256 = 4551f875b2f292a3824a60e070e9fdb03be09290c426f24fda0c1ba64abafdf2
terminal marker = present
AWMA_VM_COVERAGE(3090304/3090304, untranslated=0, unobserved=0) = present
```

Every required V4 matrix point is incomplete in the recovered immutable root:

```text
P34_HITPATH_0_80   terminal=0  coverage=0
P34_HITPATH_0_0    terminal=0  coverage=0
P34_HITPATH_10_0   terminal=0  coverage=0
P34_HITPATH_5_80   terminal=0  coverage=0
P34_HITPATH_2_80   terminal=0  coverage=0
P34_HITPATH_10_40  terminal=0  coverage=0
```

`V4_MATRIX_STATUS.txt` (SHA256
`4121636df93f67decb838ded4fd91a57ba465a5e9cc47948a202cf83968f4a6a`)
records only Wave A/B/C launch PIDs; it is not a completion receipt.

## Review boundary

No matrix, target-delta, coverage invariant, envelope, run-receipt, raw-index,
or SHA256SUMS closure artifact has been fabricated from memory or partial logs.
Consequently no `FINAL_SHA` satisfying the V4 publication contract exists, and
`AWMA_174_V4_REMOTE_PUBLICATION_CLOSED_VERIFIED_V2` has not been emitted.

Requested ChatGPT review: decide whether the missing six complete immutable
matrix receipts require a distinct scientific requalification decision. This
zero-science publication-repair Goal does not authorize a rerun or a claim that
the partial logs represent complete points.
