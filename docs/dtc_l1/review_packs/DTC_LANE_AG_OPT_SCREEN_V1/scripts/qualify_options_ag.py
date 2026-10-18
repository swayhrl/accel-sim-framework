#!/usr/bin/env python3
"""Full production option registration, including Framework trace options; CPU only."""
from common import *
from strict_screen import echo,require
import argparse

AE='-gpgpu_dtc_l1_tag_hash_bankrow'
AC='-gpgpu_dtc_l1_collect_wb_pipeline'
def main(trace_build,label):
 raw=RAW/'cpu-qualification'/label;raw.mkdir(parents=True,exist_ok=False)
 results=[];expected={}
 for workload in ['GEMM','Gaussian']:
  original=json.loads((PACK/f'inputs/T/inputs/{workload}_OO128_SPEC.json').read_text())
  old=json.loads((PACK/f'controls/{workload}_CALIBRATION_REFERENCE.json').read_text())['effective_options']
  maps={}
  for lineage,arm in [('x2','omitted'),('ag','omitted'),('ag','BASE'),('ag','AC'),('ag','AE'),('ag','COMPOSITE_CPU')]:
   base=BUILD/('x2-trace-reference' if lineage=='x2' else trace_build)
   cfgs=[PACK/'config'/n for n in ['FAST64_OO.config','FINITE_PRIMARY_COMMON.config','trace.config']]
   cfgs.append(PACK/'inputs/AA5/config/K0_64x8.config' if arm=='omitted' else PACK/f'config/{arm}.config')
   args=[str(base/'ag-options-cpu-probe'),'-trace',original['trace_list']]
   for c in cfgs:args.extend(['-config',str(c)])
   name=f'{workload}_{lineage}_{arm}'
   env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='')
   env['LD_LIBRARY_PATH']=str(BUILD/('x2-reference' if lineage=='x2' else trace_build.replace('trace-','')))
   # The executable's absolute RPATH binds its own Core build; no foreign LD path.
   env.pop('LD_LIBRARY_PATH')
   r=subprocess.run(args,cwd=raw,env=env,capture_output=True,timeout=30)
   for stream in ['stdout','stderr']:(raw/(name+'.'+stream)).write_bytes(getattr(r,stream))
   require(r.returncode==0,name+': '+r.stderr.decode()[-2000:])
   text=r.stdout.decode();require('kernels=0 GPU_cycle_calls=0 simulation_threads_started=0 trace_files_opened=0' in text,'CPU_only_options_marker')
   options=echo(text);maps[lineage+arm]=options
   if lineage=='x2':
    delta={k:[v,options.get(k)] for k,v in old.items() if options.get(k)!=v}
    require(not delta,'X2_all_old_T_effective_values_changed:'+json.dumps(delta))
   else:
    require(options[AE]==['1' if arm in ['AE','COMPOSITE_CPU'] else '0'],'actual_AE_switch_value')
    require(options[AC]==['1' if arm in ['AC','COMPOSITE_CPU'] else '0'],'actual_AC_switch_value')
    common={k:v for k,v in options.items() if k not in [AE,AC]}
    require(common==maps['x2omitted'],'DEFAULT_OFF_full_actual_Core_Framework_registration_equivalence')
    if arm not in ['omitted','COMPOSITE_CPU']:expected[workload+'_'+arm]=options
   results.append(dict(label=name,status='PASS_FULL_PRODUCTION_OPTIONS_CPU',options=len(options),
       argv=args,stdout_sha256=sha(raw/(name+'.stdout')),probe_sha256=sha(base/'ag-options-cpu-probe')))
 write(PACK/(label.upper()+'_RESULT.json'),dict(status='PASS_ALL_OPTIONS_OFF_EQUALS_X2_AND_OLD_T_PUBLIC_CONFIG',
     cases=results,expected=expected,trace_files_opened=0,GPU_cycle_calls=0,simulation_threads_started=0,new_simulations=0))
 print('PASS: all original T effective values preserved; full X2/Core/Framework parser OFF/ON echo, zero trace opens')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--trace-build',required=True);p.add_argument('--label',required=True);a=p.parse_args();main(a.trace_build,a.label)
