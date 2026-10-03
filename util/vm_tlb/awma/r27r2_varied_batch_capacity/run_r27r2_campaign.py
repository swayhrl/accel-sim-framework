#!/usr/bin/env python3
"""Process runner for R27R2 varied-input qualification/capacity/trajectory."""
from __future__ import annotations
import argparse,json,math,os,time,traceback
from pathlib import Path
import torch
from component import VariedTiedWeightTrainer,r26,sha,tsha,BANK_SHA

ATOL=RTOL=1e-2
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def clean(x):return {k:v for k,v in x.items() if k!='diagnostic_tensors'}
def load(p):return torch.load(p,map_location='cpu',weights_only=False)
def passed(m):return all(v.get('allclose',False) and v.get('finite',False) for v in m.values())
def compare(g,r,names):
 out={}
 for n in names:
  if n in ('loss','next_loss'):out[n]=r26.scalar_metrics(float(g[n]),float(r[n]))
  elif n in ('step','stream_cursor'):
   d=abs(int(g[n])-int(r[n]));out[n]={'observed':g[n],'reference':r[n],'max_abs':d,'mean_abs':d,'max_rel':0.0,'cosine_similarity':1.0,'finite':True,'allclose':d==0,'shape':[],'dtype':'int'}
  else:out[n]=r26.tensor_metrics(g[n],r[n])
 return out
def state_obs(s):return {'weight':s['weight'],'m':s['m'],'v':s['v'],'step':s['step'],'stream_cursor':s['stream_cursor']}

def trainer(a,batch=1,checkpoint=None):return VariedTiedWeightTrainer(a.model,a.bank,batch,a.legacy_tokens,common_path=None if checkpoint else a.common,checkpoint=checkpoint)

def mode_qualify(a):
 root=Path(a.root);tmp=root/'checkpoints/b1_reference_temp';tmp.mkdir(parents=True,exist_ok=True);t=trainer(a);refs=[]
 for idx in range(4):
  x=t.run_stream_step('b0',index=idx,diagnostic=True);n=t.next_loss_at(idx+1);s,rec=t.save_checkpoint(tmp/f'b0_k{idx+1}.pt','b0');torch.save(x['diagnostic_tensors'],tmp/f'b0_diag_k{idx+1}.pt');refs.append({'loss':x['loss'],'next_loss':n,'step':t.step,'stream_cursor':t.stream_cursor,'state_receipt':rec});del x,s
 details={};first=None;c1_checkpoint=None
 for policy in ('c1','s2'):
  t.restore_common(a.common);rows=[]
  for idx in range(4):
   x=t.run_stream_step(policy,index=idx,diagnostic=True);n=t.next_loss_at(idx+1);got=t.snapshot_cpu(policy);ref=load(tmp/f'b0_k{idx+1}.pt');dref=load(tmp/f'b0_diag_k{idx+1}.pt')
   go={'loss':x['loss'],'next_loss':n,'dH':x['diagnostic_tensors']['dH'],'gradient':x['diagnostic_tensors']['gradient'],**state_obs(got)};ro={'loss':refs[idx]['loss'],'next_loss':refs[idx]['next_loss'],'dH':dref['dH'],'gradient':dref['gradient'],**state_obs(ref)};m=compare(go,ro,tuple(go));ok=passed(m);rows.append({'trajectory_index':idx+1,'bank_index':idx,'qualified':ok,'metrics':m,'input_ids_sha256':x['input_ids_sha256'],'labels_sha256':x['labels_sha256']})
   if first is None and not ok:first={'policy':policy,'trajectory_index':idx+1,'metrics':{k:v for k,v in m.items() if not v['allclose'] or not v['finite']}}
   if policy=='c1' and idx==1:
    _,c1_checkpoint=t.save_checkpoint(root/'checkpoints/B1_C1_K2.pt','c1')
   del x,got,ref,dref,go,ro
  details[policy]=rows
 qualified=all(x['qualified'] for p in details.values() for x in p)
 out={'status':'PASS' if qualified else 'FAIL','qualified':qualified,'tolerance':{'rtol':RTOL,'atol':ATOL},'details':details,'first_mismatch':first,'c1_switch_checkpoint':c1_checkpoint,'common_migration':t.migration,'continuous_steps_per_lineage':4}
 dump(root/'raw/B1_NUMERICAL_QUALIFICATION.json',out)
 for p in tmp.glob('*'):p.unlink()
 tmp.rmdir();t.close()
 if not qualified:raise RuntimeError('R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','B1_steps':4},sort_keys=True))

