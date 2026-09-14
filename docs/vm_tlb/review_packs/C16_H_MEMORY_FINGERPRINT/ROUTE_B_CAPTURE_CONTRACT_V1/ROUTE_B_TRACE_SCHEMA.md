# Route B trace schema

One Route B manifest binds exactly one preselected full-mangled CUDA function,
one model/runtime/scenario identity, a frozen NVBit static map SHA256, and a
disjoint frozen subset of that map's `memory_space=GLOBAL && has_mref=1` rows.
The formal union of all subset manifests must equal that map predicate; rows
with `LOCAL`, `SHARED`, or `UNKNOWN_SPACE` are rejected before capture and
cannot enter GPU-VA fingerprints.

The static-map row is the authority for `static_index`, instruction offset/PC,
opcode, `is_load`, `is_store`, `has_mref`, SASS, exact full/mangled function,
function address, and code-object SHA. `access_kind` is `READ`, `WRITE`, or
`ATOMIC` from the static opcode, with unknown patterns rejected rather than
guessed. Width must carry both the NVBit instruction-size semantics and the
per-event requested byte width; neither may be inferred from an address delta.

Every address-bearing event must serialize:

```text
run/deployment/scenario/phase/decode-step; kernel launch ordinal and exact
launch function; static index; instruction offset/PC; opcode; MREF ordinal;
memory-space; access kind; width; active mask; predicate mask (if serialized);
active-lane IDs in mask order; per-active-lane GPU VA; terminal linkage.
```

The parser must verify popcount(active mask) against serialized lane count,
never manufacture a predicate mask, and label the address domain
`GPU_VA_OBSERVED`. A manifest records raw SHA256/size, map SHA256, output
checksum, terminal `COMPLETE`, tool binary/source identity, and `SET_ONLY`.
An incomplete terminal, a map/function/code-object mismatch, a zero GLOBAL
row count, or an unrecognized memory space is an admission failure.

The currently mapped bridge functions demonstrate the required exhaustive
predicate: Prefill LargeIndex has indices `34:LDG.E`, `101:LDG.E.U16`, and
`130:STG.E.U16`; Decode SmallIndex has `17:LDG.E`, `85:LDG.E.U16`, and
`104:STG.E.U16`. Index 34 was forbidden as the historical **Route A selected
target**, but it is neither excluded nor special under Route B's predeclared
all-GLOBAL-MREF predicate when this function is eventually selected.

If an approved static subset exceeds the pre-capture budget, partition sorted
GLOBAL-MREF static indices deterministically into contiguous index groups A/B/C
using the frozen budget estimate. Partition membership cannot depend on address
or performance results; group-map hashes and a union/no-overlap proof are
required before launch. The union is the only whole-kernel statement.
