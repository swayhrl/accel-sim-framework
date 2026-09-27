# Literature closure

- Linear Layouts v5 (`https://arxiv.org/html/2505.23819v5`) explicitly covers minimal layout conversion, register permutation, warp shuffles, optimal shared swizzling, and real benchmarks. These are baseline capabilities, not R82 contributions.
- FIBER (`https://arxiv.org/abs/2608.19628`) proposes a shared-register view with thread/register decoupling, dynamic parallelism scaling, dataflow scheduling, and operand delivery. R82 did not reconstruct or narrow-claim that architecture.
- Tensor Seeks Layout (`https://arxiv.org/abs/2608.21555`) formalizes global layout selection and conversion cost. R82's one local `keep_dims` intervention is not a global solver.

Final novelty state: `NO_ARCHITECTURE_NOVELTY_CLAIM`; no further primary-text novelty closure is required for this stopped software result.
