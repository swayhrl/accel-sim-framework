# Open issue

The sole blocker is Hugging Face authorization on the remote host.

Required user action: make a token that has accepted the Llama 3.2 license and
can read `meta-llama/Llama-3.2-1B` revision
`4e20de362430cd3b72f300e6b0f18e50e7166e08` available to the remote pilot
session as `HF_TOKEN`. Keep it out of terminal transcripts, repository files,
and review packs.

After that action, rerun P5 first. Do not jump directly to P6. The existing
host/work root, CUDA toolkit, locked venv, NVBit build, and copied evidence may
be reused after their provenance/preflight checks are rerun.
