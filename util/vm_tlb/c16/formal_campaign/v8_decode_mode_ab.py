import json,hashlib,torch,os,time
from pathlib import Path
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.cache_utils import DynamicCache
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer,Qwen2RotaryEmbedding
R=Path('/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28');cfg=Qwen2Config.from_pretrained(R);idx=json.loads((R/'model.safetensors.index.json').read_text())['weight_map']
def ten(k):
 with safe_open(R/idx[k],framework='pt',device='cpu') as s:return s.get_tensor(k)
def layer():
 l=Qwen2DecoderLayer(cfg,0).to(dtype=torch.bfloat16);l.load_state_dict({n:ten('model.layers.0.'+n) for n in l.state_dict()},strict=True);return l.cuda().eval()
ids=json.loads(Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json').read_text());next_id=json.loads(Path('/data/c16/v8_raw_full_stream.json').read_text())['next_token'];emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,dtype=torch.bfloat16);emb.weight.data.copy_(ten('model.embed_tokens.weight'));emb=emb.cuda().eval();rot=Qwen2RotaryEmbedding(config=cfg).cuda();l=layer()
def nvtx_pre(_m,_x): torch.cuda.nvtx.range_push('C16_V8_RAW_MODULE:model.layers.0.mlp.down_proj'); return None
def nvtx_post(_m,_x,_o): torch.cuda.nvtx.range_pop(); return None
l.mlp.down_proj.register_forward_pre_hook(nvtx_pre);l.mlp.down_proj.register_forward_hook(nvtx_post);cache=DynamicCache();x=emb(torch.tensor([ids],device='cuda'));pos=torch.arange(len(ids),device='cuda').unsqueeze(0)
with torch.inference_mode(): l(x,position_ids=pos,past_key_value=cache,use_cache=True,cache_position=torch.arange(len(ids),device='cuda'),position_embeddings=rot(x,pos));prekey=cache.key_cache[0].cpu().clone();prevalue=cache.value_cache[0].cpu().clone();dec=emb(torch.tensor([[next_id]],device='cuda'));dpos=torch.tensor([[len(ids)]],device='cuda');ref=l(dec,position_ids=dpos,past_key_value=cache,use_cache=True,cache_position=torch.tensor([len(ids)],device='cuda'),position_embeddings=rot(dec,dpos))[0]
state={'decode_input':dec.cpu(),'position':dpos.cpu(),'key':prekey,'value':prevalue,'reference':ref.cpu(),'next_token':next_id};torch.save(state,'/data/c16/v8_target_layer0_decode.pt');del l;torch.cuda.empty_cache();l=layer();c=DynamicCache();c.key_cache=[state['key'].cuda()];c.value_cache=[state['value'].cuda()];dec=state['decode_input'].cuda();dpos=state['position'].cuda()
with torch.inference_mode(): out=l(dec,position_ids=dpos,past_key_value=c,use_cache=True,cache_position=torch.tensor([len(ids)],device='cuda'),position_embeddings=rot(dec,dpos))[0]
eq=torch.equal(out.cpu(),state['reference']);diff=(out.cpu().float()-state['reference'].float()).abs().max().item();q={'schema':'C16_V8_MODE_A_B_DECODE_V1','status':'PASS' if eq else 'FAIL','target_layer':0,'semantic_role':'mlp.down_proj within native Qwen2DecoderLayer','phase':'DECODE','decode_token':next_id,'bitwise_equal':eq,'max_abs':diff,'state_sha256':hashlib.sha256(Path('/data/c16/v8_target_layer0_decode.pt').read_bytes()).hexdigest()}
trace=os.environ.get('C16_WARP_OUTPUT');ctxout=os.environ.get('C16_V8_ADDRESS_CONTEXT_OUT');smap=os.environ.get('C16_V8_STATIC_MAP')
if trace and ctxout and smap and Path(trace).is_file():
 def sh(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
 ctx={'schema_version':'C16_ADDRESS_CONTEXT_V1','same_process_only':True,'address_space_id':hashlib.sha256((str(os.getpid())+str(time.time_ns())).encode()).hexdigest(),'target_id':'Q7RAW_S2_DECODE_LAYER0_MLP_DOWN','static_index':os.environ.get('C16_WARP_STATIC'),'function_occurrence':os.environ.get('C16_WARP_FUNCTION_OCCURRENCE'),'trace_path':trace,'trace_sha256':sh(trace),'static_map_path':smap,'static_map_sha256':sh(smap),'model_id':'Qwen/Qwen2.5-7B-Instruct','revision':'a09a35458c702b33eeacc393d103063234e8bc28','pair_input_sha256':'0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9','target_state_sha256':q['state_sha256'],'semantic_role':q['semantic_role']};Path(ctxout).write_text(json.dumps(ctx,indent=2)+'\n');q['address_context_sha256']=sh(ctxout)
Path('/data/c16/v8_decode_mode_ab.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
