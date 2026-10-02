# Rejected alternatives (not proposals)

The following are explicitly outside this Goal and do **not** become fallback branches if compiler-native mapping fails:

| Alternative | Why rejected here |
|---|---|
| More pre/post Python module hooks or a new Observer V3 variant | The pinned compiled call path bypasses post-trace child-module hooks; adding variants does not restore the missing authority. |
| More per-module CUDA Events or synchronization | Changes launch/scheduling behavior and still does not establish compiled semantic boundaries. |
| `torch.compiler.disable` on selected modules, deliberate graph breaks, or global disable-compile | Produces a different execution identity from accepted MODE_B; would require new strong-baseline and correctness qualification. |
| Custom marker op, NVTX op inside compiled graph, or editing Qwen forward/vLLM | Alters the compiled graph and kernel cache/dispatch; not an unmodified strong software path. |
| Reusing historical MODE_C Graph-OFF semantic fractions | MODE_C failed correctness and disabled torch.compile; its fractions are neither legal nor transferable to MODE_B. |
| Guessing module/layer from kernel-name substrings or fixed launch positions | Fused/generated kernels and repeated layers/steps make that mapping ambiguous without compiler provenance and same-run instance correlation. |

No rescue scan, new capture, custom instrumentation or mechanism experiment is authorized by this rejection list.
