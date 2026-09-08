# Final C10B blocker: C5 prefill provenance

There is no C9 architecture contradiction, source-provenance defect in the
implemented Core, standard-mode regression, F5 model gap, or resource
deferral remaining in C10B-0 through C10B-5.

The final blocker is precise and immutable:

1. `configs/vm_tlb/segment_maps/M4B_PREFILL_WEIGHT_SEGMENT_MAP.tsv` is marked
   `M4B_WEIGHT_SEGMENT_MAP_V1` and identity-mapped. It has a VA range only;
   it has no C10 V2 `pa_base_ppn`, provisioned context/ASID transaction,
   approved physical extent evidence, or lifecycle registration outcome.
2. There is no prefill `M4B_WEIGHT_SEGMENT_REGISTRATION_V2` artifact in the C
   scratch or Framework C configuration inputs. Decode1's V2 descriptor is
   for a different VA range and cannot be reused.
3. There is no immutable prefill trace-list copied into the C scratch to bind
   a C5 command and ROI hash. The retained prefill object map is telemetry
   evidence only.

C9 requires privileged driver/runtime verification of allocation, ASID,
read-only permission, pinning, mapping class, full-page boundaries and
physical contiguous extents. It explicitly forbids using `OBJECT_WEIGHT` or
an identity `ppn=vpn` shortcut as eligibility/mapping. Creating a prefill V2
descriptor by extrapolating the V1 range or object map would therefore invent
the exact architecture/provenance this Goal was required to preserve.

The resolution is to supply an immutable prefill trace-list and a driver-owned
C10 V2 registration artifact with verified non-identity physical extents. It
is intentionally outside this Goal; no C5 command may be run until then.
