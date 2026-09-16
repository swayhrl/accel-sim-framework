import hashlib,json,os,platform
from pathlib import Path
import torch,transformers
root=Path('/data/c16/models/.incoming/deepseek_v2_lite/604d5664dddd88a0433dbae533b7fe9472482de0')
payload=Path('/data/c16/deepseek_v23/authority/deepseek-v2-lite__S2_TEXT.json')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
files=[]
for p in sorted(root.iterdir()):
 if p.is_file():files.append({'name':p.name,'size_bytes':p.stat().st_size,'sha256':sha(p)})
d=json.loads(payload.read_text());ids=d.get('token_ids',[[]])[0]
r={'asset_root':str(root),'revision':'604d5664dddd88a0433dbae533b7fe9472482de0','asset_payload_bytes':sum(x['size_bytes'] for x in files),'asset_payload_files':len(files),'expected_v22_asset_bytes':31418842074,'asset_size_match':sum(x['size_bytes'] for x in files)==31418842074,'config_sha256':sha(root/'config.json'),'expected_config_sha256':'f346286b0f1c8b044252fd54cb4fa78b9fab6472a6e8bebb9edfe03d414ea03d','config_match':sha(root/'config.json')=='f346286b0f1c8b044252fd54cb4fa78b9fab6472a6e8bebb9edfe03d414ea03d','modeling_deepseek_sha256':sha(root/'modeling_deepseek.py'),'configuration_deepseek_sha256':sha(root/'configuration_deepseek.py'),'tokenizer_json_sha256':sha(root/'tokenizer.json'),'input_path':str(payload),'input_payload_sha256':sha(payload),'expected_input_payload_sha256':'2ca11cff95f13bcdd0efcb3f5b2d6c0b8f7e30c9e67492d6b291362c09ff6935','input_payload_match':sha(payload)=='2ca11cff95f13bcdd0efcb3f5b2d6c0b8f7e30c9e67492d6b291362c09ff6935','input_token_count':len(ids),'input_token_sequence_sha256':hashlib.sha256(json.dumps(ids,separators=(',',':')).encode()).hexdigest(),'expected_token_sequence_sha256':'14009279ed85b3de1f2510df84a3a8b2ba7a0d35f00c79d250d8e0e47cff63df','runtime':{'python':platform.python_version(),'torch':torch.__version__,'torch_cuda':torch.version.cuda,'transformers':transformers.__version__},'files':files}
Path('/data/c16/deepseek_v23/authority/PREFLIGHT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps(r,indent=2,sort_keys=True))
