"""Offline publication validator. No torch/vLLM/NVML imports or lock attempts."""
import pathlib,json,csv,io,hashlib,subprocess,sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=ROOT/'docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1';TOOL=pathlib.Path(__file__).parent

def validate():
 contract=json.loads((OUT/'FROZEN_SCIENCE_CONTRACT.json').read_text());inputs=json.loads((OUT/'INPUT_RECEIPT.json').read_text());resource=json.loads((OUT/'GPU_RESOURCE_RECEIPT.json').read_text());analysis=json.loads((OUT/'ANALYSIS.json').read_text())
 checks=[]
 for name,info in contract['frozen_files'].items():
  f=ROOT/name;assert hashlib.sha256(f.read_bytes()).hexdigest()==info['sha256'] and f.stat().st_size==info['bytes'],name
 checks.append('Pre-lock frozen source/input/runtime hashes unchanged')
 assert [p['point'] for p in contract['G2_points']]==['C01','C02','C03','C04','C05','C06','C07','C08']
 assert contract['G1_capacity']['max_model_len']==544 and contract['G2_capacity']['max_model_len']==2080
 assert len(inputs['inputs'])==4
 for source in ['TRAIN_A_DISCOVERY_00','TRAIN_A_DISCOVERY_01']:
  rows=[r for r in inputs['inputs'] if r['source']==source];assert sorted(r['prompt_tokens'] for r in rows)==[512,2048]
 assert len(json.loads((OUT/'SOURCE_AND_RUNTIME.json').read_text())['asset_files'])==12
 checks.append('Frozen input matrix, capacities and full model identity receipts')
 if analysis['status']=='GPU_RESOURCE_DEFERRED':
  assert resource['status']=='GPU_RESOURCE_DEFERRED' and not resource['lock_acquired'] and resource['GPU_model_initializations']==0
  assert not resource.get('NVML_initialized',False) and resource['samples']==[] and resource['EXCLUSIVITY_EVIDENCE_COMPLETE'] is False
  assert analysis['points']==[] and analysis['G2_same_capacity_contrasts']==[]
  assert not (OUT/'raw/G1.json').exists() and not (OUT/'raw/G2.json').exists()
  assert list(csv.DictReader(io.StringIO((OUT/'FORMAL_SAMPLES.tsv').read_text()),delimiter='\t'))==[]
  checks.append('Lock conflict is nonblocking terminal DEFER; zero GPU/NVML/model/formal observations')
 assert analysis['hardware_headroom_or_projection_claims']==0 and analysis['pure_prefill_or_decode_ITL_claims']==0
 for f in TOOL.glob('*.py'):compile(f.read_text(),str(f),'exec')
 for f in OUT.rglob('*.json'):
  if '.private' not in f.parts:json.loads(f.read_text())
 allowed=[str(TOOL.relative_to(ROOT))+'/',str(OUT.relative_to(ROOT))+'/']
 changes=subprocess.check_output(['git','status','--porcelain=v1','--untracked-files=all'],cwd=ROOT,text=True).splitlines()
 for line in changes:
  path=line[3:];assert any(path.startswith(prefix) for prefix in allowed),path
  assert '.private/' not in path and '__pycache__/' not in path
 checks.append('Only own source/output whitelist modified; private and helper bytecode ignored')
 # All public payload is metadata/source, never text or token arrays.
 for f in OUT.rglob('*'):
  if not f.is_file() or '.private' in f.parts:continue
  assert f.suffix not in ['.safetensors','.bin','.pt','.txt']
  if f.suffix=='.json':
   def check_keys(x):
    if isinstance(x,dict):
     for k,v in x.items():assert k not in ['prompt_token_ids','token_ids','generated_text','prompt_text','source_text'],(f.name,k);check_keys(v)
    elif isinstance(x,list):
     for v in x:check_keys(v)
   check_keys(json.loads(f.read_text()))
 checks.append('Public metadata has no source text/generated text/input or output token arrays')
 return {'status':'PASS','checks':checks,'completed_native_points':len(analysis['points']),'scientific_status':analysis['status']}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
