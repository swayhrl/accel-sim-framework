"""Additive Lane3 frozen-binary affected checks using existing runner and V2 schema."""
import argparse,copy,json,os,resource,shutil,subprocess,time
from pathlib import Path
from registry import Registry,write_json,process_identity
from run import require,digest,asset_manifest,content_hash,process_tree_rss,terminate_owned
from headroom_config import PARALLEL_EXPERIMENT,PARALLEL_COORDINATION,FINITE_OVERRIDES,H0,options,validate_runtime_dump
from independent_headroom_r19 import native_options,safe
from package_r0 import freeze_checksums

REPO=Path(__file__).resolve().parents[3]
H=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'
ORIGINAL=Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs')
OUT=Path('/workspace/ep_l2_potential20261017_lane5_results')

def git(*a):return subprocess.check_output(['git',*a],cwd=REPO)


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--handoff',required=True,type=Path);p.add_argument('--revision',type=int,default=1);a=p.parse_args();handoff=json.loads(a.handoff.read_text());profile=handoff['profile'];pub=handoff['publication'];prefix=handoff['pack_repository_path']
 require(profile in FINITE_OVERRIDES and handoff['identity']['binary_sha256']=='23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee','Only independently checked frozen-binary positive profiles')
 remote=git('rev-parse','refs/remotes/origin/hrl/ep-l2-ft20261016-lane3-v1').decode().strip();require(subprocess.run(['git','merge-base','--is-ancestor',pub,remote],cwd=REPO).returncode==0,'Producer handoff not fetched from GitHub')
 raw=git('show',pub+':'+prefix+'/evidence/PROFILE_MANIFEST.json');require(raw==Path(handoff['manifest']).read_bytes() and digest(handoff['manifest'])==handoff['manifest_sha256'],'Published manifest differs');m=json.loads(raw)
 producer=json.loads(git('show',pub+':'+prefix+'/evidence/RECEIPT.json'));source=json.loads(git('show',pub+':'+prefix+'/SOURCE_IDENTITY.json'));build=producer['fixture_build_identity']
 require(producer['status']=='AFFECTED_PRODUCTION_PASS_PENDING_INDEPENDENT_ADMISSION' and producer['runtime_code_recompiled'] is False and m['allowed_overlay']==FINITE_OVERRIDES[profile],'Producer condition/source scope differs')
 fixture=Path(handoff['replay'][0]['command'][2]);require(digest(fixture)==build['binary_sha256'],'Changed actual fixture binary')
 src='util/ep_l2/parallel_potential_lane3/'+({'ICNT2_H0':'icnt_probe.cc','WAD256_Q4':'wad_probe.cc'}.get(profile,'production_probe.cc'));require(__import__('hashlib').sha256(git('show',source['tool_source_commit']+':'+src)).hexdigest()==source['executed_fixture_sha256']==build['fixture_source_sha256'],'Fixture exact source not bound')
 require(digest(m['binary'])==m['identity']['binary_sha256']==handoff['identity']['binary_sha256'],'Main binary changed')
 for path,sha in build['archives_sha256'].items():require(digest(path)==sha,'Official native archive changed')
 for root,key in [(Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-fixed-r1'),'core_source_commit'),(Path('/workspace/worktrees/accel-sim-ep-l2-ft20261017-lane1-a1-fixed-r1'),'framework_source_commit')]:
  require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==m['identity'][key] and not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root),'Runtime source moved/dirty')
 # All positive producer pack bytes are content checked; prior failures stay frozen.
 for line in git('show',pub+':'+prefix+'/SHA256SUMS').decode().splitlines():
  sha,name=line.split('  ',1);require(__import__('hashlib').sha256(git('show',pub+':'+prefix+'/'+name)).hexdigest()==sha,'Producer pack frozen checksum mismatch')
 pack=REPO/('docs/ep_l2/review_packs/FT20261017_LANE5_PARALLEL_'+profile+'_CONFIG_QUALIFICATION_r'+str(a.revision));require(not pack.exists(),'Preserve prior independent revision');pack.mkdir()
 write_json(pack/'LANE3_MANIFEST.json',m);write_json(pack/'LANE3_RECEIPT.json',producer);write_json(pack/'LANE3_HANDOFF.json',handoff);write_json(pack/'LANE3_SOURCE.json',source)
 qpath=H/('PARALLEL_'+profile+'_INDEPENDENTLY_QUALIFIED_r'+str(a.revision)+'.json');specdir=H/('parallel_specs_admitted_r'+str(a.revision))/profile;specdir.mkdir(parents=True,exist_ok=False);modes={};specpaths=[];tests=[];r=Registry();lease=None;proc=None;resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 try:
  safe();lease=r.build_lease('lane5',cpu=1,memory=4*2**30)
  for mode,row in m['modes'].items():
   require(asset_manifest(row['configs'],ordered=True)==row['ordered_configs'],'Producer config content moved')
   base=json.loads((ORIGINAL/('convolutionSeparable_'+mode+'.json')).read_text());baseopts=options([x['path'] for x in base['configs']]);require(options([x['path'] for x in row['configs']])=={**baseopts,**FINITE_OVERRIDES[profile]}==row['effective_options'],'Producer has extra effective option changes')
   overlay=row['configs'][-1]['path'];require(options([overlay])==FINITE_OVERRIDES[profile],'Non-whitelisted overlay')
   configs=base['configs']+[{'name':'config-5.config','path':overlay}];manifest=asset_manifest(configs,ordered=True)
   require(content_hash({'ordered_configs':manifest[:5],'auxiliary_assets':[],'environment':base['environment']})==H0[mode],'Original H0 content changed')
   for workload,offset in [('convolutionSeparable',0),('FWT_7_21',2)]:
    cellbase={'ROP40_H0':1,'ICNT2_H0':9,'WAD256_Q4':13}[profile]+offset
    spec=copy.deepcopy(json.loads((ORIGINAL/(workload+'_'+mode+'.json')).read_text()));spec.update(configs=configs,experiment_id=PARALLEL_EXPERIMENT,regime=profile,profile=mode,cell_id='F'+f'{cellbase+(mode=="U_WB16"):03d}',qualified_release=str(qpath),result_root=str(OUT),runner_tooling_source_commit=git('rev-parse','HEAD').decode().strip())
    spec['native_legacy_semantic_proof']=json.loads((ORIGINAL/'FWT_7_21_B16_BANKED.json').read_text())['native_legacy_semantic_proof']
    spec['identity']['runtime_config_sha256']=content_hash({'ordered_configs':manifest,'auxiliary_assets':[],'environment':base['environment']});sp=specdir/(workload+'_'+mode+'.json');write_json(sp,spec);specpaths.append(str(sp))
   modes[mode]={'ordered_configs':manifest,'auxiliary_assets':[],'environment':base['environment'],'runtime_config_sha256':spec['identity']['runtime_config_sha256'],'effective_options':row['effective_options']}
   command=[str(fixture),profile,*[x['path'] for x in configs]];log=pack/(mode+'.log');safe()
   with log.open('xb') as stream:
    proc=subprocess.Popen(command,cwd=pack,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True,env=dict(os.environ,**base['environment']));pid=process_identity(proc.pid);start=time.monotonic();peak=0
    while proc.poll() is None:
     safe();peak=max(peak,process_tree_rss(proc.pid));require(peak<4*2**30 and time.monotonic()-start<180 and log.stat().st_size<128*2**20,'Affected check resource/time cap');time.sleep(.2)
   require(proc.returncode==0,'Independent affected check failed');text=log.read_text();producer_log=next(v['log'] for v in handoff['replay'] if mode in Path(v['log']).name);require(native_options(text)==native_options(Path(producer_log).read_text()),'Actual native full options differ')
   dump=validate_runtime_dump(log,spec);markers=[x for x in text.splitlines() if x.startswith('L3_PRODUCTION_PASS|')];require(len(markers)==1,'No exact native close marker');values=dict(v.split('=',1) for v in markers[0].split('|')[1:])
   if profile=='WAD256_Q4':
    boundary=[dict(v.split('=',1) for v in x.split('|')[1:]) for x in text.splitlines() if x.startswith('L3_WAD_BOUNDARY_PASS|')]
    require(len(boundary)==1 and all(boundary[0][k]==v for k,v in {'cap':'256','live':'256','lower_accepted_data_released':'256','set_done':'0','257th_refused_before_mutation':'1','same_address_blocked':'1','physical_payload_slots':'1168'}.items()),'Actual WAD256 boundary absent')
    for k,v in {'regime':profile,'mode':'2' if mode=='U_WB16' else '1','exact_once':'1282','real_set_done':'257','WAD_drained':'1','data_before_control_release':'1','resident_read_after_WB_drain':'1','evicted_WB_UID_snapshots':'256','max_bank_ops':'1','native_detailed_dram':'1','dram_hold_fixture_only':'1'}.items():require(values[k]==v,'Incomplete actual WAD closure '+k)
    rops=[]
   else:
    for k,v in {'regime':profile,'mode':'2' if mode=='U_WB16' else '1','exact_once':'40','wb_lower_accept_and_set_done':'5','two_dirty_sector_versions':'1','cold_sectors':'2','subpartitions_exercised':'2','credit_drained':'1','bank_max_ops_per_physical_cycle':'1','fixed_delay_gpu_cycles':'100','fixed_delay_verified':'1','runtime_archives_unchanged':'1'}.items():require(values[k]==v,'Incomplete actual production marker '+k)
    if profile=='ICNT2_H0':
     noc=[dict(v.split('=',1) for v in x.split('|')[1:]) for x in text.splitlines() if x.startswith('L3_ICNT_LOCAL_XBAR_PASS|')];require(len(noc)==1 and all(noc[0][k]==v for k,v in {'network_mode':'2','bidirectional_packets':'20','exact_once':'1','drained':'1'}.items()),'Actual local crossbar bidirectional completion/drain missing')
    rops=[dict(v.split('=',1) for v in x.split('|')[1:]) for x in text.splitlines() if x.startswith('L3_ROP_READY|')];require(len(rops)==40 and all(int(x['delta'])>= (40 if profile=='ROP40_H0' else 160) for x in rops) and min(int(x['delta']) for x in rops)==(40 if profile=='ROP40_H0' else 160),'Actual ROP ready timing differs')
   tests.append({'status':'PASS','mode':mode,'command':command,'process':pid,'log':str(log),'log_sha256':digest(log),'peak_rss_bytes':peak,'actual_runtime':dump,'actual_marker':values,'ROP_minimum_delay_verified_events':len(rops),'ROP_delta_histogram':dict(__import__('collections').Counter(x['delta'] for x in rops))});proc=None
  for path,sha in build['archives_sha256'].items():require(digest(path)==sha,'Native archive changed during independent replay')
 finally:
  if proc is not None:terminate_owned(proc)
  if lease:r.release_build(lease,'lane5')
  write_json(pack/'INDEPENDENT_AFFECTED.json',{'tests':tests,'status':'PASS' if len(tests)==2 else 'FAILED_RETAIN_ALL','lease':lease,'lease_released':bool(lease),'full_applications':0,'compiler_started':False})
 evidence=[{'path':str(p),'sha256':digest(p)} for p in sorted(pack.iterdir()) if p.is_file()]
 review={'status':'INDEPENDENT_CONFIG_PASS','coordination_commit':PARALLEL_COORDINATION,'experiment_id':PARALLEL_EXPERIMENT,'regime':profile,'identity':m['identity'],'modes':modes,'evidence':evidence,'spec_paths':specpaths,'producer_owner':'lane3','producer_publication':pub,'producer_publication_verified':True,'independent_affected_production_pass':True,'independent_affected_executions':2,'canonical_base_normalization':'Producer config4 bytes differ in comments from accepted original; full native options equal. Lane5 restores exact5-layer H0 bytes and independently executes these exact normalized configs plus official overlay. New config hashes reflect actual ordered bytes.','scope':'One real partition/two subpartitions; no64slice application PASS yet. Original11 gates reused only same exact runtime/source/input scope. Full native input/64slice closure remains mandatory.'};write_json(pack/'INDEPENDENT_CONFIG_REVIEW.json',review)
 q=copy.deepcopy(json.loads((H/'R19_D4_INDEPENDENTLY_QUALIFIED_r1.json').read_text()));q.update(release_name='PARALLEL_'+profile+'_INDEPENDENTLY_QUALIFIED_r1',downstream_producer_publication=pub,downstream_config_qualification={'path':str(pack/'INDEPENDENT_CONFIG_REVIEW.json'),'sha256':digest(pack/'INDEPENDENT_CONFIG_REVIEW.json')});write_json(qpath,q);freeze_checksums(pack)
 print(json.dumps({'profile':profile,'status':'INDEPENDENT_CONFIG_PASS','tests':len(tests),'specs':len(specpaths),'new_application_starts':0}))
if __name__=='__main__':main()
