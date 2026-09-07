# B2 — transactional V2 Segment registration

## Admission boundary

`weight_segment_map` treats a readable, schema-valid
`M4B_WEIGHT_SEGMENT_REGISTRATION_V2` file as a privileged driver registration
transaction. It first parses header and every descriptor into local staging
state. Only the terminal success path swaps `staged_ranges` into the live
image, records ASID/epoch, marks `ACCEPTED_V2`, and permits a later lifecycle
install.

The following semantic outcomes return an empty disabled image and a
machine-readable `segment_registration_status`; the controller's
`begin_segment_install()` rejects it and requests use conventional paging:

| Status | Admission condition |
| --- | --- |
| `REJECTED_EMPTY` | no usable extent |
| `REJECTED_CAPACITY` | more than N=8 extents |
| `REJECTED_OVERLAP` | ordered extent overlaps its predecessor |
| `REJECTED_UNSORTED` | duplicate or descending VA-base extent |
| `REJECTED_ASID_EPOCH` | header/descriptor ASID or epoch mismatch, zero epoch, duplicate/invalid provisioning field |
| `REJECTED_RIGHTS` | descriptor is not read-only |
| `REJECTED_MAPPING_CLASS` | mapping class is not v1 class 0 |
| `REJECTED_EXTENT` | partial/non-numeric descriptor field, reversed extent, or 33-bit VPN/PPN overflow |

The status is emitted as `vm_weight_segment_registration_status`; the schema
field distinguishes `NONE_OR_SEMANTICALLY_REJECTED` from an accepted V2 or
historical V1 artifact. No prefix of a rejected submission is copied into a
local replica. The request-admission predicate also requires
`segment_active()`, so a rejection or partial install bypasses even the
Segment latency path and proceeds through conventional L1/L2/PTW paging.

## Deliberate error distinction

Unreadable artifact, unsupported schema, malformed required provenance, or
non-numeric mandatory field remains a project configuration assertion. That
is infrastructure/schema corruption, not an architecturally valid driver
transaction being refused. The distinction avoids silently hiding a broken
experiment while ensuring expected capacity/rights/lifecycle policy failures
fall back without an abort.

## Physical mapping preservation

An accepted extent is `(ASID, epoch, VA_base_vpn, VA_limit_vpn, PA_base_ppn,
read_only, mapping_class)`. Segment hit PA uses
`PA_base_ppn + (VPN - VA_base_vpn)`, not `PPN=VPN`. Conventional PTE
completion only uses that registered PPN while the Segment lifecycle is
active; otherwise it follows the normal page-table mapping.

The added unrun C++ directed source test covers nine extents, overlap,
unsorted ordering, rights, mapping class, ASID mismatch, zero epoch, invalid
extent and the zero-live-image invariant. The Python static validator repeats
these transactional state-model cases without invoking a compiler.
