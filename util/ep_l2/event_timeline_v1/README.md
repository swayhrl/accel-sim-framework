# Portable offline EPET views

Python3.9+ standard library only. Run in isolation; no model, controller, native actor, GPU, shared registry, or old workspace is needed. Distribute the complete EPET_OFFLINE_VIEWS_V1 package together. Decoder f20 and converter1c38 are copied byte-for-byte and hard-pinned; original sources and frozen header/contract are unchanged.

Application-wire component:

    python3 -I epet_views.py render --raw /absolute/accepted/raw.log --kernel-catalog /absolute/expected-kernels.json --out-root /absolute/fresh-output

Expected-kernels.json is an independently supplied ordered list of exact {"uid": integer, "name": "full kernel name"} objects, not a catalogue inferred by the tool from the same wire. Duplicate UIDs, incomplete names, wrong order/content, missing catalogue, and mismatching geometry reject. Actual Source/Input/native/model/scientific acceptance remains external. The wrapper checks only EPET wire/component closure and retained-event display, even when the caller calls its input accepted.

Bundled contract SHAe5b078dc5a544c9ae5ba0d3415b017be92f2961b36e8a7ad2a219098388f8bfa and header SHA43abce5b30c3628e9ee7232f2f98c5a1c1bd471537f05139869be82df098f978 correspond to Core78f4. Optional --contract/--header select another file path only if its bytes have those same hashes. Expected geometry is strictly64slices/32sets/8ways. The decoder is always synthetic=False for render. Header/contract SHA alone does not identify the runtime binary, input, or science owner.

Explicit CPU component mode, never application evidence:

    python3 -I epet_views.py synthetic-cpu --raw /absolute/header-fixture.wire --out-root /absolute/fresh-cpu-output

The two modes are distinct CLI subcommands. A successful synthetic-cpu output cannot be relabelled as an application proof by this wrapper. CPU mode still checks the same final header/contract and geometry. It allows no expected catalogue, or an optional explicitly supplied one. render has not been positively tested using a synthetic wire; its negative wrong/missing catalogue controls reject before creating output.

Outputroot must be absent, its parent must already exist, and input/output/package paths must contain no symlinks or parent-traversal components. Existing outputs are never overwritten or merged. On a rare rendering I/O failure a partial fresh outputroot is left for inspection; choose another fresh root for any explicitly requested new attempt.

Files:

- VERIFIED_EPET_COMPONENT.json: strict decoder result, explicitly component-only/no science authority.
- views/EVENTS.csv, UID_TIMELINES.json, UID_TIMELINE.html, SYNTHETIC_ORDINAL.vcd, README.txt and VIEW_MANIFEST.json: unchanged converter outputs.
- OFFLINE_VIEW_PACKAGE_RECEIPT.json: module/input/header/contract/catalogue/result/view hashes, mode, scopes and no-authority flags.

VCD horizontal coordinates are recorded global ordinals, synthetic display steps. The compulsory VCD timescale token is not a conversion to real seconds/ns/ps. CORE/L2/DRAM counters remain separate signals. SameCORE R6->7->6 events are separate display positions. Missing/censored spans, unknown fields, partial snapshots and distinct generation namespaces remain explicit. Only recorded packet creation/split links supply known parent edges; address equality does not invent ancestry. Browser UIDs/generations remain decimal strings to avoid JavaScript precision loss. Selected-window absence is not proof of no pressure or no event throughout an application. CSV/JSON contain every retained event; HTML displays first1000matching rows.

Engineering only: test_portable_views.py passed14 controls on the existing final-header CPU fixture. Receipt engineering_runs/dfc13738-b03b-487f-a635-41b6114df7e0/RESULT.json SHA1b1296c7f53d020f7f3d5a4cf40e0f057e63d3d01c671aa280a767dcd422717c. It exercised the independent synthetic CLI, exact ROOT rebound, all view outputs and sameCORE ordering, no-overwrite/symlink rejection, missing/wrong catalogue rejection and header/contract/decoder hash rejection. Positive application-wire execution awaits Main's actual accepted ON raw and independently bound catalogue. No new application was needed or run.
