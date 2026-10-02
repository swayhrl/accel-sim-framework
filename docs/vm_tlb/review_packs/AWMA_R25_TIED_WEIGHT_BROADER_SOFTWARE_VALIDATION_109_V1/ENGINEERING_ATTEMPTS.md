# Engineering attempts

The first wrapper attempt stopped before CUDA because the lock-held sentinel environment variable was missing. The first compact BF16 accumulation passed one-step but crossed the fixed trajectory tolerance on D0. A bounded FP32 compact accumulator then passed D0 but crossed the same tolerance on H0. The final frozen implementation remaps indices to the sorted compact domain and uses the native embedding-backward reducer; both points were rerun from scratch and passed. Earlier receipts remain in node164 raw only and were not used for formal timing.
