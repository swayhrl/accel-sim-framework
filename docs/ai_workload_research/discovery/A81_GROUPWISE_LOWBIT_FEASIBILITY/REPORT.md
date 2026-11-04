# Round A81 | Group-wise Low-Bit Computation Idea Feasibility V1

Executor: Codex, A81-LBIT, node 109. Final scientific state: **NO_REAL_TENSOR_AUTHORITY / STOP**.
**Do not enter a GPU stage.** G0 failed the real-input-pair authority gate; G1 was not admitted. This is an availability result, not a numerical failure, measured hardware no-go, or rejection of all group-wise low-bit opportunities.

## Scientific object and decisive evidence

Question: can repeated W4 values remove enough computation after scales, floating-point sums, indexing and state to justify a new unit?

Selected frozen natural family: Qwen/Qwen2.5-7B-Instruct-AWQ revision b25037543e9394b818fdfca67ab2a00ecc7dd641, AutoAWQ B0, layer-0 up_proj; gate_proj is the potential independent projection check. Actual accepted dimensions are M=1, K=3584, N=18944, K-group size 128 (28 groups/output), from frozen contract, canonical tensor identities and geometry. The available dump covers D0-D3 M1. Historical grouped M32/M64 experiments use synthetic inputs and are excluded. No larger-M accepted natural configuration was recovered; stacking decode steps would invent one.

The strongest immediate counterevidence is concrete: /data/c16/models/.incoming/qwen2p5_7b_instruct_awq is readable and empty. The exact revision directory, config, index and both safetensors shards are absent. Historical shard hashes (3,996,422,976 and 1,574,406,784 bytes) survive in the frozen environment receipt, but cannot provide weight values. This finding is scoped to authority-linked paths and their parent, not a claim of global nonexistence. No global cache search, alternate model, node164 scan, download or old-Goal recovery followed the STOP.

Positive evidence: the original 17,026,074-byte B0 archive is readable; SHA256 0e1b0975c0781dd9c5d248051379b950a0a8dbc45c872345212db80d42cd4a97 matches the FINAL frozen RAW_INDEX. A restricted standard-library metadata parser allowlists tensor descriptors, checks CPU/little-endian/contiguous FP16 storage and reads original bytes without torch. Eight layer-0 up/gate input digests match authenticated B0 occurrences (four per projection). No activation values or input text are committed.

The user-prespecified missing-W4 STOP applies. G0 quantized-code frequencies, distributions, U values and measured repetition are NA. G1 CPU A/B references, errors and Numeric PASS are NOT_ADMITTED, not successful empty tests. No CPU mathematical-reference program is submitted.

## Numeric and cost boundary

This is **W4A16**, not W4A4: unsigned packed AWQ codes, reverse nibble order [0,4,1,5,2,6,3,7], affine zero points, FP16 scales per K128/output and FP16 activations. Historical weight/zero/scale hashes exist but bytes cannot be revalidated. Frozen conversion identity includes half2 rounding and operand layout. The accepted kernel uses FP16 dequant operands, FP32 MMA accumulation, split8 FP16 scratch and an 8-to-1 reduction. Bias, if present, must be preserved; exact config could not be recovered.

A conditional bucket identity sums activations sharing weight code c, multiplies each sum by source-exact D_AWQ(c,z,s), and combines. D_AWQ must include the original dequant rounding; moving an ideal real scale outside does not preserve FP16 coefficients automatically. Scale-group intersections with original accumulation partitions, scratch casts and reduction order matter. Real-arithmetic equivalence is not floating-point bitwise equivalence.

LOGICAL_REPETITION, REMOVABLE_ARITHMETIC and NET_HARDWARE_COST remain distinct. For a full group of 128 with U<=16 codes, ideal coefficient products fall from 128 to U. First-insertion assignment leaves 128-U bucket additions and U-1 combine additions: still 127 FP additions. A simple bank needs up to 16 FP32 accumulators (64 bytes) per live row/group/output, 128 decode/select operations, bucket RMW, initialization/reset and up to U coefficient setup operations. Setup reuse across M must be accounted separately; the accepted dequant kernel already amortizes coefficients across its M tile. Group scale application cannot be amortized across incompatible scales.

