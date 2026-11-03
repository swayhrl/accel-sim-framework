# Disk-before-claim: independent CPU review

PASS for one Root source-bound callback of owner_disk_preclaim.py SHAa4c5aaf17ad92adb2ae8141fb864b73377ce8db2ded64056e7b4b75fd9f99d38. The reviewer did not call apply, prepare, run, registration or model control.

The wrapper first uses the existing memory-aware choose result, then checks the exact realcandidate through fresh resource accounting before creating a claim. Allthree physical_RAM_pass/physical_disk_pass/admission_disk_pass fields must be exactTrue. It restricts future admission and leaves existing workers, model identity, engine, guard, specs,16 grants and all62 sourcepins unchanged. The current first16 scope has equal64MiB pointoutput caps; this addresses speculative allpending reservations without weakening actual perpoint checks.

Twelve independent puregated_choose cases pass: accepted choiceidentity, nochoice bypass, each requiredfield false/missing, nonbool1, wrong/duplicatecandidate and resourceerror. Inputclaims/pending are unchanged in thefixtures. Actual samePID/new-schedulerRLock/source checks remain in the callback, which retains the prior callable and source/receipt in its marker.

Operational precondition: fresh existing callback directory with APPLIED.json absent and writable. Since the candidate installs its marker/wrapper before writing that receipt, any later receiptwrite failure requires inspection and forward reconciliation of the installedmarker; never blindly resubmit. No performance acceptance, extra modelcredit or newdispatcher is created. See DISK_PRECLAIM_REVIEW.json for exactchecks and the actualscript for reproducibility.
