# Minimal linear texture address observer prototype

Status: the finite actual GPU address-observation experiment passes for the exact controlled micro. It is not a standard ADA9/full v8 trace, simulator consumer release, scientific result or performance qualification. SourceKEEP applies to every version and failed attempt. Frozen55/c8/v8 and the completed CUDA/PolyBench phase5 source branch were not modified.

## Exact tested boundary

The supported source is linear_tex_u32_indirect_v2.cu. It creates one cudaResourceTypeLinear allocation containing 128 unsigned32 single-component elements (512 bytes), with point/element-type/non-normalized descriptor settings, one texture object, one CUDA context/default stream and one kernel launch of one block with 37 threads. Indices are signed int32 and all 37 are verified within [0,127]. API texture handles must fit unsigned32 and the actually used GPR32 value must equal the entire API handle. Handles with nonzero high32 are rejected rather than inventing an unobserved high register.

The actual sm89 instruction is `TLD.SCR.B.LZ RZ, R9, R5, R2, 1D, 0x1`. Coordinate R5, handle R2 and the later STG value R9 are actual dynamic observations. NVBit reports TEXTURE and width4 but **zero native MREF operands**. The proven address is resolved from the actual driver resource CUdeviceptr and signed dynamic index: base + index*4. This value has the explicit origin API_RESOURCE_LINEAR_SIGNED_INDEX_RESOLUTION_NOT_NVBIT_NATIVE_MREF. Neither opaque texture handle1 nor a CUDAarray handle is treated as a GPU virtual address.

The original direct-parameter micro compiles to TLD.SCR.LZ with an implicit selector. It has no dynamic handle operand and is actually rejected by the prototype before application kernel completion. No ABI meaning is guessed for its selector0x58. Arrays, pitched2D, filtering/interpolation, vector components, surfaces, cubemaps, unknown layouts and other instruction shapes stay HOLD.

## Strongest frozen evidence

- producer_v2_full_descriptor/producer.so SHA256 8307019236b9e2ddab086e2186045ce7da4b2b5f41197fe75078892fca3343db. Earlier a313 producer_v1 evidence is retained; only host full-descriptor serialization was added. GPU inject.cu and common.h bytes are identical across the two versions.
- control/CONTRACT_LINEAR_U32_FULL_DESCRIPTOR_V2.json SHA256 dc37fd51a834342d9447ca26a5c95c20dc09bfc0b32039647a528381c73a372f.
- control/qualify_linear_texture_proto_v3_full_descriptor.py SHA256 538f71e60369e1320d22dfaf1f35fecce273b99bf2e1cdee745fe32492dc0cc6.
- Application ELF SHA256 9d5ccda8de79be73a9b5278ebf5c3c4176543e530f7301c45ca4344030d33937; actual-loaded5160-byte cubin SHA256 83f26c01fbf4ccfd580e6f1aab5f036cf0b988378ecd739a548aefea4eafb255, ELF sm89.
- evidence/FINAL_QUALIFICATION_V3.json and evidence/positive_qualification_v3_full_descriptor/QUALIFICATION.json are the final CPU qualifications and per-lane resolved sidecar.
- Actual positive raw attempt: native_attempts/linear_full_descriptor_v2/linear_tex_u32_indirect_producer_v1_full_descriptor_v2/attempt001.

The positive contains raw144-byte driver resource and raw104-byte driver texture descriptors, all named fields, create/destroy lifetime, actual three HtoD input byte capsules, queried application resource/pointer attributes and actual loaded code. All 37 source words and indices equal the unloaded native run; every GPU output word and next-STG source register agrees with the CPU reference. There are 24 original static SASS instructions including padding and 26 dynamic warp records: 13 executed original instructions per warp, two physical warps with masks0xffffffff and0x1f. The actual SCR-without-B GPU negative is rejected; fifteen CPU negatives reject bad signed indices, handles/high bits, masks, missing/duplicate records, arrays/components, fake nativeMREF, input/output corruption and descriptor corruption. Negative attempts never create qualification objects.

## Raw schema and limitations

DYNAMIC_WARPS.jsonl stores ordinal, original byte-PC, physical warp, active/guard masks, per-explicit-register-slot values[slot][32], full P/UP bit vectors and ordinary nativeMREF fields. REG_SLOTS pc= lines in PRODUCER_API_AND_STATIC.log define each slot. INSTR pc= retains original SASS and NVBit operand types/widths. Sidecar keys are context/launch/CTA/warp/dynamic ordinal/original PC/lane; the TLD sidecar preserves index, handle, backing base, width, resolved VA, origin and original SASS.

This observer captures **pre-instruction** explicit NVBit register operands plus explicit MREF base registers. It does not capture constant-bank data/dynamic offsets or complete PLR implicit dependencies. UR4/UR5 at ULDC are pre-load snapshots, not the loaded result; implicit UR dependencies of later LDG are not silently claimed captured. Therefore direct conversion to a complete ADA9/full v8 stream is HOLD. The next viable route is a separate v8 fullproducer derivative that preserves its existing complete typed/constant contract and adds a separately tagged dynamic texture index/handle plus actual API resource table. The consumer must issue an actual texture memory request while keeping original TLD identity; replacing TLD with LDG or accepting the existing no-memory SPECIAL2 decode is not a qualification.

## Static scope and actual-code boundaries

The finite census covers official SDK4.2.9 82 plus modern v11.8 205 source programs: 287 total, 87 source API/intrinsic/descriptor hits. It inspects 261 distinct fixed ELF contents; 250 cuobjdump successes and 11 tool rejections/truncations are retained separately. Fifty-four contents contain TEX/TLD/SULD/SUST; aggregate static instruction-line counts are1357/138/23/40. These are static embedded-code counts, not runtime workloads, requests or eligibility. No standing scanner remains.

The actual loaded cubin is the executed-module authority. cuobjdump --extract-elf all reports two same-basename embedded entries; only the final extracted file is retained and equal to the actual-loaded SHA. The earlier same-name bytes were not independently retained, so unique/all embedded-owner proof is HOLD. This does not erase the actual loaded module. Matching CUDA12.8 nvdisasm provides successful PLR for this12.8 cubin. Private13 offline PLR rejects Std/Old format conversion and is not used here. Earlier NVBit startup failures with the attempted13 environment are retained; successful runtime uses12.8 and an explicit CUDA bin PATH. No isolated cause beyond these actual outcomes is claimed.

NVIDIA's official CUDA12.8.1 Texture Object Management documentation defines the linear descriptor as a real device pointer plus format/size, states texture objects are opaque, and states linear-resource filter/address modes are ignored: https://docs.nvidia.com/cuda/archive/12.8.1/cuda-runtime-api/group__CUDART__TEXTURE__OBJECT.html . The prototype's formula is a scoped inference from that linear resource contract joined to actual descriptors, dynamic indices and full value evidence. It is not a measurement of array tiling, cache transactions or hardware physical addresses.

All GPU calls used the cooperative lock, fixed RTX4080 UUID, idle/resident identity/VRAM guards and bounded own process groups. All GPU work is terminal. No simulation, foreign service termination, source cleanup or performance experiment was performed. verify_portable_cold_namespace_v1.py can re-run the frozen CPU checker after restore using file-lookup-only namespace relocation; raw receipts, pointer values, paths inside the recorded contract and code bytes remain unchanged.
