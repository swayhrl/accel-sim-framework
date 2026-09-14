#!/usr/bin/env python3
"""One campaign-scoped parent-lease nsys G1 census; never writes history."""
from __future__ import annotations
import argparse, os, subprocess, time, uuid
from pathlib import Path
from c16_native_common import ContractError, atomic_json, repo_root, sha256_file
from execution_budget import MeasurementActive
from profiler_wrapper import write_parent_lease_closeout, write_parent_lease_start
from retry570_recovery_v3_campaign_budget import RecoveryV3CampaignLease, initialize
from runtime_native_runner import load_binding

def main() -> None:
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('binding','campaign_ledger','historical_ledger','target','receipt','runner_receipt','parent_lease','output'):
  p.add_argument('--'+n.replace('_','-'),type=Path,required=True)
 p.add_argument('--historical-sha256',required=True); p.add_argument('--budget-scope',required=True)
 p.add_argument('--nsys',type=Path,required=True); p.add_argument('--run-id',required=True)
 p.add_argument('--adapter',required=True); p.add_argument('--implementation-key',required=True)
 p.add_argument('--dtype',required=True); p.add_argument('--quantization',required=True)
 a=p.parse_args()
 if any(x.exists() for x in (a.receipt,a.runner_receipt,a.parent_lease,a.output)): raise ContractError('G1 refuses retained-output overwrite')
 if not a.nsys.is_file() or not os.access(a.nsys,os.X_OK): raise ContractError('absolute nsys missing')
 if str(uuid.UUID(a.run_id)) != a.run_id: raise ContractError('run id must be UUID')
 binding=load_binding(a.binding,canary=False)
 ident={'deployment_id':binding['deployment_id'],'model_id':binding['model_id'],'model_revision':binding['model_revision'],'tokenizer_revision':binding['tokenizer_revision'],'scenario_id':binding['scenario']['scenario_id'],'input_hash':binding['input']['raw_input_sha256'],'implementation_key':a.implementation_key,'dtype':a.dtype,'quantization':a.quantization,'run_id':a.run_id,'code_commit':subprocess.check_output(['git','-C',str(repo_root()),'rev-parse','HEAD'],text=True).strip()}
 initialize(ledger_path=a.campaign_ledger,historical_ledger=a.historical_ledger,expected_historical_sha256=a.historical_sha256,identity=ident,budget_scope=a.budget_scope)
 MeasurementActive.assert_available(a.campaign_ledger); started=time.monotonic(); parent=None; rc=None
 with RecoveryV3CampaignLease(a.campaign_ledger,ident,'NSYS',capture=False,budget_scope=a.budget_scope) as lease:
  parent,token=write_parent_lease_start(a.parent_lease,{'identity':ident},'nsys',lease)
  env=dict(os.environ); env.update({'C16_G_PARENT_LEASE_RECEIPT':str(a.parent_lease),'C16_G_PARENT_LEASE_TOKEN':token,'C16_G_MEASUREMENT_ACTIVE_MARKER':str(a.campaign_ledger.parent.parent/'control'/'MEASUREMENT_ACTIVE')})
  cmd=[str(a.nsys),'profile','--force-overwrite=true','--trace=cuda,nvtx,osrt','-o',str(a.output),os.sys.executable,str(Path(__file__).with_name('runtime_native_runner.py')),'--mode','baseline','--receipt',str(a.runner_receipt),'--binding-receipt',str(a.binding),'--execute-native','--adapter',a.adapter,'--implementation-key',a.implementation_key,'--dtype',a.dtype,'--quantization',a.quantization,'--run-id',a.run_id,'--budget-ledger',str(a.campaign_ledger),'--budget-owned-by-wrapper','--parent-lease-receipt',str(a.parent_lease)]
  with MeasurementActive(a.campaign_ledger,ident,'NSYS_RECOVERY_V3_G1'):
   rc=subprocess.run(cmd,env=env).returncode
  elapsed=time.monotonic()-started; raw=(a.output.with_suffix('.nsys-rep')).stat().st_size if a.output.with_suffix('.nsys-rep').is_file() else 0
  terminal='COMPLETE' if rc==0 and raw>0 else 'FAILED_OR_ABORTED'; lease.finish(elapsed_seconds=elapsed,raw_bytes=0,terminal_status=terminal,evidence_classification='SCIENTIFIC' if terminal=='COMPLETE' else 'NON_SCIENTIFIC_DIAGNOSTIC')
 close=write_parent_lease_closeout(a.parent_lease,parent,terminal_status=terminal,elapsed_seconds=time.monotonic()-started,returncode=rc)
 value={'schema_version':'C16_G_RECOVERY_V3_G1_NSYS_V1','execution_mode':'NATIVE_GPU','scientific_eligible':terminal=='COMPLETE','identity':ident,'runtime':{'profiler_mode':'NSYS_LIGHTWEIGHT_CENSUS_PARENT_LEASED'},'checks':{'parent_lease_receipt':str(a.parent_lease),'parent_lease_closeout':str(close),'campaign_namespace':str(a.campaign_ledger),'child_acquired_second_lease':False,'command':cmd},'artifacts':{'terminal_status':terminal,'output_path':str(a.output),'output_bytes':raw,'output_sha256':sha256_file(a.output.with_suffix('.nsys-rep')) if raw else 'NA','elapsed_seconds':time.monotonic()-started}}
 atomic_json(a.receipt,value); print(a.receipt)
 if terminal!='COMPLETE': raise SystemExit(2)
if __name__=='__main__':
 try: main()
 except ContractError as e: raise SystemExit('FAIL Recovery-V3 G1: '+str(e))
