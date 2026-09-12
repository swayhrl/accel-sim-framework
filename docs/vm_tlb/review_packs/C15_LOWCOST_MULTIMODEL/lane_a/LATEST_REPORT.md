# C15 lane A — static library published; integration pending

Status: `C15-1.6 COMPLETE / PASS`; `C15-1.3` and `C15-1.5` are scientifically
`INCONCLUSIVE` for configurations lacking a verified Safetensors header.

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

Next: fetch B/C only at fixed commits, accept only a hash-valid publish manifest,
and write any synthesis solely under `lane_a/integration/`.
