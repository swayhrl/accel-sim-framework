# Engineering fixes and excluded attempts

Attempt 0 used an invalid explicit Liger registry name and exited before model
forward or timing. The standard unoverridden path was restored; the inner dispatcher
reported only nvidia-triton as available on SM89.

Attempt 1 used Liger default BF16 classifier-gradient accumulation. Loss and
grad_hidden passed, but grad_weight exceeded the frozen 1e-2/1e-2 contract
(max abs 0.0625). Before formal timing, one upstream-supported correctness repair
selected accum_dtype=torch.float32. Storage/output remained BF16 and tolerances
did not change. Attempt 2 passed.

An unusable Ascend registration warning appeared during discovery; the recorded
available implementation remained exactly nvidia-triton. Excluded receipts are kept
under raw/EXCLUDED_PREPATH_ATTEMPT0 and raw/EXCLUDED_NUMERICAL_ATTEMPT1.