def mode_resume_switch(a):
 root=Path(a.root);src=root/'checkpoints/B1_C1_K2.pt';t=trainer(a,checkpoint=str(src));loaded={'step':t.step,'cursor':t.stream_cursor,'tied':True};c1=t.run_stream_step('c1',diagnostic=True);c1n=t.next_loss_at(3);c1s=t.snapshot_cpu('c1');t.load_checkpoint(src);s2=t.run_stream_step('s2',diagnostic=True);s2n=t.next_loss_at(3);s2s=t.snapshot_cpu('s2')
 go={'loss':s2['loss'],'next_loss':s2n,'dH':s2['diagnostic_tensors']['dH'],'gradient':s2['diagnostic_tensors']['gradient'],**state_obs(s2s)};ro={'loss':c1['loss'],'next_loss':c1n,'dH':c1['diagnostic_tensors']['dH'],'gradient':c1['diagnostic_tensors']['gradient'],**state_obs(c1s)};m=compare(go,ro,tuple(go));ok=passed(m) and loaded=={'step':3,'cursor':2,'tied':True}
 dump(root/'raw/B1_CHECKPOINT_SWITCH_QUALIFICATION.json',{'qualified':ok,'source':str(src),'source_sha256':sha(src),'fresh_process_load':loaded,'final_step':t.step,'final_cursor':t.stream_cursor,'metrics':m});t.close()
 if not ok:raise RuntimeError('R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','fresh_load':True,'switch':True},sort_keys=True))

def mode_probe(a):
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True);started=time.time();t=None;phase='MODEL_BANK_COMMON_LOAD'
 try:
  t=trainer(a,a.batch);steps=[];post=None
  for idx in range(5):
   phase='TRAIN_STEP';x=t.run_stream_step(a.policy,index=idx);phase='FINITE_CHECK';finite,name,row=t.finite_state();growth=None if post is None else x['post_step_allocated_bytes']-post;post=x['post_step_allocated_bytes'];x.update({'trial_step':idx+1,'bank_index':idx,'warmup_designation':idx<2,'finite_state':finite,'finite_failure_tensor':name,'finite_failure_row':row,'transient_active_growth_bytes':growth});
   if not math.isfinite(x['loss']) or not finite or t.step!=idx+2 or t.stream_cursor!=idx+1:raise RuntimeError('probe invariant')
   steps.append(clean(x));print(json.dumps({'progress':'probe','policy':a.policy,'batch':a.batch,'step':idx+1}),flush=True)
  value={'status':'PASS','outcome':'PASS','policy':a.policy,'batch':a.batch,'five_complete_steps':True,'start_step':1,'final_step':t.step,'final_cursor':t.stream_cursor,'steps':steps,'bank_sha256':BANK_SHA,'common_sha256':'09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55','elapsed_seconds':time.time()-started,'pid':os.getpid(),'lock_sentinel':os.environ.get('R27R2_GPU_LOCK_HELD')};dump(out,value);t.close();print(json.dumps({'outcome':'PASS','policy':a.policy,'batch':a.batch},sort_keys=True))
 except torch.cuda.OutOfMemoryError as e:
  free=total=alloc=reserved=None
  try:free,total=torch.cuda.mem_get_info();alloc=torch.cuda.memory_allocated();reserved=torch.cuda.memory_reserved()
  except Exception:pass
  value={'status':'OOM','outcome':'OOM','policy':a.policy,'batch':a.batch,'oom_phase':getattr(t,'phase',phase) if t else phase,'error':repr(e),'traceback':traceback.format_exc(),'free_bytes':free,'total_bytes':total,'allocated_bytes':alloc,'reserved_bytes':reserved,'elapsed_seconds':time.time()-started,'pid':os.getpid(),'bank_sha256':BANK_SHA,'common_sha256':'09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55'};dump(out,value);print(json.dumps({'outcome':'OOM','policy':a.policy,'batch':a.batch,'phase':value['oom_phase']},sort_keys=True))
 except Exception as e:
  dump(out,{'status':'ERROR','outcome':'UNKNOWN','policy':a.policy,'batch':a.batch,'phase':getattr(t,'phase',phase) if t else phase,'error':repr(e),'traceback':traceback.format_exc()});raise

