# Findings

All six Recovery-V2 traces pass formal admission and SHA/size closure.

- S3, S4, and S5 Prefill have matching selected-target structural counts:
  8,192 records, 262,144 lane addresses, 1,120 observed 128B lines, 35
  observed 4KiB buckets, and 19 observed 2MiB buckets. These are
  independent-process reproducibility results, not absolute-VA overlap claims.
- S5 Decode2/3/4 each has 64 selected requests and 2,048 lane-address records.
  Within each capture all 2,048 lanes repeat one observed 4-byte GPU VA; the
  three absolute VAs differ, so exact/32B/64B/128B overlap is zero across all
  decode-step pairs and across the three-way relation.
- Decode2 and Decode3 share an observed 4KiB and 64KiB bucket; Decode4 is in
  another such bucket. All three are in one observed 2MiB bucket. These are
  GPU-VA set relations only, not physical-page, TLB, or cache evidence.
- Compared structurally, Prefill has contiguous two-byte lane accesses and
  Decode repeats a four-byte address across active lanes. No Prefill-to-Decode
  absolute VA set comparison or Jaccard is computed.
