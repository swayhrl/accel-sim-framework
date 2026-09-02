# M4A-C0 rented-host pilot review pack

Final status: `PILOT_BLOCKED`.

The host, locked environment, NVBit generic chain, and real rank0-only
injection proof passed. The pilot stopped before P5 because the remote had no
usable Hugging Face credential for the frozen gated Llama revision. Therefore
there is no Llama workload output, no `DIAGNOSTIC_PILOT` decode1 trace, and no
formal prefill/decode evidence in this pack.

Persistent copy-back root: `/workspace/m4a-rented-host-pilot/` on the main
development server. Its selected source/destination SHA256 comparisons are
recorded in `COPYBACK_AND_PARSER.md`.