def mode_common_numeric(a):
 root=Path(a.root);t=trainer(a,a.batch);c=t.run_stream_step('c1',index=0,diagnostic=True);cn=t.next_loss_at(1);cs=t.snapshot_cpu('c1');t.restore_common(a.common);s=t.run_stream_step('s2',index=0,diagnostic=True);sn=t.next_loss_at(1);ss=t.snapshot_cpu('s2');go={'loss':s['loss'],'next_loss':sn,'dH':s['diagnostic_tensors']['dH'],'gradient':s['diagnostic_tensors']['gradient'],**state_obs(ss)};ro={'loss':c['loss'],'next_loss':cn,'dH':c['diagnostic_tensors']['dH'],'gradient':c['diagnostic_tensors']['gradient'],**state_obs(cs)};m=compare(go,ro,tuple(go));ok=passed(m);dump(root/'raw/COMMON_BATCH_NUMERICAL.json',{'batch':a.batch,'qualified':ok,'metrics':m});t.close();
 if not ok:raise RuntimeError('R27R2_NUMERIC_OR_STATE_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','batch':a.batch},sort_keys=True))

def mode_common_trajectory(a):
 root=Path(a.root);ck=root/'checkpoints/common_trajectory';tmp=ck/'temp';tmp.mkdir(parents=True,exist_ok=True);t=trainer(a,a.batch);cscalar=[];crec={}
 for idx in range(32):
  x=t.run_stream_step('c1',index=idx);n=t.next_loss_at(idx+1);cscalar.append({'trajectory_index':idx+1,'loss':x['loss'],'next_loss':n,'step':t.step,'cursor':t.stream_cursor,'input_ids_sha256':x['input_ids_sha256'],'labels_sha256':x['labels_sha256'],'memory':clean(x)});k=idx+1
  if k in (1,4,8,16,32):
   path=(ck if k in (16,32) else tmp)/f'c1_k{k}.pt';state,rec=t.save_checkpoint(path,'c1');crec[str(k)]=rec;del state
  print(json.dumps({'progress':'common_c1','k':k}),flush=True)
 t.restore_common(a.common);comparisons=[];srec={};first=None
 for idx in range(32):
  x=t.run_stream_step('s2',index=idx);n=t.next_loss_at(idx+1);k=idx+1;m={'loss':r26.scalar_metrics(x['loss'],cscalar[idx]['loss']),'next_loss':r26.scalar_metrics(n,cscalar[idx]['next_loss']),'step':compare({'step':t.step},{'step':cscalar[idx]['step']},('step',))['step'],'stream_cursor':compare({'stream_cursor':t.stream_cursor},{'stream_cursor':cscalar[idx]['cursor']},('stream_cursor',))['stream_cursor']}
  if k in (1,4,8,16,32):
   got=t.snapshot_cpu('s2');ref=load((ck if k in (16,32) else tmp)/f'c1_k{k}.pt');m.update(r26.state_metrics(got,ref))
   if k in (16,32):
    path=ck/f's2_k{k}.pt';torch.save(got,path);srec[str(k)]={'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'step':got['step'],'stream_cursor':got['stream_cursor'],'weight_sha256':tsha(got['weight']),'m_sha256':tsha(got['m']),'v_sha256':tsha(got['v'])}
   del got,ref
  ok=passed(m);comparisons.append({'trajectory_index':k,'qualified':ok,'metrics':m,'input_ids_sha256':x['input_ids_sha256'],'labels_sha256':x['labels_sha256'],'memory':clean(x)});
  if first is None and not ok:first={'trajectory_index':k,'metrics':{z:q for z,q in m.items() if not q['allclose'] or not q['finite']}}
  print(json.dumps({'progress':'common_s2','k':k,'qualified':ok}),flush=True)
 qualified=all(x['qualified'] for x in comparisons) and t.step==33 and t.stream_cursor==32;dump(root/'raw/COMMON_32_STEP_TRAJECTORY.json',{'qualified':qualified,'batch':a.batch,'c1_scalars':cscalar,'comparisons':comparisons,'c1_checkpoints':crec,'s2_checkpoints':srec,'first_mismatch':first,'final_step':t.step,'final_cursor':t.stream_cursor})
 for p in tmp.glob('*'):p.unlink()
 tmp.rmdir();t.close()
 if not qualified:raise RuntimeError('R27R2_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','common_steps':32},sort_keys=True))

