"""One-shot independent terminal review/package; no launch, compiler or ledger mutation."""
import argparse
import csv
import json
from pathlib import Path
import runpy
import shutil
import time

from acceptance import load_current_authority, current_manifest
from campaign_r0 import publish_pair, csv_write
from package_r0 import freeze_checksums
from registry import Registry, run_key, write_json
from run import inspect, digest, validate_summary, require, GATES

REPO=Path(__file__).resolve().parents[3]
ORDER=('sad','vectorAdd_4M','cfd_097k','convolutionSeparable','FWT_7_21')


def review(spec,registry,native_proof=None):
    key=run_key(spec['identity']);row=registry['runs'][key]
    require(row['status']=='COMPLETE_VALID' and row['identity']==spec['identity'],'No exact valid canonical terminal')
    directory=Path(row['result_directory']);result=json.loads((directory/'run_status.json').read_text())
    require(result['status']=='COMPLETE_VALID' and result['exit_code']==0 and result['run_key']==key and result['identity']==spec['identity'],'Invalid exact runtime result')
    require(json.loads((directory/'input_spec.json').read_text())==spec,'Frozen runtime spec differs')
    scoped_spec=dict(spec)
    if native_proof is not None:
        supplemental={'path':str(native_proof),'sha256':digest(native_proof)}
        require('native_legacy_semantic_proof' not in spec or spec['native_legacy_semantic_proof']['sha256']==supplemental['sha256'],'Different frozen native proof')
        scoped_spec['native_legacy_semantic_proof']=supplemental
    audit=inspect(scoped_spec) # Original immutable inputs + separately bound r17 evidence.
    # GATES is a set: ordering may differ across Python processes. Compare
    # exact gate/hash membership and retain every other ordered input field.
    original=result['audit']['qualification_evidence'];fresh=audit['qualification_evidence']
    require(len(original)==len(fresh)==len(GATES) and
            {(r['gate'],r['sha256']) for r in original}=={(r['gate'],r['sha256']) for r in fresh},
            'Qualification gate/hash membership changed')
    audit['qualification_evidence']=original
    require(audit==result['audit']==json.loads((directory/'input_audit.json').read_text()),'Input/qualification/authority audit changed')
    require(digest(directory/'accel-sim.out')==spec['identity']['binary_sha256'],'Frozen runtime binary changed')
    for item in audit['configs']+audit['auxiliary_assets']:
        require(digest(directory/item['name'])==item['sha256'],'Frozen config/asset changed')
    raw=directory/'raw.log';require(digest(raw)==result['raw_log_sha256'],'Raw log changed')
    parser=runpy.run_path(spec['parser']['path']);summary=parser['parse'](raw,spec)
    require(summary==result['summary']==json.loads((directory/'terminal_summary.json').read_text()),'Independent reparse differs')
    require(validate_summary(summary,spec['identity'])==result['validation'],'Native terminal validation differs')
    return result,directory


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workload',choices=ORDER,required=True)
    ap.add_argument('--spec-b',type=Path,required=True);ap.add_argument('--spec-u',type=Path,required=True)
    ap.add_argument('--stage',type=Path,required=True);ap.add_argument('--pack',type=Path,required=True);ap.add_argument('--deadline-unix',type=float,required=True);ap.add_argument('--native-legacy-proof',type=Path);a=ap.parse_args()
    require(time.time()<a.deadline_unix,'Bounded CONTINUE deadline');require(not a.pack.exists(),'Frozen pack already exists')
    state=load_current_authority();ledger=current_manifest(state);accepted={r['workload'] for r in ledger['rows'] if r['scientific_acceptance']=='CURRENT_ACCEPTED'}
    require(a.workload==next(w for w in ORDER if w not in accepted),'Original frozen pair order changed')
    specs=[json.loads(p.read_text()) for p in (a.spec_b,a.spec_u)]
    require(all(s['identity']['workload']==a.workload for s in specs),'Different workload')
    base,unified=specs
    for name in ('core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','epoch_range','ideal_vector','termination_contract'):
        require(base['identity'][name]==unified['identity'][name],'Mismatched pair '+name)
    bf=dict(base['identity']['feature_vector']);uf=dict(unified['identity']['feature_vector'])
    require(bf.pop('unified_wb') is False and uf.pop('unified_wb') is True and bf==uf,'Different mechanism/budget dimensions')
    registry=Registry();lease=registry.build_lease('lane5',cpu=1,memory=2*1024**3)
    try:
        snap=registry.snapshot();reviewed=[review(s,snap,a.native_legacy_proof) for s in specs];results=[r for r,d in reviewed]
        require(results[0]['summary']['instructions']==results[1]['summary']['instructions'],'Different application instruction counts')
        a.stage.mkdir(parents=True,exist_ok=True);source=publish_pair(a.workload,results,specs,a.stage)
        require(json.loads((source/'PAIR_RECEIPT.json').read_text())['status']=='COMPLETE_VALID','Pair packaging invalid')
        a.pack.mkdir(parents=True)
        for p in source.iterdir():
            if p.is_file():shutil.copyfile(p,a.pack/p.name)
        raw_index=[];manifest=[];rows=[]
        for mode,spec,(result,directory) in zip(('B16_BANKED','U_WB16'),specs,reviewed):
            arm=a.pack/mode;arm.mkdir()
            for name in ('input_spec.json','input_audit.json','run_status.json','terminal_summary.json','raw.log'):
                shutil.copyfile(directory/name,arm/name)
            raw_index.append({'workload':a.workload,'mode':mode,'run_key':result['run_key'],'raw_log':str(directory/'raw.log'),'sha256':result['raw_log_sha256'],'bytes':(directory/'raw.log').stat().st_size,'status':'COMPLETE_VALID'})
            identity=spec['identity'];rows.append({'run_key':result['run_key'],'identity':identity,**{k:identity[k] for k in ('core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','workload')},'mode':mode,'scientific_acceptance':'CURRENT_ACCEPTED','original_terminal_status':'COMPLETE_VALID','raw_log_sha256':result['raw_log_sha256'],'observed_cycles':result['summary']['cycles'],'instructions':result['summary']['instructions']})
            manifest.append({'mode':mode,'identity':identity,'run_key':result['run_key'],'qualification_sha256':result['audit']['qualified_release_sha256'],'atomic_input_scope':spec['atomic_input_scope'],'input_audit':result['audit'],'hardware_terminal':result['summary'],'registry_terminal':snap['runs'][result['run_key']]})
        csv_write(a.pack/'RAW_LOG_INDEX.csv',raw_index)
        review_receipt={'status':'INDEPENDENT_TERMINAL_AND_CURRENT_AUTHORITY_REVIEW_PASS','workload':a.workload,'scientific_acceptance_rows_proposed':rows,'checked_current_authority':state['binding'],'review_resource_lease':lease,'review_resource_lease_terminal':'RELEASED_IN_FINALLY','no_simulator_or_compiler_started':True,'next_step':'Publish these exact rows in next V2 generation and remote-read back before announcing current acceptance','scope':'Symbolic32B sector version/request/hardware lifecycle; full native non-atomic inputs only; no numeric SASS output; no geomean until5; C1 legacy headroom excluded'}
        if a.native_legacy_proof:
            review_receipt['supplemental_native_legacy_semantic_proof']={'path':str(a.native_legacy_proof),'sha256':digest(a.native_legacy_proof)}
        elif specs[0].get('native_legacy_semantic_proof'):
            review_receipt['supplemental_native_legacy_semantic_proof']=specs[0]['native_legacy_semantic_proof']
        write_json(a.pack/'SCIENTIFIC_REVIEW.json',review_receipt);write_json(a.pack/'SOURCE_MANIFEST.json',{'runs':manifest})
        comparison=json.loads((a.pack/'COMPARISON.json').read_text())
        (a.pack/'README.md').write_text('# Repaired official R0.1 '+a.workload+' paired full application\n\nIndependent hardware-terminal/current-authority/input review PASS. Current scientific acceptance requires the matching new V2 rows. Exact immutable artifacts and raw index retained.\n\nB16 cycles '+str(results[0]['summary']['cycles'])+'; U_WB16 cycles '+str(results[1]['summary']['cycles'])+'; B16/U_WB16 '+str(comparison['speedup_B16_over_U_WB16'])+'x. One pair only; no group geomean. Negative controls/ties/regressions retained.\n\nSame repaired producing Core/Framework/vendor/binary and full input content; only frozen B/U mode changes. Ordinary symbolic sector oracle, not numerical SASS output. No TVD/RO/Ideal. Legacy C1 resident-headroom is not used for causal claims. Borrowing/copy/bank event counts alone do not prove a capacity advantage.\n')
        freeze_checksums(a.pack)
        print(json.dumps({'status':review_receipt['status'],'pack':str(a.pack),'cycles':[r['summary']['cycles'] for r in results],'speedup':comparison['speedup_B16_over_U_WB16']}))
    finally:registry.release_build(lease,'lane5')


if __name__=='__main__':main()
