# M4A merge-prep integration manifest

Scope: immutable main-server Route-E rank-0 formal archives only. Capture
executable SHA: `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`; model is
`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`.

| ROI | archive SHA256 | files | semantic COMPUTE / NCCL | coverage final SHA256 |
| --- | --- | ---: | ---: | --- |
| prefill | `f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181` | 724 | 692 / 32 | `6fd209619fae6e348afd109933fe90cf9828d2e65d461b5dc50ccc90d6f4ab5a` |
| decode1 | `5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad` | 772 | 740 / 32 | `dc56d89e0e3e6c1f1483fa560fdecf8d4183ac56c15b679911da094a2096c828` |

`ADDRESS_COVERAGE.md` supplies exact active-lane references, byte totals,
page coverage, VA bounds, and decoder evidence. Raw traces and full ordering
remain preserved; semantic NCCL observation is evidence only. NCCL policy is
explicitly deferred to M4B integration. Later documentation-only commits must
not be represented as capture executable SHAs.
