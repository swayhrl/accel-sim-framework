"""Generate an evidence-based closure draft; final mode has strict guards."""
import sys
sys.dont_write_bytecode=True
from local_common import *
from t2_closure_audit import OUT,table,dump
import argparse,csv,collections,datetime

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');args=ap.parse_args()
    x=load(OUT/'CONTENT_AND_RESTORE_CLOSURE.json');baseline=load(OUT/'TAKEOVER_BASELINE.json');progress=load(OUT/'PROGRESS_SUMMARY.json')
    with (OUT/'FROZEN115_FINAL_STATE_TABLE.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==115 and len({r['asset_id'] for r in rows})==115
    assert x['frozen_sha256']==baseline['scope_sha256']=='718f30ec3bc8e5ece20df02cd472ebee17eac320f7b5a9e5b5e69841cc63cc04'
    done=x['committed'];holds=[r for r in rows if r['status']=='HOLD'];pending=[r for r in rows if r['status'] not in ['COMMITTED','HOLD']]
    categories=load(OUT/'HOLD_CLASSIFICATIONS.json') if (OUT/'HOLD_CLASSIFICATIONS.json').exists() else {}
    allowed={'RESOURCE','SCIENTIFIC_IDENTITY','RECOVERY_EVIDENCE','ORIGINAL_CONTENT_ANOMALY','PERMISSION','CONTRACT'}
    if args.final:
        assert not pending and not x['driver_live'],'EXECUTION_STILL_ACTIVE_OR_PENDING'
        assert not x['audit_errors'],'UNRESOLVED_CONTENT_AUDIT_FAILURES'
        for row in holds:
            c=categories[row['asset_id']];assert c['category'] in allowed and c.get('evidence') and c.get('bounded_repair_or_nonrepair_reason'),'HOLD_NOT_JUSTIFIED'
            assert c.get('terminal') is True and c.get('expected_reason')==row['reason'],'HOLD_IS_TRANSIENT_OR_CLASSIFICATION_IS_STALE'
        stop=load(OUT/'FINAL_PROCESS_SHUTDOWN_AUDIT.json')
        assert stop['driver_stopped'] and stop['supervisor_stopped'] and stop['publisher_stopped'],'TASK_OWNED_PROCESSES_NOT_CLOSED'
        assert stop['unrelated_processes_signaled']==0
    by_kind=[]
    for kind,total in [('TRACE',51),('DTC_RAW',63),('Q05_FIXED10000',1)]:
        group=[r for r in rows if r['kind']==kind];assert len(group)==total
        by_kind.append(dict(kind=kind,total=total,committed=sum(r['status']=='COMMITTED' for r in group),HOLD=sum(r['status']=='HOLD' for r in group),pending=sum(r['status'] not in ['COMMITTED','HOLD'] for r in group),committed_bytes=sum(int(r['expected_bytes']) for r in group if r['status']=='COMMITTED')))
    restore_counts=dict(collections.Counter(z['native_restore_status'] for z in done));native=[z for z in done if z['full_native_restore_performed']];new=[z for z in done if z['asset_id'] not in baseline['committed_asset_ids']]
    rc=x['retirement'];initial_alloc={k:v['unlinked_file_allocated_bytes'] for k,v in rc['initial'].items()};package=rc['package'];pool_delta=rc['initial_pool_observed_interval_delta']+package['actual_observed_SSD_increase_bytes'];source_delta=rc['initial_Source_observed_interval_delta']+package['actual_observed_SSD_increase_bytes']
    extra_path=OUT/'reclaim_174new/DONE.json'
    extra=load(extra_path) if extra_path.exists() else None
    if args.final and (OUT/'reclaim_174new/QUALIFIED.json.gz').exists():
        assert extra,'ADDITIONAL_174NEW_RETIREMENT_NOT_FINISHED'
        verification=load(OUT/'reclaim_174new/INDEPENDENT_CLOSURE.json')
        assert verification['status']=='PASS' and verification['unclosed_file_intents']==0,'NEW_174NEW_RETIREMENT_NOT_CLOSED'
    status=('FINAL_WITH_CLASSIFIED_HOLDS' if holds else 'FINAL_ALL_FROZEN_SCOPES_COMMITTED') if args.final else 'DRAFT_IN_PROGRESS_NOT_GOAL_COMPLETION'
    proof=dict(schema='LANE_T2_REQUIREMENT_CLOSURE_AUDIT_V1',status=status,unix=x['unix'],scope=115,groups=by_kind,committed=len(done),pending=len(pending),HOLD=len(holds),content_audit_errors=x['audit_errors'],prior20_control_readbacks_PASS=sum(z['control_readback']=='PASS' for z in x['prior20_reuse']),T2_new_committed_assets=len(new),T2_new_logical_bytes=sum(z['bytes'] for z in new),native_restore_status_counts=restore_counts,full_native_restore_verified_assets=len(native),full_native_restore_verified_bytes=sum(z['bytes'] for z in native),scientific_acceptance_changed=False,retirements_replayed=False,new_T2_Source_retirement_bytes=0,requirements={
        'all115_have_final_state':not pending,'all_committed_match_frozen_identity_range_SHA_and_COMMIT':not x['audit_errors'] and len(done)==x['committed_ledger_count'],
        'each_HOLD_has_specific_classified_evidence':all(r['asset_id'] in categories and categories[r['asset_id']].get('category') in allowed for r in holds),
        'prior20_not_counted_as_new_transfer':True,'Trace51_DTC63_Q05_1_denominators_preserved':True,'Source_retirement_INTENT_DONE_all_closed':all(not z['unclosed'] for z in rc['initial'].values()),
        'Q05_exact223499B_acceptance_identity':any(z['asset_id']=='AWMA_Q05_FIXED10000_EXACT_RAW' for z in done),
        'partial_transactions_explained':'REQUIRES_FINAL_STOPPED_EXECUTION_AUDIT','task_owned_processes_stopped':'REQUIRES_FINAL_SHUTDOWN_AUDIT','final_GitHub_publication_and_independent_readback':'REQUIRES_FINAL_REMOTE_READBACK'})
    proof['additional_174new_verified_copy_retirement']=extra
    io_policy_path=OUT/'ACTIVE_SCIENCE_IO_GATE_USER_AUTHORIZATION.json'
    io_policy=load(io_policy_path) if io_policy_path.exists() else None
    proof['active_science_IO_gate_user_authorization']=io_policy
    dump('REQUIREMENT_CLOSURE_AUDIT.json',proof)
    when=datetime.datetime.fromtimestamp(x['unix'],datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    lines=[f'# Lane T2 archive report — {status}',f'\nEvidence snapshot: {when}. Original queue SHA256 `{x["frozen_sha256"]}`.',
        f'\nThe original 115 scopes remain unchanged. **{len(done)} committed, {len(holds)} current HOLD, {len(pending)} pending/in-progress**. Content archived in this execution: {sum(z["bytes"] for z in done):,} bytes. T2 adds {len(new)} assets / {sum(z["bytes"] for z in new):,} bytes after the {len(baseline["committed_asset_ids"])}-asset takeover baseline.',
        '\n| Group | Frozen | Committed | HOLD | Pending | Committed logical bytes |','|---|---:|---:|---:|---:|---:|']
    for z in by_kind:lines.append(f'| {z["kind"]} | {z["total"]} | {z["committed"]} | {z["HOLD"]} | {z["pending"]} | {z["committed_bytes"]:,} |')
    lines += ['\nThe complete 115-row state table is `FROZEN115_FINAL_STATE_TABLE.csv`; new asset IDs and COMMITs are `NEW_T2_COMMITTED_ASSETS.csv`. `MEMBER_SHA_INDEX.csv.gz` and its lossless hash receipt retain every audited committed member SHA, numeric metadata and genuine164 path. `CONTENT_AND_RESTORE_CLOSURE.json` contains the COMMIT → manifest/ranges/tree and Source EOF proof checks. This review does not claim to have repeated all large payload hashes.',
        f'\nPrior 20 trace selectors: {sum(z["control_readback"]=="PASS" for z in x["prior20_reuse"])}/20 metadata/COMMIT readbacks PASS; their {sum(z.get("bytes",0) for z in x["prior20_reuse"]):,} bytes are reused, never added to T2 new bytes. The already archived R13 package is {package["logical_bytes"]:,} bytes and remains separately accounted. `TRACE51_COVERAGE.csv` identifies metadata supplements and reused input bodies; `.trace`, `.traceg`, full/fraction/trim and packages/expanded members are not equated.',
        '\n`POLYBENCH_VARIANT_COVERAGE.csv` carries the 28 mandatory historical variants and four supplemental rows. Historical out-of-queue content or scientific HOLDs remain explicit and do not become new tasks or successful frozen-copy claims. `Q05_EXACT_SCOPE.json` binds fixed10000 run.log to SHA256 `06822c9fb9d2de0208eb51fb61c82f21150f509b8320662fd935efbac283843f`; natural R0 is a different object.',
        f'\nComplete native Target recovery is verified for {len(native)} scopes of this frozen115 execution / {sum(z["bytes"] for z in native):,} bytes. These are not necessarily new T2 restorations. Other restoration states: `{json.dumps(restore_counts,sort_keys=True)}`. Full native restores above the qualified 240 MiB window were not performed. Their immutable raw trees, complete file SHA, original numeric metadata and bounded recovery helpers are retained; unrestricted full native recovery and scientific runtime acceptance are not claimed.',
        f'\nHistorical exact retirement: {rc["initial"]["TARGET"]["done"]:,} T-owned test-copy files, {rc["initial"]["SOURCE"]["done"]} approved Source kernel files, plus the one cold polybench package. Allocated bytes unlinked: Target test copies {initial_alloc["TARGET"]:,}; Source kernel files {initial_alloc["SOURCE"]:,}; Source package {package["source_allocated_before_bytes"]:,}. Independently observed operation-interval SSD free-space deltas: pool {pool_delta:,}; Source unlink intervals {source_delta:,}. These are distinct measures and are not added to archive volume. T2 has not replayed any retirement or performed a new Source retirement.',
        f'\nCurrent shared SSD free: {x["resources"]["/root/data"]["available_bytes"]:,} bytes; Share/MD127 free: {x["resources"]["/root/share"]["available_bytes"]:,}; genuine164 free: {x["resources"]["/root/share/mnt164"]["available_bytes"]:,}. Current free-space changes include other projects and are not attributed to this archiver.',
        '\nAll per-asset genuine164 bundle and recovery entries are in `CONTENT_AND_RESTORE_CLOSURE.json`; prior 20 reuse links are in the same file. The existing five-minute publication receipts remain `../checkpoint/recovery_20261025/PUBLICATION_RECEIPTS.jsonl`. Final process shutdown, partial-transaction accounting and GitHub remote readback must be independently closed before Goal completion.']
    if extra:
        lines.append(f'\nAdditional user-authorized 174-new cold compiler-copy retirement: {extra["files"]:,} exact files; logical bytes {extra["logical_bytes_unlinked"]:,}; allocated file bytes unlinked {extra["allocated_bytes_unlinked"]:,}; independently observed SSD free-space interval delta {extra["observed_SSD_free_interval_delta"]:,}. Concurrent project writes prevent exclusive causal attribution of that interval delta. These measures are separate from each other, the historical releases and frozen115 archive bytes. Exact whitelist, SHA/metadata, COMMIT, INTENT/DONE, recovery test and restore entry are under `reclaim_174new/`. No old174 Source files were deleted by this additional retirement.')
        lines.append('\nRecorded execution-admission error: the one 84,346,374-byte native restore test used a base-only SSD check instead of all declared reservations and the active-science gate. It passed SHA/metadata verification and its 84,353,024 allocated bytes were removed, without counting them as original-copy reclaim. `reclaim_174new/RESTORE_TEST_ADMISSION_DEVIATION.json` preserves the executed version and correction. Future test allocations now require the original full admission plus complete test-file capacity; directed checks include reservation shortfall and active-science I/O rejection. Content/receipt closure PASS does not erase this admission deviation.')
    if io_policy:
        lines.append('\nThe subsequent explicit user authorization in `ACTIVE_SCIENCE_IO_GATE_USER_AUTHORIZATION.json` changes only the active-science avg10 I/O check to monitor-only. It does not retroactively authorize the earlier restore-test admission error. Sustained severe host-I/O protection, SSD/RAM reservations, locks, rate/staging limits and scientific identity checks remain unchanged. `io_policy_transition/` retains directed qualification, the exact old/new supervisor identities and proof that the original deadline and cumulative counters were preserved during the single policy reload; the Publisher was not restarted.')
    if holds:
        lines.append('\nCurrent explicit HOLDs:')
        lines.extend(f'- `{r["asset_id"]}`: {categories.get(r["asset_id"],{}).get("category","UNCLASSIFIED")} — {r["reason"]}' for r in holds)
    else:lines.append('\nNo current classified terminal HOLD has been established in this snapshot. Remaining pending work is not counted as successful completion.')
    if not args.final:lines.append('\nThis is an in-progress report. Execution and bounded supervision continue; no user decision is currently requested by this draft.')
    (OUT/('FINAL_REPORT.md' if args.final else 'DRAFT_FINAL_REPORT.md')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=status,committed=len(done),pending=len(pending),HOLD=len(holds),T2_new_assets=len(new),T2_new_bytes=sum(z['bytes'] for z in new))))

if __name__=='__main__':main()
