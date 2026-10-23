# 174-new unified EP-L2 / DTC-L1 management

Installed native entry: `/root/data/ep_l2_dtc_l1_management_20261023_v1/bin/`. Existing old174 execution environment and scientific controllers remain in place. This is a finite command tool, no daemon/scanner/scientific scheduler and no replacement scientific registry.

The user explicitly delegated E2/BA management review to Lane T and approved formal management cutover. Epoch1 is committed in the original EP registry and original DTC coordinator, with original lock protection, exact backups and INTENT/COMMITTED records. All preexisting scientific key/value data compare equal before/after; simulator/controller source code, qualifications, counts and T0 were not changed. Personal E2/BA review is not impersonated. Formal cutover covers daily management and result storage; scientific starts remain disabled. The mandatory consume/fork fence for future scientific dispatch is explicitly not claimed installed.

Current authoritative Source status: EP57 actual starts,44 COMPLETE_VALID results, controller STOPPED; DTC active route-repair ledger2 actual forks/2 consumed/1 accepted/0 remaining, cohortF=null, terminal stop. The obsolete top-level DTC0-start ledger and old14/40 labels are not used as current counts. Goal UI sessions cannot be inferred from files; source-owner last published Goal disposition is labeled separately. Historical collectors are listed but not adopted/stopped.

## Daily commands on174-new

```
BASE=/root/data/ep_l2_dtc_l1_management_20261023_v1/bin
$BASE/project status --project EP_L2
$BASE/project status --project DTC_L1
$BASE/project assets --project EP_L2
$BASE/project assets --project DTC_L1
$BASE/experiment inspect E057 --project EP_L2 --environment
$BASE/experiment inspect AD_GEMM --project DTC_L1 --path ENGINE/perf_counter.csv.gz
$BASE/experiment prepare E057 --project EP_L2
$BASE/result archive E057 --project EP_L2
$BASE/result archive AD_GEMM --project DTC_L1
$BASE/result restore E057 --project EP_L2 --dry-run --destination /root/data/full_result_offload_20261023_v1/NEW_ABSENT_RECOVERY
```

`prepare` never starts an application or relaunches a paid experiment. Archive checks for the existing two complete datasets reuse immutable prior SHA/restore receipts and verify control digests/current range/dependency presence, transferring0 payload. They do not assert a fresh full raw-data hash per invocation. Restore preflight writes nothing; `--execute` explicitly calls the already verified frozen restore worker only in a new admitted ABSENT task-native directory. No repeat migration or whole restore was run this round.

20 primary assets are indexed and currently accessible. Original SHA/provenance and current metadata/readability are separate fields. No claim that path existence freshly proves every trace/binary content hash. `experiment inspect` resolves registered owner identities and on-demand exact frozen member paths; unknown IDs, traversal and missing assets fail clearly. Source/network failure returns HOLD, never stale0 counts.

## New completed result outbox

Use native `outbox/` metadata, original174 local hot output, current owner scientific acceptance and a whole typed COPY_READY. `result archive NEW_ID --project EP_L2|DTC_L1 --offer /root/data/ep_l2_dtc_l1_management_20261023_v1/outbox/OFFER.json --dry-run` validates exact full owner file/directory/link rows, publication/root/whole SHA and writer/reader dispositions, current accepted identity, reserved physical space and no duplicate archived selector. `--execute` uses the pinned baseline engine with only exact namespace/no-pilot-dependency bindings, the original sole receiver and sender locks,128MiB ranges,256MiB staging cap and30MiB/s. Source always KEEP. The new-offer code-binding/permission tests passed; no new real COPY_READY offer was supplied, so first new payload operation is not labeled independently runtime-qualified here. See FUNCTION_READINESS.json. Existing data path was reused, not retested by copying prior data.

New NAS root: `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_unified_results`;174-new accesses it only through genuine164 SSHFS `/root/share/mnt164`. New result restore root: `/root/data/ep_l2_dtc_l1_management_20261023_v1/result_recovery`. Full raw-size reservations, complete metadata/SHA, close/reopen, immutable commit-last and retained verified range prefixes remain effective. Future complete offers must be normalized from raw owner publications; the binder independently compares every typed record, never trusts only a boolean qualifier. Unsupported internal hardlink groups hold rather than lose topology. Active raw, scientific locks, SQLite and controllers never move toSSHFS.

Current two complete recovery sets retain the9 pinned existing164 objects. No reupload of the9 sidecars, no bulk historical raw/trace hashing/scanning, no historical asset deletion or relocation. Recovery remains full native Target verification, not native164 execution. New-result local reclamation is a draft only; old historical data stay SOURCE_KEEP. No Source delete API exists.

## Evidence and boundaries

FUNCTION_READINESS.json distinguishes verified modes from held future scientific/new-offer payload modes. NO_START_FUNCTIONAL_AND_FENCE_TESTS.json records26 actual CLI and fence checks; OUTBOX_ENVIRONMENT_AND_FAILURE_CONTROL_TESTS.json records11 additional new control/permission/failure checks. These are engineering tests, not native scientific correctness. FORMAL_MANAGEMENT_SWITCH_RECEIPT.json, delegated_owner_reviews/, USER_AUTHORIZED_FORMAL_MANAGEMENT_SWITCH.json and original-source native preimages/journal bind the authorized management cutover. ASSET_AVAILABILITY_INDEX.json and data/asset_catalog.json provide lightweight Source/164/recovery mapping. NEXT_ACTIONS.json gives exact current commands and the remaining future scientific gates. NEW_RESULT_RECLAIM_AUTHORIZATION_PROPOSAL.json enables no cleanup.

All operations remain on existing Source environments with trusted174-new→old174 SSH; Windows orchestrates code/evidence only. Management files are native ext4, true164 retains completed result archives, Share receives0 new management payload. Scientific starts0, new result payload this round0B, full restore files created0, Source historical release0B. Original scientific values/ledgers/T0 were preserved; the only Source control-plane mutations are the explicitly authorized additive management-authority objects.

Automatic owner metadata intake is available via `python3 -B /root/data/ep_l2_dtc_l1_management_20261023_v1/tools/make_outbox_offer.py --project PROJECT --experiment ID --owner-commit SHA40 --owner-path docs/PROJECT/EXACT_COPY_READY.json --output /root/data/ep_l2_dtc_l1_management_20261023_v1/outbox/NEW_OFFER.json`. It fetches the exact published READY and auxiliary manifest records directly from Source Git, verifies every hash, resolves current owner acceptance and builds native metadata only. No manual raw/trace transfer through Windows is needed. Already archived old selectors are rejected rather than reuploaded. The2 automatic-fetch/duplicate-refusal checks bring the control-test total to39;2 project publication-lookup hashes were separately verified.
