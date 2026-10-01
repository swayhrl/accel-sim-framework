#!/usr/bin/env python3
"""Verify frozen C16 Problem Discovery V2 authorities without executing science."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import posixpath
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


PACKS = {
    'base_terminal': ('ca6c33ae0431d91aa7c6a43cbb79522402dd7580', '39d7d3f64e79870ff5aa5af3cddf3476b0e888d9', 'C16_AI_WORKLOAD_EXPLORATION_WAVE_TERMINAL_SYNTHESIS_174NEW_V1'),
    'literature': ('7aa517f7ece4478b19f22ed6cd10659b964a53f9', 'e6bccd5c126a71f3dcca056a2a877a8553c32296', 'C16_PROBLEM_DISCOVERY_V2_LITERATURE_PROBLEM_MAP'),
    'cross_lineage': ('734e6a7ca49bd8cbf16eeb0702cf80755afc23f1', '997f71ed191c5d707dfe169ad9dbdda652448010', 'C16_PROBLEM_DISCOVERY_V2_CROSS_LINEAGE_BEHAVIOR_SCREEN_174NEW_V1'),
    'translation': ('8bf4b21d408d367805a61beb9662db416625a407', '6c7cc52a19ded6890fa94f2b2fb0d355032d02f6', 'C16_PROBLEM_DISCOVERY_V2_TRANSLATION_TLB_SCREEN'),
    'nearest_neighbor': ('39c9a98938045a47903dd1b25fffba012e2dfae3', '36dbba11c04d670d7a383a330f2c510d9d5d95c2', 'C16_DEEPSEEK_WEIGHT_LINE_REVISIT_NEAREST_NEIGHBOR_GUARD_V1'),
    'deepseek_oracle': ('d23e0fd263cd9ff2b144f3d023ab60c567afb6f4', 'ec1c2baa2fd167765b60468da5c1b17bb84c0010', 'C16_DEEPSEEK_WEIGHT_LINE_REVISIT_ORACLE_SCREEN_174NEW_V1'),
}
PREFIX = 'docs/vm_tlb/review_packs'
SHA_LINE = re.compile(r'^([0-9a-f]{64})  (.+)$')


def git(*args: str) -> bytes:
    return subprocess.check_output(('git', *args))


def historical(commit: str, path: str) -> bytes:
    return git('show', f'{commit}:{path}')


def historical_json(name: str, filename: str = 'FINAL_DECISION.json') -> dict:
    commit,_,pack = PACKS[name]
    return json.loads(historical(commit, f'{PREFIX}/{pack}/{filename}'))


def verify_manifest(name: str) -> dict:
    commit,expected_tree,pack = PACKS[name]
    actual_commit = git('rev-parse', f'{commit}^{{commit}}').decode().strip()
    actual_tree = git('rev-parse', f'{commit}^{{tree}}').decode().strip()
    assert actual_commit == commit and actual_tree == expected_tree, name
    folder=f'{PREFIX}/{pack}'
    manifest=historical(commit,f'{folder}/SHA256SUMS')
    count=0
    for line in manifest.decode().splitlines():
        match=SHA_LINE.fullmatch(line)
        assert match, (name,line)
        expected,relpath=match.groups()
        assert not relpath.startswith('/'), (name,relpath)
        path=posixpath.normpath(posixpath.join(folder,relpath))
        assert not path.startswith('../') and path!='..', (name,path)
        actual=hashlib.sha256(historical(commit,path)).hexdigest()
        assert actual==expected, (name,path,expected,actual)
        count+=1
    assert count>0, name
    decision_file='FINAL_PROJECT_STATE.json' if name=='base_terminal' else 'FINAL_DECISION.json'
    return dict(commit=commit,tree=actual_tree,review_pack=folder,
                sha256sums_sha256=hashlib.sha256(manifest).hexdigest(),sha256sums_entries_verified=count,
                final_decision_blob_sha256=hashlib.sha256(historical(commit,f'{folder}/{decision_file}')).hexdigest())


def check_final_state(state: dict, handoff: str) -> None:
    assert state['status']=='C16_PROBLEM_DISCOVERY_V2_COMPLETE'
    assert state['decision']=='NO_CURRENT_C16_ARCHITECTURE_PROBLEM_READY_FOR_PROMOTION'
    for key in ('literature_qualified_problem_count','translation_qualified_problem_count','cross_lineage_qualified_problem_count','active_oracle_candidate_count','active_promotion_candidate_count'):
        assert state[key]==0, key
    assert state['new_experiment_authorized'] is False
    for field,name in (('base_terminal_commit','base_terminal'),('literature_commit','literature'),
                       ('cross_lineage_commit','cross_lineage'),('translation_commit','translation'),
                       ('nearest_neighbor_commit','nearest_neighbor'),('deepseek_oracle_commit','deepseek_oracle')):
        assert state[field]==PACKS[name][0], field
    assert state['translation_time_headroom']=='TRANSLATION_TIME_HEADROOM_UNKNOWN'
    revisit=state['deepseek_revisit']
    assert revisit['corrected_interpretation']=='SAME-WARP EXACT-BYTE REVISIT'
    assert revisit['cross_warp_revisit_count']==0
    assert revisit['cross_cta_duplicate_count']==0
    assert revisit['exact_byte_redundancy_fraction']==0.5
    assert revisit['sector_redundancy_fraction']==0.5
    assert revisit['timing_headroom']=='UNKNOWN'
    assert revisit['final_classification']=='GEMVX_SHAPE_WORK_DECOMPOSITION_EFFECT'
    assert revisit['project_status']=='SOFTWARE_KERNEL_SHAPE_OBSERVATION_ONLY'
    assert revisit['native_service_oracle_contract']=='NOT_ISSUED'
    assert 'cross-warp shared weight line' not in revisit['corrected_interpretation'].lower()
    assert 'cross-warp shared weight line' not in handoff.lower()
    assert 'NO_CURRENT_C16_ARCHITECTURE_PROBLEM_READY_FOR_PROMOTION' in handoff
    assert 'TRANSLATION_TIME_HEADROOM_UNKNOWN' in handoff
    assert 'SOFTWARE_KERNEL_SHAPE_OBSERVATION_ONLY' in handoff


def aggregate_oracle_detail() -> dict:
    commit,_,pack=PACKS['deepseek_oracle']
    data=historical(commit,f'{PREFIX}/{pack}/LINE_REVISIT_DETAIL.tsv').decode('utf-8')
    counts=defaultdict(Counter)
    for row in csv.DictReader(io.StringIO(data),delimiter='\t'):
        lineage=row['lineage']
        assert lineage in ('DEEPSEEK','OLMOE')
        c=counts[lineage]
        c['lines']+=1
        for field in ('same_warp_revisit','cross_warp_revisit','cross_CTA_duplicate_sector_visits',
                      'duplicate_sector_visits','sector_visit_count','unique_sector_count',
                      'duplicate_byte_count','dynamic_byte_count','unique_byte_count'):
            c[field]+=int(row[field])
        c[f'class_{row["classification"]}']+=1
    deep,olmoe=counts['DEEPSEEK'],counts['OLMOE']
    assert (deep['lines'],deep['same_warp_revisit'],deep['cross_warp_revisit'])==(180224,180224,0)
    assert (deep['duplicate_sector_visits'],deep['sector_visit_count'],deep['unique_sector_count'])==(180224,360448,180224)
    assert (deep['duplicate_byte_count'],deep['dynamic_byte_count'],deep['unique_byte_count'])==(5767168,11534336,5767168)
    assert deep['cross_CTA_duplicate_sector_visits']==0 and deep['class_EXACT_BYTE_REVISIT']==180224
    assert (olmoe['lines'],olmoe['duplicate_sector_visits'],olmoe['duplicate_byte_count'])==(131072,0,0)
    return {name:dict(sorted(counter.items())) for name,counter in counts.items()}


def build(out: Path | None = None, state_path: Path | None = None, handoff_path: Path | None = None) -> dict:
    packs={name:verify_manifest(name) for name in PACKS}
    base=historical_json('base_terminal','FINAL_PROJECT_STATE.json')
    literature=historical_json('literature')
    cross=historical_json('cross_lineage')
    translation=historical_json('translation')
    neighbor=historical_json('nearest_neighbor')
    oracle=historical_json('deepseek_oracle')
    traffic=historical_json('deepseek_oracle','TRAFFIC_ORACLE.json')
    detail_aggregation=aggregate_oracle_detail()
    deep=traffic['lineages']['DEEPSEEK']; olmoe=traffic['lineages']['OLMOE']
    assert base['decision']=='NO_CURRENT_C16_MECHANISM_READY_FOR_PROMOTION' and base['active_promotion_candidate_count']==0
    assert literature['decision']=='NO_NEW_LITERATURE_DRIVEN_PROBLEM_QUALIFIED' and literature['qualified_candidate_count']==0
    assert cross['decision']=='CROSS_LINEAGE_ANOMALY_QUALIFIED_FOR_ORACLE_SCREEN' and cross['qualified_candidates']==['DEEPSEEK_WEIGHT_LINE_REVISIT']
    assert translation['decision']=='NO_C16_TRANSLATION_PROBLEM_QUALIFIED_YET' and translation['qualified_problem_count']==0
    assert translation['translation_time_headroom']=='TRANSLATION_TIME_HEADROOM_UNKNOWN' and translation['future_109_contract_generated'] is False
    assert neighbor['classification']=='NEAREST_NEIGHBOR_CROWDED' and neighbor['experiment_authorized'] is False
    assert oracle['decision']=='GEMVX_SHAPE_WORK_DECOMPOSITION_EFFECT' and oracle['native_service_oracle_contract_issued'] is False
    assert (deep['weight_unique_128B_lines'],deep['same_warp_revisited_lines'],deep['cross_warp_revisited_lines'])==(180224,180224,0)
    assert (deep['O1_avoidable_fraction'],deep['O2_avoidable_fraction'])==(0.5,0.5)
    assert (deep['O2_avoidable_logical_bytes'],deep['O2_dynamic_logical_bytes'])==(5767168,11534336)
    assert deep['cross_CTA_duplicate_sector_visits']==0 and deep['classes']=={'EXACT_BYTE_REVISIT':180224}
    assert olmoe['O2_avoidable_logical_bytes']==0
    assert traffic['template6_static_map_comparison']['identical_offset_opcode_sass_count']==243
    if state_path is not None and handoff_path is not None:
        check_final_state(json.loads(state_path.read_text(encoding='utf-8')),handoff_path.read_text(encoding='utf-8'))
    report=dict(status='PASS_CPU_ONLY_AUTHORITY_AND_FINAL_STATE',packs=packs,
                decisions=dict(base=base['decision'],literature=literature['decision'],cross_lineage_original=cross['decision'],
                               translation=translation['decision'],nearest_neighbor=neighbor['classification'],deepseek_oracle=oracle['decision']),
                corrected_deepseek=dict(weight_lines=deep['weight_unique_128B_lines'],same_warp_revisited=deep['same_warp_revisited_lines'],
                                        cross_warp_revisited=deep['cross_warp_revisited_lines'],cross_cta_duplicate_sector_visits=deep['cross_CTA_duplicate_sector_visits'],
                                        sector_fraction=deep['O1_avoidable_fraction'],exact_byte_fraction=deep['O2_avoidable_fraction'],
                                        exact_avoidable_bytes=deep['O2_avoidable_logical_bytes'],exact_dynamic_bytes=deep['O2_dynamic_logical_bytes']),
                independent_line_detail_aggregation=detail_aggregation,
                no_new_experiment=True)
    if out is not None:
        out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return report


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path)
    parser.add_argument('--state',type=Path)
    parser.add_argument('--handoff',type=Path)
    args=parser.parse_args()
    result=build(args.out,args.state,args.handoff)
    print(json.dumps(dict(status=result['status'],packs={k:v['sha256sums_entries_verified'] for k,v in result['packs'].items()},corrected_deepseek=result['corrected_deepseek']),sort_keys=True))


if __name__=='__main__':
    main()
