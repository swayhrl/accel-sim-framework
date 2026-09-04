# M4R trace-policy decision

Status: `PASS`.

The immutable semantic manifests show 32 `NCCL_COLLECTIVE` entries in each ROI;
therefore `FULL_RANK0` and `COMPUTE_ONLY_TP_PARTITION` are distinct and neither
is represented as author-exact.  All required compute families and the one
observed NCCL AllReduce-BF16-TREE family bind on the final Core.

`COMPUTE_ONLY_TP_PARTITION` is selected as the primary paper-facing path because
the paper evaluates one TP=4 partition.  `FULL_RANK0` remains the required
self-capture sensitivity/provenance path and is preserved in the launch
manifest.  `NCCL_ONLY_DIAGNOSTIC` is retained for diagnosis only.

The bounded real-PTE pilots demonstrate that treatment is material rather than
silently interchangeable: the first decode1 compute kernel completed normally
in 2.62 seconds, while the representative captured NCCL AllReduce bound and
continued making startup progress through the 30-second diagnostic limit.  No
policy is claimed to be paper-exact; full-result tables retain the policy label.
