# Final decision

`C16_QWEN3_S3_KV_SCALING_109_V20_PASS`

Both exact S2_TEXT B1/T2048/D32 and S3_TEXT B1/T8192/D16 first-decode K-post states passed isolated replay bitwise equivalence, in-context signature equivalence, fresh static/path closure, full CTA/address-membership gates, complete formal capture, serial Pipeline admission and positive ACK.

The result applies only to K-cache storage read / repeat-K materialization. QK/AV are not called direct KV-cache reads.
