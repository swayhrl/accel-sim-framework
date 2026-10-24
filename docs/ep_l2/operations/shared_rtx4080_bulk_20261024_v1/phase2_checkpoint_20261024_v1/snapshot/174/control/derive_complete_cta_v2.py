#!/usr/bin/env python3
"""Independent explicit CTA-stride policy. Not a reconstruction of unknown historical crop rules."""
import pathlib,json,lzma,re,hashlib,importlib.util,os,math,time,argparse,shutil
PARSER_SHA='f4a811c779e9b106c0977af45634d1b7dc01025c9e9b2805b74de6c6c82b879b'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):
   start=time.monotonic();h.update(b);time.sleep(max(0,1/15-(time.monotonic()-start)))
 return h.hexdigest()
def save(p,o):
 with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def blocks(path):
 """Stream one block's events; no entire CTA or app is buffered."""
 with lzma.open(path,'rt') as inp:
  active=False
  for line in inp:
   if line.strip()=='#BEGIN_TB':assert not active;active=True;yield 'begin',line
   elif line.startswith('thread block = '):assert active;yield 'cta',tuple(map(int,re.findall(r'\d+',line)))
   elif line.strip()=='#END_TB':assert active;active=False;yield 'end',line
   elif active:yield 'body',line
   else:yield 'header',line
  assert not active,'truncated TB'
