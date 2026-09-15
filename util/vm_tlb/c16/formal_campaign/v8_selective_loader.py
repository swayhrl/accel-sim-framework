import hashlib,json
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer
ROOT=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28')
cfg=Qwen2Config.from_pretrained(ROOT); index=json.loads((ROOT/'model.safetensors.index.json').read_text())['weight_map']
layer=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16)
expected={f'model.layers.0.{n}' for n in layer.state_dict()}
if set(k for k in index if k.startswith('model.layers.0.')) != expected: raise RuntimeError('layer0 key set mismatch')
loaded={}; evidence=[]
for k in sorted(expected):
 f=ROOT/index[k]
 with safe_open(f,framework='pt',device='cpu') as s:t=s.get_tensor(k)
 if t.dtype!=torch.bfloat16 or t.numel()*t.element_size()!=t.nbytes: raise RuntimeError('dtype/bytes '+k)
 loaded[k.removeprefix('model.layers.0.')]=t; evidence.append({'key':k,'shape':list(t.shape),'dtype':str(t.dtype),'bytes':t.nbytes,'sha256':hashlib.sha256(t.view(torch.uint8).numpy().tobytes()).hexdigest(),'shard':f.name})
missing,unexpected=layer.load_state_dict(loaded,strict=True)
if missing or unexpected: raise RuntimeError('load mismatch')
out={'schema':'C16_V8_RAW_SELECTIVE_LAYER_LOADER_V1','status':'PASS','layer':0,'tensor_count':len(evidence),'total_bytes':sum(x['bytes'] for x in evidence),'config_hidden_size':cfg.hidden_size,'config_layers':cfg.num_hidden_layers,'evidence':evidence}
Path('/data/c16/v8_raw_loader_layer0.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in out if k!='evidence'}))
