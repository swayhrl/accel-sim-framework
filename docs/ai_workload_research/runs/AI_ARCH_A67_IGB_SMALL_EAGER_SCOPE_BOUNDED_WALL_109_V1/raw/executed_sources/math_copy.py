"""Read-only audited A61 algorithm copies; Apache-2.0 DGL example attribution retained."""
import os,hashlib,json,time
assert os.environ.get('A67_GPU_LOCK_HELD')=='1'
from paths import OLD,R,save,event
import numpy as np
import torch
import torch.nn.functional as F
import dgl
import dgl.graphbolt as gb
from torch_geometric.nn import SAGEConv
N=1000000;D=1024;B=1024;C=19
FEAT=np.load(OLD/'data/small/processed/paper/node_feat.npy',mmap_mode='r')
LABEL=np.load(OLD/'data/small/processed/paper/node_label_19.npy',mmap_mode='r').reshape(-1)
IP=np.load(OLD/'graph/indptr.npy',mmap_mode='r')
IX=np.load(OLD/'graph/indices.npy',mmap_mode='r')
KEYS=np.load(OLD/'graph/edge_keys_sorted.npy',mmap_mode='r')
def sync():torch.cuda.synchronize()
def digest_array(x):return hashlib.sha256(np.ascontiguousarray(x).tobytes()).hexdigest()
def deadline():assert time.monotonic()<float(os.environ['A67_GPU_DEADLINE'])-20,'GPU_TIME_MARGIN'
def reserve_updates(n,label,kind):
 p=R/'update_ledger.json';v=json.loads(p.read_text()) if p.exists() else {'reserved_optimizer_updates':0,'entries':[]}
 assert v['reserved_optimizer_updates']+n<=85,'A67_TOTAL_UPDATE_CAP'
 v['reserved_optimizer_updates']+=n;v['entries'].append({'label':label,'kind':kind,'reserved_updates':n,'epoch':time.time()});save('update_ledger.json',v)

def state_hash(model):
 h=hashlib.sha256()
 for name,p in model.state_dict().items():h.update(name.encode());h.update(p.detach().cpu().numpy().tobytes())
 return h.hexdigest()

class GraphSAGE(torch.nn.Module):
 # Official fixed advanced-example math; PyG2.6.1 mean SAGEConv defaults.
 def __init__(self):
  super().__init__();sizes=[1024,256,256,19];self.layers=torch.nn.ModuleList([SAGEConv(sizes[i],sizes[i+1],aggr='mean') for i in range(3)])
 def forward(self,subgraphs,x):
  h=x
  for i,(layer,subgraph) in enumerate(zip(self.layers,subgraphs)):
   h,edge_index,size=subgraph.to_pyg(h);h=layer(h,edge_index,size=size)
   if i!=len(subgraphs)-1:h=F.relu(h)
  return h

def train_step(mb,optimizer,model):
 optimizer.zero_grad();out=model(mb.sampled_subgraphs,mb.node_features['feat']);loss=F.cross_entropy(out,mb.labels);loss.backward();optimizer.step();return loss.detach()

def model_optimizer(seed):
 torch.manual_seed(seed);gb.seed(seed);model=GraphSAGE().cuda();optimizer=torch.optim.Adam(model.parameters(),lr=.003,weight_decay=0);return model,optimizer

