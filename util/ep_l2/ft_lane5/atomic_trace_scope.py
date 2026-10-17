"""Complete native trace opcode eligibility, only at a corrected release event.

Preparation/unit fixtures may run now. No production body scan of known088/e424,
no compiler/simulator, launch permission or implicit atomic-data correctness.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import time

from registry import Registry, run_key, write_json, local_resources, process_identity
from run import (asset_manifest, content_hash, digest, validate_trace_closure,
                 validate_config_closure, result_disk_free_bytes, RESULT_DISK_FLOOR)

REPO=Path(__file__).resolve().parents[3]
SCHEMA=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/continue_r13/NATIVE_ATOMIC_TRACE_SCHEMA.json'
MAPS={35:'kepler',60:'pascal',61:'pascal',70:'volta',75:'turing',80:'ampere',86:'ampere'}
GLOBAL={'OP_ATOM','OP_ATOMG','OP_RED'}
SHARED={'OP_ATOMS'}


def require(ok,reason):
    if not ok:raise ValueError(reason)


def integer(token,base=10):
    value=int(token,base);require(value>=0,'Negative native unsigned field');return value


def instruction(line,version,lineinfo,block,warp,opcodes):
    words=line.split();i=0
    if version<3:
        require(len(words)>=4 and tuple(integer(x) for x in words[:3])==block and integer(words[3])==warp,'Legacy TB/warp prefix mismatch');i=4
    if lineinfo:integer(words[i]);i+=1
    integer(words[i],16);mask=integer(words[i+1],16);require(mask<2**32,'Bad warp mask');i+=2
    nd=integer(words[i]);i+=1;require(nd<=1,'Native MAX_DST exceeded')
    for token in words[i:i+nd]:require(re.fullmatch(r'R\d+',token),'Bad destination register')
    require(len(words[i:i+nd])==nd,'Missing destination register');i+=nd
    opcode=words[i];i+=1;base=opcode.split('.')[0]
    require(base in opcodes,'Unknown native opcode; cannot infer zero atomic: '+base)
    ns=integer(words[i]);i+=1;require(ns<=4,'Native MAX_SRC exceeded')
    for token in words[i:i+ns]:require(re.fullmatch(r'R\d+',token),'Bad source register')
    require(len(words[i:i+ns])==ns,'Missing source register');i+=ns
    width=integer(words[i]);i+=1;tail=words[i:]
    require(all(re.fullmatch(r'[+-]?(?:0[xX])?[0-9a-fA-F]+',w) for w in tail),'Unparsed native memory/immediate tail')
    if width:
        require(bool(tail),'Missing native address mode');mode=integer(tail[0]);n=mask.bit_count()
        sizes={0:{1+n,2+n},1:{3,4},2:{1+max(n,1),2+max(n,1),3+n}}
        require(mode in sizes and len(tail) in sizes[mode],'Unsupported native address tail')
    else:require(len(tail)<=1,'Extra nonmemory fields')
    enum=opcodes[base]
    if enum in GLOBAL|SHARED:require(width>0,'Atomic without native memory payload')
    return opcode,enum,mask.bit_count()


def inspect_lines(lines,maps,checkpoint=lambda:None):
    meta={};version=0;lineinfo=0;grid=None;dims=None;opcodes=None;format_seen=False
    active=False;block=None;warp=None;remaining=None;warps=set();blocks=set();hist=Counter();global_hist=Counter();shared_hist=Counter();active_atomic=0;records=0;active_records=0
    for number,raw in enumerate(lines,1):
        require(len(raw)<=16384,'Oversized native line');s=raw.strip()
        if not s:continue
        if number%50000==0:checkpoint()
        if s.startswith('-') and not format_seen:
            key,sep,value=s[1:].partition('=');require(sep,'Malformed native header');key=key.strip();value=value.strip();require(key not in meta,'Duplicate native header');meta[key]=value
            if key=='binary version':
                binary=integer(value);require(binary in maps,'Unsupported binary opcode map');opcodes=maps[binary]
            elif key in ('grid dim','block dim'):
                match=re.fullmatch(r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)',value);require(match,'Bad native dimensions');v=tuple(map(int,match.groups()));require(all(v),'Zero native dimensions')
                if key=='grid dim':grid=v
                else:dims=v
            elif key=='accelsim tracer version':version=integer(value)
            elif key=='enable lineinfo':lineinfo=integer(value);require(lineinfo in (0,1),'Unknown lineinfo flag')
            continue
        if s.startswith('#traces format'):
            require(not format_seen and not active,'Duplicate/late format');format_seen=True;continue
        if s=='#BEGIN_TB':
            require(format_seen and grid and dims and opcodes is not None and not active,'Native TB/header incomplete')
            active=True;block=None;warp=None;remaining=None;warps=set();continue
        if s=='#END_TB':
            require(active and block is not None and remaining==0,'Truncated native warp/TB')
            require(warps==set(range((math.prod(dims)+31)//32)),'Missing native warp');blocks.add(block);active=False;continue
        m=re.fullmatch(r'thread block\s*=\s*(\d+),(\d+),(\d+)',s)
        if m:
            require(active and block is None,'Misplaced native block');block=tuple(map(int,m.groups()));require(block not in blocks and all(x<n for x,n in zip(block,grid)),'Duplicate/out-of-range block');continue
        m=re.fullmatch(r'warp\s*=\s*(\d+)',s)
        if m:
            require(active and block is not None and (warp is None or remaining==0),'Truncated native instruction count');warp=int(m[1]);require(warp not in warps,'Duplicate warp');warps.add(warp);remaining=None;continue
        m=re.fullmatch(r'insts\s*=\s*(\d+)',s)
        if m:
            require(active and warp is not None and remaining is None,'Misplaced insts count');remaining=int(m[1]);continue
        require(active and warp is not None and remaining is not None and remaining>0,'Unparsed/truncated/extra instruction record')
        try:opcode,enum,lanes=instruction(s,version,lineinfo,block,warp,opcodes)
        except (IndexError,TypeError) as error:raise ValueError('Truncated native instruction') from error
        remaining-=1;records+=1;active_records+=lanes;hist[opcode]+=1
        if enum in GLOBAL:global_hist[opcode]+=1;active_atomic+=lanes
        if enum in SHARED:shared_hist[opcode]+=1
    require(format_seen and not active and grid and len(blocks)==math.prod(grid),'Incomplete native grid/EOF')
    return {'status':'COMPLETE_NATIVE_OPCODE_COVERAGE','metadata':meta,'instruction_records':records,
            'active_lane_instruction_records':active_records,'blocks':len(blocks),'opcode_counts':dict(sorted(hist.items())),
            'global_atomic_records':sum(global_hist.values()),'global_atomic_active_lane_records':active_atomic,
            'global_atomic_opcodes':dict(global_hist),'shared_atomic_records':sum(shared_hist.values()),
            'shared_atomic_opcodes':dict(shared_hist),'atomic_absence':not(global_hist or shared_hist)}


class HashReader(io.RawIOBase):
    def __init__(self,raw):self.raw=raw;self.hash=hashlib.sha256();self.bytes=0
    def readable(self):return True
    def readinto(self,buffer):
        n=self.raw.readinto(buffer)
        if n:self.hash.update(memoryview(buffer)[:n]);self.bytes+=n
        return n


def kernel(path,maps,checkpoint=lambda:None):
    path=Path(path).resolve(strict=True);before=path.stat()
    with path.open('rb') as raw:
        hasher=HashReader(raw)
        with io.BufferedReader(hasher) as buffered:
            data=gzip.GzipFile(fileobj=buffered,mode='rb') if path.name.endswith('.gz') else buffered
            with io.TextIOWrapper(data,encoding='utf-8',errors='strict') as text:
                def lines():
                    while True:
                        line=text.readline(16385)
                        if not line:return
                        yield line
                report=inspect_lines(lines(),maps,checkpoint)
        checksum=hasher.hash.hexdigest();read_bytes=hasher.bytes
    after=path.stat();keys=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    require(keys(before)==keys(after) and read_bytes==before.st_size,'Trace mutated/incomplete raw read')
    return report,{'sha256':checksum,'bytes':before.st_size}


def source_maps(framework,source_commit):
    schema=json.loads(SCHEMA.read_text());framework=Path(framework).resolve(strict=True)
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=framework,text=True,env=env).strip()==source_commit,'Wrong parser-producing Framework')
    bindings={}
    for name,expected in schema['files_sha256'].items():
        data=(framework/name).read_bytes();require(hashlib.sha256(data).hexdigest()==expected,'Native parser/opcode semantics changed; review scope before scan')
        require(data==subprocess.check_output(['git','show',source_commit+':'+name],cwd=framework,env=env),'Unpublished/dirty parser source');bindings[name]=expected
    maps={}
    for binary,arch in MAPS.items():
        text=(framework/f'gpu-simulator/ISA_Def/{arch}_opcode.h').read_text();text=re.sub(r'/\*.*?\*/','',text,flags=re.S);text='\n'.join(line.split('//')[0] for line in text.splitlines())
        rows=re.findall(r'\{\s*"([A-Z0-9_]+)"\s*,\s*OpcodeChar\(\s*(OP_[A-Z0-9_]+)',text);require(rows,'Missing native opcode map')
        maps[binary]=dict(rows)
    return maps,bindings


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--spec',type=Path,required=True);ap.add_argument('--framework',type=Path,required=True)
    ap.add_argument('--critical-release-publication',required=True);ap.add_argument('--producer-receipt-path',required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--deadline-unix',type=float,required=True);args=ap.parse_args()
    spec=json.loads(args.spec.read_text());run_key(spec['identity']);identity=spec['identity']
    raw=subprocess.check_output(['git','show',args.critical_release_publication+':'+args.producer_receipt_path],cwd=REPO);producer=json.loads(raw)
    require(producer.get('owner')=='lane1' and producer.get('release')=='R0.1' and producer.get('status')=='PRODUCER_TESTS_PASS_NOT_INDEPENDENTLY_QUALIFIED','No official corrected producer')
    require(all(producer[k]==identity[k] for k in ('core_source_commit','framework_source_commit','binary_sha256')),'Scope source/binary mismatch')
    require(identity['core_source_commit'] not in ('c948184504d82b80e23eb3f4ff6cdfd328ba9355','088146f7f85b4073deb5d166a0a4484c7f3b48b2'),'r16 corrected-source milestone not reached; no repeat full input hash')
    require(not args.out.exists(),'Do not overwrite eligibility evidence');args.out.parent.mkdir(parents=True,exist_ok=True)
    def interrupted(signum,frame):raise KeyboardInterrupt('owned input audit interrupted')
    signal.signal(signal.SIGTERM,interrupted)
    report={'status':'INCOMPLETE_NO_ELIGIBILITY','scientific_acceptance_or_launch':False,'producer_publication':args.critical_release_publication,'identity':identity,'trace_files':[],
            'controller_identity':process_identity(os.getpid()),'tool_sha256':digest(__file__),
            'tooling_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()};lease=None
    def guard():
        require(time.time()<args.deadline_unix-5,'CONTINUE deadline');r=local_resources()
        require(r['disk_free_bytes']>=48*1024**3 and r['available_memory_bytes']>=64*1024**3 and result_disk_free_bytes()>=RESULT_DISK_FLOOR,'Original resource floors')
    try:
        guard();lease=Registry().build_lease('lane5',cpu=1,memory=4*1024**3);report['resource_lease']=lease
        maps,bindings=source_maps(args.framework,identity['framework_source_commit']);report['native_schema_sources']=bindings
        require(digest(spec['binary'])==identity['binary_sha256'],'Scope binary changed')
        validate_config_closure(spec);validate_trace_closure(spec)
        cfg=asset_manifest(spec['configs'],ordered=True);aux=asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else []
        require(content_hash({'ordered_configs':cfg,'auxiliary_assets':aux,'environment':spec.get('environment',{})})==identity['runtime_config_sha256'],'Scope config changed')
        write_json(args.out,report)
        files=spec['trace_files'];require(len(files)==len({x['name'] for x in files}),'Duplicate trace name');manifest=[];reports={}
        for item in files:
            guard();name=item['name'];path=Path(item['path'])
            if name==spec['entry_trace_name']:
                data=path.read_bytes();entry=data.decode('utf-8');manifest.append({'name':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
            else:
                result,binding=kernel(path,maps,guard);reports[name]=result;manifest.append({'name':name,**binding});report['trace_files'].append({'name':name,**binding,**result})
        manifest.sort(key=lambda x:x['name']);require(content_hash(manifest)==identity['trace_content_sha256'],'Full trace content identity mismatch')
        commands=[line.strip() for line in entry.splitlines() if line.strip() in reports]
        total=sum(reports[n]['global_atomic_records'] for n in commands);shared=sum(reports[n]['shared_atomic_records'] for n in commands)
        report.update(status='COMPLETE_NATIVE_OPCODE_AUDIT',trace_content_manifest=manifest,ordered_kernel_instances=len(commands),global_atomic_records_with_repeats=total,shared_atomic_records_with_repeats=shared,
                      input_scope='ATOMIC_PRESENT_REQUIRES_EXPLICIT_SCOPE_OR_B1_REVIEW' if total or shared else 'COMPLETE_INPUT_HAS_NO_NATIVE_ATOMIC_OPCODE_RECORDS',
                      limitations='Opcode/input eligibility only; no atomic numeric correctness, A1/eleven-gate qualification or performance authority')
    except BaseException as error:report['status']='FAILED_NO_ELIGIBILITY';report['error']=repr(error);raise
    finally:
        if lease:Registry().release_build(lease,'lane5')
        write_json(args.out,report)
    print(json.dumps({'status':report['status'],'input_scope':report['input_scope'],'report':str(args.out)}))


if __name__=='__main__':main()
