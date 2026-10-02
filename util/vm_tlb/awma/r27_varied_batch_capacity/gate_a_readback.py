#!/usr/bin/env python3
"""CPU-only independent R26 raw-evidence readback for R27 Gate A."""

from __future__ import annotations

import argparse, csv, hashlib, json, math, re, tarfile
from collections import defaultdict
from pathlib import Path

import torch


EXPECTED = {
    "archive_sha256": "c8319694dc33858bb0760f97f80f4a509e07e9ce7eadb6b10b28a7823f0696c3",
    "manifest_sha256": "8e0e30a90856f152cf1221c6a660ce6ceeeca84c402ed59cd8a6956f1e371159",
    "manifest_items": 207,
    "common_sha256": "09e293774ac9dcb535e1a3d47d72878ff68f3831476175060b1016bce8a28b55",
    "common_bytes": 2626691315,
    "weight_sha256": "834af272c43aca72e7c22f522ec43b231c48c1e2673dfb1274d6a2fcba6e0302",
    "m_sha256": "445daf620b70a6b03eba66bda3b7e1ccaf1c29e7384c8aec1126d6c0b314932f",
    "v_sha256": "efaabc21904a155649d41ca4286bddaf211574a224bd7d34cb584a424a885d21",
}


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def tensor_sha(t):
    a=t.detach().contiguous().cpu().view(torch.uint8).numpy()
    return hashlib.sha256(memoryview(a)).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--parent',required=True);ap.add_argument('--git-pack',required=True);ap.add_argument('--remote-readback',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
    parent=Path(a.parent);pack=Path(a.git_pack);errors=[];discrepancies=[]
    manifest_path=parent/'R26_PUBLICATION_MANIFEST.tsv';archive=parent/'r26_compact_raw_publication.tgz';common_path=parent/'COMMON_POST_BOOTSTRAP.pt'
    manifest=list(csv.DictReader(manifest_path.open(),delimiter='\t')); by_asset={x['asset']:x for x in manifest}
    checks={
        'manifest':{'path':str(manifest_path),'bytes':manifest_path.stat().st_size,'sha256':sha(manifest_path)},
        'archive':{'path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive)},
        'common_checkpoint':{'path':str(common_path),'bytes':common_path.stat().st_size,'sha256':sha(common_path)},
    }
    if checks['manifest']['sha256']!=EXPECTED['manifest_sha256']: errors.append('manifest SHA mismatch')
    if checks['archive']['sha256']!=EXPECTED['archive_sha256']: errors.append('archive SHA mismatch')
    if len(manifest)!=EXPECTED['manifest_items']: errors.append(f"manifest count {len(manifest)}")
    if checks['common_checkpoint']['sha256']!=EXPECTED['common_sha256'] or checks['common_checkpoint']['bytes']!=EXPECTED['common_bytes']: errors.append('common checkpoint file mismatch')
    # Prove the compact archive is readable and contains the relevant raw families.
    with tarfile.open(archive,'r:gz') as tf:
        names=tf.getnames()
    archive_summary={'members':len(names),'has_capacity_summary':any(x.endswith('raw/CAPACITY_SEARCH_SUMMARY.json') for x in names),'has_capacity_trials':any('/capacity_trials/' in x for x in names),'has_runner_source':any(x.endswith('source/runner/run_r26_campaign.py') for x in names)}
    if not all(archive_summary.values()): errors.append(f'archive content incomplete {archive_summary}')
    # Independent remote byte readback must show three authority hashes plus all manifest entries OK.
    lines=Path(a.remote_readback).read_text().splitlines(); ok=[x for x in lines if x.endswith(': OK')]
    remote_summary={'lines':len(lines),'manifest_ok_entries':len(ok),'first_three':lines[:3]}
    if len(ok)!=EXPECTED['manifest_items'] or len(lines)!=EXPECTED['manifest_items']+3: errors.append('remote manifest readback count mismatch')
    if not lines[0].startswith(EXPECTED['archive_sha256']) or not lines[1].startswith(EXPECTED['manifest_sha256']) or not lines[2].startswith(EXPECTED['common_sha256']): errors.append('remote authority hash prefix mismatch')

    # Git raw index and node164 manifest must agree for every selected endpoint receipt/log.
    raw_index=list(csv.DictReader((pack/'RAW_DATA_INDEX.tsv').open(),delimiter='\t'))
    def rel_from_git(path):
        marker='/r26_tied_weight_production_capacity_109_v1_20261002/'
        return path.split(marker,1)[1] if marker in path else None
    git_by_rel={rel_from_git(x['path']):x for x in raw_index if rel_from_git(x['path'])}
    selected=[x for x in manifest if ('raw/capacity_trials/' in x['asset'] or 'logs/capacity_trials/' in x['asset']) and ('confirm_pass_endpoint' in x['asset'] or 'confirm_oom_endpoint' in x['asset'])]
    selected_receipts=[x for x in selected if x['asset'].endswith('.json')]; selected_logs=[x for x in selected if x['asset'].endswith('.log')]
    if len(selected_receipts)!=12 or len(selected_logs)!=12: errors.append(f'endpoint selected counts receipts={len(selected_receipts)} logs={len(selected_logs)}')
    file_evidence=[]; groups=defaultdict(list)
    local_dir=parent/'capacity_trials'
    for x in selected:
        local=local_dir/Path(x['asset']).name; got=sha(local) if local.exists() else None; size=local.stat().st_size if local.exists() else None
        git=git_by_rel.get(x['asset'])
        item={'asset':x['asset'],'manifest_bytes':int(x['bytes']),'manifest_sha256':x['sha256'],'local_path':str(local),'local_bytes':size,'local_sha256':got,'git_index_bytes':None if git is None else int(git['bytes']),'git_index_sha256':None if git is None else git['sha256']}
        item['qualified']=local.exists() and size==int(x['bytes']) and got==x['sha256'] and git is not None and int(git['bytes'])==size and git['sha256']==got
        if not item['qualified']: errors.append(f"selected file mismatch {x['asset']}")
        file_evidence.append(item)
        if x['asset'].endswith('.json') and local.exists():
            value=json.loads(local.read_text()); groups[(value['policy'],int(value['batch']),value['outcome'])].append((value,local))
    expected_groups={('c1',70,'PASS'):3,('c1',71,'OOM'):3,('s2',71,'PASS'):3,('s2',72,'OOM'):3}
    observed_groups={k:len(v) for k,v in groups.items()}
    if observed_groups!=expected_groups: errors.append(f'endpoint groups {observed_groups}')

    parsed={'c1_b70':[],'c1_b71':[],'s2_b71':[],'s2_b72':[]}
    model_id='meta-llama/Llama-3.2-1B';revision='4e20de362430cd3b72f300e6b0f18e50e7166e08'
    for key,items in groups.items():
        policy,batch,outcome=key; bucket=f'{policy}_b{batch}'
        for value,path in items:
            rec={'receipt':str(path),'outcome':outcome,'policy':policy,'batch':batch}
            stem=path.stem; log=local_dir/f'{stem}.log'; text=log.read_text(); progress=[json.loads(x) for x in text.splitlines() if x.startswith('{') and '"progress"' in x]
            rec['log']=str(log);rec['completed_steps_from_log']=len(progress);rec['progress']=progress
            if outcome=='PASS':
                steps=value.get('steps',[]); auth=value.get('batch_binding',{}); ident=auth.get('identity',{})
                rec.update({'five_complete_steps':value.get('five_complete_steps'),'final_step':value.get('final_step'),'step_count':len(steps),'losses_finite':all(math.isfinite(float(s['loss'])) for s in steps),'step_counters':[s['step'] for s in steps],'growth_after_first':[s.get('transient_active_growth_bytes') for s in steps[1:]],'input_ids_sha256':auth.get('input_ids_sha256'),'labels_sha256':auth.get('labels_sha256'),'input_shape':auth.get('input_shape'),'model_id':ident.get('model_id'),'revision':ident.get('revision'),'default_policy':auth.get('default_policy'),'s2_opt_in':auth.get('capacity_policy_requires_explicit_opt_in')})
                if not (rec['five_complete_steps'] and rec['final_step']==6 and rec['step_count']==5 and rec['losses_finite'] and rec['step_counters']==[2,3,4,5,6] and rec['completed_steps_from_log']==5 and rec['model_id']==model_id and rec['revision']==revision): errors.append(f'PASS invariant {path.name}')
                if policy=='s2' and batch==71 and any(x!=0 for x in rec['growth_after_first']): errors.append(f'S2 B71 active growth {path.name}')
            else:
                err=value.get('error','');tb=value.get('traceback','');phase=value.get('oom_phase')
                req=re.search(r'Tried to allocate ([0-9.]+ MiB)',err)
                rec.update({'oom_phase':phase,'error':err,'traceback_has_cuda_oom':'OutOfMemoryError' in tb,'request':None if req is None else req.group(1),'free_bytes':value.get('free_bytes'),'total_bytes':value.get('total_bytes'),'allocated_bytes':value.get('allocated_bytes'),'reserved_bytes':value.get('reserved_bytes')})
                if not (phase=='BACKBONE_COMPACT_LOOKUP_BACKWARD' and rec['traceback_has_cuda_oom']): errors.append(f'OOM invariant {path.name}')
                if policy=='c1' and batch==71 and not (rec['completed_steps_from_log']==2 and rec['request']=='142.00 MiB'): errors.append(f'C1 B71 raw detail {path.name}')
            parsed[bucket].append(rec)

    # Cross-check published B70/B71/B72 R26 repeated-input hashes, not the new R27 bank.
    bindings=list(csv.DictReader((pack/'BATCH_INPUT_BINDINGS.tsv').open(),delimiter='\t')); bindings={int(x['batch']):x for x in bindings}
    binding_summary={b:bindings.get(b) for b in (70,71,72)}
    if any(binding_summary[b] is None for b in binding_summary): errors.append('missing B70/B71/B72 Git binding')
    for value,_ in groups.get(('c1',70,'PASS'),[])+groups.get(('s2',71,'PASS'),[]):
        b=int(value['batch']);auth=value['batch_binding'];ref=bindings[b]
        if auth['input_ids_sha256']!=ref['input_ids_sha256'] or auth['labels_sha256']!=ref['labels_sha256']: errors.append(f'PASS binding disagreement B{b}')

    # Load the remote-readback CPU common state and independently hash tensor payloads.
    state=torch.load(common_path,map_location='cpu',weights_only=False)
    checkpoint={
        'schema':state.get('schema'),'logical_step':state.get('step'),'policy_metadata':state.get('policy_metadata'),
        'weight':{'shape':list(state['weight'].shape),'dtype':str(state['weight'].dtype),'sha256':tensor_sha(state['weight']),'device':state['weight'].device.type},
        'm':{'shape':list(state['m'].shape),'dtype':str(state['m'].dtype),'sha256':tensor_sha(state['m']),'device':state['m'].device.type},
        'v':{'shape':list(state['v'].shape),'dtype':str(state['v'].dtype),'sha256':tensor_sha(state['v']),'device':state['v'].device.type},
        'cpu_rng_sha256':tensor_sha(state['cpu_rng']),'cuda_rng_sha256':tensor_sha(state['cuda_rng']),
        'all_tensors_cpu':all(v.device.type=='cpu' for v in state.values() if isinstance(v,torch.Tensor)),
        'identity':state.get('identity'),
    }
    if checkpoint['logical_step']!=1 or checkpoint['weight']['sha256']!=EXPECTED['weight_sha256'] or checkpoint['m']['sha256']!=EXPECTED['m_sha256'] or checkpoint['v']['sha256']!=EXPECTED['v_sha256'] or not checkpoint['all_tensors_cpu']: errors.append('common checkpoint tensor mismatch')
    # The frozen runner/search source proves all trials receive the same --common and fixed model/token arguments.
    source_checks=[]
    for name,expected in [('component.py','40524ba0134913921eb62ffcd14cffa1a9726c370cceb1330838ba3104b9b341'),('run_r26_campaign.py','1935970ec268ad68549af11b7b74886e8b84ae95491879258e481ac5e6b78b17'),('capacity_search.py','ef636603ded1e7df52cad391882e91f3860585c3523091726f1f5f8142f37d53')]:
        p=pack.parent.parent.parent.parent/'util/vm_tlb/awma/r26_tied_weight_production_capacity'/name
        # Resolve from repository root instead of relying on the above relative guess.
        p=Path.cwd()/'util/vm_tlb/awma/r26_tied_weight_production_capacity'/name
        source_checks.append({'path':str(p),'sha256':sha(p),'expected':expected,'qualified':sha(p)==expected})
    if not all(x['qualified'] for x in source_checks): errors.append('frozen source mismatch')
    result={'schema':'R27_GATE_A_R26_RAW_READBACK_V1','status':'R27_PARENT_RAW_QUALIFIED' if not errors else 'R27_PARENT_RAW_NOT_QUALIFIED','qualified':not errors,'authority_files':checks,'archive_summary':archive_summary,'remote_readback':remote_summary,'selected_file_evidence':file_evidence,'endpoint_group_counts':{str(k):v for k,v in observed_groups.items()},'parsed_endpoints':parsed,'r26_input_bindings':binding_summary,'common_checkpoint':checkpoint,'frozen_source':source_checks,'discrepancies':discrepancies,'errors':errors,'interpretation':'R26 five-step witness raw evidence verified; this does not assert allocator cause'}
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'errors':errors,'selected_files':len(file_evidence),'remote_ok':len(ok)},sort_keys=True))
    raise SystemExit(0 if result['qualified'] else 2)


if __name__=='__main__':main()