def mode_common_resume(a):
 root=Path(a.root);ck=root/'checkpoints/common_trajectory';src=ck/f'{a.policy}_k16.pt';refp=ck/f'{a.policy}_k32.pt';t=trainer(a,a.batch,checkpoint=str(src));sc=[]
 for idx in range(16,32):x=t.run_stream_step(a.policy,index=idx);n=t.next_loss_at(idx+1);sc.append({'trajectory_index':idx+1,'loss':x['loss'],'next_loss':n,'step':t.step,'cursor':t.stream_cursor});print(json.dumps({'progress':f'resume_{a.policy}','k':idx+1}),flush=True)
 got,rec=t.save_checkpoint(ck/f'{a.policy}_resumed_k32.pt',a.policy);ref=load(refp);m=r26.state_metrics(got,ref);m['stream_cursor']=compare({'stream_cursor':got['stream_cursor']},{'stream_cursor':ref['stream_cursor']},('stream_cursor',))['stream_cursor'];traj=json.loads((root/'raw/COMMON_32_STEP_TRAJECTORY.json').read_text());last=traj['c1_scalars'][-1] if a.policy=='c1' else traj['comparisons'][-1];ref_loss=last['loss'] if a.policy=='c1' else last['metrics']['loss']['observed'];ref_next=last['next_loss'] if a.policy=='c1' else last['metrics']['next_loss']['observed'];m['loss']=r26.scalar_metrics(sc[-1]['loss'],ref_loss);m['next_loss']=r26.scalar_metrics(sc[-1]['next_loss'],ref_next);ok=passed(m) and t.step==33 and t.stream_cursor==32;dump(root/f'raw/COMMON_RESUME_{a.policy.upper()}.json',{'qualified':ok,'policy':a.policy,'source':str(src),'source_sha256':sha(src),'reference':str(refp),'reference_sha256':sha(refp),'resumed':rec,'metrics':m,'final_step':t.step,'final_cursor':t.stream_cursor});t.close();
 if not ok:raise RuntimeError('R27R2_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','policy':a.policy},sort_keys=True))

def mode_common_switch(a):
 root=Path(a.root);src=root/'checkpoints/common_trajectory/c1_k16.pt';t=trainer(a,a.batch,checkpoint=str(src));c=t.run_stream_step('c1',index=16,diagnostic=True);cn=t.next_loss_at(17);cs=t.snapshot_cpu('c1');t.load_checkpoint(src);s=t.run_stream_step('s2',index=16,diagnostic=True);sn=t.next_loss_at(17);ss=t.snapshot_cpu('s2');go={'loss':s['loss'],'next_loss':sn,'dH':s['diagnostic_tensors']['dH'],'gradient':s['diagnostic_tensors']['gradient'],**state_obs(ss)};ro={'loss':c['loss'],'next_loss':cn,'dH':c['diagnostic_tensors']['dH'],'gradient':c['diagnostic_tensors']['gradient'],**state_obs(cs)};m=compare(go,ro,tuple(go));ok=passed(m);dump(root/'raw/COMMON_POLICY_SWITCH.json',{'qualified':ok,'source':str(src),'source_sha256':sha(src),'metrics':m,'final_step':t.step,'final_cursor':t.stream_cursor});t.close();
 if not ok:raise RuntimeError('R27R2_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','switch':True},sort_keys=True))

