from common import *
import zipfile,sys,subprocess
urls={
'ogb_official.html':'https://ogb.stanford.edu/docs/nodeprop/',
'amazon_license.txt':'https://s3.amazonaws.com/amazon-reviews-pds/LICENSE',
'amazon_license_s3direct.txt':'https://amazon-reviews-pds.s3.amazonaws.com/LICENSE',
'dgl_wheels_torch22_cu121.html':'https://data.dgl.ai/wheels/torch-2.2/cu121/repo.html',
'dgl_v240_dataset.py':'https://raw.githubusercontent.com/dmlc/dgl/v2.4.0/python/dgl/graphbolt/impl/ondisk_dataset.py',
'dgl_v240_advanced.py':'https://raw.githubusercontent.com/dmlc/dgl/v2.4.0/examples/graphbolt/pyg/node_classification_advanced.py',
'dgl_v240_neighbor_sampler.py':'https://raw.githubusercontent.com/dmlc/dgl/v2.4.0/python/dgl/graphbolt/impl/neighbor_sampler.py',
'dgl_v240_gpu_feature.py':'https://raw.githubusercontent.com/dmlc/dgl/v2.4.0/python/dgl/graphbolt/impl/gpu_cached_feature.py',
'dgl_v240_gpu_graph.py':'https://raw.githubusercontent.com/dmlc/dgl/v2.4.0/python/dgl/graphbolt/impl/gpu_graph_cache.py',
'dgl_v240_subgraph.py':'https://raw.githubusercontent.com/dmlc/dgl/v2.4.0/python/dgl/graphbolt/sampled_subgraph.py',
'dgl_fixed_advanced.py':'https://raw.githubusercontent.com/dmlc/dgl/3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/pyg/node_classification_advanced.py',
}
for name,url in urls.items():
 r,b=request(url,'source/'+name);print(name,r['status'] if 'status'in r else r.get('error'),r['bytes'],flush=True)
 if r.get('status')!=200 and b:(ROOT/'source'/name).write_bytes(b)
old=pathlib.Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014');torch=old/'wheels/torch-2.2.0+cu121-cp310-cp310-linux_x86_64.whl'
with zipfile.ZipFile(torch) as z:
 meta=z.read(next(n for n in z.namelist() if n.endswith('.dist-info/METADATA'))).decode();print('TORCH_REQUIRES',[s for s in meta.splitlines() if s.startswith('Requires-Dist:')]);print('TORCH_EXPANDED',sum(x.file_size for x in z.infolist()))
print('OLD_PYTHON',subprocess.check_output([str(old/'venv/bin/python'),'-c','import sys; print(sys.executable,sys.version,sys.base_prefix)'],text=True))
print('DEPENDENCY_CACHE_EXPANDED',sum(sum(x.file_size for x in zipfile.ZipFile(p).infolist()) for p in (old/'wheels').glob('nvidia*.whl')))