class DataContext:
 def __init__(self,arm,pinned):
  self.arm=arm;self.gpu_features=None;self.graph=None;self.cache=None
  pi,pj,px=pinned
  if arm=='FULL_RESIDENT_GPU':
   self.graph=gb.fused_csc_sampling_graph(pi.cuda(),pj.cuda());self.gpu_features=px.cuda();f=gb.TorchBasedFeature(self.gpu_features)
  else:
   self.graph=gb.fused_csc_sampling_graph(pi,pj);f=gb.TorchBasedFeature(px)
   if arm=='PINNED_CACHE_ON':f=gb.gpu_cached_feature(f,128*1024**2);self.cache=f
  self.store=gb.BasicFeatureStore({('node',None,'feat'):f});sync()
 def loader(self,ids):
  ids=np.asarray(ids,dtype=np.int64);item=gb.ItemSet((torch.from_numpy(ids.copy()),torch.from_numpy(np.asarray(LABEL[ids],dtype=np.int64))),names=('seeds','labels'));dp=gb.ItemSampler(item,batch_size=B,shuffle=False,drop_last=True,seed=1);dp=dp.copy_to(device='cuda');pinned=self.arm!='FULL_RESIDENT_GPU';on=self.arm=='PINNED_CACHE_ON'
  dp=dp.sample_neighbor(self.graph,[10,10,10],replace=False,deduplicate=True,overlap_fetch=pinned,asynchronous=True,num_gpu_cached_edges=1000000 if on else 0,gpu_cache_threshold=1);dp=dp.fetch_feature(self.store,node_feature_keys=['feat'],overlap_fetch=pinned);return gb.DataLoader(dp,num_workers=0)
 def stats(self):
  d={'arm':self.arm,'feature_cache_capacity_bytes':0,'graph_cache_capacity_edges_requested':1000000 if self.arm=='PINNED_CACHE_ON' else 0,'DRAM_and_PCIe_bytes':'UNKNOWN_NOT_MEASURED'}
  if self.cache is not None:d.update(feature_cache_capacity_bytes=int(self.cache.cache_size_in_bytes),feature_cache_miss_rate=float(self.cache.miss_rate))
  c=self.graph._gpu_graph_cache
  if c is not None:d.update(graph_cache_total_queries=int(c.total_queries),graph_cache_total_misses=int(c.total_miss),graph_cache_miss_rate=float(c.miss_rate) if c.total_queries else 'UNKNOWN_ZERO_EXPOSED_QUERIES')
  else:d['graph_cache']='NONE'
  return d

def validate_mb(mb,label):
 sync();ids=mb.input_nodes.detach().cpu().numpy();assert len(mb.seeds)==B and mb.node_features['feat'].dtype==torch.float32 and mb.labels.dtype==torch.int64;assert np.array_equal(mb.labels.cpu().numpy(),LABEL[mb.seeds.cpu().numpy()].astype(np.int64))
 idx=np.linspace(0,len(ids)-1,min(256,len(ids)),dtype=np.int64);assert np.array_equal(mb.node_features['feat'][torch.as_tensor(idx,device='cuda')].cpu().numpy(),np.asarray(FEAT[ids[idx]])),'FEATURE_READBACK_OR_FALLBACK_FAILED'
 layers=[]
 for l,sg in enumerate(mb.sampled_subgraphs):
  ip=sg.sampled_csc.indptr.cpu().numpy();ix=sg.sampled_csc.indices.cpu().numpy();src=sg.original_row_node_ids.cpu().numpy();dst=sg.original_column_node_ids.cpu().numpy();degree=np.diff(ip);original_degree=IP[dst+1]-IP[dst];assert np.array_equal(degree,np.minimum(10,original_degree)),'SAMPLED_FANOUT_SEMANTICS'
  columns=np.repeat(dst,degree);sources=src[ix];samplekeys=columns*N+sources;pos=np.searchsorted(KEYS,samplekeys);assert (pos<len(KEYS)).all() and np.array_equal(KEYS[pos],samplekeys),'SAMPLED_DIRECTION_OR_EDGE_MEMBERSHIP'
  for j in np.flatnonzero(original_degree<=10)[:128]:assert np.array_equal(np.sort(sources[ip[j]:ip[j+1]]),np.sort(IX[IP[dst[j]]:IP[dst[j]+1]])),'LOW_DEGREE_FULL_NEIGHBOR_CACHE_SEMANTICS'
  layers.append({'layer':l,'source_nodes':len(src),'destination_nodes':len(dst),'sampled_edges':len(ix),'sample_edge_ID_sha256':digest_array(samplekeys),'input_node_duplicate_fraction':1-float(len(np.unique(src)))/len(src),'mean_original_destination_degree':float(original_degree.mean()),'max_sampled_degree':int(degree.max())})
 out={'label':label,'batch_size':B,'seed_ID_sha256':digest_array(mb.seeds.cpu().numpy()),'input_ID_sha256':digest_array(ids),'input_nodes':len(ids),'feature_sample_rows':len(idx),'feature_sample_sha256':digest_array(np.asarray(FEAT[ids[idx]])),'layers':layers,'status':'PASS'};event('INPUT_SAMPLE_CACHE_SEMANTICS_PASS',**out);return out