def check_warps(warps,threads):
 assert set(warps)==set(range((threads+31)//32)),'missing/extra warp'
 for wid,w in warps.items():
  assert w['n']==w['expected'] and w['exited']==(1<<min(32,threads-wid*32))-1,'incomplete warp/EXIT'
def consume(line,warps,current,parse,threads):
 if line.startswith('warp = '):
  current=int(line.split('=',1)[1]);assert current not in warps
  warps[current]={'n':0,'expected':None,'exited':0};return current
 if line.startswith('insts = '):assert current is not None;warps[current]['expected']=int(line.split('=',1)[1]);return current
 if not line.strip():return current
 assert current is not None
 r=parse(line);w=warps[current];allowed=(1<<min(32,threads-current*32))-1
 assert current<(threads+31)//32 and all(not r[k]&~allowed for k in ['mask','active','pred'])
 assert not r['mask']&w['exited'],'executed after EXIT'
 if r['opcode']=='EXIT':w['exited']|=r['mask']
 w['n']+=1;return current
def verify_derived(root,parent,parse):
 asset=json.loads((root/'ASSET.json').read_text());selected=iter((root/'SELECTION_MAP.jsonl').open());total=0
 for kernel in asset['kernels']:
  threads=math.prod(kernel['block']);count=0;warps={};current=None;digest=None;expected=None
  for event,value in blocks(root/kernel['path']):
   if event=='begin':digest=hashlib.sha256(value.encode());warps={};current=None;expected=json.loads(next(selected));assert expected['kernel']==kernel['name']
   elif event=='cta':
    assert list(value)==expected['derived'] and value==(count,0,0)
    linear=count*asset['sampling']['stride'];gx,gy,gz=kernel['original_grid']
    assert expected['origin_linear']==linear and expected['origin']==[linear%gx,(linear//gx)%gy,linear//(gx*gy)]
   elif event=='body':digest.update(value.encode());current=consume(value,warps,current,parse,threads)
   elif event=='end':
    digest.update(value.encode());check_warps(warps,threads);assert digest.hexdigest()==expected['parent_body_sha256'],'selected record bytes differ from parent'
    assert sum(w['n'] for w in warps.values())==expected['records'];total+=expected['records'];count+=1
   elif event=='header' and value.startswith('-grid dim = '):assert tuple(map(int,re.findall(r'\d+',value)))==(kernel['selected_ctas'],1,1)
  assert count==kernel['selected_ctas']
 try:next(selected)
 except StopIteration:pass
 else:raise AssertionError('unused/extra selection mapping')
 return {'status':'COMPLETE_CTA_PARENT_MEMBER_EQUALITY_PASS','selected_records':total,'selected_ctas':sum(k['selected_ctas'] for k in asset['kernels']),'all_selected_warps_complete':True,'all_selected_active_predicate_masks_within_physical_launch':True,'full_xz_crc_and_eof':True,'all_selected_bodies_byte_identical_parent_except_declared_cta_coordinate_remap':True}
def derive(parent,root,stride,qualification_fixture=False):
 assert stride>=1 and not root.exists();root.mkdir(parents=True)
 commit=json.loads((parent/'COMMIT.json').read_text());assert commit['kind']==('SYNTHETIC_DERIVATION_FIXTURE' if qualification_fixture else 'FULL_APPLICATION_TRACE') and commit['status']=='COMMITTED_VERIFIED'
 assert sha(parent/'MANIFEST.json')==commit['manifest_sha256'];manifest=json.loads((parent/'MANIFEST.json').read_text())
 for f in manifest['files']:
  p=parent/f['path'];assert parent in p.parents and not p.is_symlink() and p.stat().st_size==f['bytes'] and sha(p)==f['sha256']
 full=json.loads((parent/'ASSET.json').read_text());assert full['producer_semantic_qualification']==('SYNTHETIC_TYPED_BODY_FIXTURE_NOT_GPU_PROOF' if qualification_fixture else 'ADA7_ORDINARY_FULL_RECORD_PASS')
 parser=parent/'contract/validate_v7.py';assert sha(parser)==PARSER_SHA
 spec=importlib.util.spec_from_file_location('frozen_parser',parser);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 validation=json.loads((parent/'FULL_RECORD_VALIDATION.json').read_text());by_name={pathlib.Path(k['name']).name.replace('.trace.xz','.traceg.xz'):k for k in validation.get('per_kernel',[])}
 # Imported first Vector predates the compact per-kernel receipt; use parsed parent header as an independent structural check.
 (root/'traces').mkdir();(root/'tools').mkdir();shutil.copyfile(parser,root/'tools/validate_v7.py');shutil.copyfile(__file__,root/'tools/derive_complete_cta_v1.py')
 kernels=[];maps=root/'SELECTION_MAP.jsonl'
 with maps.open('x') as outmap:
  for source in sorted((parent/'traces').glob('*.traceg.xz')):
   # Header is small and read separately; records stay streaming.
   header=[]
   with lzma.open(source,'rt') as inp:
    for line in inp:
     if line.strip()=='#BEGIN_TB':break
     header.append(line)
   grid=tuple(map(int,re.findall(r'\d+',next(x for x in header if x.startswith('-grid dim = ')))));block=tuple(map(int,re.findall(r'\d+',next(x for x in header if x.startswith('-block dim = ')))));threads=math.prod(block)
   assert 0<threads<=1024;total=math.prod(grid);nselected=(total+stride-1)//stride;dest=root/'traces'/source.name
   for i,line in enumerate(header):
    if line.startswith('-grid dim = '):header[i]='-grid dim = (%d,1,1)\n'%nselected
   count=0;selected=0;keep=False;warps={};current=None;digest=None;original=None
   with dest.open('xb') as raw:
    with lzma.LZMAFile(raw,'w',preset=1) as out:
     out.write(''.join(header).encode())
     for event,value in blocks(source):
      if event=='begin':begin=value;keep=False;warps={};current=None
      elif event=='cta':
       x,y,z=value;linear=x+grid[0]*(y+grid[1]*z);assert (0<=x<grid[0] and 0<=y<grid[1] and 0<=z<grid[2]) and linear==count,'noncanonical/missing parent CTA';count+=1;keep=linear%stride==0;original=value
       if keep:out.write(begin.encode());out.write(('thread block = %d,0,0\n'%selected).encode());digest=hashlib.sha256(begin.encode())
      elif event=='body' and keep:out.write(value.encode());digest.update(value.encode());current=consume(value,warps,current,module.parse,threads)
      elif event=='end' and keep:
       out.write(value.encode());digest.update(value.encode());check_warps(warps,threads)
       outmap.write(json.dumps({'kernel':source.name,'origin':original,'origin_linear':(count-1),'derived':[selected,0,0],'parent_body_sha256':digest.hexdigest(),'records':sum(w['n'] for w in warps.values())})+'\n');selected+=1
    raw.flush();os.fsync(raw.fileno())
   assert count==total and selected==nselected
   kernels.append({'name':source.name,'path':'traces/'+source.name,'original_grid':grid,'derived_grid':[nselected,1,1],'block':block,'parent_ctas':total,'selected_ctas':nselected,'parent_grouped_sha256':sha(source),'derived_grouped_sha256':sha(dest)})
  outmap.flush();os.fsync(outmap.fileno())
 for name in ['kernelslist.g']:
  shutil.copyfile(parent/'traces'/name,root/'traces'/name)
 asset={'schema':'COMPLETE_CTA_DERIVED_TRACE_V1','kind':'DERIVED_COMPLETE_CTA_TRACE','asset_id':full['asset_id']+'_CTA_STRIDE_%d_V1'%stride,'parent_asset_id':full['asset_id'],'parent_commit_sha256':sha(parent/'COMMIT.json'),'parent_manifest_sha256':commit['manifest_sha256'],'parent_binary_sha256':full['binary_sha256'],'parent_full_application':full['full_application'],'capture_gpu_uuid':full['capture_gpu_uuid'],'actual_cubin_arch':full['actual_cubin_arch'],'suite':full['suite'],'source_version':full['source_version'],'program':full['program'],'numerical_status':'INHERITED_PARENT_ONLY: '+full['numerical_status'],'producer_semantic_qualification':'PARENT_ADA7_FULL_RECORD_PASS_WITH_EXACT_SELECTED_BODY_EQUALITY','consumer_qualification':'NOT_GRANTED; sparse CTA grid remap and cache-context profile require explicit qualification','sampling':{'kind':'DETERMINISTIC_COMPLETE_CTA_STRIDE','stride':stride,'selection':'all kernels retained; original CUDA linear CTA index % stride == 0','linear_index':'x + Nx*(y + Ny*z)','coordinate_remap':'selected original indices in ascending CUDA order -> (j,0,0); original block shape and all SASS/masks/addresses/dependencies retained','historical_crop_equivalence':'NOT_CLAIMED; independent explicit policy'},'kernels':kernels,'generator_sha256':sha(pathlib.Path(__file__)),'frozen_parser_sha256':PARSER_SHA,'gpu_capture_repeated':False,'source_keep':True,'release_bytes':0}
 if qualification_fixture:asset.update(kind='SYNTHETIC_DERIVATION_FIXTURE_OUTPUT_NOT_FORMAL_WORKLOAD',producer_semantic_qualification='SYNTHETIC_TYPED_BODY_TRANSFORM_ONLY; NOT_GPU_CAPTURE_QUALIFICATION')
 save(root/'ASSET.json',asset);result=verify_derived(root,parent,module.parse);save(root/'DERIVED_VALIDATION.json',result)
 print(json.dumps(dict(result,asset_id=asset['asset_id'],path=str(root))))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('parent');a.add_argument('dest');a.add_argument('--stride',type=int,default=40);a.add_argument('--qualification-fixture',action='store_true');args=a.parse_args();derive(pathlib.Path(args.parent).resolve(),pathlib.Path(args.dest).resolve(),args.stride,args.qualification_fixture)
