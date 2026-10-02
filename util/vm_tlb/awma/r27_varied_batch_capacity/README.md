# R27 varied-batch capacity tooling

- `gate_a_readback.py` independently checks the R26 node164 archive, 207-item
  manifest, CPU common checkpoint, endpoint receipts/logs, bindings, and frozen
  source without CUDA.
- `finalize_r27_negative.py` constructs the Gate-B input-availability STOP pack.
- `publish_r27.py` publishes and hash-closes the compact R27 audit evidence.

This execution stopped before component migration, tokenization, CUDA/JIT, and
capacity observation because the sole pinned WikiText-2 train parquet could not
be obtained byte-for-byte. The scripts do not provide a fallback corpus, split,
model, tokenizer, or synthetic proxy.

The two failed Gate-A audit attempts preserved in raw evidence were parser
constant transcription errors only; the final audit reads exact 64-character
