# Diagnostic and superseded evidence

- oracle/vectorAdd_4M_r1: initial offline command carried an incorrect declared Framework source SHA. The diagnostic is preserved with EXCLUDED_DIAGNOSTIC.md and is not promoted, counted in coverage or consumed by a runtime binding.
- oracle/vectorAdd_4M_r2: valid earlier producer 901de6e2... output; superseded by the uniform five-workload development_r3 input set. It is not mixed into the final coverage table.
- development_r3: exactly five complete input certificates from d2ba33bd..., each independently rehashed and checked by the current launch verifier. None has a post-first-kernel host write. FWT's zero qualifying lines are retained as a valid negative result.
- The raw log index preserves historical diagnostic/build logs as well as selected validation; selection authority is INPUT_INDEX.json and RO_READY_MANIFEST.json, not mere presence in a log index.
- Saturation/illegal-operation directed fixtures intentionally exercise rejection; drain checks apply to completed transactions and epoch-end refusal is tested separately. They are not reported as full workload or formal performance rows.
