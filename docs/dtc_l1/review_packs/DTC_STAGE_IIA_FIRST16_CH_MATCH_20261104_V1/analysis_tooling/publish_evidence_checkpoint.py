"""Root-only read-only evidence export. Never imports model engines or dispatches work."""
from pathlib import Path
import argparse,fcntl,hashlib,importlib.util,json,re,subprocess,urllib.request

P=Path
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_stage_iia_first16_execution_20261104_v1')
R=P('/root/data/dtc_stage_iia_first16_20261104_v1')
SRC=A/'publication_service_v2/report_only_publisher.py'
PUBLISHER_PIN='273d976fa3498c6c981882c02df41f5c2de1f688582ea72a9d58749a9efc6930'
PLOT_PIN='9d996a2784a96a4ab5b970a73ddc5eeb481ab66b538dd3b4558d9e8781ef017e'

def load_utilities():
 assert hashlib.sha256(SRC.read_bytes()).hexdigest()==PUBLISHER_PIN
 s=importlib.util.spec_from_file_location('root_readonly_export_utilities',SRC)
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--tag',required=True)
 ap.add_argument('--visual-manifest',required=True,help='Exact figure manifest whose two PNGs Root has visually checked.')
 ap.add_argument('--packet',action='append',default=[],help='164-relative evidence-directory=manifest-SHA256.')
 ap.add_argument('--require-all16',action='store_true')
 args=ap.parse_args()
 assert re.fullmatch(r'[a-zA-Z0-9_-]{1,90}',args.tag)
 assert re.fullmatch(r'[0-9a-f]{64}',args.visual_manifest)
 m=load_utilities();O=m.O;REL=m.REL
 receipts=A/'root_scientific_checkpoint_tool_v1/receipts';receipts.mkdir(parents=True,exist_ok=True)
 receipt=receipts/(args.tag+'.json')
 with (A/'PUBLICATION.lock').open('a+b') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  if not receipt.exists():
   assert m.git('branch','--show-current')==m.B and not m.git('status','--porcelain')
   assert not(A/'publication_service_v2/PENDING_PUSH.json').exists()
   bp_path=A/'agents/B_runtime_analysis_v1/PUBLICATION_PROVIDER.json';bp_bytes=bp_path.read_bytes();bp=json.loads(bp_bytes)
   fp=m.rd(A/'agents/A_figures_v1/PUBLICATION_PROVIDER.json')
   assert fp['source_provider_sha256']==hashlib.sha256(bp_bytes).hexdigest(),'RERENDER_FIGURES_FROM_CURRENT_PROVIDER_FIRST'
   assert fp['accepted_CH']==bp['summary']['accepted_CH'] and fp['common_both_F_n']==bp['summary']['common_both_F_n']
   assert m.sha(bp['manifest']['path'])==bp['manifest']['sha256']
   assert m.sha(fp['manifest']['path'])==fp['manifest']['sha256']==args.visual_manifest
   assert bp['summary']['remaining48_locked'] is True
   assert m.sha(A/'agents/A_figures_v1/plot_first8.py')==PLOT_PIN
   audit=m.rd(A/'root_completion_audit_v1/LATEST.json');assert m.sha(audit['path'])==audit['sha256']
   if args.require_all16:
    assert bp['all_registered16_terminal_verified'] is True
    assert m.rd(audit['path'])['science_execution_complete'] is True
   files=[];provenance=[]
   def copy(p,target):
    p=P(p);dst=O/target;assert dst.is_relative_to(O);dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(p.read_bytes());files.append(str(dst.relative_to(m.W)));provenance.append(dict(source=str(p),target=target,sha256=m.sha(dst)))
   for row in bp['files']:
    assert m.sha(row['path'])==row['sha256'];copy(row['path'],'analysis/'+row['name'])
   m.put(O/'analysis/PROVIDER.json',bp);files.append(REL+'/analysis/PROVIDER.json')
   for row in fp['files']:
    assert m.sha(row['path'])==row['sha256'];copy(row['path'],'figures/current/'+row['name'])
   copy(fp['manifest']['path'],'figures/current/MANIFEST.json')
   m.put(O/'figures/CURRENT_PROVIDER.json',fp);files.append(REL+'/figures/CURRENT_PROVIDER.json')
   qual=m.rd(O/'figures/SOURCE_QUALIFICATION.json');qual.update(current_render_manifest_sha256=fp['manifest']['sha256'],Root_PNG_visual_inspection='PASS_BOTH_PLOTS_EXACT_VISUAL_MANIFEST',current_accepted_CH=fp['accepted_CH'],current_common_programs=fp['common_both_F_n']);m.put(O/'figures/SOURCE_QUALIFICATION.json',qual);files.append(REL+'/figures/SOURCE_QUALIFICATION.json')
   text='''# First8 scientific comparison figures

Current coverage is defined by CURRENT_PROVIDER.json and current/MANIFEST.json. These bind the exact B independent result-provider snapshot; the generic periodic publisher may later advance the table before the next chart export. The figure itself prints its timestamp, acceptedCH/16 and common n/8. This is the fixed first8 population, with no per-program winner selection.

Both plots preserve pending/missing/negative states rather than plotting them as zero. Performance is own-design P0/variant cycles, and I=S_DH/S_CH. All F128/F256 GM points use the exact same common accepted input set. Display labels are rounded to3 decimals: a label1.000 is not a claim of exact zero response; use raw cycles and the six-decimal paired table for that distinction (ATAX is a relevant example).

The original3-result tooling qualification and four-result C review remain frozen as-of evidence. Current images/data/environment/source are verified by the current render manifest. The plot source9d996a27 and isolated true164 Matplotlib environment are unchanged. Rerender on174-new with the documented isolated interpreter and plot_first8.py --provider <B_runtime_analysis_v1/PUBLICATION_PROVIDER.json>; Root then visually checks the two PNGs and exports the exact manifest. No simulation is launched by plotting/exporting.

Matched downstream options do not imply matched L1 physical capacity, area, timing or active frontend resources. Consume the separate active-path and cost clarification. Final all16 scientific review and subsequent48 proposal are separate requirements, not implied by a chart checkpoint.
'''
   (O/'figures/README.md').write_text(text);files.append(REL+'/figures/README.md')
   copy(audit['path'],'root_audit/LATEST_REQUIREMENT_AUDIT.json')
   resource=m.rd(A/'root_resource_trajectory_v1/LATEST.json');d=P(resource['snapshot']);assert m.sha(d/'MANIFEST.json')==resource['manifest_sha256']
   for p in d.iterdir():
    if p.is_file():copy(p,'resource_trajectories/'+p.name)
   for value in args.packet:
    name,pin=value.rsplit('=',1);assert re.fullmatch(r'[0-9a-f]{64}',pin)
    d=(A/name).resolve();assert d.is_relative_to(A.resolve()) and d!=A
    assert m.sha(d/'MANIFEST.json')==pin
    for row in m.rd(d/'MANIFEST.json')['files']:
     p=d/row['path'];assert p.is_relative_to(d) and m.sha(p)==row['sha256'];copy(p,'independent_reviews/'+d.name+'/'+row['path'])
    copy(d/'MANIFEST.json','independent_reviews/'+d.name+'/MANIFEST.json')
   for p in (R/'analysis').glob('*.RESULT.json'):copy(p,'accepted_or_negative_receipts/'+p.name)
   q=m.rd('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_STAGE_IIA_FIRST16_CH_MATCH_20261104_V1']
   assert q['budget']==len(q['admitted_specs'])==16 and q['remaining']==16-len(q['consumed'])
   batch=m.rd(R/'analysis/BATCH_STATE.json')
   for target,value in [('snapshots/NEW_REQUEST.json',q),('snapshots/BATCH_STATE.json',batch),('LATEST_STATUS.json',dict(UTC=m.utc(),status='FIRST16_EVIDENCE_CHECKPOINT_NOT_GOAL_COMPLETION',summary=bp['summary'],batch_running=batch['running'],next48_released=False,models_launched_by_publication_service=0))]:
    m.put(O/target,value);files.append(REL+'/'+target)
   copy(P(__file__),'analysis_tooling/publish_evidence_checkpoint.py')
   metadata=dict(schema='DTC_STAGEII_FIRST16_ROOT_SCIENTIFIC_EXPORT_V1',tag=args.tag,UTC=m.utc(),analysis_provider=bp,figure_provider=fp,require_all16=args.require_all16,Root_requirement_audit=audit,closed_resource_snapshot=resource,evidence_packets=args.packet,provenance=provenance,goal_complete=False,next48_released=False,new_model_starts=0)
   m.put(O/'ROOT_SCIENTIFIC_EXPORT.json',metadata);files.append(REL+'/ROOT_SCIENTIFIC_EXPORT.json')
   mf=m.rd(O/'MANIFEST.json');mf.update(UTC=m.utc(),root_latest_checkpoint=args.tag,files=[dict(path=str(p.relative_to(O)),sha256=m.sha(p),bytes=p.stat().st_size)for p in sorted(O.rglob('*'))if p.is_file()and p!=O/'MANIFEST.json']);m.put(O/'MANIFEST.json',mf);files.append(REL+'/MANIFEST.json')
   m.git('add','-f','--',*files);assert set(m.git('diff','--cached','--name-only').splitlines())<=set(files)
   m.git('diff','--cached','--check','--',REL+'/figures/README.md',REL+'/ROOT_SCIENTIFIC_EXPORT.json',REL+'/MANIFEST.json',REL+'/analysis_tooling/publish_evidence_checkpoint.py')
   m.git('commit','-m','docs(dtc): export verified scientific evidence '+args.tag,'--',*files)
   names=['MANIFEST.json','ROOT_SCIENTIFIC_EXPORT.json','analysis/STAGEIIA_FIRST16_RESULTS.md','figures/current/MANIFEST.json','figures/current/CH_DH_P0_normalized_first8.png','root_audit/LATEST_REQUIREMENT_AUDIT.json']
   m.put(receipt,dict(status='COMMITTED_PUSH_PENDING',commit=m.git('rev-parse','HEAD'),branch=m.B,tag=args.tag,manifest_sha256=m.sha(O/'MANIFEST.json'),expected_readbacks={n:m.sha(O/n)for n in names},goal_complete=False))
  v=m.rd(receipt)
  # A later ordinary report may already include this committed checkpoint. Never rewind it.
  m.git('merge-base','--is-ancestor',v['commit'],'HEAD')
  m.git('push','origin','HEAD:refs/heads/'+m.B)
  head=m.git('rev-parse','HEAD');remote=m.git('ls-remote','origin','refs/heads/'+m.B,timeout=35).split()[0];assert head==remote
  op=urllib.request.build_opener(urllib.request.ProxyHandler({'https':'http://127.0.0.1:27890'}));checks={}
  for n,pin in v['expected_readbacks'].items():
   url='https://raw.githubusercontent.com/swayhrl/accel-sim-framework/'+v['commit']+'/'+REL+'/'+n;b=op.open(url,timeout=25).read();assert hashlib.sha256(b).hexdigest()==pin;checks[n]=dict(url=url,sha256=pin)
  v.update(status='PUSH_LSREMOTE_HTTPS_VERIFIED',UTC=m.utc(),verified_remote_head=remote,HTTPS_readbacks=checks);m.put(receipt,v)
  m.put(A/'ROOT_LATEST_SCIENTIFIC_CHECKPOINT_PUBLICATION.json',v);print(json.dumps(v))

if __name__=='__main__':main()
