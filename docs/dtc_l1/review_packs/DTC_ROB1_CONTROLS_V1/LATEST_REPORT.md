# ROB1 cohort3 first-sample admission failure: WAIT_RESOURCE

Status: **WAIT_RESOURCE_FIRST_SAMPLE_FAILED_NO_PAIRED_ADMISSION**.

Coordinatorfacb1991cf134f881b730453a2b86ec7342ba5b2 conditionally released one new finite preflight after a separate parent's single host-IO sample changed. ROB1's actual fresh sample at2026-10-19 13:46:04.953UTC reports host IO-full avg10 **25.81%**, above25%; cgroup IO0% cannot override this failure. Per the explicit first-failure rule, ROB1 took no second sample and started no controller/configure/build. A paired admission/OOM delta is not claimed. Memory PSI/headroom and sampled disk5.596GB are recorded; source/Core/controller/hook/request identities remain clean and exact.

COHORT3_PREFLIGHT_WAIT_RESOURCE.json preserves this finite attempt. The raw sample is `/workspace/dtc-evidence-closure-20261019-v1/rob1/cohort3-preflight/sample1.txt`; its SHA is recorded in COHORT3_PREFLIGHT_RAW_INDEX.tsv. Cohort2's distinct failed paired admission atfd5cedb6 remains preserved. There is no retry loop, poller, background dispatcher, linked-fixture/original-reference execution, simulator, trace scan, execution lock or AG4 change. A later attempt requires a new coordinator release.

Exact matching-b107 library/actual-LDST build request remains prepared and unchanged. Prior standalone quota/service_entry helper PASS is retained; actual parser/constructor/real RF WB integration and wholebinary OFF equivalence remain unqualified. Core remains [b1077667f7a2bcc72260733f88f5798f167346d1](https://github.com/swayhrl/gpgpu-sim/commit/b1077667f7a2bcc72260733f88f5798f167346d1). Candidate remains PROVISIONAL_O K0/OO128/Tag64x8/AE0/AD0; R only GEMM/BICG collector4->1.
