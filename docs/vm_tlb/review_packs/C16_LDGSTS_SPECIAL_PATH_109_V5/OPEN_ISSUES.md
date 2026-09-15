# Open issues

No scientific blocker remains for the five V5 target sets. The remote receiver exposed a recoverable concurrent-admission catalog `.partial` collision for the S2 Prefill Attention and S3 Prefill Attention bundles. Both remained un-ACKed, were quarantined; their stale unadmitted catalog entries were moved into a timestamped remote recovery audit directory, the snapshot was rebuilt, and the exact local-closed sources were re-verified, admitted serially, and ACKed. No GPU workload was rerun and no raw capture artifact was altered.

This closure does not establish cross-path ordering, cross-process VA equality, or whole-kernel reuse distance.
