"""Reuse immutable, committed NAS objects; never operate the other task."""
from pathlib import Path
import json,hashlib,stat

ROOT=Path('/root/data/shared_sm70_trace_library_20261024_v1')
OTHER=Path('/root/data/research_asset_verified_offload_20261024_v1')
NAS=Path('/root/share/mnt164/huangrulin')

def digest(raw):return hashlib.sha256(raw).hexdigest()

def discover():
    candidates={}
    ledger=OTHER/'control/LEDGER.jsonl'
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            row=json.loads(line)
            if row.get('status')=='ARCHIVED_CONTENT_VERIFIED':
                bundle=Path(row['true164_bundle'].replace('/home/shared','/root/share/mnt164',1))
                candidates[str(bundle)]=(bundle,row)
    payload=NAS/'traces/bundles/_payload'
    if payload.exists():
        for commit in payload.glob('*/COMMIT.json'):
            candidates[str(commit.parent)]=(commit.parent,None)
    found={};receipts=[]
    for bundle,ledger_row in candidates.values():
        assert bundle.resolve().is_relative_to(NAS)
        raw=(bundle/'SOURCE_MANIFEST.json').read_bytes()
        commit_raw=(bundle/'COMMIT.json').read_bytes();commit=json.loads(commit_raw)
        manifest=json.loads(raw);mh=digest(raw)
        assert commit['manifest_sha256']==mh and commit['object_id']==manifest['object_id']
        if ledger_row:
            assert ledger_row['manifest_sha256']==mh and ledger_row['commit_sha256']==digest(commit_raw)
        proof_raw=(bundle/'TREE_VERIFICATION.json').read_bytes()
        assert digest(proof_raw)==commit['tree_verification_sha256']
        assert digest((bundle/'RANGE_INDEX.json').read_bytes())==commit['range_index_sha256']
        proof={x['relative_path']:x for x in json.loads(proof_raw)}
        receipt=json.loads((bundle/'RECEIPT.json').read_bytes())
        assert receipt['Source_full_SHA_matches'] and receipt['true164_closed_reopen_whole_SHA_matches']
        assert receipt['manifest_sha256']==mh and receipt['object_id']==manifest['object_id']
        for member in manifest['members']:
            rel=Path(member['relative_path']);assert not rel.is_absolute() and '..' not in rel.parts
            p=bundle/'tree'/rel;s=p.lstat();ident=proof[str(rel)]['actual_tree_identity']
            assert stat.S_ISREG(s.st_mode) and not p.is_symlink() and p.resolve().is_relative_to(NAS)
            assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==tuple(ident[k] for k in ['dev','inode','size','mtime_ns'])
            assert (proof[str(rel)]['sha256'],proof[str(rel)]['size'])==(member['sha256'],member['size'])
            found.setdefault(member['sha256'],{'path':str(p),'kind':'ADOPTED_OTHER_COMMITTED_TRUE164_OBJECT' if ledger_row else 'ADOPTED_OWN_COMMITTED_TRUE164_OBJECT','proof_reference':str(bundle/'COMMIT.json'),'manifest_sha256':mh,'commit_sha256':digest(commit_raw),'expected_identity':[s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns],'full_SHA_proof_reused':True,'independent_current_full_SHA_required_before_final_acceptance':True})
        receipts.append({'bundle':str(bundle),'manifest_sha256':mh,'members':len(manifest['members']),'other_task':bool(ledger_row)})
    return found,receipts
