"""Two strict Gaussian16 result branches; independent device counters are mandatory."""
import pathlib,json,hashlib,argparse
from gaussian16_observed_io_oracle_v1 import need,validate
FAN1='_Z4Fan1PfS_ii';FAN2='_Z4Fan2PfS_S_iii'
BINARY='50fad6fdc65b005af1384c83a1b825df405f7b894ed649b98ee145a0b7cd01d1'
SO='bd2723b387aef31343608440a76a0ccba6b276fc046f4e70f306f8f2ea2a8668'
def counters(path):
 expected={(1,FAN1,0x280),(2,FAN1,0x960),(3,FAN1,0x80),(3,FAN1,0x2e0),(3,FAN2,0x90),(3,FAN2,0x100),(3,FAN2,0x220),(3,FAN2,0x2e0)}
 pairs={};ends=[];calibration={};registered=set();ctx=None;phase=0;kid=1;eof=None
 rows=path.read_text().splitlines()
 for index,line in enumerate(rows):
  f=line.split('\t');need(eof is None,'record after observer EOF')
  if f[0]=='SITE_REGISTER':
   need(phase==0 and len(f)==6 and f[5]=='DEVICE_ATOMIC_INDEPENDENT_OF_TRACE_CHANNEL','static site register grammar/boundary')
   site=(int(f[2]),f[3],int(f[4],16));need(site in expected and site not in registered,'exact once all static CFI/EXIT sites')
   if ctx is None:ctx=f[1]
   need(int(ctx,16)>0 and f[1]==ctx,'all registered context stable');registered.add(site)
  elif f[0]=='LAUNCH':
   need(len(f)==10 and f[9]=='DEVICE_ATOMIC_INDEPENDENT_OF_TRACE_CHANNEL'and 1<=kid<=30,'actual independent device counter record')
   kind=phase+1;need(phase in(0,1)and int(f[1])==kid and int(f[4])==kind and int(f[6],16)==(0x280 if kind==1 else 0x960)and f[5]==FAN1,'ordered exact two CFI sites per launch')
   need((kind,FAN1,int(f[6],16))in registered and f[2]==ctx and f[3]==(FAN1 if kid%2 else FAN2),'registered site/source30 order/context')
   issues=int(f[7]);lanes=int(f[8]);need(0<=issues<=lanes<=32*issues,'effective lane issue relationship')
   pairs[(kid,kind)]=dict(context=ctx,issues=issues,lanes=lanes);phase+=1
  elif f[0]=='CALIBRATION':
   need(phase==2 and len(f)==4 and int(f[1])==kid,'ordered calibration grammar')
   issues=int(f[2]);lanes=int(f[3]);need(issues>0 and issues<=lanes<=32*issues and lanes==(128 if kid%2 else 256),'actual allphysicalthread EXIT calibration')
   owner=FAN1 if kid%2 else FAN2;need({v for v in expected if v[0]==3 and v[1]==owner}<=registered,'all actual EXIT static sites registered before calibration')
   calibration[kid]=dict(issues=issues,lanes=lanes);phase=3
  elif f[0]=='LAUNCH_END':
   need(phase==3 and f==['LAUNCH_END',str(kid)],'ordered complete launch end');ends.append(kid);kid+=1;phase=0
  elif f[0]=='EOF':
   need(index==len(rows)-1 and phase==0 and kid==31 and len(f)==4,'unique last observer EOF after30closed launches');eof=list(map(int,f[1:]))
  else:raise ValueError('unknown observer line')
 need(registered==expected and ends==list(range(1,31)),'all8 static registrations and30ends')
 c=sum(v['issues']for(k,t),v in pairs.items()if t==1);r=sum(v['issues']for(k,t),v in pairs.items()if t==2);need(eof==[30,c,r],'full observer aggregate EOF')
 return dict(context=ctx,call_issues=c,ret_issues=r,call_effective_lanes=sum(v['lanes']for(k,t),v in pairs.items()if t==1),ret_effective_lanes=sum(v['lanes']for(k,t),v in pairs.items()if t==2),rows=60,launches=30,static_sites=sorted(registered),calibration=calibration,per_site=[dict(kernel_id=k,kind=t,**v)for(k,t),v in pairs.items()])
def verify_ref(r,root=None):
 p=pathlib.Path(r['path'])
 if root is not None and not p.resolve().is_relative_to(root.resolve()):
  remote=pathlib.Path(json.loads((root/'EXECUTION.json').read_text())['capture_root']);need(p.is_relative_to(remote),'exact run evidence alias');p=root/p.relative_to(remote)
 need(p.is_file()and not p.is_symlink(),'closed evidence regular ref')
 if root is not None:need(p.resolve().is_relative_to(root.resolve()),'closed evidence private run path')
 need(p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],'evidence ref current bytes/SHA')
 return p
