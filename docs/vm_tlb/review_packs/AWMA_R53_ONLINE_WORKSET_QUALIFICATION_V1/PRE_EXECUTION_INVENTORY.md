# Pre-execution inventory

- Node109 RTX4080, driver 580.178.04, 16,376 MiB; GPU initially idle.
- `/data/c16` had about 291 GiB free; host had about 60 GiB available.
- Dedicated R53 environment created under the stage root; accepted C16 environment, system CUDA and driver were not modified.
- Direct Hugging Face endpoint timed out; exact-revision download used `hf-mirror.com`, whose response bound `X-Repo-Commit` to the required revision.
- B1 short canary passed. B4 full 512-token canary passed with peak allocated/reserved about 3.26/3.48 GB, so B2 fallback was not activated.
- HumanEval generated code was never executed.
