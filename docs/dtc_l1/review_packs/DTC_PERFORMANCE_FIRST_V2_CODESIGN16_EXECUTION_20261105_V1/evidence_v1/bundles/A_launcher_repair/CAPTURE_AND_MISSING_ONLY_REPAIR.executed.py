from pathlib import Path
import json,hashlib,os,gzip,datetime,subprocess,ast
R=Path('/root/data/dtc_perf_first_v2_codesign16_20261105_v1');V1=Path('/root/data/dtc_perf_first_remaining28_20261104_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1');O=A/'engineering_incidents/launcher_runtime_missing_v1';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
 p=Path(p);v=dict(path=str(p),lexists=os.path.lexists(p),exists=p.exists(),symlink=p.is_symlink())
 if p.is_symlink():v['link_target']=os.readlink(p)
 if p.exists():v['actual_realpath']=str(p.resolve());v['device']=p.stat().st_dev;v['mode']=oct(p.stat().st_mode&0o777);v['bytes']=p.stat().st_size;v['sha256']=sha(p)if p.is_file()else None
 return v
base=Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py');lines=base.read_text().splitlines();source=dict(path=str(base),sha256=sha(base),first_line=162,last_line=179,text='\n'.join(f'{n}: {lines[n-1]}'for n in range(162,180)))
launch=[];done=[];raw=[]
for dp in sorted((R/'control/qualification_ledger').glob('*.DONE.json')):
 d=json.loads(dp.read_text());done.append(dict(path=str(dp),sha256=sha(dp),cohort=d['cohort'],uuid=d['uuid'],native_simulator_observed=d['native_simulator_observed'],launcher_wait_returncode=d['launcher_wait_returncode'],stop_reason=d['stop_reason']))
 out=Path(d['output']);lp=out/'NATIVE_LAUNCH.json'
 if lp.exists():
  j=json.loads(lp.read_text());launch.append(dict(path=str(lp),sha256=sha(lp),argv=j['argv'],cohort=d['cohort'],uuid=d['uuid']))
 rp=out/'raw.log.gz'
 if rp.exists():
  assert rp.stat().st_size<4096
  content=gzip.decompress(rp.read_bytes());assert len(content)<4096;raw.append(dict(path=str(rp),sha256=sha(rp),text=content.decode(errors='replace'),native_PID_MAP_exists=(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').exists(),cohort=d['cohort']))
assert len(done)==16 and all(d['native_simulator_observed']is False and d['launcher_wait_returncode']==127 for d in done)
fixed=[]
for p in sorted((R/'control/specs').glob('*.json')):fixed.append(dict(path=str(p),sha256=sha(p)))
for p in [R/'tools/perf16_native.py',R/'tools/perf16_ops.py',R/'control/EXECUTION_PLAN.json',R/'control/BUILD_PROFILE.json',R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',R/'control/SCIENCE_AUTHORIZATION.json']:
 fixed.append(dict(path=str(p),sha256=sha(p)))
first=json.loads(Path(fixed[0]['path']).read_text());model=Path(first['native_simulator_argv'][0]);fixed.append(dict(path=str(model),sha256=sha(model)))
libs=[info(p)for p in sorted((V1/'tools/lib').iterdir())];binary=info(V1/'tools/bin/strace')
plan=[]
for rel in ['tools/bin','tools/lib']:
 dst=R/rel;src=V1/rel;target=src.resolve();assert src.is_symlink()and target.is_dir();plan.append(dict(destination=str(dst),before=info(dst),reference=info(src),intended_link_target=str(target)))
(O/'BEFORE_REPAIR_EVIDENCE.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),classification='CHARGED_LAUNCHER_START_FAILURE_MODEL_NOT_OBSERVED',rootcause='new root omitted tools/bin and tools/lib; spec runtime_files and prepare checked model dependencies but not launcher dependency closure',launcher_source=source,actual_closed_done=done,actual_launches=launch,closed_small_raw=raw,missing_layout=plan,reference_strace=binary,reference_tracer_libs=libs,fixed_assets_to_preserve=fixed,all16_consumed_not_refundable=True,no_same_identity_retry=True),indent=2)+'\n')
# User/Root-authorized missing-only layout repair. No source/spec/ledger overwrite.
created=[]
for row in plan:
 dst=Path(row['destination']);target=Path(row['intended_link_target'])
 if os.path.lexists(dst):assert dst.is_symlink()and dst.resolve()==target,'EXISTING_UNEXPECTED_LAYOUT_DO_NOT_REPLACE'
 else:dst.symlink_to(target,target_is_directory=True);created.append(info(dst))
for item in fixed:assert sha(item['path'])==item['sha256'],'FIXED_SCIENTIFIC_OR_PINNED_ASSET_CHANGED'
assert sha(R/'tools/bin/strace')==binary['sha256']
for lib in libs:assert sha(R/'tools/lib'/Path(lib['path']).name)==lib['sha256']
(O/'LAYOUT_REPAIR_RECORD.json').write_text(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),created_symlinks=created,links=[info(R/rel)for rel in ['tools/bin','tools/lib']],same_legacy_launcher_byte_identity=True,fixed_assets_preserved=True,model_starts=0,scientific_identity_retries=0,registry_or_plan_writes=0,reference_assets_or_modes_modified=False),indent=2)+'\n')
print(json.dumps(dict(created=[x['path']for x in created],strace_SHA=binary['sha256'],tool_libs=len(libs),original16launcher127=len(done),closed_raw_read_n=len(raw),model_binary_SHA=sha(model),scientific_retries=0)))