def mode_witness_trajectory(a):
 root=Path(a.root);ck=root/'checkpoints/witness_s2';ck.mkdir(parents=True,exist_ok=True);t=trainer(a,a.batch);steps=[];post=None;receipts={}
 for idx in range(32):
  x=t.run_stream_step('s2',index=idx);n=t.next_loss_at(idx+1);finite,name,row=t.finite_state();growth=None if post is None else x['post_step_allocated_bytes']-post;post=x['post_step_allocated_bytes'];steps.append({'trajectory_index':idx+1,'loss':x['loss'],'next_loss':n,'step':t.step,'cursor':t.stream_cursor,'finite':finite,'failure_tensor':name,'failure_row':row,'growth':growth,'input_ids_sha256':x['input_ids_sha256'],'labels_sha256':x['labels_sha256'],'memory':clean(x)});k=idx+1
  if k in (16,32):state,rec=t.save_checkpoint(ck/f's2_k{k}.pt','s2');receipts[str(k)]=rec;del state
  if not finite:raise RuntimeError('witness nonfinite')
  print(json.dumps({'progress':'witness_s2','k':k}),flush=True)
 ok=t.step==33 and t.stream_cursor==32 and all(x['finite'] for x in steps);dump(root/'raw/WITNESS_S2_32_STEP.json',{'qualified':ok,'batch':a.batch,'steps':steps,'checkpoints':receipts,'final_step':t.step,'final_cursor':t.stream_cursor});t.close();
 if not ok:raise RuntimeError('R27R2_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','witness_steps':32},sort_keys=True))

def mode_witness_resume(a):
 root=Path(a.root);ck=root/'checkpoints/witness_s2';src=ck/'s2_k16.pt';refp=ck/'s2_k32.pt';t=trainer(a,a.batch,checkpoint=str(src));sc=[]
 for idx in range(16,32):x=t.run_stream_step('s2',index=idx);n=t.next_loss_at(idx+1);finite,name,row=t.finite_state();sc.append({'k':idx+1,'loss':x['loss'],'next_loss':n,'finite':finite,'step':t.step,'cursor':t.stream_cursor});print(json.dumps({'progress':'witness_resume','k':idx+1}),flush=True)
 got,rec=t.save_checkpoint(ck/'s2_resumed_k32.pt','s2');ref=load(refp);m=r26.state_metrics(got,ref);m['stream_cursor']=compare({'stream_cursor':got['stream_cursor']},{'stream_cursor':ref['stream_cursor']},('stream_cursor',))['stream_cursor'];raw=json.loads((root/'raw/WITNESS_S2_32_STEP.json').read_text());m['loss']=r26.scalar_metrics(sc[-1]['loss'],raw['steps'][-1]['loss']);m['next_loss']=r26.scalar_metrics(sc[-1]['next_loss'],raw['steps'][-1]['next_loss']);ok=passed(m) and all(x['finite'] for x in sc) and t.step==33 and t.stream_cursor==32;dump(root/'raw/WITNESS_S2_RESUME.json',{'qualified':ok,'batch':a.batch,'source':str(src),'source_sha256':sha(src),'reference':str(refp),'reference_sha256':sha(refp),'resumed':rec,'metrics':m,'final_step':t.step,'final_cursor':t.stream_cursor});t.close();
 if not ok:raise RuntimeError('R27R2_EXTENDED_CAPACITY_TRAJECTORY_NOT_QUALIFIED')
 print(json.dumps({'status':'PASS','witness_resume':True},sort_keys=True))

def args():
 p=argparse.ArgumentParser();p.add_argument('--mode',required=True,choices=('qualify','resume_switch','probe','common_numeric','common_trajectory','common_resume','common_switch','witness_trajectory','witness_resume'));p.add_argument('--root',required=True);p.add_argument('--model',required=True);p.add_argument('--bank',required=True);p.add_argument('--legacy-tokens',required=True);p.add_argument('--common',required=True);p.add_argument('--policy',choices=('c1','s2'));p.add_argument('--batch',type=int,default=1);p.add_argument('--output');a=p.parse_args();
 if a.mode in ('probe','common_resume') and not a.policy:p.error('--policy required')
 if a.mode=='probe' and not a.output:p.error('--output required')
 return a
if __name__=='__main__':
 a=args()
 try:globals()[f'mode_{a.mode}'](a)
 except Exception as e:dump(Path(a.root)/'raw/failures'/f'{a.mode}_{a.policy or "na"}_B{a.batch}_{int(time.time())}.json',{'mode':a.mode,'policy':a.policy,'batch':a.batch,'error':repr(e),'traceback':traceback.format_exc()});raise
