from safetensors import safe_open
class Materializer:
 def __init__(self,root,weight_map): self.root=str(root);self.map=dict(weight_map)
 def load(self,names,device='cpu'):
  if len(names)!=len(set(names)): raise ValueError('duplicate tensor request')
  missing=set(names)-set(self.map)
  if missing: raise KeyError(sorted(missing))
  out={}
  for shard in sorted(set(self.map[n] for n in names)):
   with safe_open(self.root+'/'+shard,framework='pt',device=device) as f:
    for n in names:
     if self.map[n]==shard: out[n]=f.get_tensor(n)
  if set(out)!=set(names): raise ValueError('incomplete materialization')
  return out
