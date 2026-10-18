#!/usr/bin/env python3
"""Cross-check AC ON normal-frame populations against original common fields."""
from common import *
from strict_screen import pipeline_contract,numeric
import re

def last_common(text):
 parts=re.findall(r'AC_NORMAL_BEGIN id=\d+\n(.*?)AC_NORMAL_END id=\d+\n',text,re.S)
 assert len(parts)==3
 return numeric(parts[-1])

def main():
 raw=RAW/'cpu-qualification'/('pipeline-join64-'+sha(PACK/'scripts/strict_screen.py')[:12]);raw.mkdir(parents=True,exist_ok=False)
 # Generation scenario has actual lower ownership and no synthetic prime()
 # retirements, making its public/frontend and real LDST populations equal.
 build=BUILD/'combined-preview';exe=build/'ag-ac-ae-composite-probe'
 argv=[str(exe),str(CORE/'configs/tested-cfgs/SM7_GV100/gpgpusim.config'),'1','generation','4','3','1','1','64']
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',LD_LIBRARY_PATH=str(build),AG_CPU_AE_VALUE='1')
 r=subprocess.run(argv,cwd=raw,env=env,capture_output=True,timeout=60)
 (raw/'stdout').write_bytes(r.stdout);(raw/'stderr').write_bytes(r.stderr)
 assert r.returncode==0,r.stderr[-2000:]
 text=r.stdout.decode();d=last_common(text);result=pipeline_contract(text,'AC',d)
 assert result['cumulative_sums']['cacheable_retires']==2
 negatives=[]
 for name,arm,stats in [('wrong_common_sectors','AC',dict(d,DTC_SERVICE_V1_collected_sectors=d['DTC_SERVICE_V1_collected_sectors']+1)),
     ('OFF_export','BASE',d)]:
  try:pipeline_contract(text,arm,stats)
  except ValueError as exc:negatives.append(dict(case=name,rejected=True,reason=str(exc)))
  else:raise AssertionError(name+' accepted')
 primed=RAW/'cpu-qualification/ac-ae-independent-and-composite/independent-80/one-normal64-k1.stdout'
 try:pipeline_contract(primed.read_text(),'AC',last_common(primed.read_text()))
 except ValueError as exc:negatives.append(dict(case='CPU_pair_prime_frontend_retirements_are_a_different_population',rejected=True,reason=str(exc)))
 else:raise AssertionError('synthetic priming population joined incorrectly')
 write(PACK/'AC_PIPELINE_PUBLIC_JOIN_CPU.json',dict(status='PASS_REAL64SM_ON_FRAME_AND_THREE_JOIN_NEGATIVES',
     argv=argv,stdout_sha256=sha(raw/'stdout'),stderr_sha256=sha(raw/'stderr'),
     strict_sha256=sha(PACK/'scripts/strict_screen.py'),parser_sha256=sha(PACK/'inputs/AC/scripts/parse_collect_wb.py'),
     rows=64,actual_return_generations=2,negative_cases=negatives,raw=str(raw),
     fixture_population_finding='pair fixture prime() retires synthetic frontend seeds outside LDST; full-input strict equality is retained, not relaxed',
     full_simulations_started=0))
 print('PASS: actual64SM two-generation ACxAE normal/common join; three population/OFF negatives rejected')

if __name__=='__main__':main()
