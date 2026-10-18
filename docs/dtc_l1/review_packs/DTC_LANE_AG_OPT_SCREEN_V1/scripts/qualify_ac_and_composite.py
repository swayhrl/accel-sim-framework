#!/usr/bin/env python3
"""AG-owned fixed AC matrix plus all four AC/AE finite CPU combinations."""
from common import *
import importlib.util
import resource
import sys

def main():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 raw=RAW/'cpu-qualification/ac-ae-independent-and-composite';raw.mkdir(parents=True,exist_ok=False)
 build=BUILD/'combined-preview';reference=BUILD/'x2-reference'
 source=CORE/'tests/dtc_l1_collect_wb_pipeline_probe.cc'
 assert sha(source)=='1937f68cf1659705dd0c38136b4dc9194de5b92181107a543aae23983572bb02'
 receipts=[]
 def run(argv,label,env=None,timeout=180):
  r=subprocess.run(list(map(str,argv)),cwd=raw,capture_output=True,env=env,timeout=timeout)
  for stream in ['stdout','stderr']:(raw/(label+'.'+stream)).write_bytes(getattr(r,stream))
  receipts.append(dict(label=label,argv=list(map(str,argv)),returncode=r.returncode,
      stdout_sha256=sha(raw/(label+'.stdout')),stderr_sha256=sha(raw/(label+'.stderr'))))
  write(PACK/'AC_AE_AG_CPU_COMMANDS.json',receipts)
  assert r.returncode==0,(label,r.returncode,r.stderr[-3000:]);return r.stdout.decode()
 def compile_probe(source,include,library,target,macros):
  argv=['/usr/bin/g++','-std=c++17','-O1','-UNDEBUG','-fno-access-control','-DCUDART_VERSION=11080',
      *macros,'-I'+str(include/'src'),'-I'+str(include/'libcuda'),'-I/usr/local/cuda-11.8/include',str(source),
      '-L'+str(library),'-Wl,-rpath,'+str(library),'-lcudart','-ldl','-lz','-lGL','-pthread','-o',str(target)]
  run(argv,'compile_'+target.name)
 baseline=reference/'ag-ac-baseline-probe'
 compile_probe(source,BUILD/'x2-source',reference,baseline,['-DDTC_COLLECT_WB_PROBE_BASELINE=1'])
 matrix=PACK/'inputs/AC/scripts/run_cpu_matrix.py'
 run([sys.executable,matrix,'--probe',build/'dtc_l1_collect_wb_pipeline_probe','--baseline-probe',baseline,
      '--core',CORE,'--baseline-library',reference/'libcudart.so','--output',raw/'independent-80'],
      'fixed_AC_independent_matrix',timeout=300)
 fixed=json.loads((raw/'independent-80/CPU_TEST_RECEIPTS.json').read_text())
 assert len(fixed['processes'])==80 and len(fixed['negative_parser_checks'])==16
 write(PACK/'AC_AG_INDEPENDENT_CPU.json',dict(**fixed,qualification_source='AG_UNCOMMITTED_EXACT_AC_AE_UNION',
     source_review_sha256=sha(PACK/'COMBINED_SOURCE_REVIEW.json'),raw=str(raw/'independent-80')))
 # A test-only actual-parser seam changes no production code. It selects the
 # real AE flag and screening Tag geometry before constructing the actual LDST.
 seam='''#ifdef AG_COMPOSITE_AE
    const char *ae_value = std::getenv("AG_CPU_AE_VALUE");
    assert(ae_value);
    const char *ag_options[] = {"AG_CPU", "-gpgpu_dtc_l1_tag_hash_bankrow", ae_value,
        "-gpgpu_dtc_l1_logical_sets", "64", "-gpgpu_dtc_l1_logical_ways", "8",
        "-gpgpu_dtc_l1_physical_lines", "640", "-gpgpu_dtc_l1_oo_pib_entries", "128",
        "-gpgpu_dtc_l1_lower_outstanding_cap", "32768"};
    option_parser_cmdline(parser, sizeof(ag_options)/sizeof(ag_options[0]), ag_options);
#endif
'''
 text=source.read_text();assert text.count('    cfg.init();')==1
 composite_source=PACK/'scripts/ac_ae_composite_cpu_probe.cc'
 composite_source.write_text(text.replace('    cfg.init();',seam+'    cfg.init();',1))
 exe=build/'ag-ac-ae-composite-probe'
 compile_probe(composite_source,CORE,build,exe,['-DAG_COMPOSITE_AE=1'])
 sys.path.insert(0,str(PACK/'inputs/AC/scripts'))
 import run_cpu_matrix as oracle
 import parse_collect_wb
 cases=[];controlled={}
 for ac in ['0','1']:
  for ae in ['0','1']:
   for scenario,sectors,k1 in oracle.CASES:
    label=f'composite_AC{ac}_AE{ae}_{scenario}_{sectors}_K{k1}'
    env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',
        LD_LIBRARY_PATH=str(build),AG_CPU_AE_VALUE=ae)
    argv=[exe,CORE/'configs/tested-cfgs/SM7_GV100/gpgpusim.config',ac,scenario,sectors,3,1,k1,1]
    out=run(argv,label,env)
    assert 'AC_RESULT status=PASS_CPU_LDST_COMPONENT' in out and 'kernel_launches=0 gpu_cycles=0' in out
    parsed=parse_collect_wb.parse(out,enabled=ac=='1',sms=1)
    if ac=='1':
     row=parsed['rows'][0]
     assert row['bank_capacity_bytes']==81920 and row['total_buffer_capacity_bytes']==163840
     edges=[oracle.numbers(l) for l in out.splitlines() if l.startswith('AC_EDGE ')]
     assert sum(e['sectors'] for e in edges)==row['collected_sectors']
     assert sum(e['retires'] for e in edges)==row['retires']
     prior=overlap=0
     for e in edges:overlap+=bool(e['sectors'] and e['closed']>prior);prior=e['closed']
     assert row['overlap_cycles']==overlap
    # Changing the Tag set for these no-conflict bounded identities must not
    # change any original state timing/counters outside the explicit Tag rows.
    key=(ac,scenario,sectors,k1)
    edge='\n'.join(l for l in out.splitlines() if l.startswith(('AC_EDGE ','AC_ENTRY ')))
    if ae=='0':controlled[key]=edge
    else:assert controlled[key]==edge,('HASH_CROSSED_PIPELINE_OWNERSHIP_OR_QUOTAS',label)
    cases.append(dict(label=label,status='PASS_BOUNDED_FINITE_INTERLEAVING_AND_CONSERVATION',
        final_pipeline=parsed,actual_production_LDST=True))
 assert len(cases)==68
 write(PACK/'AC_AE_COMPOSITE_CPU.json',dict(status='PASS_ALL_FOUR_AC_AE_COMBINATIONS_68_CPU_PROCESSES',cases=cases,
     source_sha256=sha(composite_source),library_sha256=sha(build/'libcudart.so'),
     geometry=dict(sets=64,ways=8,physical=640,PIB=128,lower=32768),
     AD='HOLD_UNQUALIFIED_NOT_COMPILED_IN',AF='NOT_COMPILED_IN',performance_runs=0,
     field_scope='ON_only_diagnostic_no_OFF_imputation',raw=str(raw)))
 print('PASS: independent AC80 processes/16 parser negatives; 68 actual LDST ACxAE CPU combinations; no simulations')

if __name__=='__main__':main()
