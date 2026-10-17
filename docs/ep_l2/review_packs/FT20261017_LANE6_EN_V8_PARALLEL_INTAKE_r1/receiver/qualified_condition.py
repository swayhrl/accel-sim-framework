"""Positive native-reader mapping of a published Lane5 r19 condition envelope.

This extends only the exact-config mapping of the frozen native reader. It
does not change the original producer object, feature/ideal/resource gates,
scientific authority, qualified certificate, raw input or runtime options.
"""
import hashlib,importlib.util,json,sys,types
from pathlib import Path

def require(ok,reason):
 if not ok:raise ValueError(reason)

def digest(raw):return hashlib.sha256(raw).hexdigest()

def qualified_headroom_mode(repo,adapter,q,producer,row,spec,result,published):
 require(adapter.get('experiment_id')=='EPL2_DOWNSTREAM_HEADROOM_R19','Exact experiment required')
 regime=adapter.get('regime');require(regime in ('Q4','D4','D2','L25'),'Only initial qualified r19 conditions accepted by this revision')
 require(spec.get('experiment_id')==adapter['experiment_id'] and spec.get('regime')==regime,'Spec/adapter condition mismatch')
 for key in ('experiment_id','regime'):
  if key in row:require(row[key]==adapter[key],'CSV condition mismatch')
 binding=q.get('downstream_config_qualification');require(isinstance(binding,dict),'Missing official independent condition envelope')
 path=binding['path'];require('docs/ep_l2/' in path and '..' not in Path(path).parts,'Unmapped condition path')
 relative=path[path.index('docs/ep_l2/'):];raw=published(adapter['qualification_publication'],relative)
 require(digest(raw)==binding['sha256'] and Path(path).read_bytes()==raw,'Condition envelope bytes differ')
 envelope=json.loads(raw)
 require(envelope['status']=='INDEPENDENT_CONFIG_PASS' and envelope['coordination_commit']=='28e8fce027046643b909c58469e9c7697522a3df','Not independently qualified r19')
 require(envelope['experiment_id']==adapter['experiment_id'] and envelope['regime']==regime,'Wrong published condition')
 for key in ('core_source_commit','framework_source_commit','binary_sha256'):require(envelope['identity'][key]==spec['identity'][key]==q[key],'Condition source/binary mismatch')
 require(q['binary_sha256']=='23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee','New runtime requires new qualification')
 for item in envelope['evidence']:
  path=item['path'];require('docs/ep_l2/' in path,'Unmapped condition evidence')
  raw=published(adapter['qualification_publication'],path[path.index('docs/ep_l2/'):]);require(digest(raw)==item['sha256'],'Published affected production evidence differs')
 # Run the actual published Lane5 read-only positive validator, not a draft.
 vb=adapter.get('headroom_validator_binding');require(isinstance(vb,dict),'Exact published Lane5 validator binding required')
 require(vb['path']=='util/ep_l2/ft_lane5/headroom_config.py','Wrong validator path')
 source=published(vb['publication_commit'],vb['path']);require(digest(source)==vb['sha256'],'Published validator source differs')
 previous=sys.modules.get('registry');stub=types.ModuleType('registry')
 stub.canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
 namespace={'__name__':'lane6_published_read_only_headroom_config'}
 try:
  sys.modules['registry']=stub;exec(compile(source,vb['path'],'exec'),namespace)
 finally:
  if previous is None:sys.modules.pop('registry',None)
  else:sys.modules['registry']=previous
 require(namespace.get('EXPERIMENT')==adapter['experiment_id'] and namespace.get('COORDINATION')=='28e8fce027046643b909c58469e9c7697522a3df','Validator contract mismatch')
 audit=result['audit'];checked=namespace['validate'](spec,q,audit['configs'],audit['auxiliary_assets'])
 require(checked is not None and checked['regime']==regime,'Condition validator rejected/misclassified regime')
 mode=dict(producer['modes'][row['mode']]);condition_mode=envelope['modes'][row['mode']]
 mode['runtime_config_sha256']=condition_mode['runtime_config_sha256']
 mode['ordered_config_manifest']=condition_mode['ordered_configs']
 return mode