def numeric_oracle(mb,model,opt,label):
 deadline();sync();params={n:p.detach().cpu().double().requires_grad_() for n,p in model.named_parameters()};data=[];need=np.arange(16,dtype=np.int64)
 for l in [2,1,0]:
  sg=mb.sampled_subgraphs[l];ip=sg.sampled_csc.indptr.cpu().numpy();ix=sg.sampled_csc.indices.cpu().numpy();pieces=[ix[ip[j]:ip[j+1]] for j in need];flat=np.concatenate(pieces);src=np.unique(np.concatenate((need,flat)));dest=np.repeat(np.arange(len(need)),[len(x) for x in pieces]);data.append({'layer':l,'need':need,'src':src,'edge_src':np.searchsorted(src,flat),'edge_dst':dest,'root':np.searchsorted(src,need),'counts':np.array([len(x) for x in pieces])});need=src
 data.sort(key=lambda x:x['layer']);global_input=mb.input_nodes.cpu().numpy();h=torch.from_numpy(np.array(FEAT[global_input[data[0]['src']]],dtype=np.float64,copy=True))
 for m in data:
  l=m['layer'];agg=torch.zeros((len(m['need']),h.shape[1]),dtype=torch.float64);agg.index_add_(0,torch.from_numpy(m['edge_dst']),h[torch.from_numpy(m['edge_src'])]);agg=agg/torch.from_numpy(np.maximum(m['counts'],1))[:,None];h=F.linear(agg,params[f'layers.{l}.lin_l.weight'],params.get(f'layers.{l}.lin_l.bias'))+F.linear(h[torch.from_numpy(m['root'])],params[f'layers.{l}.lin_r.weight']);h=F.relu(h) if l<2 else h
 reference=h;model.zero_grad();out=model(mb.sampled_subgraphs,mb.node_features['feat']);labels=mb.labels[:16].cpu();loss_ref=F.cross_entropy(reference,labels);loss=F.cross_entropy(out[:16],mb.labels[:16]);assert torch.allclose(out[:16].detach().cpu().double(),reference.detach(),atol=1e-5,rtol=1e-4),'FORWARD_NUMERIC_GATE';assert torch.allclose(loss.detach().cpu().double(),loss_ref.detach(),atol=1e-5,rtol=1e-4),'LOSS_NUMERIC_GATE';loss.backward(retain_graph=True);loss_ref.backward();maxgrad=0
 for n,p in model.named_parameters():
  g=p.grad.detach().cpu().double();r=params[n].grad;assert torch.isfinite(g).all() and torch.allclose(g,r,atol=1e-5,rtol=1e-3),'GRADIENT_NUMERIC_GATE '+n;maxgrad=max(maxgrad,float((g-r).abs().max()))
 opt.zero_grad();full_loss=F.cross_entropy(out,mb.labels);full_loss.backward();before={n:p.detach().cpu().clone() for n,p in model.named_parameters()};grad={n:p.grad.detach().cpu().clone() for n,p in model.named_parameters()};assert all(torch.isfinite(g).all() for g in grad.values()) and sum(float(g.abs().sum()) for g in grad.values())>0
 reserve_updates(1,label,'G1_CANARY');opt.step();sync();maxupdate=0
 for n,p in model.named_parameters():
  expected=before[n]-.003*grad[n]/(grad[n].abs()+1e-8);actual=p.detach().cpu();assert torch.allclose(actual,expected,atol=1e-6,rtol=1e-4),'ADAM_FIRST_UPDATE_GATE '+n;maxupdate=max(maxupdate,float((actual-expected).abs().max()))
 result={'status':'PASS','label':label,'oracle_seeds':16,'oracle_input_nodes':len(data[0]['src']),'forward_max_abs_error':float((out[:16].detach().cpu().double()-reference.detach()).abs().max()),'loss_FP32':float(loss.detach()),'loss_FP64_reference':float(loss_ref.detach()),'max_parameter_gradient_abs_error':maxgrad,'max_Adam_first_update_abs_error':maxupdate,'full_batch_loss':float(full_loss.detach()),'FP32_training_oracle_FP64_only':True};event('MODEL_NUMERIC_PASS',**result);return result
