import json, os, hashlib
from pathlib import Path
def digest(p):
 h=hashlib.sha256();h.update(Path(p).read_bytes());return h.hexdigest()
def freeze(bundle, manifest, artifacts):
 bundle=Path(bundle); partial=Path(str(bundle)+'.partial')
 if bundle.exists() or partial.exists(): raise FileExistsError(bundle)
 partial.mkdir(parents=True)
 rows=[]
 for name,data in artifacts.items():
  p=partial/name;p.write_bytes(data);rows.append({'name':name,'sha256':digest(p),'bytes':len(data)})
 manifest=dict(manifest);manifest.update({'schema_version':'Q30_TARGET_LAYER_STATE_V1','artifacts':rows})
 (partial/'manifest.json').write_text(json.dumps(manifest,sort_keys=True))
 os.rename(partial,bundle)
def validate(bundle, revision, layer):
 m=json.loads((Path(bundle)/'manifest.json').read_text())
 if m['model_revision']!=revision or m['layer_id']!=layer: raise ValueError('identity mismatch')
 for a in m['artifacts']:
  if digest(Path(bundle)/a['name'])!=a['sha256']:raise ValueError('sha mismatch')
 return m