W4A16 buckets retain FP sums, not integer counts. At length 128 a W4A4 operand-pair counter could need 8 bits to cover 0..128; a naive 256-counter bank is 256 bytes before decode (the author's R29 is mechanism-specific). That different contract cannot replace this activation path.

Register banks, selectors, ports, coefficient conversion, spills, index traffic and split scratch may cancel multiplication savings. No measured code distribution or candidate net-cost prediction exists. Formula counts are **ALGORITHMIC_COST_ESTIMATE**, never PPA, chip energy or speedup evidence.

Frozen cross-runtime tolerance atol=0.05, rtol=0.01 is recorded unchanged. Its applicability to a future CPU comparison must be justified for matching outputs; it does not turn this skipped reference into Numeric PASS. No errors were measured.

## Required frozen counterexamples

- **E-C04:** shared-residency retained local up-proj effects without stable material whole-decode benefit. Traffic is not critical-path time.
- **E-C05:** M1 simulated window slowed 0.2054%, target up slowed 0.2777%; M1F target-zero window ceiling 0.9557%, selector coverage 1.7917%. Historical scope only.
- **E-C06:** grouped CTA mapping absorbed most Split-K locality opportunity; M64 split1 beat split8 about 4.93%. These are not natural value statistics.
- **E-C09:** vLLM merged gate/up and AWQ/Marlin already exist. Historical canonical identity passed; 14/336 cross-runtime output occurrences failed frozen tolerance. Neither performance ranking nor exact numerical compatibility follows.
- **E-C10:** M1 tile fill 6.25% is not a 93.75% time saving. Marlin overlaps dequant/MMA and reshuffles weight/scales; QUICK covers dequant/layout interleaving; FLUTE covers LUT dequant and specialized dataflow. Their exact-format limits remain binding. No concrete compatible residual is demonstrated.
- **E-C16:** 75% conversion duplication is address/representation reuse, not weight-value frequency. Invalid-output isolated oracle slowed (0.8262x). Predecode 1.0929x changed kernel/representation, grew footprint 3.8496x and excluded materialization. Neither is an implementable hardware bound.

E-C16's natural SHARE3 subset f=0.0173997666 gives zero-target ceiling 1.0177078796x only for that subset. Grouped synthetic shapes differ from this real natural family. A complete-application denominator for an A81 bucket mechanism is not established; no numerical transfer is made. Strong software may absorb an eventual candidate, but missing real weights prevent classifying this untested candidate SOFTWARE_ABSORBED.

## Focused primary-source check

[Cambricon-C author overview](https://yongwei.site/zh/cambricon-c/) (MICRO 2024; DOI 10.1109/MICRO61859.2024.00047) explains 256 pairs of two four-bit operands and R29 counting. This needs two small discrete alphabets. Arbitrary FP16 activations require weighted FP sums. The linked full PDF timed out, so detailed author benchmark quantization/group-scale settings remain SOURCE_INCOMPLETE. No author energy claim is transferred.

[LUT Tensor Core, fixed arXiv v3](https://arxiv.org/html/2408.06003v3) studies mixed-precision activation-tile precompute, cross-column table reuse, affine reinterpretation and bit-serial weights. Table construction, mux/broadcast state and scale correction have costs. Its INT8 table quantization adds a numeric contract and cannot silently replace FP16 here. The [author artifact](https://github.com/Hamerlate/lut_tensor_core) advertises RTL/synthesis and A100 simulation; neither was run.

Current [Marlin](https://github.com/IST-DASLab/marlin) and [FLUTE](https://github.com/HanGuo97/flute) author READMEs were checked read-only beside exact frozen C16 evidence. Generic LUT/dequant feature existence does not prove exact AWQ compatibility or a candidate-specific hardware opportunity.

## Decision and handoff

**No GPU promotion.** The single final state is NO_REAL_TENSOR_AUTHORITY. Full Cambricon-C paper verification and a candidate application denominator also remain incomplete; neither replaces the primary STOP.

A future independent source review would first need an already-existing legally readable copy of this exact revision, verified canonical tensors, matching accepted activations, exact rounding schedule and an applicable frozen tolerance. This is a proposal only, not authorization to download weights, change precision/group size, resume old experiments, access 164, launch G2 or design RTL.

SOURCE_AND_NUMERIC_CONTRACT.json records identities; EVIDENCE.json records fixed source blobs, historical extracts and raw readbacks; G0_COST_AND_REDUNDANCY.tsv separates NA from conditional formulas; G1_REFERENCE_RESULT.json records non-admission; RECEIPT.json records resource and publication boundaries.
