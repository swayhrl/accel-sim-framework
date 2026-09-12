# C15 lane A — static library and fixed-input integration published

Status: `C15_LOWCOST_FOUNDATION_PARTIAL_READY_FOR_REVIEW`. `C15-1.6` and
`C15-5.1` are `COMPLETE / PASS`; `C15-1.3`, `C15-1.5`, `C15-5.2`, and `C15-5.4`
are scientifically `INCONCLUSIVE` rather than over-claimed.

The frozen plan contains 12 candidates. Ten deployment configurations are bound
to a source-backed immutable model revision: nine distinct model lineages plus
the Qwen2.5-7B raw/AWQ storage pair. Three configurations have complete,
range-verified tensor storage catalogs; the other seven are config-static only.
This separation is deliberate—no absent header has been turned into a byte count.

Seven configurations support the explicitly-assumed standard-KV formula; one
DeepSeek configuration is verified as MLA/compressed and is explicitly rejected by
the standard adapter. Two further configurations lack the static dtype/head facts
needed for a curve. All page values are file-layout scenarios, never GPU VA, PA,
TLB working set, or TLB misses.

Network metadata cost recorded by the final receipt is 833,322 B, versus a 1-GiB
campaign budget. Full weights, GPU work, SASS, simulator build/replay, and Core
changes remain zero. The current filesystem reading is still slightly below the
64-GiB reserve, so outputs remain small review artifacts only.

Integration consumed only hash-valid publish manifests from B
`721e30f377dab36d826dc7ea9d47e11c5d85aa5c` and C
`a51d6c91b1e7d7df27a4af80823a29ff30bb9806`. B supplies no new native capture;
C reports `SAMPLER_NOT_QUALIFIED`. The review package therefore makes no dynamic
cross-model, cache/TLB, performance, or upgrade claim. See `integration/`.
