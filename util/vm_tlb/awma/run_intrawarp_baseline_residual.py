#!/usr/bin/env python3
from __future__ import annotations
import argparse, concurrent.futures, hashlib, json, os, shlex, shutil, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

STAGE='AWMA_INTRAWARP_TRANSLATION_BASELINE_AND_RESIDUAL_V1'
REPO=Path('/root/workspace/accel-sim-framework-awma-intrawarp-translation-baseline-residual-v1')
RUNTIME=Path('/root/awma_intrawarp_translation_baseline_residual_v1_runtime')
DURABLE=Path('/root/share/mnt164/huangrulin/awma_intrawarp_translation_baseline_residual_v1/raw')
INPUTS=RUNTIME/'inputs'
CONFIG=REPO/'configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config'
TRACE_CONFIG=REPO/'gpu-simulator/configs/tested-cfgs/SM89_RTX4080_AWMA_V1/trace.config'
BINARY=RUNTIME/'bin/unified_accel-sim.out'
CORE_LIB=RUNTIME/'src/gpgpu-sim/lib/gcc-11.4.0/cuda-12040/release'
TARGETS={
 'T0':('PREFILL_FLASH','kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz','d8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a',527896,499441),
 'T1':('PREFILL_GEMM','kernel-45-ctx_0x60d38cb72530.traceg.xz','e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c',665802,647437),
 'T2':('DECODE_GEMV','kernel-17039-ctx_0x5ddb6907c160.traceg.xz','b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138',93079,94034),
 'SPLITKV':('FLASH_FWD_SPLITKV','kernel-17543-ctx_0x5be0856adcb0.traceg.xz','282a9b18510bd0aaf54ec528c65bfb39d49b052902c6b87f3b85bb2973096371',73923,73915),
 'COMBINE':('FLASH_FWD_SPLITKV_COMBINE','kernel-16813-ctx_0x5c9946e7f280.traceg.xz','d153db1548517f24eebd80c1a5dc48785ab28ace173b2937dd4f7b4a7005dcb9',10480,10480),
 'A1':('DECODE_GEMV_PAIR_A_S2_T2048','kernel-16828-ctx_0x608ad97ab300.traceg.xz','49f83c02fbb01dcc9167c6790271103e98d42f318c0344b5f26b8433b704d099',114123,115415),
 'A2':('DECODE_GEMV_PAIR_A_T8192','kernel-16828-ctx_0x573505e282b0.traceg.xz','c8135003bae105108707ab6b024ca56e50146df88d1692068d92e99511ada2ca',117698,115700),
}
def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def utc()->str:return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def trace_args():
 out=[]
 for raw in TRACE_CONFIG.read_text().splitlines():
  line=raw.strip()
  if line and not line.startswith('#'):out.extend(shlex.split(line))
 return out
