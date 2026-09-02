# Validation summary

| Check | Result | Evidence |
|---|---|---|
| Python syntax | PASS | `python3 -m py_compile util/llm_trace_capture/*.py` |
| Deterministic contiguous-layout planner | PASS | built-in self-test covers ordering, alignment, and duplicate-name rejection |
| Metadata schema validator | PASS | built-in self-test covers range coverage and unknown addresses |
| M4A-C authorization guard | PASS | execution without `M4A_C_AUTHORIZED=1` returns `BLOCKED` before arguments are acted on |
| Shell syntax / help | PASS | `bash -n` and `--help` |
| Local preflight | expected BLOCKED | no `nvidia-smi`, no built tracer/postprocessor, and only 231 GiB free; no capture attempted |
| Whitespace check | PASS | `git diff --check` |

The local preflight result proves `EXTERNAL_SM86_GPU_REQUIRED`; it is not a
failure of the pre-capture package.  Parser/simulator compatibility of the
future Llama SASS trace remains an M4A-C requirement because no such trace is
available locally.
