# Retry570 NVBit nvdisasm path-repair closeout

Status: `NVBIT_NVDISASM_PATH_CONTRACT_FIXED_RUNTIME_SMOKE_NOT_QUALIFIED`.

`nvdisasm` was installed at `/usr/local/cuda-12.4/bin/nvdisasm`; CUDA was not reinstalled or upgraded. The original child inherited a PATH without that directory. The fixed Lane G contract validates and records the absolute file, prefixes its parent directory into each injected child PATH, and supplies `NVDISASM=nvdisasm`; it is not an interactive-shell-only fix.

Gate A resolved/runs nvdisasm 12.4.127. Gate B passed NVBit 1.8 official `instr_count_bb` plus vectoradd, including its banner, instruction-count kernel row, and app terminal result. Gate C used the same exact contract and official tool in Lane G's PyTorch microreproducer. It passed the old PATH error (NVBit banner and first CUDA-work submission observed), but no first CUDA-kernel completion or official kernel marker appeared before 60 seconds.

The historical C raw label is retained but normalized only as a 60-second path-smoke timeout, not a 300-second long-watch diagnosis. Thus the startup configuration failure is closed, but the separate PyTorch/NVBit first-kernel gate remains blocked. Formal long-watch reapplication is not qualified. No model, C target, trace, scientific capture, or 6+6 rerun occurred. Raw files are outside Git and locally SHA-closed.
