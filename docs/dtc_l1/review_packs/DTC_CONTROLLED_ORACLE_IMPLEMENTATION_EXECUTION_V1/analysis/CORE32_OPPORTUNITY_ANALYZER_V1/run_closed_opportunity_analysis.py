"""Read one S closed snapshot and immutable derived gzip facts; never raw logs."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import oracle_opportunity_analyzer as oa

def sha(data): return hashlib.sha256(data).hexdigest()

def run(snapshot_path, matrix_path, settings_path, out_dir, c1_path=None):
    target = Path(out_dir)
    target.mkdir(exist_ok=False)
    inputs = target / 'inputs'; inputs.mkdir()
    sb = Path(snapshot_path).read_bytes(); snapshot = json.loads(sb)
    mb = Path(matrix_path).read_bytes(); matrix = json.loads(mb)
    setting_bytes = Path(settings_path).read_bytes(); settings = json.loads(setting_bytes)
    (inputs/'SOURCE_SNAPSHOT.json').write_bytes(sb)
    (inputs/'FROZEN_MATRIX.json').write_bytes(mb)
    (inputs/'ANALYZER_SETTINGS.json').write_bytes(setting_bytes)
    facts, pins = {}, []
    derived_root = Path(snapshot_path).resolve().parent
    for row in snapshot['rows']:
        if row.get('classification') != 'accepted' or row.get('status') != 'ACCEPTED_RUNTIME_CLOSER':
            continue
        declared = Path(row['kernel_evidence_path'])
        name = 'KERNEL_FACTS.' + row['result_sha256'] + '.json.gz'
        oa.require(declared.name == name, 'ONLY_CLOSED_S_DERIVED_KERNEL_CACHE_IS_READABLE')
        # Read only the flat cache alongside this snapshot, also supporting an
        # immutable copied snapshot/cache bundle. Never follow a raw_path.
        path = derived_root / name
        data = path.read_bytes()
        oa.require(sha(data) == row['kernel_evidence_sha256'], 'KERNEL_FACTS_SHA_CHANGED')
        facts[row['plan_id']] = json.loads(gzip.decompress(data))
        (inputs/path.name).write_bytes(data)
        pins.append({'path':str(path),'original_declared_path':str(declared),'sha256':sha(data),'plan_id':row['plan_id']})
    c1 = json.loads(Path(c1_path).read_bytes()) if c1_path else None
    if c1_path: (inputs/'C1_CONTEXT.json').write_bytes(Path(c1_path).read_bytes())
    result = oa.analyze(snapshot,matrix,facts,matrix_sha256=sha(mb),snapshot_sha256=sha(sb),
        expected_build_identity=settings['expected_build_identity'],expected_configs_by_mode=settings['expected_configs_by_mode'],c1_context=c1)
    encoded=(json.dumps(result,indent=2,allow_nan=False)+'\n').encode()
    (target/'CORE32_ORACLE_OPPORTUNITY_ANALYSIS.json.gz').write_bytes(gzip.compress(encoded,mtime=0))
    summary={k:result[k] for k in ('schema','matrix_sha256','source_snapshot_sha256','source_snapshot_generated_utc',
        'fixed_population','initial_population','runtime_closer_accepted_cells','analysis_identity_work_supported_cells',
        'cell_population','cell_status_counts','classification_counts','independent_review_status_counts','mode_statistics',
        'mode_common_intersections','four_cell_common_accepted','boundaries','ROI_validation_scope')}
    summary['paired_programs']=[{k:p[k] for k in ('program','mode','cycles','OFF_cycles','S','H')} for p in result['matched_program_pairs']]
    summary['raw_files_read_by_this_analyzer']=0
    (target/'SUMMARY.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    lines=['# Controlled Oracle opportunity: closed-evidence snapshot','',
        '**Preliminary runtime-closer acceptance; final independent review stays separate.**','',
        f"Frozen population:32 programs/128 cells. Runtime-accepted:{result['runtime_closer_accepted_cells']}; identity/work supported:{result['analysis_identity_work_supported_cells']}. This is incomplete coverage until all declared cells close.",'',
        '| Mode | Matched pairs /32 | GM S on that accepted subset | Faster / equal / slower |','|---|---:|---:|---:|']
    for m in oa.MODES[1:]:
        st=result['mode_statistics'][m]['CORE32']; gm=st['GM_S_over_accepted_matched_subset']
        lines.append(f"|{m}|{st['accepted_matched_pairs']}/32|{gm if gm is not None else 'UNKNOWN'}|{st['faster']}/{st['equal']}/{st['slower']}|")
    lines+=['','Mode subset GMs with different denominators are not direct mode comparisons. Same-set pairwise and four-cell intersections are separately recorded.',
        f"Four-cell accepted intersection:{result['four_cell_common_accepted']['accepted_common_inputs']}/32.",'',
        '| Program | OFF | M | L2 | L1 |','|---|---:|---:|---:|---:|']
    for p in result['program_records']:
        vals=[]
        for m in oa.MODES:
            c=p['C2_controlled_Oracle_cells'][m]
            vals.append((str(c['cycles']) + (' [ANALYSIS HOLD]' if not c['analysis_identity_and_work_supported'] else ''))
                if c['runtime_closer_accepted'] else c['status'])
        lines.append('|'+p['program']+'|'+'|'.join(vals)+'|')
    lines+=['','## Current matched observations','']
    for p in result['matched_program_pairs']:
        lines.append(f"- {p['program']} / {p['mode']}:S={p['S']:.9f},H={p['H']:.9f}; actual same-build OFF={p['OFF_cycles']},Oracle={p['cycles']}.")
    if not result['matched_program_pairs']: lines.append('No matched accepted OFF/Oracle pair exists. All S/H remain unknown.')
    lines+=['','C1 actual structural results are kept in a separate field with their old source/build identities and statuses. They never replace current OFF and are never combined into an Oracle GM.',
        'Per-kernel records retain ordinal/name, actual kernel cycles, cumulative totals, explicit CTA differences and as-printed counters. Counter resets/deltas and causal critical paths are not inferred.',
        'Printed missing values remain null. Source-derived zero and its exact proof remain separate. No best-Oracle GM or theoretical/implementable upper-bound claim is produced.',
        'This analyzer reads only the snapshot and immutable S-derived kernel facts; it reads no raw log, launches no model, and changes no scientific/runtime state.','']
    (target/'SUMMARY.md').write_text('\n'.join(lines))
    meta={'snapshot_path':str(snapshot_path),'snapshot_sha256':sha(sb),'matrix_path':str(matrix_path),'matrix_sha256':sha(mb),
        'settings_sha256':sha(setting_bytes),'kernel_cache_pins':pins,'c1_context_sha256':sha(Path(c1_path).read_bytes()) if c1_path else None,
        'raw_files_read':0,'scientific_starts':0,'management_or_watch_mutations':0,'module_sha256':sha(Path(oa.__file__).read_bytes())}
    (target/'INPUT_PROVENANCE.json').write_text(json.dumps(meta,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot',required=True);p.add_argument('--matrix',required=True);p.add_argument('--settings',required=True)
    p.add_argument('--out',required=True);p.add_argument('--c1-context')
    args=p.parse_args(); summary=run(args.snapshot,args.matrix,args.settings,args.out,args.c1_context)
    print(json.dumps({'runtime_accepted':summary['runtime_closer_accepted_cells'],'analysis_supported':summary['analysis_identity_work_supported_cells'],
        'matched_pairs':len(summary['paired_programs']),'raw_files_read':0,'out':args.out}))
