#!/usr/bin/env python3
"""One-shot final EXT1 scientific receipt publication after accepted archive closure."""
import datetime,hashlib,json,shutil,subprocess
from pathlib import Path
P=Path
R=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
N=P('/root/data/ep_l2_dtc_l1_native_v2')
REVIEW=R/'review'
BRANCH='hrl/ep-l2-optional-clean128-exact5-20261109-v1'
DEST=REVIEW/'docs/ep_l2/operations/ep_l2_optional_clean128_exact5_execution_20261109_v1/phase_v1/final_ext1_v1'
REQ='EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1'
CASE='EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1'
OLD={0:'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',2:'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'}
OPTION='-gpgpu_ep_l2_victim_extension'
def sha(p):
 h=hashlib.sha256()
 with P(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(REVIEW),*args],text=True).strip()
def read(p):return json.loads(P(p).read_bytes())
def main():
 assert git('branch','--show-current')==BRANCH and git('status','--porcelain')==''
 assert git('ls-remote','origin','refs/heads/'+BRANCH).split()[0]==git('rev-parse','HEAD')
 reg=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
 q=reg['registered_future_requests'][REQ]
 assert q['budget']==1 and q['remaining']==0 and set(q['consumed'])=={CASE}
 row=q['consumed'][CASE];assert row['state']=='CLOSED_ACCEPTED'
 assert row['consumed']==1 and CASE not in read(R/'control/DISPATCH_CLAIMS.json')['claims']
 monitor=read(R/'control/EXT1_BACKGROUND_MONITOR_STATUS.json')
 assert monitor['status']=='ACCEPT_ARCHIVE_COMMAND_FINISHED' and monitor['returncode']==0
 assert monitor['registry_state']=='CLOSED_ACCEPTED' and monitor['uuid']==row['uuid']
 out=P(row['output']);point=out/'ACCEPTED_POINT.json';done=out/'NATIVE_EXIT.json';validation=out/'VALIDATED_APPLICATION_BUNDLE.json'
 receipt=R/'cases'/CASE/'control/ARCHIVE_RECEIPT.json'
 p=read(point);d=read(done);a=read(receipt);v=read(validation)
 assert p['cohort']==CASE and p['uuid']==d['uuid']==a['uuid']==row['uuid']
 assert p['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED' and d['launcher_wait_returncode']==0 and d['stop_reason'] is None
 assert d['new_attempt_consumed']==1 and sha(validation)==p['validation_ref']['sha256']
 spec=R/'cases'/CASE/'control/FROZEN_SPEC.json';new_spec=read(spec)
 assert sha(spec)==p['spec_ref']['sha256']
 assert v['status']=='EP_FULL_PERF_VALIDATED_PENDING_MAIN_NOT_APPLICATION_ACCEPTED'
 assert v['application']['actual_options']==new_spec['expected_effective_options']
 assert len(v['application']['actual_options'])==283
 assert a['status']=='TRUE164_RESULT_SHA_AND_TWO_NATIVE_TARGET_RESTORES_PASS' and len(a['native_restores'])==2
 assert len({z['target'] for z in a['native_restores']})==2
 assert all(z['status']=='INDEPENDENT_NATIVE_TARGET_COMPLETE_SHA_RESTORE_PASS' for z in a['native_restores'])
 manifest=P(a['manifest_ref']['path']);archive=P(a['archive_ref']['path'])
 assert sha(manifest)==a['manifest_ref']['sha256'] and sha(archive)==a['archive_ref']['sha256']
 assert a['source_keep'] is True and p['source_keep'] is True
 old_q=reg['registered_future_requests']['EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1']
 evidence={1:(p,new_spec,v,point,spec,validation)}
 for mode,case in OLD.items():
  old_row=old_q['consumed'][case]
  assert old_row['state']=='CLOSED_ACCEPTED' and old_row['consumed']==1
  old_out=P(old_row['output']);old_point=old_out/'ACCEPTED_POINT.json'
  old_spec=R/'cases'/case/'control/FROZEN_SPEC.json'
  old_validation=old_out/'VALIDATED_APPLICATION_BUNDLE.json'
  op,os,ov=read(old_point),read(old_spec),read(old_validation)
  assert op['status']=='EP_FULL_PERF_APPLICATION_ACCEPTED' and op['uuid']==old_row['uuid']
  assert sha(old_spec)==op['spec_ref']['sha256'] and sha(old_validation)==op['validation_ref']['sha256']
  assert ov['application']['actual_options']==os['expected_effective_options']
  evidence[mode]=(op,os,ov,old_point,old_spec,old_validation)
 base=evidence[0][1]['expected_effective_options']
 for mode,(ep,es,ev,_,__,___) in evidence.items():
  assert ep['source_identity']==p['source_identity']==es['source_identity']
  assert ep['input_identity_sha256']==p['input_identity_sha256']==es['input_identity_sha256']
  assert (ep['profile'],ep['mode'],ep['kernel_count'],ep['CTA'],ep['instructions'])==('REF32x8_L100','WV_ZERO_RO',100,6400,2193446000)
  assert ev['application']['ordered_kernel_catalog']==v['application']['ordered_kernel_catalog']
  options=es['expected_effective_options']
  assert len(options)==283 and set(options)==set(base) and options[OPTION]==str(mode)
  assert {k for k in options if options[k]!=base[k]}==({OPTION} if mode else set())
 phase_dir=R/'documents/EXT1_TRIPLET_PHASE_20261110_V1'
 if not phase_dir.exists():
  subprocess.check_call(['/usr/bin/python3','-B',str(R/'runtime/analyze_stencil_triplet.py')],
                        cwd='/root/workspace',timeout=3600)
 phase=read(phase_dir/'TRIPLET_PHASE_EVIDENCE.json')
 assert phase['schema']=='EP_L2_STENCIL_EXT012_PHASE_COMPARISON_V1'
 assert phase['cycles']=={'EXT0':evidence[0][0]['cycles'],'EXT1':p['cycles'],'EXT2':evidence[2][0]['cycles']}
 assert phase['source_identity']==p['source_identity'] and phase['input_identity_sha256']==p['input_identity_sha256']
 assert len(phase['rows'])==100
 assert not DEST.exists();DEST.mkdir(parents=True)
 for name,src in {'ACCEPTED_POINT.json':point,'NATIVE_EXIT.json':done,'FROZEN_SPEC.json':spec,
  'VALIDATED_APPLICATION_BUNDLE.json':validation,'ARCHIVE_RECEIPT.json':receipt,
  'ARCHIVE_MANIFEST.json':manifest,'BACKGROUND_MONITOR_STATUS.json':R/'control/EXT1_BACKGROUND_MONITOR_STATUS.json',
  'ACCEPT_ARCHIVE_LOG.txt':R/'control/EXT1_ACCEPT_ARCHIVE_20261110.log',
  'publish_ext1_final.py':R/'runtime/publish_ext1_final.py',
  'analyze_stencil_triplet.py':R/'runtime/analyze_stencil_triplet.py',
  'analyze_stencil_phase_ext1_base.py':R/'runtime/analyze_stencil_phase_ext1_base.py',
  'TRIPLET_PHASE_EVIDENCE.json':phase_dir/'TRIPLET_PHASE_EVIDENCE.json',
  'TRIPLET_PHASE_ROWS.csv':phase_dir/'TRIPLET_PHASE_ROWS.csv',
  'TRIPLET_PHASE_REPORT.md':phase_dir/'TRIPLET_PHASE_REPORT.md'}.items():shutil.copyfile(src,DEST/name)
 c0=evidence[0][0]['cycles'];c2=evidence[2][0]['cycles'];c1=p['cycles']
 assert c0==4768893 and c2==4786427
 summary={'schema':'EP_L2_STENCIL_EXT1_FINAL_SAME_SOURCE_COMPARISON_V1',
   'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request':REQ,'cohort':CASE,'uuid':row['uuid'],
   'source_identity':p['source_identity'],'input_identity_sha256':p['input_identity_sha256'],
   'actual_option_count':283,'only_option_difference':OPTION,'ordered_kernel_count':len(v['application']['ordered_kernel_catalog']),
   'cycles':{'EXT0':c0,'EXT1':c1,'EXT2':c2},
   'delta_cycles':{'EXT1_minus_EXT0_migration_bundle':c1-c0,
                   'EXT2_minus_EXT1_CLEAN_policy_bundle':c2-c1,
                   'EXT2_minus_EXT0_total':c2-c0},
   'accepted_point_sha256':sha(point),'archive_sha256':sha(archive),
   'native_restore_targets':[z['target'] for z in a['native_restores']],
   'application_numeric_output':'UNKNOWN','physical_PPA':'UNKNOWN','source_keep':True,
   'one_start_consumed':True,'automatic_retry':False}
 (DEST/'FINAL_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 audit={'schema':'EP_L2_EXT1_COMPARABILITY_AUDIT_V1','cases':{
   'EXT'+str(mode):{'cohort':ep['cohort'],'accepted_point_sha256':sha(epath),
     'frozen_spec_sha256':sha(spath),'validation_sha256':sha(vpath),'cycles':ep['cycles']}
   for mode,(ep,es,ev,epath,spath,vpath) in evidence.items()},
   'source_identity':p['source_identity'],'input_identity_sha256':p['input_identity_sha256'],
   'all_283_actual_options_match_frozen_specs':True,'only_option_difference':OPTION,
   'ordered_100_kernel_catalog_equal':True}
 (DEST/'COMPARABILITY_AUDIT.json').write_text(json.dumps(audit,indent=2,ensure_ascii=False)+'\n')
 decision=('CLEAN 策略包净改善；若整体仍比 EXT0 慢，下一轮优先审查迁移成本。' if c2<c1 else
           'CLEAN 策略包在此输入上净变慢，应停止同结构 CLEAN 扩点并先分析机制成本。' if c2>c1 else
           'CLEAN 策略包的应用 cycles 净差为零，后续先分析成本。')
 report=f'''# Stencil EXT1 单点最终回执\n\n新增单点 `{CASE}` 以 Source5、同一 Stencil 输入和完整 283 项实际配置完成一次正式消费，Native 状态 `CLOSED_ACCEPTED`，无重试和退款。三点的 Source、ELF、输入、100 个有序 kernel、6400 CTA 和 2,193,446,000 指令一致；283 项实际选项仅 `{OPTION}` 分别为 0/1/2。完整 raw 留在 174-new 执行根。真164 归档 SHA256 `{sha(archive)}`，并通过两个不同 Native 目标的独立完整恢复；Source KEEP。\n\n| 比较 | 应用 cycles | 净差 |\n|---|---:|---:|\n| EXT0 | {c0} | 基线 |\n| EXT1 | {c1} | EXT1−EXT0 = {c1-c0:+d} |\n| EXT2 | {c2} | EXT2−EXT1 = {c2-c1:+d} |\n\nEXT2−EXT0 = {c2-c0:+d} cycles。EXT1−EXT0 是扩展硬件迁移包的净效应；EXT2−EXT1 是同一扩展硬件下开启 CLEAN 策略包的净增量，包含查询、spill、占用和服务成本。{decision}这三个确定性单点不能把局部机制各自分解为独占关键路径周期，也不证明物理 PPA、能耗、数值 oracle 或跨负载收益；应用数值输出仍为 UNKNOWN。\n\n验收、归档、三点一致性及逐 kernel 阶段分析证据见同目录 JSON/CSV；固定 Host、启动身份和实时准入见相邻 `live_ext1_v1/`。\n'''
 (DEST/'README.md').write_text(report)
 manifest_index={str(z.relative_to(DEST)):sha(z) for z in DEST.rglob('*') if z.is_file()}
 (DEST/'EVIDENCE_INDEX.json').write_text(json.dumps(manifest_index,indent=2)+'\n')
 git('add',str(DEST.relative_to(REVIEW)))
 git('commit','-m','ep-l2: close accepted stencil ext1 with true164 restores')
 head=git('rev-parse','HEAD')
 git('push','origin','HEAD:refs/heads/'+BRANCH)
 assert git('ls-remote','origin','refs/heads/'+BRANCH).split()[0]==head
 assert git('status','--porcelain')==''
 print(json.dumps({'status':'EXT1_FINAL_REVIEW_PUBLISHED','commit':head,'readback':True,'cycles':summary['cycles'],'deltas':summary['delta_cycles']}))
if __name__=='__main__':main()
