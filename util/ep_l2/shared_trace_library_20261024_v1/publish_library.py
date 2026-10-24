from pathlib import Path
import json,hashlib,os,re,sys,collections,gzip
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');NAS=Path('/root/share/mnt164/huangrulin/traces')
sys.path.insert(0,str(R/'tools'));import library_copy as e
objects=json.loads((R/'control/ALL_OBJECTS.json').read_text());bundles=json.loads((R/'control/ALL_BUNDLES.json').read_text());v=e.v9();gate=e.Resources();gate(True)
def canon(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def publish(p,x):e.publish_bytes(p,canon(x),v)
def slug(x):return re.sub('[^A-Za-z0-9_.+-]+','_',x).strip('_') or 'unknown'
def relative_link(path,target):
 path.parent.mkdir(parents=True,exist_ok=True)
 rel=os.path.relpath(target,path.parent)
 if os.path.lexists(path):assert path.is_symlink() and path.resolve()==target.resolve(),('VIEW_COLLISION',str(path));return
 path.symlink_to(rel)
sealed={}
expanded=json.loads((R/'control/EXPANDED_BUNDLES.json').read_text())
architecture_by_sha={m['sha256']:'70' for b in expanded for m in b['members'] if m['relative_path']!='kernelslist.g'}
for index in sorted((R/'control').glob('ARCHIVE_[0-9]*.json.gz')):
 for m in json.loads(gzip.decompress(index.read_bytes()))['members']:
  if m.get('sha256') and m.get('binary_version','UNKNOWN')!='UNKNOWN':
   old=architecture_by_sha.setdefault(m['sha256'],m['binary_version']);assert old==m['binary_version']
for sha,o in objects.items():
 p=Path(o['storage']['path']);s=p.stat();assert p.is_file() and s.st_size==o['size']
 assert p.resolve().is_relative_to(Path('/root/share/mnt164/huangrulin'))
 if 'expected_identity' in o['storage']:assert [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns]==o['storage']['expected_identity']
 elif o['storage'].get('batch_id'):assert (NAS/'bundles/_payload'/o['storage']['batch_id']/'COMMIT.json').is_file()
 sealed[sha]={'sha256':sha,'size':s.st_size,'true164_path':str(p).replace('/root/share/mnt164','/home/shared',1),'verified_identity':[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns],'storage_kind':o['storage']['kind'],'source_provenance':o['sources'],'proof':o['storage']}
assets=[]
for b in bundles:
 gate();bid=b['bundle_id'];directory=NAS/'bundles'/bid;tree=directory/'tree';tree.mkdir(parents=True,exist_ok=True)
 for m in b['members']:
  p=e.safe(tree,m['relative_path']);target=Path(objects[m['sha256']]['storage']['path']);relative_link(p,target)
 kind='fraction' if b['extent']=='FRACTION_OR_TRIM_PATH' else 'regular'
 version='3.1' if b['version']=='3.1' else '2.0-ft' if b['version']=='2.0-ft' else 'unknown' if b['version']=='unconfirmed' else '9.1-capture' if b['suite']=='CUDA Samples' else '1.0-mapped' if b['suite']=='PolyBench/GPU' else 'suite11'
 view=Path('views')/slug(b['suite'])/version/slug(b['program'])/kind/bid
 relative_link(NAS/view,tree)
 architecture=','.join(sorted({architecture_by_sha.get(m['sha256'],'UNKNOWN') for m in b['members'] if m['relative_path']!='kernelslist.g'})) or 'UNKNOWN'
 asset={**b,'kind':kind,'architecture':architecture,'source_version_evidence':b['version'],'version':version,'kernel_launches':len(b['ordered_kernel_members']),'logical_bytes':sum(m['size'] for m in b['members']),'view_path':str(Path('/root/workspace/assets/traces')/view),'relative_view_path':str(view),'relative_tree_path':str(Path('bundles')/bid/'tree'),'availability':'READY_ALL_DECLARED_MEMBERS','scientific_qualification_granted':False,'aliases':sorted(set(b.get('prior_asset_aliases',[])))}
 # Any archive member with different/unknown binary header remains accurately
 # tagged, rather than being promoted solely by directory name.
 versions=set()
 for alias in b['source_aliases']:
  if alias.get('host')=='174_ARCHIVE':versions.add('ARCHIVE_HEADER_EVIDENCE_IN_INDEX')
 if versions:asset['archive_header_evidence']='See immutable archive index; no ISA qualification is granted'
 publish(directory/'MANIFEST.json',asset);assets.append(asset)
issues={'schema':'SHARED_TRACE_INPUT_ISSUES_V1','expanded_input_observations':json.loads((R/'control/INCOMPLETE_INPUTS_RETAINED.json').read_text()),'archive_input_issues':json.loads((R/'control/ARCHIVE_INPUT_ISSUES.json').read_text()),'status':'METADATA_ONLY_NOT_READY_INPUTS','source_disposition':'SOURCE_KEEP'}
publish(NAS/'quarantine/INPUT_ISSUES.json',issues)
statistics=Path('/root/data/ep_l2_main_20261023_v1/worktree/docs/ep_l2/operations/ep_main_sm70_trace_statistics_20261024_v3/PROGRAM_STATISTICS.json')
coverage=[]
for row in json.loads(statistics.read_text()):
 family=lambda p:'particlefilter' if p.startswith('particlefilter') else 'srad' if p.startswith('srad') else p
 matched=[a for a in assets if a['suite']==row['suite'] and family(a['program'])==row['program'] and (a['suite']!='Rodinia' or a['version']=='3.1')]
 coverage.append({'suite':row['suite'],'program_family':row['program'],'registered_assets':len(matched),'regular_assets':sum(a['kind']=='regular' for a in matched),'fraction_assets':sum(a['kind']=='fraction' for a in matched),'availability':'READY_REGISTERED_INPUTS' if matched else 'NO_REGISTERED_COMPLETE_INPUT','source_scope_note':'CUDA source-version denominator remains separate; official archive findings are additional inputs'})
publish(NAS/'catalog/SUITE_COVERAGE.json',{'schema':'SHARED_TRACE_SUITE_COVERAGE_V1','rows':coverage,'archive_additional_programs':sorted({(a['suite'],a['version'],a['program']) for a in assets if not any(r['suite']==a['suite'] and r['program']==family(a['program']) for r in json.loads(statistics.read_text()))})})
body={'schema':'SHARED_SM70_TRACE_LIBRARY_V1','access_scope':'ALL_PROJECTS_IN_174NEW_NAMESPACE','objects':sealed,'assets':sorted(assets,key=lambda a:(a['suite'],a['version'],a['program'],a['kind'],a['bundle_id'])),'issues_path':'quarantine/INPUT_ISSUES.json','coverage_path':'catalog/SUITE_COVERAGE.json','science_acceptance_granted':False,'source_disposition':'SOURCE_KEEP','source_release_bytes':0}
cid=hashlib.sha256(canon(body)).hexdigest();body['catalog_id']=cid
versions=NAS/'catalog/versions';versions.mkdir(exist_ok=True,parents=True);publish(versions/(cid+'.json'),body)
current=NAS/'catalog/CURRENT'
if os.path.lexists(current):assert current.is_symlink() and json.loads(current.read_text())['catalog_id']==cid
else:current.symlink_to('versions/'+cid+'.json')
tools=NAS/'tools';tools.mkdir(exist_ok=True)
source=(R/'tools/trace_assets_public.py').read_bytes();e.publish_bytes(tools/'trace_assets.py',source,v)
wrapper=b'#!/bin/sh\nset -eu\nunset LD_PRELOAD LD_LIBRARY_PATH CUDA_INJECTION64_PATH TRACES_FOLDER PYTHONHOME PYTHONPATH VIRTUAL_ENV CONDA_PREFIX\nSCRIPT=$(/usr/bin/readlink -f -- "$0")\nHERE=$(CDPATH= cd -- "$(/usr/bin/dirname -- "$SCRIPT")" && pwd)\nexec /usr/bin/python3 -I -S -B "$HERE/trace_assets.py" "$@"\n'
e.publish_bytes(tools/'trace-assets',wrapper,v);(tools/'trace-assets').chmod(0o555);(tools/'trace_assets.py').chmod(0o444)
public=Path('/root/workspace/assets');public.mkdir(exist_ok=True)
entry=public/'traces'
if os.path.lexists(entry):assert entry.is_symlink() and entry.resolve()==NAS.resolve()
else:entry.symlink_to(NAS)
bin=public/'bin';bin.mkdir(exist_ok=True)
cmd=bin/'trace-assets'
if os.path.lexists(cmd):assert cmd.is_symlink() and cmd.resolve()==(tools/'trace-assets').resolve()
else:cmd.symlink_to(tools/'trace-assets')
for a in assets:
 for p in [NAS/a['relative_tree_path'],NAS/a['relative_tree_path']/'..',NAS/a['relative_view_path']/'..']:
  p.resolve().chmod(0o555)
receipt={'status':'PUBLISHED_SHARED_READONLY_DATA_INTERFACE','catalog_id':cid,'assets':len(assets),'objects':len(sealed),'unique_content_bytes':sum(o['size'] for o in sealed.values()),'public_root':str(entry),'public_command':str(cmd),'all_projects_no_activation':True,'filesystem_root_user_security_barrier_claimed':False,'readonly_scope':'Public command exposes only list/show/verify and explicit new local materialization; sealed metadata and data are not writable through it','source_keep':True,'scientific_starts':0}
publish(NAS/'receipts/LIBRARY_PUBLICATION.json',receipt);(R/'control/LIBRARY_PUBLICATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
