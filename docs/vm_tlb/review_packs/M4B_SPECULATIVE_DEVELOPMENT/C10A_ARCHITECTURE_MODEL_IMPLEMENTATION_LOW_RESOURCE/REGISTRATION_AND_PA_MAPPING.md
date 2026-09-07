# Registration and physical-address mapping

V2 artifact header: `M4B_WEIGHT_SEGMENT_REGISTRATION_V2`.

Its metadata binds ROI/source/archive/object-map provenance, then states one
`provisioned_asid`, one nonzero 16-bit `epoch`, and up to eight sorted,
non-overlapping descriptors:

```
descriptor <asid> <epoch> <va_base_vpn> <va_limit_vpn>
           <pa_base_ppn> <read_only=1> <mapping_class=0>
```

For a 64KiB request wholly in descriptor extent `d`, C10-A returns:

```
PPN = d.pa_base_ppn + (VPN - d.va_base_vpn)
PA  = PPN * 64KiB + page_offset(VA)
```

This removes the former formal shortcut `PPN=VPN`. The direct focused case
uses VA VPN 16 -> PA PPN 256 and a second non-contiguous extent VPN 32 -> PPN
512. A request conservatively falls back for wrong ASID, invalid page class,
non-read access, range/boundary crossing, or no descriptor.

The object range map is consulted only to attach observational telemetry. A V2
descriptor hit does not require `OBJECT_WEIGHT`; a telemetry label does not
create a descriptor hit.

For ordinary PTW completion on a registered V2 page, `registered_ppn()`
supplies the same PPN before the generic page-table backend. Candidate and
conventional paths therefore cannot silently compare two different mappings.

Current limitation: V2 parse failures still use assert-style configuration
rejection rather than a live driver transaction that returns an explicit
all-replica rejection and continues with conventional paging. This is a named
C10-B correctness/lifecycle blocker, not an accepted registration outcome.