def overlay():return ['-gpgpu_vm_mode','2','-gpgpu_vm_page_size','65536','-gpgpu_vm_l1_tlb_entries','32','-gpgpu_vm_l1_tlb_assoc','32','-gpgpu_vm_l1_tlb_ports','1','-gpgpu_vm_l1_tlb_lookup_latency','10','-gpgpu_vm_l2_tlb_entries','768','-gpgpu_vm_l2_tlb_assoc','16','-gpgpu_vm_l2_tlb_ports','1','-gpgpu_vm_l2_tlb_lookup_latency','80','-gpgpu_vm_translation_mshr_entries','32','-gpgpu_vm_pwq_entries','32','-gpgpu_vm_walkers','16','-gpgpu_vm_ptw_mode','1','-gpgpu_vm_pt_levels','4','-gpgpu_vm_virtual_address_bits','49','-gpgpu_vm_pwc_mode','1','-gpgpu_vm_pwc_entries','128','-gpgpu_vm_pwc_lookup_latency','1']
def run(target,arm,timeout,overwrite):
 family,name,expected,off,pre=TARGETS[target]; payload=INPUTS/name
 if sha(payload)!=expected:raise RuntimeError(f'{target}: trace SHA mismatch')
 label={'off':'OFF_NEUTRALITY','observer-prel1':'PREL1_SOURCE_OBSERVER','reference':'WARP_VPN_DEDUP_REFERENCE'}[arm]
 d=DURABLE/f'{target}_{label}_10_80'; rc=d/'rc.txt'
 if not overwrite and rc.is_file() and rc.read_text().strip()=='0':return {'target':target,'arm':arm,'rc':0,'status':'SKIPPED_EXISTING_PASS'}
 d.mkdir(parents=True,exist_ok=True); traces=d/'traces'
 if traces.exists():shutil.rmtree(traces)
 traces.mkdir();(traces/name).symlink_to(payload);(traces/'kernelslist.g').write_text(name+'\n')
 env=os.environ.copy();env['LD_LIBRARY_PATH']=f"{CORE_LIB}:{env.get('LD_LIBRARY_PATH','')}"
 for k in tuple(env):
  if k.startswith('GPGPUSIM_AWMA_') or k in ('GPGPUSIM_READY_APPLICATION_V2','GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH'):env.pop(k,None)
 env.update(GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH='1',GPGPUSIM_AWMA_PASSIVE_MEMO_OBSERVER='0',GPGPUSIM_AWMA_MECHANISM_DIAGNOSTICS='1',GPGPUSIM_AWMA_OWNER_WAIT_DIAGNOSTICS='1',GPGPUSIM_VM_COVERAGE_KERNEL_UID='1',GPGPUSIM_READY_APPLICATION_DIAGNOSTICS='1',GPGPUSIM_READY_APPLICATION_QUIESCENCE_DIAGNOSTICS='1')
 if arm=='observer-prel1':env.update(GPGPUSIM_AWMA_TRANSLATION_CANDIDATE='prel1_exact_coalescer',GPGPUSIM_AWMA_PREL1_COMPARE_LATENCY='0',GPGPUSIM_AWMA_INTRAWARP_SOURCE_OBSERVER='1')
 elif arm=='reference':env.update(GPGPUSIM_AWMA_TRANSLATION_CANDIDATE='warp_vpn_dedup_reference')
 cmd=['nice','-n','10',str(BINARY),'-config',str(CONFIG),'-trace','traces/kernelslist.g']+trace_args()+overlay()
 receipt={'stage':STAGE,'target':target,'family':family,'arm':arm,'accepted_off_cycles':off,'accepted_prel1_cycles':pre,'argv':cmd,'environment':{k:env[k] for k in sorted(env) if k.startswith('GPGPUSIM_')},'binary_sha256':sha(BINARY),'config_sha256':sha(CONFIG),'trace_config_sha256':sha(TRACE_CONFIG),'trace_sha256':sha(payload)}
 (d/'command.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');(d/'start_utc.txt').write_text(utc()+'\n');start=time.monotonic()
 with (d/'run.log').open('w') as out,(d/'run.stderr').open('w') as err:
  try:r=subprocess.run(cmd,cwd=d,env=env,stdout=out,stderr=err,timeout=timeout).returncode
  except subprocess.TimeoutExpired:r=124
 rc.write_text(f'{r}\n');(d/'end_utc.txt').write_text(utc()+'\n');(d/'wall_seconds.txt').write_text(f'{time.monotonic()-start:.6f}\n')
 return {'target':target,'arm':arm,'rc':r,'status':'PASS' if r==0 else 'FAIL'}
def main():
 p=argparse.ArgumentParser();p.add_argument('arm',choices=('off','observer-prel1','reference'));p.add_argument('--targets',nargs='+');p.add_argument('--workers',type=int,default=1);p.add_argument('--timeout-seconds',type=int,default=21600);p.add_argument('--overwrite',action='store_true');a=p.parse_args()
 if a.workers not in (1,2):p.error('one or two low-priority workers only')
 targets=a.targets or (['T2'] if a.arm=='off' else (['T1','T2'] if a.arm=='observer-prel1' else list(TARGETS)))
 if any(t not in TARGETS for t in targets):p.error('unknown target')
 DURABLE.mkdir(parents=True,exist_ok=True);results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  fs=[pool.submit(run,t,a.arm,a.timeout_seconds,a.overwrite) for t in targets]
  for f in concurrent.futures.as_completed(fs):r=f.result();results.append(r);print(json.dumps(r,sort_keys=True),flush=True)
 results.sort(key=lambda x:x['target']);(RUNTIME/f'{a.arm}_launcher_results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
 return 0 if all(r['rc']==0 for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
