# N3 source-only decoder and capture recipe review

This is a static compatibility argument, not current replay admission. No
trace header, body, archive, payload hash, native generation or full simulator
is read or executed for this review. The unchanged R2 input-scan/simulation
10 GiB disk gate remains closed under the coordinator's published resource
observation. Existing A primary body proofs are reused without another scan.

Source target is Framework build
`18a68dcccd795f1b6cda75504e9450d00c9cee02`, whose relevant blobs are identical
to COV1 delivery `8f76a8a50ec5e56dd49f93224a64b253383b0420`:

|Consumer source|Git blob|Static finding|
|---|---|---|
|gpu-simulator/trace-parser/trace_parser.cc|316da183f732f2a18cd42931e69037362e4415bd|Header parser reads the actual binary/tracer version; instruction parser branches for pre-v3 records and v6 optional immediate/register values|
|gpu-simulator/trace-driven/trace_driven.cc|8a467abbbcf945c48c43b6030aaf08dc5b0f41fd|Actual binary version70 selects Volta_OpcodeMap; unsupported versions are rejected|
|gpu-simulator/ISA_Def/volta_opcode.h|Pinned same Framework Git object, not an inspected trace opcode list|VOLTA_BINART_VERSION is70; an ISA map existing does not prove every captured opcode form is accepted|

The source-backed capture is V100 SM70, not the unadmitted SM89 capture from
109. Its `NVBit-v1.8` metadata identifies the capture tool release; it does
not by itself establish the numeric Accel-Sim trace ABI header version or
all record grammar. Metadata from the existing M5 immutable store records
50 grouped members, an ordered kernel geometry manifest with374 CTAs each,
fixed input/reference identity and full checker success. Those inherited
records do not become a current full-input or parser test.

The exact wrapper source is gpgpu-workloads
`de9cf4293f418877aa9cdb6a2395338ca06674a6`, using Parboil dependency
`4e0fc54866546efa44fe93af57c9cef62f6c8eb9`. In
`suites/parboil-wrapper/spmv/jds_kernels.cu`, d_index selects x_vec entries,
d_perm chooses destination elements, and the JDS pointer/count tables supply
the access bounds. A valid source-level domain requires:

- Each visited JDS data/index offset is within the converted allocation.
- Every indirect x_vec index is within the fixed input vector.
- d_perm is an in-range injective permutation for active output rows.
- JDS depth/count tables satisfy the kernel's prefetch and final-element
  accesses, including rows with short/zero counts under converter rules.
- MatrixMarket symmetry, duplicate and row-order handling agree with the
  accepted native reference and JDS conversion.

Separate source cudaMalloc calls allocate the input arrays and output. The
wrapper memset/HtoD/symbol-copy sequence precedes a synchronization. Fifty
same-default-stream launches follow, with an explicit final synchronization,
DtoH result and synchronization before free. Source inputs are unchanged
across those launches. Destination writes repeat across invocations; all50
remain required. None of these source statements recovers compiled route,
captured initialization coverage, value propagation or input-domain validity.
SEM1's conditional source support remains conditional.

The exact existing producer recipe is `spmv -i bcsstk18.mtx,vector.bin -o
result.bin`, CUDA11.8 `-arch=sm_70 -O2 -cudart shared`, the frozen wrapper and
NVBit1.8 capture. Prefer the already captured immutable bundle; no producer,
GPU, node connection or re-capture is requested. Matrix/vector/reference
hashes and all50 boundaries remain fixed in `manifests/N3.json` and
`evidence/N3_LOCAL_CAPTURE_RESULT.json`.

After the unchanged resource gate and exact role admission, remaining
qualification should be one bounded, shared pass over this one fixed N3
input, plus the small fixed input conversion/reference checks if available.
That pass must establish actual ABI, whole-member hashes against the already
published immutable vector, all50 ordered kernels/CTAs/instructions, opcode
forms, complete terminal boundaries and typed accesses. It must preserve
unknown aliases/object ranges rather than infer values from address behavior.
There is no reason to repeat the eight primary A body audit or change N3
after timing results. If resources/assets remain unavailable, report this
input as qualified only at the inherited capture/source level.

Status: SOURCE_COMPATIBILITY_CANDIDATE_CURRENT_FORMAT_BODY_AND_INDEX_DOMAIN_UNQUALIFIED.

Additional exact source limits: `spmv_jds.h` declares5000-entry constant
arrays for jds_ptr_int and sh_zcnt_int. Their copied depth/nzcnt_len must fit
those capacities, and warp_id accesses must fit the initialized count range.
The kernel parameter d_nzcnt is not the lookup used by the source kernel;
the count access is sh_zcnt_int[warp_id]. The wrapper reads a dim-length
vector after COO-to-JDS conversion; qualifying a general rectangular matrix
requires the actual index range to fit that allocation rather than assuming
col_count=dim. N3 remains the fixed captured bcsstk18 input, not an arbitrary
matrix promise. Volta map header blob is
fee14f0c3d9da12c4058e53d93c2102ee8468d00 at the same frozen build.
