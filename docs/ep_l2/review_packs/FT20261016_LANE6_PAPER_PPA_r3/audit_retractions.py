#!/usr/bin/python3
"""Read-only live acceptance/retraction audit. Never execute a simulator or edit old assets."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import patch
from acceptance_gate import load_current_acceptance, require, REPORT
from result_intake import canonical_sha, summarize
from native_pair_intake import read_native_packet

OLD_PUBLICATION = '6a3c00cb17aaff2a2c23c5990e7ef90f294aa8df'
OLD_PACK = 'docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_r2'


def sha(b):return hashlib.sha256(b).hexdigest()


def audit(repo, out):
    here=Path(__file__).resolve().parent
    require(not out.exists(), 'Use a new audit revision directory')
    binding=json.loads((here/'CURRENT_ACCEPTANCE_BINDING.json').read_text())
    current=load_current_acceptance(repo,binding)
    require(current.table.get('status') == 'SUSPENDED' and len(current.table['rows']) == 10,
            'This audit is the frozen review-r3 withdrawal snapshot; use a new revision for repaired results')
    require(all('SUSPENDED' in current.matrix.get(key, {}).get('status', '') for key in ['R0', 'R1']),
            'Unexpected original release supersession state')
    sources=list(current.bindings)
    def read(commit,path):
        b=subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path])
        sources.append({'commit':commit,'path':path,'sha256':sha(b),'bytes':len(b)})
        return b
    # Validate each of the six original row identities from immutable native packs.
    # Full raw bytes are preserved elsewhere; this verifies the authoritative raw
    # hash INDEX and original receipt, not a new raw/model validation.
    native_results=[]; run_results=[]
    receipt=json.loads(read(current.commit,REPORT+'RECEIPT.json'))
    packs=receipt['formal_campaign']['completed_pair_packs']
    old_packet=json.loads(read(OLD_PUBLICATION,OLD_PACK+'/FORMAL_WB_PAIR_INPUTS.json'))['runtime_packet']
    adapter_template=json.loads((here/'REJECTED_OLD_SAD_ADAPTER.json').read_text())
    q=old_packet['qualification']
    for base in sorted(packs):
        pair=json.loads(read(current.commit,base+'/PAIR_RECEIPT.json'))
        require(len(pair['specs'])==len(pair['results'])==2,'Original pair cardinality changed')
        for spec,result in zip(pair['specs'],pair['results']):
            ident=spec['identity'];key=result['run_key']
            require(key==canonical_sha(ident) and result['identity']==ident,'Original run-key/identity mismatch')
            matching=[r for r in current.table['rows'] if r['run_key']==key]
            require(len(matching)==1,'Missing original acceptance row');row=matching[0]
            require(row['raw_log_sha256']==result['raw_log_sha256'],'Original raw hash index mismatch')
            require(row['observed_cycles']==result['summary']['cycles'] and row['instructions']==result['summary']['instructions'],'Original native totals mismatch')
            run={'workload':ident['workload'],'mode':row['mode'],'status':result['status'],'identity':ident,'run_key':key,
                 'raw_log_sha256':result['raw_log_sha256'],'summary':result['summary']}
            try:
                current.check_run(run)
            except ValueError as error:
                require('SUSPENDED_OR_UNACCEPTED' in str(error),'Unexpected denial reason: '+str(error))
                reason=str(error)
            else:raise ValueError('Old revoked row unexpectedly accepted')
            # Completed single sides cannot escape summary validation while mate is missing.
            try:summarize({'evidence_kind':'FUNCTIONAL_IMPLEMENTATION','qualification':q,'runs':[run]},current)
            except ValueError as error:require('SUSPENDED_OR_UNACCEPTED' in str(error),'Summary failed for an unrelated reason')
            else:raise ValueError('Old row unexpectedly entered summary')
            run_results.append({'run_key':key,'identity':ident,'raw_log_sha256':result['raw_log_sha256'],'original_terminal_status':result['status'],
                'scientific_acceptance':row['scientific_acceptance'],'consumer_status':'REJECTED','reason':reason})
        adapter={**adapter_template,'native_pairs':[{'publication_commit':current.commit,'pair_repository_path':base}]}
        try:read_native_packet(repo,adapter,current)
        except ValueError as error:require('SUSPENDED_OR_UNACCEPTED' in str(error),'Native intake failed for an unrelated reason')
        else:raise ValueError('Old native pair accepted')
        native_results.append({'pair_repository_path':base,'native_intake':'REJECTED_SCIENTIFIC_SUPERSESSION'})
    require(len(run_results)==6 and len(native_results)==3,'Unexpected retired campaign scope')
    # Real end-to-end plotting entry rejects the old sad packet with latest authority
    # before creating ANY output dir. No manual plot exclusion is used.
    with tempfile.TemporaryDirectory(prefix='ep-l2-lane6-r3-denial-') as tmp:
        target=Path(tmp)/'must_not_exist'
        argv=['plot_qualified_pairs.py',str(here/'REJECTED_OLD_SAD_ADAPTER.json'),'--framework-repo',str(repo),'--output-dir',str(target)]
        try:
            with patch.object(sys,'argv',argv),contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(here/'plot_qualified_pairs.py'),run_name='__main__')
        except ValueError as error:require('SUSPENDED_OR_UNACCEPTED' in str(error),'Plot denied for unrelated reason')
        else:raise ValueError('Revoked plot was emitted')
        require(not target.exists(),'Revoked plot output directory created')
    # History and parametric PPA reuse, explicitly excluding formal_sad.
    reused=json.loads((here/'REUSED_ASSET_MANIFEST.json').read_text())
    for asset in reused['files']:
        require(sha(read(asset['source_commit'],asset['source_path']))==asset['sha256'],'Historical reuse source digest')
        require(sha((repo/asset['path']).read_bytes())==asset['sha256'],'Reused asset modified')
    preserved=[]
    for revision in ['r1','r2']:
        base='docs/ep_l2/review_packs/FT20261016_LANE6_PAPER_PPA_'+revision
        names=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',OLD_PUBLICATION,'--',base]).decode().splitlines()
        for name in names:
            b=read(OLD_PUBLICATION,name);require((repo/name).read_bytes()==b,'Frozen old pack modified: '+name)
        preserved.append({'revision':revision,'files_byte_identical':len(names)})
    # No output is written until all live checks have succeeded.
    current.assert_fresh()
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD']).decode().strip()
    tools=[]
    for name in ['audit_retractions.py','acceptance_gate.py','result_intake.py','native_pair_intake.py','plot_qualified_pairs.py']:
        path=str((here/name).relative_to(repo));b=read(head,path)
        require(b==(here/name).read_bytes(),'Commit exact offline tool source before generating evidence')
        tools.append({'path':path,'commit':head,'sha256':sha(b)})
    generated={
      'ACCEPTANCE_AUDIT.json':{'status':'PASS','authority':current.provenance(),'accepted_application_runs':0,'accepted_formal_pairs':0,
          'whole_group_geomean':None,'six_completed_rows_rejected':run_results,'three_native_pairs_rejected':native_results,
          'old_sad_plot_entry':'REJECTED_NO_OUTPUT_DIRECTORY','pending_not_run_rows':[r for r in current.table['rows'] if r['original_terminal_status']=='NOT_RUN'],
          'old_revisions_preserved':preserved,'raw_validation_scope':'Original Git receipt and raw HASH INDEX verified; no old raw/CSV/binary modified or requalified',
          'new_scientific_experiments':0},
      'AUTHORITATIVE_ACCEPTANCE_SNAPSHOT.json':current.table,
      'AUTHORITATIVE_VALIDATION_SNAPSHOT.json':current.matrix,
      'SOURCE_EVIDENCE_MANIFEST.json':{'generator_source_commit':head,'review_authority':'a41bfb55934303a4d4a342762f74a16d137d0316',
          'scientific_contract':'6c136e2a56a008695f8c8b815723bf8f1a760db9','tools':tools,'sources':sources}}
    out.mkdir(parents=True)
    for name,value in generated.items():(out/name).write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    print(json.dumps({'status':'PASS','rejected_runs':6,'rejected_native_pairs':3,'formal_figures_emitted':0,'preserved':preserved,'source_blobs':len(sources)}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--framework-repo',type=Path,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();audit(args.framework_repo.resolve(),args.output_dir.resolve())
