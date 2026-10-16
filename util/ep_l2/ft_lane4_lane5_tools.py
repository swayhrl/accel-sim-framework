"""Load exact Lane5-published runner bytes while sharing its original registry."""
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(root,results):
    client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
    registry_path=Path(client['registry_client']).resolve()
    if digest(registry_path)!=client['registry_client_sha256']:
        raise ValueError('Lane5 registry client changed')
    sys.path.insert(0,str(registry_path.parent))
    registry=importlib.import_module('registry')
    if Path(registry.__file__).resolve()!=registry_path:raise ValueError('wrong registry module')
    if not client.get('runner_sha256'):
        return client,registry,importlib.import_module('run')
    commit=client['runner_source_commit']
    if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('invalid published Lane5 runner commit')
    folder=Path(results)/'tool_cache'/commit;folder.mkdir(parents=True,exist_ok=True)
    manifests=[]
    for name in ['validate.py','feature_schema.py','run.py']:
        raw=subprocess.check_output(['git','-C',str(root),'show',commit+':util/ep_l2/ft_lane5/'+name])
        path=folder/name;expected=hashlib.sha256(raw).hexdigest()
        if path.exists():
            if digest(path)!=expected:raise ValueError('frozen Lane5 tool cache changed')
        else:
            with path.open('xb') as stream:stream.write(raw)
        manifests.append(dict(path=str(path),sha256=expected,git_source=commit+':util/ep_l2/ft_lane5/'+name))
    if digest(folder/'run.py')!=client['runner_sha256']:
        raise ValueError('Lane5 runner/source contract mismatch')
    # run imports immutable functions from these exact modules. Temporary
    # aliases avoid mixing in another lane's uncommitted working-tree edits.
    missing=object();previous={k:sys.modules.get(k,missing) for k in ['validate','feature_schema']}
    try:
        for name in ['validate','feature_schema','run']:
            module_name='lane5_'+name+'_'+commit
            spec=importlib.util.spec_from_file_location(module_name,folder/(name+'.py'))
            module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module
            spec.loader.exec_module(module)
            if name!='run':sys.modules[name]=module
            else:runner=module
    finally:
        for name,value in previous.items():
            if value is missing:sys.modules.pop(name,None)
            else:sys.modules[name]=value
    client['consumed_runner_inputs']=manifests
    client['registry_authority_note']='Original Lane5 registry module/path and central lock; runner support files only are frozen locally'
    return client,registry,runner
