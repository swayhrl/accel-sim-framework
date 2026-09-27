#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,importlib.metadata,json,math,subprocess,sys
from pathlib import Path

import torch
import transformers
import triton
from safetensors import safe_open
from transformers import AutoTokenizer,AutoConfig

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
AUTHOR=ROOT/'source/himuon'
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
R53=Path('/data/c16/awma/r53_online_workset_qualification_20260927/REQUEST_SELECTION.tsv')
NAMES=[
 'model.layers.0.self_attn.q_proj.weight',
 'model.layers.0.mlp.up_proj.weight',
 'model.layers.0.mlp.down_proj.weight',
 'model.layers.12.self_attn.q_proj.weight',
 'model.layers.12.mlp.up_proj.weight',
 'model.layers.12.mlp.down_proj.weight',
]

def sha_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def sha_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def canonical(value)->bytes:return json.dumps(value,separators=(',',':'),sort_keys=True,ensure_ascii=False).encode()
def dump(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

ROOT.mkdir(parents=True,exist_ok=True)
source_commit=subprocess.check_output(['git','-C',str(AUTHOR),'rev-parse','HEAD'],text=True).strip()
assert source_commit=='af89eda9a0176effed99e1fe19cc1f8a1a2c9588'
source_files=[
 'src/himuon/optimizers/himuon.py',
 'src/himuon/triton_kernels/ns5_smem.py',
 'src/himuon/triton_kernels/XXT.py',
 'src/himuon/triton_kernels/ba_plus_cAA.py',
 'src/himuon/triton_kernels/fused_bmm_add.py',
 'microbench/experiments/exp_ns5_rect_bench.py',
 'tests/integration/test_himuon_dispatch.py',
 'tests/integration/test_himuon_self_consistency.py',
]
source_receipt={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'repository':'tang0389/himuon','commit':source_commit,
 'source_sha256':{rel:sha_file(AUTHOR/rel) for rel in source_files},
 'license':'MIT',
 'verified_code_facts':{
  'cross_layer_bucket_batching':'himuon.py:_plan_buckets/_execute_plan',
  'cached_bucket_plan':'himuon.py:self._cached_plan',
  'reused_concat_buffers':'himuon.py:self._concat_buffers/_ensure_concat_buffer',
  'optimizer_step_cuda_graph':'himuon.py:_capture_graph/step',
  'small_tile_fused_dispatch':'himuon.py:newton_schulz and ns5_smem.py',
  'large_tile_compiled_three_kernel':'himuon.py:_newton_schulz_3kernel',
  'author_same_map_benchmark':'exp_ns5_rect_bench.py:ns_3kernel and ns5_smem',
  'author_bf16_self_consistency_tolerance':'test_himuon_self_consistency.py:rtol=1e-2,atol=1e-2'},
 'fused_only_if_tile_product_le_16384':True,
 'coefficients':[3.4445,-4.7750,2.0315],
 'steps':5,'norm_epsilon':1e-7}
dump(ROOT/'R101_SOURCE_RECEIPT.json',source_receipt)

model_sha=sha_file(MODEL/'model.safetensors')
assert model_sha=='fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe'
config=AutoConfig.from_pretrained(MODEL,local_files_only=True)
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
with R53.open(newline='') as f:selection=list(csv.DictReader(f,delimiter='\t'))
assert selection and all(r.get('raw_prompt') for r in selection)
raw_prompts=[]
for r in selection:
    text=r['raw_prompt']
    if sha_bytes(text.encode())!=r['raw_prompt_sha256']:
        raise ValueError(f'R53 raw prompt hash mismatch {r.get("canonical_id")}')
    raw_prompts.append(text)
sep='\n\n---\n\n'
cycles=1
combined=sep.join(raw_prompts)
tokens=tok(combined,add_special_tokens=False)['input_ids']
while len(tokens)<512:
    cycles+=1
    combined=sep.join(raw_prompts*cycles)
    tokens=tok(combined,add_special_tokens=False)['input_ids']
parts={'TRAIN_DISCOVERY_256':tokens[:256],
       'TRAIN_HOLDOUT_256':tokens[256:512]}
for name,ids in parts.items():
    assert len(ids)==256
    (ROOT/'raw'/f'{name}.json').write_text(json.dumps(ids,separators=(',',':'))+'\n')
input_receipt={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'input_class':'ACCEPTED_R53_RAW_PROMPTS_DETERMINISTIC_QWEN_TOKEN_STREAM',
 'r53_request_selection_path':str(R53),'r53_request_selection_sha256':sha_file(R53),
 'r53_row_order_canonical_ids':[r['canonical_id'] for r in selection],
 'r53_raw_prompt_sha256':[r['raw_prompt_sha256'] for r in selection],
 'separator_repr':repr(sep),'cycle_count':cycles,
 'combined_text_sha256':sha_bytes(combined.encode()),
 'combined_token_count':len(tokens),
 'tokenizer_json_sha256':sha_file(MODEL/'tokenizer.json'),
 'tokenizer_config_sha256':sha_file(MODEL/'tokenizer_config.json'),
 'add_special_tokens':False,'chat_template_applied':False,
 'model_revision':'7ae557604adf67be50417f59c2c2f167def9a775',
 'model_weight_sha256':model_sha,
 'parts':{name:{'count':len(ids),'token_ids_json_sha256':sha_bytes(canonical(ids)),
                 'raw_token_tensor_sha256':sha_bytes(torch.tensor(ids,dtype=torch.int64).view(torch.uint8).numpy().tobytes()),
                 'file_sha256':sha_file(ROOT/'raw'/f'{name}.json')}
          for name,ids in parts.items()}}
dump(ROOT/'R101_INPUT_RECEIPT.json',input_receipt)
model_identity={'model':'Qwen/Qwen2.5-0.5B-Instruct','revision':input_receipt['model_revision'],
 'weight_path':str(MODEL/'model.safetensors'),'weight_sha256':model_sha,
 'config_sha256':sha_file(MODEL/'config.json'),'config_hidden_size':config.hidden_size,
 'config_vocab_size':config.vocab_size,
 'weight_downloaded_this_goal':False}
dump(ROOT/'MODEL_IDENTITY_RECEIPT.json',model_identity)

shapes={}
with safe_open(MODEL/'model.safetensors',framework='pt',device='cpu') as source:
    keys=set(source.keys())
    for name in NAMES:
        if name not in keys:raise ValueError(f'missing exact target {name}')
        sl=source.get_slice(name)
        shapes[name]=tuple(sl.get_shape())

tile_rows=[]
for name,shape in shapes.items():
    h,w=shape
    for tile in [128,256,512]:
        ph=(-h)%tile;pw=(-w)%tile
        count=((h+ph)//tile)*((w+pw)//tile)
        tile_rows.append({'population':'DISCOVERY_LAYER0' if '.layers.0.' in name else 'CONDITIONAL_HOLDOUT_LAYER12',
          'parameter_name':name,'matrix_h':h,'matrix_w':w,'tile_edge':tile,
          'padded_h':h+ph,'padded_w':w+pw,'pad_h':ph,'pad_w':pw,
          'tile_count':count,'bf16_input_bytes':count*tile*tile*2,
          'author_dispatch':'FUSED_NS5_ELIGIBLE' if tile==128 else 'COMPILED_3KERNEL',
          'tile_order':'parameter role order q/up/down; tile row major from HiMuon._tile'})
with (ROOT/'TILE_POPULATIONS.tsv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(tile_rows[0]),delimiter='\t',lineterminator='\n')
    w.writeheader();w.writerows(tile_rows)

gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,compute_cap,driver_version',
                              '--format=csv,noheader'],text=True).strip()
env={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'environment_path':str(ROOT/'env'),'python':sys.version.replace('\n',' '),
 'torch':torch.__version__,'torch_cuda':torch.version.cuda,
 'transformers':transformers.__version__,'triton':triton.__version__,
 'himuon':importlib.metadata.version('himuon'),'datasets':importlib.metadata.version('datasets'),
 'gpu_driver':gpu,'system_cuda_or_driver_changed':False,
 'source_commit':source_commit,
 'cache_paths':{'hf':str(ROOT/'cache/hf'),'triton':str(ROOT/'cache/triton'),
                'cuda':str(ROOT/'cache/cuda'),'inductor':str(ROOT/'cache/inductor'),
                'tmpdir':str(ROOT/'tmp')},
 'python_env_isolated_from_c16_and_r102':True}
dump(ROOT/'ENVIRONMENT_RECEIPT.json',env)

prereg={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
 'source_receipt_sha256':sha_file(ROOT/'R101_SOURCE_RECEIPT.json'),
 'model_identity_receipt_sha256':sha_file(ROOT/'MODEL_IDENTITY_RECEIPT.json'),
 'input_receipt_sha256':sha_file(ROOT/'R101_INPUT_RECEIPT.json'),
 'environment_receipt_sha256':sha_file(ROOT/'ENVIRONMENT_RECEIPT.json'),
 'discovery_input':'TRAIN_DISCOVERY_256',
 'holdout_input':'TRAIN_HOLDOUT_256_CONDITIONAL_ONLY',
 'discovery_parameters':NAMES[:3],'holdout_parameters':NAMES[3:],
 'microstate':'one BF16 next-token CE/backward; zero momentum; author Nesterov G=grad+0.95*buf=1.95*grad; no update',
 'tile_edges':[128,256,512],
 'same_map_control':{'tile_edge':128,'arms':['F128_AUTHOR_NS5_SMEM','K128_AUTHOR_EQUIVALENT_COMPILED_3KERNEL'],
   'same_input_and_shape':True,'five_steps':5,'coefficients':[3.4445,-4.7750,2.0315],
   'norm_epsilon':1e-7,'rtol':1e-2,'atol':1e-2,
   'cosine_reference':'author microbench FP32 eager finite NS'},
 'large_tile_arms':['L256_AUTHOR_COMPILED_3KERNEL','L512_AUTHOR_COMPILED_3KERNEL'],
 'large_tile_per_map_only':True,
 'timing':{'canary_per_arm':1,'warmups_per_arm':2,'formal_repetitions_per_arm':7,
           'paired_interleaved_F128_K128':True,
           'materiality_fraction':0.05,'effect_over_larger_jitter':3},
 'author_software_baseline':['cross_layer_batch','cached_plan','reused_concat','torch_compile','legal_cuda_graph'],
 'holdout_trigger':'same-map S128 material and real L256/L512 material after strong software baseline',
 'ncu_trigger':'S128 material or large-tile material optimizer fraction; max two profiles',
 'no_step_or_coefficient_or_tile_local_map_change':True,
 'no_parameter_sweep':True,'frozen_before_gpu_gradient':True}
dump(ROOT/'PREREGISTRATION.json',prereg)
print(json.dumps({'source_commit':source_commit,'discovery_tile_counts':{
  str(t):sum(r['tile_count'] for r in tile_rows if r['population']=='DISCOVERY_LAYER0' and r['tile_edge']==t)
  for t in [128,256,512]},
  'input_token_hashes':{k:v['token_ids_json_sha256'] for k,v in input_receipt['parts'].items()},
  'preregistration_sha256':sha_file(ROOT/'PREREGISTRATION.json')},indent=2))
