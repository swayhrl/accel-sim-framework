# Updated holdout plan — zero Stage A holdout execution

MP04, MP07, and MP08 remain prospective holdouts. Stage A must not initialize them, produce their outputs, inspect their timing, or run profiling/tracing on them. Existing asset/input identity receipts do not constitute model output. The original design/preflight records are immutable history; this revision narrows execution scope without relabeling a viewed point as holdout.

| Point | Current status | Future use |
|---|---|---|
| MP04 Qwen BF16 B16 | `HOLDOUT_NOT_EXECUTED` | DQ2 batch-ladder validation only after frozen discovery analysis. |
| MP07 Granite MoE | `DEFERRED_MOE_HOLDOUT`, `NO_ASSET_REQUIRED_NOW` | DQ4b is not execution-ready; no Granite asset preparation or Stage A/B automatic MoE transfer test. |
| MP08 Qwen BF16 long context | `HOLDOUT_NOT_EXECUTED` | DQ1/DQ3/DQ4a validation after discovery freeze; translation remains unknown/inactive. |

After Stage A analysis, 174 must first commit `DISCOVERY_FREEZE_RECEIPT.json` with at least the DQ, phenomenon, predicted sign, estimator, materiality threshold, STOP rule, exact holdout IDs, and the source/raw/script identities required by `HOLDOUT_NONEXECUTION_GOVERNANCE_V2.md` at asset closure commit `c3f625e46adb8d5c4082ded8b61858c710e1f4e9`. Only a separately reviewed Stage B runner may execute an authorized holdout after verifying the committed receipt SHA/tree and exact allowlist. No threshold, sign, estimator, or holdout substitution after looking at holdout output. Stage A requires no X.509 setup because it emits no holdout output; the old X.509 proposal remains historical rather than rewritten.
