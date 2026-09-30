# Final decision

EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT

The accepted real R101 Qwen input, real final hidden, exact checkpoint lm_head,
shifted labels, mean reduction, BF16 storage, and complete
loss/grad_hidden/grad_weight contract all qualified.

The fastest qualified no-full-logits arm is CCE exact/no-filter. A valid NSYS
timeline and memory identity bind a full FP32 classifier-gradient accumulator to an
explicit 0.751779 ms zero-initialization phase, 9.55%
of profiled GPU kernel time. This exceeds the 5% screen without counting mandatory
GEMM/softmax-gradient kernels or the mandatory portion of output commitment.

This establishes only a bounded local state/lifetime residual on one RTX4080 and one
real Qwen shape. It is not a training-step, second-model, multi-GPU, or hardware
speedup claim. No mechanism is proposed.
