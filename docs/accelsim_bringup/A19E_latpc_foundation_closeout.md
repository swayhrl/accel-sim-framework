# A19E LATPC foundation closeout guidance

## Goal
Close A19 round with review pack and final recommendation.

## Required script
scripts/accelsim/a19e_latpc_foundation_closeout.py

## Tasks
1. Collect all MD + CSV reports from A19A-D
2. Generate review pack:
   review_packs/A19_LATPC_VM_TLB_PTW_FOUNDATION_review_pack_<timestamp>.tar.gz
3. Write summary MD:
   - Round identity
   - Scope
   - Modules scanned
   - Hook mapping
   - Foundation assessment
   - Recommended next steps (A20 mechanism implementation)
   - Limitations
4. Validate final git status --short clean
5. Include tracked scripts/docs/source files only

## Output files
.local_reports/A19E_latpc_foundation_closeout_<timestamp>.md
.local_reports/A19E_latpc_readiness_checklist_<timestamp>.csv
.review_packs/A19_LATPC_VM_TLB_PTW_FOUNDATION_review_pack_<timestamp>.tar.gz
