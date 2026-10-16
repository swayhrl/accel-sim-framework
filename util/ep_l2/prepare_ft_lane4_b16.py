#!/usr/bin/env python3
"""Derive one ideal run from Lane 5's independently qualified baseline spec.

The baseline remains owned by Lane 5, and its exact source/binary/trace identity
is retained. This tool does not manufacture or qualify a common release.
"""
import argparse
import copy
import json
from pathlib import Path
from run_ft_lane4_diagnostic import B16_MODES, ROOT, load_tools, validate_b16_variant, inspect_baseline


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-spec',type=Path,required=True)
    p.add_argument('--mode',choices=B16_MODES,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();client,api,tools=load_tools()
    baseline=json.loads(a.baseline_spec.read_text());baseline_audit=inspect_baseline(baseline,tools)
    spec=copy.deepcopy(baseline)
    spec.update(owner='lane4',mode=a.mode,campaign_class='B16_IDEAL_DIAGNOSTIC',
                baseline_spec=baseline,baseline_run_key=api.run_key(baseline['identity']),
                lane5_dependency=client,
                baseline_qualified_release_sha256=baseline_audit['qualified_release_sha256'])
    overlay=ROOT/'tests/ep_l2/ft_lane4/b16'/(a.mode.lower()+'.config')
    spec['configs'].append({'name':'lane4-ideal-vector.config','path':str(overlay)})
    spec['identity']['ideal_vector']=B16_MODES[a.mode]
    configs=tools.asset_manifest(spec['configs'],ordered=True)
    assets=tools.asset_manifest(spec['auxiliary_assets']) if spec['auxiliary_assets'] else []
    traces=tools.asset_manifest(spec['trace_files'])
    spec['identity']['runtime_config_sha256']=tools.content_hash(
        {'ordered_configs':configs,'auxiliary_assets':assets,'environment':spec.get('environment',{})})
    validate_b16_variant(spec,tools,api)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x') as f:
        json.dump({'run_key':api.run_key(spec['identity']),'spec':spec,
                   'audit':{'configs':configs,'assets':assets,'traces':traces}},f,indent=2);f.write('\n')
    print(api.run_key(spec['identity']))


if __name__=='__main__':main()
