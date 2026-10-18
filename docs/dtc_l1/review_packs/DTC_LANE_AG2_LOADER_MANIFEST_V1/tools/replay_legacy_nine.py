#!/usr/bin/env python3
"""Counterfactual CPU replay only; never alters or authorizes the stopped run."""
from pathlib import Path
import sys,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'history/scripts'))
from common import *

def check(rows,registry):
 for row in rows:
  binding=registry.get(str(Path(row['path']).resolve()))
  if not binding or binding['sha256']!=row['observed_sha256']:return False
  if binding['role']=='ELF':
   if row['classification_current_file']!='ELF':return False
  elif binding['role']=='DECLARED_LDSO_CACHE_DATA':
   if row['path']!='/etc/ld.so.cache' or row['classification_current_file']!='NON_ELF_DATA':return False
  else:return False
 return True

def main():
 with (PACK/'OBSERVED_MAPPING_IDENTITY.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
 manifest=json.loads((PACK/'EXECUTABLE_PREREGISTRATION.json').read_text())
 original={str(Path(x['path']).resolve()):dict(sha256=x['sha256'],role='ELF') for x in manifest['runtime_files']}
 assert not check(rows,original)
 # This digest was observed AFTER launch, so it can only illustrate a future
 # registration schema. It cannot satisfy the original pre-launch contract.
 future=copy.deepcopy(original)
 cache=next(r for r in rows if r['path']=='/etc/ld.so.cache')
 future['/etc/ld.so.cache']=dict(sha256=cache['observed_sha256'],role='DECLARED_LDSO_CACHE_DATA')
 cases=[]
 def verify(name,data,registry,expected):
  observed=check(data,registry);assert observed is expected,name
  cases.append(dict(case=name,expected=expected,observed=observed,status='PASS_CPU_REPLAY_ONLY'))
 verify('original_registry_rejects_same_cache_gap',rows,original,False)
 verify('counterfactual_explicit_cache_role_and_digest_matches_stored_rows',rows,future,True)
 bad=copy.deepcopy(future);bad['/etc/ld.so.cache']['sha256']='0'*64
 verify('changed_cache_digest_rejected',rows,bad,False)
 bad=copy.deepcopy(future);elf=next(r['path'] for r in rows if r['classification_current_file']=='ELF');bad[elf]['sha256']='0'*64
 verify('changed_ELF_digest_rejected',rows,bad,False)
 extra=dict(path='/UNREGISTERED_ELF',observed_sha256='1'*64,classification_current_file='ELF')
 verify('unregistered_ELF_rejected',rows+[extra],future,False)
 extra=dict(path='/UNREGISTERED_DATA',observed_sha256='2'*64,classification_current_file='NON_ELF_DATA')
 verify('unregistered_nonELF_data_rejected',rows+[extra],future,False)
 bad=copy.deepcopy(future);bad['/etc/ld.so.cache']['role']='UNKNOWN'
 verify('digest_without_explicit_role_rejected',rows,bad,False)
 bad=copy.deepcopy(future);bad['/etc/ld.so.cache']['role']='ELF'
 verify('cache_misdeclared_as_ELF_rejected',rows,bad,False)
 changed=copy.deepcopy(rows);next(r for r in changed if r['path']=='/etc/ld.so.cache')['classification_current_file']='ELF'
 verify('ELF_masquerading_as_cache_data_rejected',changed,future,False)
 write(Path('/workspace/dtc-lane-ag2-loader-manifest-174-v1/raw/LEGACY_NINE_REPLAY.json'),dict(status='PASS_9_COUNTERFACTUAL_CPU_REPLAY_CASES_ONLY',cases=cases,
     script_sha256=sha(Path(__file__)),input_table_sha256=sha(PACK/'OBSERVED_MAPPING_IDENTITY.tsv'),
     no_simulator_started=True,no_loader_invoked=True,no_trace_read=True,no_current_guard_changed=True,
     original_attempt_status='FAILED_UNCHANGED',retroactive_acceptance=False,
     live_system_loader_startup_coverage='STILL_REQUIRED_FOR_ANY_FUTURE_EXECUTOR',
     cache_prelaunch_SHA_for_original_attempt='UNAVAILABLE_NEVER_RETROACTIVELY_FABRICATED',
     execution_authority=False,new_attempt_authorized=False))
 print('PASS: 9 counterfactual CPU replay cases; original attempt remains failed; no execution authority or new simulation.')

if __name__=='__main__':main()
