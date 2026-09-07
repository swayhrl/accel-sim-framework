# B3/B6 — pinned-epoch lifecycle and local replicas

The controller now begins with disabled local Segment images rather than
constructor-installed copies. The deterministic privileged-control seam is:

```
INACTIVE --begin_segment_install--> INSTALLING --all N replica acks--> ACTIVE
ACTIVE   --begin_segment_revoke--> REVOKING   --all N replica acks--> INACTIVE
```

`begin_segment_install()` accepts only an atomically accepted registration,
records its active ASID/epoch, clears every local image, and resets per-SID
ack bits. `acknowledge_segment_install(sid)` copies the same canonical image
to exactly that local replica. `segment_active()` becomes true only after all
replicas have acknowledged; lookup code gates descriptor access on that
state.

`begin_segment_revoke()` removes global eligibility immediately by leaving
`ACTIVE`. Each revoke acknowledgement clears its own local image. Only after
all acks may the controller return to `INACTIVE`, clear active ASID/epoch and
allow a new install. A normal mapping invalidate/ASID flush on the active
ASID enters the same revoke path. This is the model-side prerequisite before
remap, free or context reuse.

The v1 model has one active provisioned ASID. A second installation attempt
while installing/active/revoking is refused, so it cannot silently replace a
live context; that context continues conventional translation until the
privileged lifecycle has revoked and installed a new image.

Epoch `0xffff` is never silently reused: final revoke sets an explicit
quiesce-required latch. Only `quiesce_segment_epoch_wrap()` in `INACTIVE`
clears it; C10-B must validate the associated global invalidation/runtime
protocol.

Observable fields include lifecycle state, registration status, provisioned
ASID/epoch, lifecycle-active ASID/epoch, install/revoke attempts/results,
per-replica ack totals and epoch wrap quiesces. These are source-delivered
telemetry names, not inspected runtime output.
