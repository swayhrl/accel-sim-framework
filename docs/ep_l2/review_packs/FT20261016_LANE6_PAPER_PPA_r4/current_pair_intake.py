#!/usr/bin/python3
"""Lane-6 bridge: exact Lane-5 V2 API + unchanged r3 native/eleven-gate validation.

No registry instance, run launch, model test or old artifact mutation. A live
Lane-5 fetch and final ref check are mandatory; never accept from cached state.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
R3=HERE.with_name('FT20261016_LANE6_PAPER_PPA_r3')
R3_COMMIT='70675cc3b2cd63e29fc7ab2b0b54dc924011f5e4'


def require(ok,message):
    if not ok:raise ValueError(message)


def vendor_api():
    source=json.loads((HERE/'SOURCE_MANIFEST.json').read_text())
    for name in ['acceptance.py','registry.py']:
        records=[r for r in source['sources'] if r['path']=='util/ep_l2/ft_lane5/'+name]
        require(len(records)==1 and hashlib.sha256((HERE/'upstream_lane5'/name).read_bytes()).hexdigest()==records[0]['sha256'],'Pinned Lane5 API bytes changed')
    def module(name,path):
        spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    previous=sys.modules.get('registry')
    try:
        sys.modules['registry']=module('lane6_pinned_registry',HERE/'upstream_lane5/registry.py')
        api=module('lane6_pinned_acceptance',HERE/'upstream_lane5/acceptance.py')
    finally:
        if previous is None:sys.modules.pop('registry',None)
        else:sys.modules['registry']=previous
    return api


def live_head(repo):
    raw=subprocess.check_output(['git','ls-remote','--exit-code','origin','refs/heads/hrl/ep-l2-ft20261016-lane5-v1'],cwd=repo,timeout=25).decode().splitlines()
    require(len(raw)==1,'Ambiguous current authority');return raw[0].split()[0]


def legacy_modules(repo):
    for name in ['acceptance_gate.py','result_intake.py','native_pair_intake.py']:
        relative=str((R3/name).relative_to(Path(repo).resolve()))
        b=subprocess.check_output(['git','show',R3_COMMIT+':'+relative],cwd=repo)
        require(b==(R3/name).read_bytes(),'Frozen r3 consumer bytes changed')
    if str(R3) not in sys.path:sys.path.insert(0,str(R3))
    import acceptance_gate,native_pair_intake,result_intake
    return acceptance_gate,native_pair_intake,result_intake


def bridge(repo,state):
    api=vendor_api();api.current_manifest(state)
    require(state['binding']['kind']=='FETCHED_GITHUB_BRANCH','Paper intake requires fetched GitHub authority')
    old,_,_=legacy_modules(repo)
    class V2Context(old.AcceptanceSnapshot):
        def assert_fresh(self):
            api.current_manifest(state)
            require(live_head(repo)==state['binding']['publication_commit'],'Authority advanced; fetch/rebind before emission')
        def check_run(self,run):
            api.require_current_result(run['identity'],run['raw_log_sha256'],run['summary']['cycles'],run['summary']['instructions'],state)
            require(run['status']=='COMPLETE_VALID','Original terminal is not complete')
            matches=[r for r in state['manifest']['rows'] if r['run_key']==run['run_key']]
            require(len(matches)==1 and matches[0]['mode']==run['mode'] and matches[0]['workload']==run['workload'],'Mode/workload acceptance mismatch')
        def provenance(self):
            return {'authority':state['binding'],'consumer':'PINNED_LANE5_V2_API_WITH_R3_NATIVE_AND_ELEVEN_GATES',
                    'schema':api.SCHEMA,'legacy_validator_commit':R3_COMMIT}
    context=V2Context();context.assert_fresh();return context


def fetch_state(repo):
    # Keep exact upstream API unchanged; bound the entire worker externally.
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='gc.auto',GIT_CONFIG_VALUE_0='0')
    try:
        output=subprocess.check_output([sys.executable,str(Path(__file__).resolve()),'--fetch-worker',str(repo)],env=env,timeout=45,stderr=subprocess.PIPE)
    except (subprocess.SubprocessError,OSError) as e:
        raise ValueError('Current scientific authority unavailable; no cached fallback') from e
    return json.loads(output)


def consume(repo,adapter,state):
    context=bridge(repo,state);_,native,results=legacy_modules(repo)
    spec={**adapter,'current_acceptance':context.provenance()}
    packet=native.read_native_packet(repo,spec,context)
    summary=results.summarize(packet,context)
    require(bool(summary['pairs']),'No current scientifically accepted complete pair; no summary emitted')
    context.assert_fresh()
    return {'summary':summary,'normalized_packet':packet,'current_authority':state['binding']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch-worker',type=Path);parser.add_argument('--framework-repo',type=Path);parser.add_argument('--adapter',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.fetch_worker:
        print(json.dumps(vendor_api().fetch_current_authority(args.fetch_worker),sort_keys=True));return
    require(args.framework_repo is not None and args.adapter is not None and args.output is not None,'Explicit repo/new-release adapter/new output required')
    require(not args.output.exists(),'Do not overwrite a frozen revision')
    state=fetch_state(args.framework_repo.resolve());data=consume(args.framework_repo.resolve(),json.loads(args.adapter.read_text()),state)
    bridge(args.framework_repo.resolve(),state).assert_fresh()
    with args.output.open('x') as stream:json.dump(data,stream,sort_keys=True,indent=2);stream.write('\n')

if __name__=='__main__':main()
