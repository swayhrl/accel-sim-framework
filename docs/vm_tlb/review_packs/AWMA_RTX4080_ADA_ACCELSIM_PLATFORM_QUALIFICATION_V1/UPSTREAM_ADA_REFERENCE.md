# Upstream Ada engineering reference

Reviewed, not merged wholesale:

- Framework PR #548: https://github.com/accel-sim/accel-sim-framework/pull/548
- exact Framework head: `0c840b276bfecc6c7d1590efd7d5a22b8dff05f6`
- matching contributor gpgpu-sim branch head: `dc56ca74fa51d333cacb6a8aac91bce804301ae1`

Selectively reused:

- binary version 89 constant;
- SM89 to Ampere opcode-map selection;
- trace-config conventions;
- closest available Ada base-config scaffold.

Not accepted as hardware authority: the PR is open/unmerged; the 4060 Laptop scale and undocumented pipeline values are not RTX4080 facts. The already-qualified local SM89 subset audit remains parser-admission evidence only, not full Ada ISA fidelity.
