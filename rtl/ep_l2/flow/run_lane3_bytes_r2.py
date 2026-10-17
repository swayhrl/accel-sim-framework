#!/usr/bin/env python3
"""Compile actual full-size RTL and compare its output with pinned Lane3 oracle.
Abstract observe events are mapped to explicit base-suite coverage, not counted
as assertions executed by the byte oracle. Full scope is in COVERAGE_R2.md.
Caller must hold central admission lease. Never modifies the R1 fixture.
"""
import argparse,json,hashlib,subprocess,gzip,re,importlib.util
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
repo=Path(__file__).resolve().parents[3];root=repo/'rtl/ep_l2';sp=root/'r2/LANE3_SHARED_STIMULI.json';rp=root/'r2/lane3_byte_reference.py';raw=sp.read_bytes();stim=json.loads(raw)
assert hashlib.sha256(raw).hexdigest()=='297e1d9547e9cae1ae998ef4eff6361acd1a6f85d737d1390b58032ea868a921'
assert hashlib.sha256(rp.read_bytes()).hexdigest()=='7000ec4892560dfcdc00e81b90a631a7446c552a7b6cb83db8e0e7de250a7a90'
spec=importlib.util.spec_from_file_location('independent',rp);refmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(refmod);refmod.verify(stim)
def linehex(b):return bytes(b)[::-1].hex()
body=[];expect={};snap_id=0
for n,case in enumerate(stim['cases']):
 tag=n+20;cid=case['case_id'];base=case['line_address'];initial=bytes.fromhex(case['initial_line_hex']);ref=refmod.ByteReference(base,initial)
 body.append(f'install({tag},64\'h{base+128*n:x},1024\'h{linehex(initial)},{{128{{1\'b1}}}},15,0,0);')
 snapshots={}
 for e in case['events']:
  if e['op']=='store':
   payload=bytes.fromhex(e['data_hex']);off=e['address']-base;v=bytearray(128);v[off:off+len(payload)]=payload
   body.append(f'write_bytes({tag},1024\'h{linehex(v)},128\'h{e["byte_mask_128_hex"]});');ref.store(e['address'],payload)
  elif e['op']=='read':
   key=e['snapshot_id'];expected=ref.load(key,e['address'],e['size']);assert expected.hex()==e['expected_hex'];snapshots[key]=snap_id;snap_id+=1
   body.extend([f'read_check({tag});',f'lane3_snapshot[{snapshots[key]}]=last_rsp_data;',f'$display("LANE3_OBS {cid} {e["step"]} %h",last_rsp_data);'])
   expect[(cid,e['step'])]=(e['address']-base,e['size'],expected.hex())
  elif e['op']=='expect_snapshot':
   key=e['snapshot_id'];expected=ref.snapshots[key];body.append(f'$display("LANE3_OBS {cid} {e["step"]} %h",lane3_snapshot[{snapshots[key]}]);')
   # All current immutable snapshots begin at line offset0.
   expect[(cid,e['step'])]=(0,len(expected),expected.hex())
  elif e['op']=='observe':body.append(f'// {cid} step{e["step"]}: lifecycle assertion belongs to full base fixture; not the byte oracle.')
 body.extend([f'read_check({tag});',f'$display("LANE3_FINAL {cid} %h",last_rsp_data);'])
body+=['if(!module_drained || accepted!=replies+aborted || reference_count!=0)$fatal(1,"Lane3 byte adapter drain");','$display("LANE3_ACTUAL_RTL_10_VECTORS PASS mode%0d",MODE);','$finish;']
tb=(root/'tb/ep_l2_slice_tb.sv').read_text().replace('    reg [127:0] mask;', '    reg [1023:0] lane3_snapshot[0:31];\n    reg [127:0] mask;')
tb=tb.replace('        if(GEN_W<8)begin','\n'.join('        '+x for x in body)+'\n        if(GEN_W<8)begin',1);fixture=a.out/'lane3_actual_tb.sv';fixture.write_text(tb)
rows=[]
for mode,label in enumerate(('B16','UNIFIED','S64')):
 binary=a.out/(label+'.vvp');cmd=['iverilog','-g2012','-s','ep_l2_slice_tb','-P',f'ep_l2_slice_tb.MODE={mode}','-o',str(binary),'-DEP_L2_FULL_TOP','-f','rtl/ep_l2/flow/full_slice_filelist.f',str(fixture)]
 with (a.out/(label+'-compile.log')).open('w') as f:subprocess.run(cmd,cwd=repo,stdout=f,stderr=subprocess.STDOUT,check=True)
 with (a.out/(label+'-run.log')).open('w') as f:subprocess.run(['stdbuf','-oL','-eL','vvp',str(binary)],stdout=f,stderr=subprocess.STDOUT,timeout=600,check=True)
 text=(a.out/(label+'-run.log')).read_text();observed={}
 for cid,step,val in re.findall(r'LANE3_OBS (C\d+) (\d+) ([0-9a-fA-F]+)',text):observed[(cid,int(step))]=bytes.fromhex(val)[::-1]
 assert set(observed)==set(expect)
 for key,(offset,size,expected) in expect.items():assert observed[key][offset:offset+size].hex()==expected,(label,key)
 final=dict(re.findall(r'LANE3_FINAL (C\d+) ([0-9a-fA-F]+)',text));assert len(final)==10
 for case in stim['cases']:assert bytes.fromhex(final[case['case_id']])[::-1].hex()==case['final_line_hex']
 blob=binary.read_bytes();binary.with_suffix('.vvp.gz').write_bytes(gzip.compress(blob,6,mtime=0));binary.unlink()
 rows.append({'mode':label,'status':'ACTUAL_RTL_BYTE_COMPARISON_PASS','comparisons':len(observed),'full_line_final_comparisons':10,'binary_sha256':hashlib.sha256(blob).hexdigest(),'compile_command':cmd,'abstract_observe_events':'NOT_EXECUTED_BY_BYTE_ADAPTER; see base-suite lifecycle mapping'})
 print(label,'Lane3 actual10vectors PASS',flush=True)
receipt={'rows':rows,'stimulus_sha256':hashlib.sha256(raw).hexdigest(),'reference_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'generated_fixture_sha256':hashlib.sha256(fixture.read_bytes()).hexdigest(),'RTL_sha256':{str(f.relative_to(repo)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (root/'rtl').glob('*.sv')},'scope':'non-atomic numeric RTL reads/snapshots only; protocol observe assertions separately covered by base fixture; no GPU numerical claim'}
(a.out/'LANE3_BYTE_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
