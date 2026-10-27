# Input and coverage review — DTC L2 MLP exploration V1

This review describes the actually registered initial350-cell matrix. It is a coverage and provenance check, not a claim that all simulations have finished. Live completion and failure counts belong to the current result ledger and must be timestamped separately.

Read-only verification time: 2026-10-27T10:55:01.024218+00:00. **322 assertions passed;35 frozen ordinary representatives,350 initial cells,6 exact P0 references and344 fresh-start identities.**

## Frozen input contract

The35 identities exactly follow the user-approved representative freeze from commit `71584878be0c80375f9d25bcd80e171b7bf4478d`, SHA256 `a4157b56b48d8d8df048b9f64e62d54b091e80176d7a05169ef9c64b0c06da9d`. Every registered input has a prior full-body-qualified manifest, exact selected digest, normal-capture asset extent and matching declared trace entry. No fraction/trim trace is admitted; b+tree/hotspot derived models are excluded. Historical72-input breadth is not reopened.

Identity freezing certifies representative trace selection under the retained declared-trace contract. It does not newly certify capture-time executable identity, full native application scope or numerical correctness. No whole trace body was rehashed by this coverage review.

Suite counts: CUDA Samples: 9, Parboil: 7, PolyBench/GPU: 9, Rodinia: 10.

| Program | Suite | Input digest | Kernels | CTA | Active instructions | Old quad incomplete |
|---|---|---|---:|---:|---:|---|
| 2DCONV | PolyBench/GPU | `d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0` | 1 | 65536 | 620347492 | no |
| 3DCONV | PolyBench/GPU | `79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d` | 254 | 65024 | 823239400 | no |
| 3MM | PolyBench/GPU | `977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d` | 3 | 3072 | 1813512192 | no |
| ATAX | PolyBench/GPU | `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950` | 2 | 32 | 145666048 | no |
| bfs | Parboil | `1df9d5479504d9c7c5f5ef176e9604ce1b43421c7b6be440597259607d3971c0` | 11 | 76 | 121542388 | yes; retained |
| BICG | PolyBench/GPU | `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef` | 2 | 32 | 145666048 | no |
| BlackScholes | CUDA Samples | `b31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0` | 1 | 480 | 13830125 | no |
| convolutionSeparable | CUDA Samples | `4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449` | 2 | 27648 | 714547200 | no |
| cutcp | Parboil | `af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8` | 11 | 1331 | 8538061976 | yes; retained |
| dwt2d | Rodinia | `e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008` | 10 | 342 | 6312741 | no |
| fastWalshTransform | CUDA Samples | `f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3` | 16 | 7040 | 180944896 | no |
| gaussian | Rodinia | `16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3` | 126 | 1071 | 4526592 | no |
| GEMM | PolyBench/GPU | `fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318` | 1 | 1024 | 739246080 | no |
| GESUMMV | PolyBench/GPU | `769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4` | 1 | 16 | 190918656 | yes; retained |
| heartwall | Rodinia | `731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980` | 1 | 51 | 6900708 | no |
| histo | Parboil | `2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64` | 80 | 4260 | 2196264084 | yes; retained |
| histogram | CUDA Samples | `3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58` | 8 | 1130 | 17088656 | no |
| hybridsort | Rodinia | `09f94fcc7494a03b160b40b705cbc7ff5f41e88e8ee417d187e5c7fbcac82123` | 68 | 115324 | 6276086260 | yes; retained |
| lavamd | Rodinia | `ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8` | 1 | 1000 | 10396775488 | yes; retained |
| lud | Rodinia | `b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8` | 46 | 1376 | 22950272 | no |
| mergeSort | CUDA Samples | `dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48` | 13 | 209 | 10111750 | no |
| mri-q | Parboil | `dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4` | 4 | 390 | 1411757056 | no |
| MVT | PolyBench/GPU | `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079` | 2 | 32 | 145666048 | no |
| myocyte | Rodinia | `977e34578994c3d2d1cbd1a8ecf13e09efc43b03bcb8615a141cf2a24c9d5992` | 5993 | 11986 | 42921588 | yes; retained |
| particlefilter_float | Rodinia | `b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4` | 36 | 72 | 71467509 | no |
| particlefilter_naive | Rodinia | `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e` | 9 | 72 | 35981229 | no |
| sad | Parboil | `db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9` | 3 | 1782 | 157583646 | no |
| scalarProd | CUDA Samples | `2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954` | 1 | 128 | 730610912 | yes; retained |
| scan | CUDA Samples | `6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39` | 33 | 166608 | 1963460720 | yes; retained |
| sgemm | Parboil | `ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453` | 1 | 528 | 1658916864 | no |
| srad_v1 | Rodinia | `0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4` | 502 | 181000 | 10136693400 | no |
| stencil | Parboil | `c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266` | 100 | 6400 | 2193446000 | yes; retained |
| SYRK | PolyBench/GPU | `b51811aca9dc70cfe109fad8de73d5305647bc16d70b9289c1c918f4d3ab5d39` | 1 | 4096 | 5626658816 | yes; retained |
| transpose | CUDA Samples | `65151d2c661f88f3b463dba9a3ce49d98848affabe19a36ccf23295f3b1e8fdc` | 24 | 24576 | 208428288 | no |
| vectorAdd | CUDA Samples | `e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799` | 1 | 23438 | 84000768 | yes; retained |