def decide(root,reader):
 root=pathlib.Path(root);qa=validate(root);obs=counters(root/'traces/ada-cfi-observer.tsv');need(obs['context']==qa['io'][0]['context'],'counter/io actual context join')
 need(reader['schema']=='GAUSSIAN16_FULL_RECORD_CFI_READER_V3'and reader['status']=='PASS'and reader['launches']==30 and reader['full_record_complete']is True and reader['loaded_map_complete']is True,'whole source/loaded/static/record reader required')
 need(reader.get('reader_contract')=='GAUSSIAN16_EXECUTED_STATIC_RECORD_JOIN_CPU_V4'and all(reader.get(k)is True for k in ['format_complete','executed_static_operands_joined','executed_static_memory_constant_joined']),'Root reviewed executed static record contract required')
 for row in reader['rows']:
  need(row['result']['schema']=='GAUSSIAN16_CONSUMER_FULL_RECORD_STATIC_JOIN_V4'and row['result']['reader_contract']==reader['reader_contract']and all(row['result'].get(k)is True for k in ['format_complete','executed_static_operands_joined','executed_static_memory_constant_joined']),'each actual launch executed static fields closed')
 need(reader.get('fixture_or_partial_launch_override')is False,'partial reader never qualifies')
 need(len(reader['rows'])==30 and [r['result']['kernel_id']for r in reader['rows']]==list(range(1,31)),'ordered exact30 reader rows')
 for rr in reader['sidecar_refs']:verify_ref(rr,root)
 for rr in reader['rows']:verify_ref(rr['trace_ref'],root)
 import re
 commands=reader['commandlist_memcpy_commands'];need(len(commands)==3,'all three actual HtoD commandlist entries')
 for cmd,r in zip(commands,qa['io'][:3]):
  m=re.fullmatch(r'MemcpyHtoD,\s*(?:0x)?([0-9a-fA-F]+),\s*([0-9]+)',cmd);need(m is not None and int(m[1],16)==int(r['device'],16)and int(m[2])==r['bytes'],'actual HtoD command/journal range join')
 execution=json.loads((root/'EXECUTION.json').read_text());loaded=json.loads((root/'LOADED_MAPS.json').read_text());need(execution['binary_sha256']==BINARY and execution['tool_sha256']==SO and execution['exit_code']==0 and loaded['binary_sha256']==BINARY and loaded['producer_sha256']==SO,'actual exact binary/producer execution+hostmaps contract')
 for kid,row in obs['calibration'].items():
  need(reader['exit_effective_lanes_by_launch'][str(kid)]==row['lanes'],'actual trace EXIT/independent calibration join')
  r=reader['rows'][kid-1]['result'];need(r['CTAs']==1 and r['warps_per_CTA']==(4 if kid%2 else 8)and r['EXIT_effective_lanes']==row['lanes']and r['EOF_decompressor_closed']is True,'actual all launch dimensions/EOF/EXIT joins')
  for kind,name in [(1,'CALL'),(2,'RET')]:
   q=next(v for v in obs['per_site']if v['kernel_id']==kid and v['kind']==kind)
   need(r[name+'_issue_records']==q['issues']and r[name+'_effective_lanes']==q['lanes'],'perlaunch trace/counter join')
 for k in ['call_issues','ret_issues','call_effective_lanes','ret_effective_lanes']:need(reader[k]==obs[k],'trace/independent counter mismatch '+k)
 if obs['call_issues']==obs['ret_issues']==0:
  branch='EXACT_GAUSSIAN16_INPUT_NO_EXECUTED_UNSUPPORTED_CFI_CANDIDATE'
  generic=False
 else:
  need(obs['call_issues']>0 and obs['ret_issues']>0 and all(x['result']['all_CTA_warp_EXIT_CFI_closed']is True for x in reader['rows']),'nonzero complete CFI lane frames')
  branch='EXACT_GAUSSIAN16_NONZERO_CFI_INPUT_CANDIDATE';generic=False
 return dict(status=branch,independent_observer=obs,observed_io_QA=qa,generic_CALL_RET_support_granted=generic,other_input_qualification=False,old_queue_status_mutated=False,Root_review_required=True,public_or_science_qualification=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--reader',required=True);p.add_argument('--output',required=True);a=p.parse_args();out=pathlib.Path(a.output);need(not out.exists(),'new result');r=decide(pathlib.Path(a.root),json.loads(pathlib.Path(a.reader).read_text()));out.write_text(json.dumps(r,indent=2)+'\n')
if __name__=='__main__':main()
