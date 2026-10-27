"""Fixed Gaussian16 execution/post/receiver composition. No approval is issued here."""
import pathlib,sys,os,json,hashlib,subprocess,time,resource
G=pathlib.Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/gaussian16_inner_manifest_closure_repair_20261027_v6/runtime/gaussian')
sys.path.insert(0,str(G.parent));sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from gaussian16_result_gate_v1 import decide,verify_ref,BINARY,SO,need
ARGV=['/data/c16/rtx4080_suite_fill_20261024_v1/assets/gpu-app-collection/src/cuda/rodinia/3.1/cuda/gaussian/gaussian','-s','16']
PROFILE='GAUSSIAN16_DIRECT_RETPAIR_INPUT_OBSERVER_V2_CANDIDATE'
MAP='09a8918db2494e8a498fdafb84125a79bfde9ea7c871315220dd72ae38b9099b'
CUBIN='690c2d76dff5785f9d5d253a04b3ccd725db59f94d2893077e456fa8de35a5a1'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def save(p,x):
 with pathlib.Path(p).open('x')as f:json.dump(x,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def ref(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def plan():
 j=json.loads((G/'JOB_TEMPLATE.json').read_text());need(j['task']['argv']==ARGV and j['task']['binary_sha256']==BINARY,'one exact original Gaussian16')
 return dict(family='gaussian',package=G,job=j,argv=ARGV,binary_sha256=BINARY,SO_path=G/'producer.so',SO_sha256=SO,semantic_profile=PROFILE,seconds=120,growth=64)
def environment(root):
 p=plan();env={k:v for k,v in os.environ.items()if k in('HOME','USER','LOGNAME','LANG','LC_ALL','TZ')}
 env.update(PATH='/usr/local/cuda-12.8/bin:/usr/bin:/bin',LD_LIBRARY_PATH=p['job']['task']['env']['LD_LIBRARY_PATH'],LD_PRELOAD=str(p['SO_path'])+':libcuda.so.1',CUDA_VISIBLE_DEVICES='GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59',ADA_SEMANTIC_MAP=str(G/'semantic-map.tsv'),TRACES_FOLDER=str(root),ADA_INPUT_SNAPSHOT='1',ADA_INPUT_MAX_COPY_BYTES='1024',ADA_INPUT_MAX_TOTAL_BYTES='2112',ACTIVE_FROM_START='1',INSTR_BEGIN='0',INSTR_END='4294967295',TRACE_FILE_COMPRESS='1',TOOL_COMPRESS='1',ENABLE_SPINLOCK_FAST_FORWARD='0',TERMINATE_UPON_LIMIT='0',C16_EXACT_ROOT_FUNCTION_ONLY='0',C16_USE_NVBIT_STATIC_INDEX='0',TRACE_LINEINFO='0',EXCLUDE_PRED_OFF='0',TOOL_VERBOSE='0',TOOL_TRACE_CORE='0',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',TMPDIR=str(root/'tmp'),TMP=str(root/'tmp'),TEMP=str(root/'tmp'),CUDA_CACHE_PATH=str(root/'cuda_cache'),CUDA_CACHE_DISABLE='1',NVDISASM='/usr/local/cuda-12.8/bin/nvdisasm',PYTHONDONTWRITEBYTECODE='1')
 return env
def localize(root,s):
 p=pathlib.Path(s)
 if not p.is_absolute():p=root/p
 # Receiver aliases are explicitly bound in EXECUTION, not discovered by suffix.
 if not p.resolve().is_relative_to(root.resolve()):
  e=json.loads((root/'EXECUTION.json').read_text());remote=pathlib.Path(e['capture_root'])
  need(p.is_relative_to(remote),'exact capture-root alias only');p=root/p.relative_to(remote)
 need(p.resolve().is_relative_to(root.resolve())and not p.is_symlink(),'private closed path');return p
def limits():
 resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));resource.setrlimit(resource.RLIMIT_CPU,(120,120));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def post(root,absolute_deadline):
 root=pathlib.Path(root);need(not(root/'FULL_READER.json').exists(),'one post only')
 commands=[['/usr/bin/python3','-B',str(G/'postprocess_v8.py'),str(root/'traces'),'--scratch-budget',str(64*1024**2)],['/usr/bin/python3','-B',str(G/'full_reader.py'),'--traces',str(root/'traces'),'--reader',str(G/'consumer_full'),'--out',str(root/'FULL_READER.json')]]
 for i,cmd in enumerate(commands):
  remaining=absolute_deadline-time.time()-30;need(remaining>1,'original Root deadline before post')
  with(root/('POST_STAGE_'+str(i)+'.log')).open('xb')as out:
   cp=subprocess.run(cmd,stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,timeout=min(120,remaining),env={k:v for k,v in os.environ.items()if k not in('LD_PRELOAD','CUDA_INJECTION64_PATH')},preexec_fn=limits)
  need(cp.returncode==0,'actual fixed post/reader failed')
 reader=json.loads((root/'FULL_READER.json').read_text());q=receive(root,reader)
 save(root/'GAUSSIAN_RESULT_GATE.json',q);return q
def receive(root,reader):
 root=pathlib.Path(root);e=json.loads((root/'EXECUTION.json').read_text());m=json.loads((root/'LOADED_MAPS.json').read_text())
 if e.get('runtime_profile_id')=='GAUSSIAN16_CROSS_HOST_RUNTIME_V4_GO_CURRENT_RESOURCES':
  from cross_host_v9 import RB
  need(e['capture_root']==str(RB/'runtime'/root.name)and e['producer_runtime_path']==str(RB/'gaussian/producer.so'),'exact approved remote run/code roots')
 need(e['task']['argv']==ARGV and e['candidate_profile_id']==PROFILE and e['tool_sha256']==SO and e['binary_sha256']==BINARY and e['exit_code']==0,'actual fixed execution identity')
 need(m['capture_process']==e['capture_process']and m['producer_sha256']==SO and m['binary_sha256']==BINARY,'maps/process exact join')
 need(ARGV[0]in m['maps']and e['producer_runtime_path']in m['maps'],'sampled actual binary+SO mappings; not device loaded module proof')
 for rr in e['runtime_code_refs']:
  r=dict(rr);p=pathlib.Path(r['path'])
  if not p.exists():
   remote=pathlib.Path('/data/c16/rtx4080_suite_fill_20261024_v1/nas_rtx4080/private_candidates/gaussian16_inner_manifest_closure_repair_20261027_v6/runtime')
   need(p.is_relative_to(remote),'fixed scientific runtime code alias only');r['path']=str(G.parent/p.relative_to(remote))
  verify_ref(r)
 need(reader['reader_ref']['sha256']=='56a1f84d8198a0c1bca3b37cf50977992962c7d45f520aec5d462dc08957ccf4','explicit V7 strict padding fullreader pin')
 # Source raw and complete grouped objects are joined one-to-one; partial stays KEEP.
 pp=json.loads((root/'traces/POSTPROCESS_V8.json').read_text());need(len(pp)==30,'exact30 raw/group closures')
 need(len({x['source']for x in pp})==len({x['grouped']for x in pp})==30,'no duplicate raw or grouped')
 for a,b in zip(pp,reader['rows']):
  raw=localize(root,a['source']);group=localize(root,a['grouped'])
  need(raw.is_file()and group.is_file()and sha(raw)==a['source_sha256']and sha(group)==a['grouped_sha256']and a['compressor_eof_and_reopen']is True,'actual raw->grouped SHA/EOF')
  need(localize(root,b['trace_ref']['path'])==group and b['trace_ref']['sha256']==a['grouped_sha256']and b['result']['source_records']==a['records'],'all fullreader/post records join')
 need(sha(root/'traces/semantic-map.tsv')==MAP,'actual exact semantic map')
 loaded=[x.split('\t')for x in(root/'traces/ada-loaded.tsv').read_text().splitlines()];need(len(loaded)==2 and {x[2]for x in loaded}=={'_Z4Fan1PfS_ii','_Z4Fan2PfS_S_iii'},'actual two loaded owner rows')
 ctx=None
 for row in loaded:
  need(len(row)==6 and row[3]=='89','loaded grammar SM89')
  if ctx is None:ctx=int(row[0],16)
  need(int(row[0],16)==ctx,'same loaded context')
  cub=localize(root,row[5]);need(cub.stat().st_size==int(row[4])and sha(cub)==CUBIN,'actual dumped loaded cubin exact whole SHA')
 stats=list((root/'traces').glob('stats_ctx_0x*'));need(len(stats)==1,'one real context stats journal')
 import csv
 statsrows=list(csv.reader(stats[0].read_text().splitlines()));need(len(statsrows)==31 and len(statsrows[0])==12,'complete12column stats header+30')
 for kid,(row,rp)in enumerate(zip(statsrows[1:],pp),1):
  row=[v.strip()for v in row];need(len(row)==12,'stats12columns');name=pathlib.Path(rp['source']).name
  expected=[1,1,1,1,128,1,1,128]if kid%2 else[1,1,1,1,16,16,1,256]
  need(row[0]==name and row[1]==('_Z4Fan1PfS_ii'if kid%2 else'_Z4Fan2PfS_S_iii')and list(map(int,row[2:10]))==expected,'stats launch/source/dimensions order')
  need(int(row[10])==int(row[11])==rp['records'],'unfiltered full report/source/consumer record counts')
 q=decide(root,reader);need(int(q['independent_observer']['context'],16)==ctx,'input/observer/loaded context join')
 q.update(schema='GAUSSIAN16_PRIVATE_RUNTIME_RECEIVER_V2',runtime_code_id='GAUSSIAN16_CROSS_HOST_RUNTIME_V4_GO_CURRENT_RESOURCES',raw_grouped_launches=30,full_reader_ref=ref(root/'FULL_READER_V7.json'),execution_ref=ref(root/'EXECUTION.json'),maps_ref=ref(root/'LOADED_MAPS.json'),Source_KEEP=True,requires_Root_control_and_reader_independent_acceptance=True,production_qualified=False)
 return q

def validate_runtime_pins(scope):
 r=scope['gaussian_runtime_pins_ref'];p=pathlib.Path(r['remote_path']);need(sha(p)==r['sha256'],'Root exact Gaussian ELF/lib baseline bytes')
 x=json.loads(p.read_text());need(x['schema']=='ROOT_GAUSSIAN16_ELF_AND_DISK_LIB_PINS_V2'and x['binary_sha256']==BINARY and x['producer_sha256']==SO and x['argv']==ARGV,'fixed Root ELF/library scope')
 need(x['needed']and len({r['path']for r in x['needed']})==len(x['needed']),'nonempty exact resolved DSO baseline')
 for q in x['needed']:need(pathlib.Path(q['path']).is_absolute()and sha(q['path'])==q['sha256'],'fresh exact disk DSO bytes')
 ar=scope['gaussian_reader_acceptance_ref'];ap=pathlib.Path(ar['remote_path']);need(sha(ap)==ar['sha256'],'Root independent reader acceptance raw')
 a=json.loads(ap.read_text());need(sha(ap)=='a940680080a7d9a55098e5da2a1b2ca339c05dcae888958d8b2c8d87da6648ad'and a['schema']=='ROOT_INDEPENDENT_GAUSSIAN_EXECUTED_READER_V4_COMPONENT_ACCEPTANCE'and a['status']=='CPU_COMPONENT_ACCEPTED_FOR_GAUSSIAN_RUNTIME_COMPOSITION'and a['reader_ref']['sha256']==sha(G/'consumer_full')and a['python_reader_ref']['sha256']==sha(G/'full_reader.py'),'new explicit Root accepted fixed reader; old known format defects HOLD')
 return x
