# Final scientific decision — R17 resident graph search / node109

**`R17_RECALL_GATE_NOT_QUALIFIED`**. This is the preregistered scientific STOP boundary.

The official `glove-100-angular.hdf5` (1,183,514×100 FP32 base, 10,000×100 FP32 queries, 10,000×100 official ground truth) was downloaded from ANN Benchmarks, hash-closed, and converted with the exact stable cuVS benchmark helper `--normalize`. The helper's `glove-100-inner` output contains L2-unit vectors; `sqeuclidean` on these vectors has the same ordering as angular/cosine distance. The converter output matched original normalized values exactly for audited rows; maximum base norm error was `2.3841858e-7`; independent exact cosine top-10 for discovery queries 0, 1 and 2 matched official GT. Discovery IDs 0..255 and sealed holdout IDs 256..511 were frozen before any search. No holdout query values or performance were used for selection.

One uncompressed CAGRA index was built on RTX4080/SM89 from the FP32 normalized base, using the stable Python runtime's actual default IVF-PQ build (`graph_degree=64`, `intermediate_graph_degree=128`, no compression/filter/update). Its graph is `(1,183,514,64)`, graph SHA256 `a68d4a2905fcab13a40872db73165fb4271a493f09b9fd61f5f1e9a401f073b8`; the serialized graph+dataset SHA256 is `6cddddb35f63d31b1308d1411d76aabcef910b11caea1778ca823f4fb63e7151`. Build time was 2.780 s, excluded from query timing. A one-sample NVML process-memory observation is not presented as an exact peak; admission/free-memory and CuPy pool observations are in `INDEX_RECEIPT.json`. Reload confirmed graph and vectors as device-resident views.

Fixed-config discovery recall@10 (official GT top-10, mean over 256 queries):

| Batch/mode, itopk64/width1 | Recall@10 |
|---|---:|
| Q1 AUTO→MULTI_CTA | 0.791016 |
| Q1 SINGLE_CTA | 0.807813 |
| Q32 AUTO→MULTI_CTA | 0.798828 |
| Q32 SINGLE_CTA | 0.807813 |
| Q256 AUTO→SINGLE_CTA | 0.807813 |
| Q256 MULTI_CTA | 0.798438 |

The six bounded Q1 MULTI_CTA grid points (`itopk={64,128,256}`, `search_width={1,2}`) reached at most **0.930078** (256/1); the 256/2 point reached 0.929688. Both are below the frozen 0.95 gate. Exact per-arm rows, source-proven AUTO aliases and the five-repeat discovery-screen samples are in the review pack; all 9,050 per-batch preliminary samples are in durable raw. Different modes/itopk may change work and quality, so their preliminary time differences are not a traversal-memory conclusion.

Because no eligible `Q1_STRONG` exists, formal timing, persistent control, Python-wrapper gate/C++ fallback, NSYS/NCU, and sealed holdout were **not entered**. This result does **not** say CAGRA is slow/fast, software sufficient, host dominated, distance dominated, or that a GPU graph-traversal mechanism is needed. It only says this exact input/index/default-build and bounded search grid did not meet the preregistered quality contract. No broader search, second index, dataset, algorithm substitution, hardware design or 174 work was started.
