# Lane4 local Ideal rolling handoff r1

Exact rebasing target is official7b8e6ac7; no old source file was substituted.
Native A1/B1/WB carrying and physical clock implementation remain unchanged.
I_WB and joint I_WB_META producer fixtures pass and can enter Lane1 integration
and Lane5 independent qualification immediately. I_WM is the same mode/key as
I_WB_META. No full application was started here. New common runtime and matching
anchors belong to Lane1/Lane5; this dev binary is not a scientific release.

24 of25 native directed executions pass, including actual joint resource
pressure, read reference and host prefill, A1 and B1. One legacy allocator test
uses fake mem_fetch pointers, incompatible with the new native atomic-sector
inspection. It failed; the real-request fixture repair and an unsuccessful
manual-link attempt are preserved. The native integrated metadata test passes;
standalone correction is explicitly not yet accepted. No checks were disabled.

See ROLLING_HANDOFF.json for per-mode status and exact inputs. All modes default
OFF; I_READ_HIT remains exclusive of WB/META/U. These are optimistic diagnostics,
not realizable EP-L2 speedups or full data-memory ceilings. I_MEM_ALL_DATA is a
separate in-progress module; no source or evidence here claims it is qualified.
