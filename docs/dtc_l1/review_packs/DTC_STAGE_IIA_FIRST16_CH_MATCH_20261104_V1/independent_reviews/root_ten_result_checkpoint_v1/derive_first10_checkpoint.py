"""Freeze the first10 accepted checkpoint; no native execution or registration calls."""
from pathlib import Path
import datetime,gzip,hashlib,json,math
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1')
R=Path('/root/data/dtc_stage_iia_first16_20261104_v1')
O=A/'root_ten_result_checkpoint_v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert not(O/'MANIFEST.json').exists(),'FROZEN_CHECKPOINT_NO_OVERWRITE'
 bp_path=A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json';bp=json.loads(bp_path.read_bytes())
 assert bp['summary']['accepted_CH']==10 and bp['summary']['common_both_F_n']==3 and bp['summary']['remaining48_locked'] is True
 files={r['name']:r for r in bp['files']}
 for r in files.values():assert sha(r['path'])==r['sha256']
 summary=json.loads(gzip.decompress(Path(files['STAGEIIA_FIRST16_SUMMARY.json.gz']['path']).read_bytes()))
 registry=Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 q=json.loads(registry.read_bytes())['registered_future_requests']['DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1']
 assert q['budget']==len(q['admitted_specs'])==len(q['consumed'])==16 and q['remaining']==0
 assert len({r['uuid']for r in q['consumed'].values()})==16 and all(r['charged']==1 for r in q['consumed'].values())
 c='E2-DTC2A16-ae34174fbbdf83b2-CH-F256-V1';rp=R/'analysis'/(c+'.RESULT.json');r=json.loads(rp.read_bytes())
 assert r['state']=='PASS_STAGEII_CH_STRICT_ARCHIVE_NATIVE_RESTORE' and r['cycles']==24651923
 digest=r['proof']['input_digest'];idx_path=R/'control/ORIGINAL_REFERENCE_INDEX.json';index=json.loads(idx_path.read_bytes());refs={}
 for cell,profile in [('CH','P0'),('DH','P0'),('DH','F256')]:
  matches=[x for x in index['rows']if x['input_digest']==digest and x['cell']==cell and x['profile']==profile];assert len(matches)==1
  ref=matches[0];p=Path(ref['source_path']);assert sha(p)==ref['sha256'];record=json.loads(p.read_bytes());assert record['proof']['performance_accepted'] is True and record['proof']['input_digest']==digest
  refs[cell+'_'+profile]=dict(path=str(p),sha256=sha(p),cycles=record['cycles'])
 sc=refs['CH_P0']['cycles']/r['cycles'];sd=refs['DH_P0']['cycles']/refs['DH_F256']['cycles'];ratio=r['cycles']/refs['DH_F256']['cycles'];interaction=sd/sc
 assert math.isclose(ratio,refs['CH_P0']['cycles']/refs['DH_P0']['cycles']*interaction,rel_tol=1e-12)
 matrix=json.loads((R/'control/MATRIX.json').read_bytes())['points'];names={p['input_digest']:p['program']for p in matrix}
 common={f:summary['common_F128_F256_metrics'][f]for f in ['F128','F256']}
 for f,m in common.items():
  for k in ['S_CH','S_DH','R','I']:assert m[k]['n']==3
  assert m['S_CH']['population']==m['S_DH']['population']==m['R']['population']==m['I']['population']
 assert common['F128']['I']['population']==common['F256']['I']['population']
 population=common['F128']['I']['population']
 audit=json.loads((A/'root_completion_audit_v1/LATEST.json').read_bytes());assert sha(audit['path'])==audit['sha256']
 owner=Path('/proc/1498278/stat').read_text().rsplit(')',1)[1].split();assert int(owner[19])==977758783 and owner[0]not in['Z','X']
 report=dict(schema='DTC_STAGEII_FIRST10_ACCEPTED_ALL16_SPENT_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),authority_commit='5001c3f35052f7f91f1ad41eeff83f2947a0878d',independent_provider=bp,registered_budget=16,consumed=16,remaining=0,unique_UUIDs=16,accepted=10,nonterminal=6,remaining48_released=False,owner=dict(pid=1498278,start_ticks=977758783,state=owner[0]),BICG_F256=dict(new_RESULT_path=str(rp),new_RESULT_sha256=sha(rp),full_input_digest=digest,new_cycles=r['cycles'],original_reference_index_sha256=sha(idx_path),references=refs,S_CH=sc,S_DH=sd,R=ratio,I=interaction,DH_cycles_above_CH_percent=100*(1/ratio-1)),common_population=[dict(input_digest=d,program=names[d])for d in population],common_F128_F256_metrics=common,Root_audit=audit,models_started_by_this_analysis=0,goal_complete=False)
 O.mkdir(exist_ok=True);(O/'TEN_RESULT_CHECKPOINT.json').write_text(json.dumps(report,indent=2)+'\n')
 lines=['# First10 accepted results; all16 identities have started','','The exact first16 request is fully consumed,16 unique UUIDs charged once, with0 unused identities. Ten new CH outcomes have strict/true164/native recovery acceptance; six remain nonterminal. No48-point release, model restart, identity refund or scientific budget expansion occurred. This is an interim checkpoint, not Goal completion.','','## New BICG-F256 matched result','',f'CH-F256 is{r["cycles"]} cycles. S_CH={sc:.6f}; S_DH={sd:.6f}; matched CH/DH R={ratio:.6f}; I={interaction:.6f}. DH uses{100*(1/ratio-1):.2f}% more cycles than matched CH. The DH performance regression remains accepted data, not an archived execution failure.','','## Equal-denominator F128/F256 comparison','','The current common accepted set is '+', '.join(names[d]for d in population)+' (n=3/8). Available F128 and F256 coverage differs, so only this common set supports direct GM comparison.','', '| F | S_CH GM | S_DH GM | R GM | I GM | I positive / zero / negative |','|---|---:|---:|---:|---:|---|']
 for f,m in common.items():lines.append('| '+f+' | '+' | '.join(format(m[k]['GM'],'.6f')for k in ['S_CH','S_DH','R','I'])+' | '+str(m['I']['positive'])+' / '+str(m['I']['neutral'])+' / '+str(m['I']['negative'])+' |')
 lines+=['','These are not first8/core32/frozen35 results. The old n=2 checkpoint has a different population and cannot be compared to this n=3 checkpoint as if the population were unchanged. No per-program F winner is selected. All original pending, negative and zero cells remain in the full paired table.','','## Live ATAX observation is separate from performance','','Consume the frozen B_atax_f256_runtime_observation_v1 package only as-of its05:27:53 to05:29:18CST samples. It verifies continued retirement and roughly comparable elapsed time to closed F128 at the same early K1 instruction position. Application instruction percentage is not wall-time percentage; no numerical live cycles or formal speedup was available. The1 to3 additional hours scenario is conditional from the second sample and is not a batch deadline or final F256 prediction.','','Some human-report range separators render as question marks. They denote lower-to-upper brackets; exact numeric endpoints are retained in the package JSON. They are not missing-data substitutes. ATAX dependency/address formulas remain inspected candidate-source descriptions, with the existing capture-ELF/numeric-state limitations, even where a runtime paragraph uses short kernel descriptions. No frozen input identity is changed.','','The earlier three-case F128 synthesis was created before the BICG-F256 terminal result; its statement that F256 was pending is a dated observation. The current accepted table now includes BICG-F256. Its F128 facts remain unchanged, and the next final analysis will incorporate every remaining strict terminal outcome.','','FR-FCFS capacity and shared credits vary together, with850MHz DRAM and10MiB L2 fixed. Active CH/DH frontends and their capacities/timing differ; no equal-area claim follows. Printed latency means, retry events, candidate source and actual runtime counters retain their separate evidence levels. Missing observations remain missing.','','Final all16 strict/archive/recovery audit, independent all16 scientific review, final matched analysis and a nonexecuting remaining48 recommendation are still required. Englishv0.23 and all historical ledgers remain unchanged.','']
 (O/'README.md').write_text('\n'.join(lines))
 source=Path(__file__);assert source.resolve().parent==O
 mf=dict(schema='DTC_STAGEII_FIRST10_CHECKPOINT_MANIFEST_V1',files=[dict(path=p.name,sha256=sha(p),bytes=p.stat().st_size)for p in sorted(O.iterdir())if p.is_file()and p.name!='MANIFEST.json'])
 (O/'MANIFEST.json').write_text(json.dumps(mf,indent=2)+'\n')
 print(json.dumps(dict(path=str(O),manifest_sha256=sha(O/'MANIFEST.json'),BICG_F256=report['BICG_F256'],common_GMs={f:{k:m[k]['GM']for k in ['S_CH','S_DH','R','I']}for f,m in common.items()},goal_complete=False)))

if __name__=='__main__':main()