## Initial configuration coverage

Each input has CH-P0 plus DH-P0/E384/E768/M8/M16/Q64/Q128/F128/F256:10cells per input,350total. E changes L2 MSHR entries192→384/768; M changes maximum merge4→8/16; Q changes L2 miss queue32→64/128; F changes FR-FCFS window64→128/256. Each non-P0 profile changes exactly one authorized factor. F also changes partition-credit capacity and is not an isolated queue-only intervention.

DRAM stays850MHz and total L2 capacity stays10MiB; cache geometry/mapping and DTC architecture remain fixed. Effective configuration and resource-cost evidence are provided by the parameter contract and frozen per-cell specs. Subsequent authorized combinations/extension profiles append new independently identified cells;350is the initial matrix, not a total execution cap.

## Six P0 references

ATAX, BICG and MVT reuse their accepted downstream18 CH/DH P0 results. This audit independently compared exact effective option dictionaries, expected instruction/CTA/kernel populations, input binding SHA, Core/Framework/binary identities, source UUID and cycles. All match; each reuse has zero new model starts. PQ/PS results are not baseline references.

| Program | Design | Original source cohort | Original UUID | Cycles |
|---|---|---|---|---:|
| ATAX | CH | `E2-DTCHASH18-eededb785179fc04-CH-P0-V1` | `681b81cd-4add-4802-a5f0-1994b9156847` | 28428842 |
| ATAX | DH | `E2-DTCHASH18-eededb785179fc04-DH-P0-V1` | `37325f35-2eb7-4a2b-bba9-5dc5d00e497f` | 31880220 |
| BICG | CH | `E2-DTCHASH18-ae34174fbbdf83b2-CH-P0-V1` | `f93c0c73-fc16-496b-9021-87ba236f60c2` | 26298698 |
| BICG | DH | `E2-DTCHASH18-ae34174fbbdf83b2-DH-P0-V1` | `fbb45ea4-716d-46f5-abfb-2842f03a8e99` | 28685812 |
| MVT | CH | `E2-DTCHASH18-f437190767aaed49-CH-P0-V1` | `bde2fff3-0d42-4920-a97c-1ed7a5be1df1` | 26581175 |
| MVT | DH | `E2-DTCHASH18-f437190767aaed49-DH-P0-V1` | `93cd6c4f-02cf-4e47-9a73-cba755167f47` | 34687540 |

## Twelve historically incomplete quads are retained

bfs, cutcp, GESUMMV, histo, hybridsort, lavamd, myocyte, scalarProd, scan, stencil, SYRK, vectorAdd. All12receive the same10-cell initial coverage as the other23. Old failures, HOLD/pending states, repair-only cycles, resource-policy stops and receipt gaps remain historical evidence; they are not replaced by new accepted performance. New runs use the designated repaired Core/Framework and require new independent strict natural-completion acceptance.

## Cutcp new namespace admission

