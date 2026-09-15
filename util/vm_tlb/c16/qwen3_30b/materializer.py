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
 def inject(self,module,full_names,prefix=''):
  tensors=self.load(full_names); local={n[len(prefix):] if prefix and n.startswith(prefix) else n:t for n,t in tensors.items()}
  expected=set(module.state_dict()); got=set(local)
  if expected!=got: raise ValueError({'missing':sorted(expected-got),'unexpected':sorted(got-expected)})
  for n,t in local.items():
   target=module.state_dict()[n]
   if tuple(target.shape)!=tuple(t.shape) or target.dtype!=t.dtype: raise ValueError('shape/dtype '+n)
  module.load_state_dict(local,strict=True,assign=True)
  return {'tensor_count':len(local),'bytes':sum(t.numel()*t.element_size() for t in local.values())}
 def release(self,module):
  module.to_empty(device='meta')
