"""Prepare r19 specs from frozen H0 complete inputs; never grants launch permission."""
import argparse
import copy
import json
from pathlib import Path

from registry import write_json,run_key
from run import asset_manifest,content_hash,require
from headroom_config import EXPERIMENT,OVERRIDES,options,H0

REPO=Path(__file__).resolve().parents[3]
H=REPO/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5'
ORIGINAL=Path('/workspace/results/ep_l2_ft20261016/lane5_a1_b1_formal_preparation_r1/specs')


def prepare(regime,overlays,qualified_release,out,runner_source,workloads=('convolutionSeparable','FWT_7_21')):
    require(regime in OVERRIDES,'Unsupported/independently unqualified downstream path')
    require(options(overlays)==OVERRIDES[regime],'Overlay is not exact r19 whitelist')
    require(not out.exists(),'Preparation revision exists; preserve old specs')
    out.mkdir(parents=True)
    native=json.loads((ORIGINAL/'FWT_7_21_B16_BANKED.json').read_text())['native_legacy_semantic_proof']
    rows=[]
    for workload in workloads:
        for mode in ('B16_BANKED','U_WB16'):
            spec=copy.deepcopy(json.loads((ORIGINAL/(workload+'_'+mode+'.json')).read_text()))
            require(spec['identity']['runtime_config_sha256']==H0[mode],'Unexpected H0 source spec')
            spec.update(experiment_id=EXPERIMENT,regime=regime,runner_tooling_source_commit=runner_source,qualified_release=str(qualified_release))
            # Existing ordinary input scope certificate for nonlegacy SAD/vectorAdd.
            if workload in ('convolutionSeparable','FWT_7_21'):spec['native_legacy_semantic_proof']=native
            for path in overlays:spec['configs'].append({'name':'config-'+str(len(spec['configs']))+'.config','path':str(path.resolve(strict=True))})
            configs=asset_manifest(spec['configs'],ordered=True);assets=asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else []
            spec['identity']['runtime_config_sha256']=content_hash({'ordered_configs':configs,'auxiliary_assets':assets,'environment':spec['environment']})
            path=out/(workload+'_'+mode+'.json');write_json(path,spec)
            rows.append({'workload':workload,'mode':mode,'spec':str(path),'run_key':run_key(spec['identity']),'runtime_config_sha256':spec['identity']['runtime_config_sha256'],'trace_content_sha256':spec['identity']['trace_content_sha256'],'effective_options':options([r['path'] for r in spec['configs']]),'ordered_configs':configs,'auxiliary_assets':assets,'environment':spec['environment']})
    report={'experiment_id':EXPERIMENT,'regime':regime,'status':'PREPARED_NOT_AUTHORIZED_PENDING_OFFICIAL_CONDITION_AND_INDEPENDENT_CHECKS','qualified_release':str(qualified_release),'new_application_runs':0,'H0_unchanged':True,'specs':rows}
    write_json(out/'PREPARATION.json',report);return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--regime',choices=tuple(OVERRIDES),required=True);p.add_argument('--overlays',type=Path,nargs='+',required=True);p.add_argument('--qualified-release',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--runner-source',required=True);p.add_argument('--workloads',nargs='+',choices=('convolutionSeparable','FWT_7_21','vectorAdd_4M','sad'),default=['convolutionSeparable','FWT_7_21']);a=p.parse_args()
    r=prepare(a.regime,a.overlays,a.qualified_release,a.out,a.runner_source,a.workloads);print(json.dumps({'status':r['status'],'regime':a.regime,'specs':len(r['specs'])}))
if __name__=='__main__':main()
