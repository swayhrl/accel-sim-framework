"""Paper-side r19 condition guard; not a producer qualification or launcher."""
from pathlib import Path

OPTIONS=( '-gpgpu_dram_partition_queues', '-gpgpu_frfcfs_dram_sched_queue_size',
 '-gpgpu_dram_return_queue_size', '-gpgpu_clock_domains', '-dram_latency',
 '-gpgpu_simple_dram_model')
H0=dict(zip(OPTIONS,['64:128:64:64','128','192','1132.0:1132.0:1132.0:850.0','100','0']))
Q4={**H0,OPTIONS[0]:'64:512:256:64',OPTIONS[1]:'512',OPTIONS[2]:'768'}
D4={**Q4,OPTIONS[3]:'1132.0:1132.0:1132.0:3400.0'}
REGIMES={'H0':H0,'Q4':Q4,'D4':D4}
ALLOWED_OVERLAY_OPTIONS=set(OPTIONS[:4])

def require(ok,reason):
 if not ok:raise ValueError(reason)

def options(text):
 result={}
 for line in text.splitlines():
  line=line.split('#',1)[0].strip()
  if not line or not line.startswith('-'):continue
  fields=line.split(None,1)
  require(len(fields)==2,'Missing option value: '+line)
  result[fields[0]]=fields[1].strip()
 return result

def verify_effective_dump(text,regime):
 require(regime in REGIMES,'Condition needs a separately published r19 selection/qualification checkpoint')
 # Runtime option dumps include unrelated empty string options. They are not
 # appended overlay keys; select the six complete r19 fields before parsing.
 actual=options('\n'.join(line for line in text.splitlines() if line.split() and line.split()[0] in OPTIONS))
 for key,value in REGIMES[regime].items():
  require(key in actual,'Missing actual runtime parameter dump: '+key)
  if key==OPTIONS[3]:require(tuple(map(float,actual[key].split(':')))==tuple(map(float,value.split(':'))),'Wrong clock domains for '+regime)
  else:require(actual[key]==value,'Wrong actual parameter '+key+' for '+regime)
 return {key:actual[key] for key in OPTIONS}

def verify_appended_contract(base_run,new_run,regime,root):
 """Additional guard AFTER full native intake; never overrides its certificate."""
 require(regime in ('Q4','D4'),'Only initial two r19 regimes are supported here')
 b,n=base_run['identity'],new_run['identity']
 for key in b:
  if key!='runtime_config_sha256':require(n[key]==b[key],'Regime changed non-config identity: '+key)
 require(new_run['summary']['instructions']==base_run['summary']['instructions'],'Full instruction count changed')
 bs,ns=base_run['original_spec'],new_run['original_spec']
 require(bs.get('environment',{})==ns.get('environment',{}),'Runtime environment changed')
 ba,na=base_run['original_result']['audit'],new_run['original_result']['audit']
 require(ba['auxiliary_assets']==na['auxiliary_assets'],'Auxiliary config assets changed')
 prefix=len(ba['configs']);require(na['configs'][:prefix]==ba['configs'] and len(na['configs'])>prefix,'r19 requires exact original five-layer config prefix and appended overlays')
 for index in range(prefix,len(na['configs'])):
  values=options((Path(root)/f'config-{index}.config').read_text())
  require(bool(values) and values.keys()<=ALLOWED_OVERLAY_OPTIONS,'Unapproved r19 overlay option')
 raw=(Path(root)/'raw.log').read_text()
 effective=verify_effective_dump(raw,regime)
 require(n['runtime_config_sha256']!=b['runtime_config_sha256'],'Diagnostic reuses H0 config hash')
 return {'regime':regime,'actual_effective_options':effective,'original_config_prefix_entries':prefix,
  'extra_overlay_entries':len(na['configs'])-prefix,'credit_limit':1279,'not_single_fifo_change':True,
  'condition_manifest_qualification':'Must already pass the official Lane5 native/envelope intake; this guard is additional'}

def interaction(b0,u0,bh,uh):
 for cycles in (b0,u0,bh,uh):require(type(cycles) is int and cycles>0,'Missing/nonpositive native GPU cycles')
 s0=b0/u0;s=bh/uh
 return {'cycles_B_H0':b0,'cycles_U_H0':u0,'cycles_B_h':bh,'cycles_U_h':uh,
  'S_H0':s0,'S_h':s,'J_h_over_H0':s/s0,'delta_cycles_B_H0_minus_h':b0-bh,
  'delta_cycles_U_H0_minus_h':u0-uh,'cross_condition_ratio_is_mechanism_speedup':False}
