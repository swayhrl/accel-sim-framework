import hashlib,json,platform
from pathlib import Path
import torch,transformers
from transformers import AutoConfig,AutoModelForCausalLM
root=Path('/data/c16/models/.incoming/deepseek_v2_lite/604d5664dddd88a0433dbae533b7fe9472482de0')
config=AutoConfig.from_pretrained(root,trust_remote_code=True,local_files_only=True)
with torch.device('meta'):
 model=AutoModelForCausalLM.from_config(config,trust_remote_code=True)
layers=model.model.layers
r={'config_class':str(type(config)),'model_class':str(type(model)),'architecture':config.architectures,'model_type':config.model_type,'layers':config.num_hidden_layers,'first_k_dense_replace':config.first_k_dense_replace,'moe_layer_freq':config.moe_layer_freq,'first_moe_layer':next(i for i,x in enumerate(layers) if x.mlp.__class__.__name__=='DeepseekV2MoE'),'attention_class':layers[0].self_attn.__class__.__name__,'attention_backend':config._attn_implementation,'cache_api':'transformers.cache_utils.DynamicCache','moe_class':layers[next(i for i,x in enumerate(layers) if x.mlp.__class__.__name__=='DeepseekV2MoE')].mlp.__class__.__name__,'n_routed_experts':config.n_routed_experts,'num_experts_per_tok':config.num_experts_per_tok,'n_shared_experts':config.n_shared_experts,'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,'modeling_source_sha256':hashlib.sha256((root/'modeling_deepseek.py').read_bytes()).hexdigest(),'configuration_source_sha256':hashlib.sha256((root/'configuration_deepseek.py').read_bytes()).hexdigest()}
Path('/data/c16/deepseek_v23r1/authority/RUNTIME_PREFLIGHT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,indent=2,sort_keys=True))
