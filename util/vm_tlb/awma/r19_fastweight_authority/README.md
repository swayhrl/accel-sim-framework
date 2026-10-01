# R19 fast-weight authority runner

`prepare_input.py` deterministically rebuilds the real Banking77 prompt used by
the R19 Lane G review pack. `fastweight_boundary.py` loads the frozen public
reproduction checkpoint, qualifies all trained TTT layers, and runs the paired
released/closed-form/update/consumer diagnostics.

CUDA execution must hold `/data/c16/locks/c16_gpu_campaign.lock`. See the review
pack `AWMA_R19_FASTWEIGHT_109_V1/REPRODUCE.md` for pinned sources and receipts.

`CONFIG_STRICT_COMPAT.patch` is a validation-decorator compatibility patch only;
it does not alter model tensors or fast-weight mathematics.