Cutcp binding: `/root/data/dtc_l2_mlp_exploration_20261027_v1/control/input_bindings/af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8.json`, SHA256 `ed7261ff852e6e9a35f96a2c85fea3876736138022fa1288e520139d060ccca1`. Prior qualified input V2 SHA256 is `e13cb2783a8897dd5c5be1804570068673549e0fbc54e82e990d7382cd22f848`:11kernels,1331CTA,8,538,061,976active instructions. The old Goal never admitted or launched its four cutcp cells. The new namespace preserves that history and consumes the existing explicit generic-ST source-format adjudication. `CUTCP_SOURCE_COMPATIBILITY.json` proves the old/new generic LD/ST resolver block and Volta opcode map are byte-identical; no input semantics/model change was introduced. The new Goal uses its own qualified binding; it does not rewrite old admission.

## Seven unresolved programs

The42ordinary-program target remains35frozen+7unresolved. None of these seven has been promoted or substituted in this phase. They do not block the35qualified identities.

| Program | Retained reason |
|---|---|
| backprop | Two different source versions (2.0-ft4096 and3.1 65536) each have a standard command. No approved reference precedence or demonstrated source/data equivalence establishes one version for the42-set. Two4096 captures also differ; do not merge or pick by their outcomes. |
| cfd | All three traces contain only three initialize kernels, one step-factor and one flux kernel, with no time_step. Source3.1 euler3d has3initialization+2000*(1step+3flux+3time_step) launches. Exact capture-binary modification/ROI contract absent. Thus no input is verified full-application capture. Candidate193K trace actually has padded193536 cells (grid1008*192), not an exact nel identity; raw mesh SHA/nel missing. Historical E1 reference097K also cannot bypass this scope gap. Retain previous193K nomination only as rejected/unresolved provenance, no silent swap to097K. |
| kmeans | 2.0-ft400 versus3.1 28k_4x_features/kdd_cup/819200 mix implementation and feature/input semantics. Dataset dimensions/content and a single intended standard configuration are not jointly bound. No one-dimensional median or arbitrary newest-version choice. |
| nn | 2.0-ft command selects3 neighbors;3.1 uses-r5. Source-version and algorithm-parameter differences matter. No approved42-set version/k precedence; two2.0-ft captures not proven equivalent. |
| nw | 2.0-ft128x128 and3.1 2048x2048 both standard configurations, but no approved reference precedence across implementations; two128 captures differ. Do not use result size or pass status to decide. |
| pathfinder | 2.0-ft1000/20/5 versus3.1 100000/100/20 changes implementation, rows/columns and pyramid height. No fixed cross-version input policy;1000/20/5 captures unproven equivalent. |
| streamcluster | 3.1 parameters3/6/16 and10/20/256 change kmin/kmax and point dimension simultaneously. Sample count alone is not a comparable scalar size. No uniquely approved reference among these tuples. |

## Evidence locations

- Runtime root: `/root/data/dtc_l2_mlp_exploration_20261027_v1`; immutable initial `control/SCOPE.json` SHA256 `5f079aed36eca8dd62906bdfaa68006d3b3f27964c506a03361f2fab0908d1d2`.
- `control/MATRIX_CURRENT.json` is appendable matrix state; use timestamp and SHA when quoting it.
- `control/WORKLOAD_INTAKE.json`, `control/UNRESOLVED7.json`, `control/input_bindings/<full-digest>.json`, and each `control/*_SPEC.json` bind exact identities.
- `control/ACTUAL_CANARY_QUALIFICATION.json` confirms four actual native/strict/archive/restore canaries passed before broad admission.
- This section’s machine-readable join is `ACTUAL_INPUT_COVERAGE_REVIEW.json`; every input has full digest, binding path/SHA, expected population, and prior completeness state.
- Source intake support: `WORKLOAD_INTAKE.json`, `CPU_METADATA_QUALIFICATION.json`, `COMPATIBILITY_NOTES.json`, `CUTCP_SOURCE_COMPATIBILITY.json`, `DOWNSTREAM18_STRICT_VERIFICATION.json` in Agent C assets.
- Result ledger states must preserve failed, running, pending and negative-performance points. GM uses a common valid set, never per-program best-profile selection.
- Englishv0.23 remains the last user-confirmed paper master; no manuscript change is part of this review.
