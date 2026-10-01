#!/usr/bin/env python3
"""Fail-closed holdout release eligibility; this tool never decrypts data."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


REQUIRED={'DQ_id','phenomenon','sign','estimator','materiality_threshold','STOP_rule','exact_holdout_points'}
HOLDOUT={'MP04','MP07','MP08'}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_release(manifest: dict,freeze_bytes: bytes,ciphertext_root: Path) -> dict:
    if manifest.get('status')!='SEALED_OUTPUTS_READY':
        raise ValueError('holdout output seal not operational')
    if manifest.get('consumer_access_allowed') is not False:
        raise ValueError('manifest must remain denied until check passes')
    commit=manifest.get('trusted_coordination_commit','')
    if not re.fullmatch(r'[0-9a-f]{40}',commit):
        raise ValueError('trusted coordination commit not pinned')
    if sha(freeze_bytes)!=manifest.get('authorized_freeze_receipt_sha256'):
        raise ValueError('freeze receipt SHA mismatch')
    freeze=json.loads(freeze_bytes)
    if not REQUIRED<=set(freeze) or set(freeze['exact_holdout_points'])!=HOLDOUT:
        raise ValueError('freeze receipt missing fields or exact point set')
    if not freeze['DQ_id'] or not freeze['phenomenon'] or freeze['sign'] not in ('POSITIVE','NEGATIVE','MIXED','NULL'):
        raise ValueError('unusable pre-frozen scientific rule')
    if not freeze['estimator'] or not freeze['materiality_threshold'] or not freeze['STOP_rule']:
        raise ValueError('unusable estimator/materiality/STOP')
    outputs=manifest.get('encrypted_outputs',[])
    if {item['point_id'] for item in outputs}!=HOLDOUT:
        raise ValueError('encrypted output inventory incomplete')
    for item in outputs:
        rel=Path(item['relative_path'])
        if rel.is_absolute() or '..' in rel.parts or rel.suffix!='.cms':
            raise ValueError('unsafe or plaintext holdout path')
        path=ciphertext_root/rel
        if not path.is_file() or sha(path.read_bytes())!=item['sha256']:
            raise ValueError('encrypted output SHA mismatch')
    return dict(status='ELIGIBLE_FOR_COORDINATOR_KEY_RELEASE_NOT_DECRYPTED',
                freeze_sha256=sha(freeze_bytes),trusted_coordination_commit=commit,
                exact_holdout_points=sorted(HOLDOUT),ciphertext_count=len(outputs))


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--freeze-receipt',type=Path,required=True)
    p.add_argument('--ciphertext-root',type=Path,required=True)
    args=p.parse_args()
    result=check_release(json.loads(args.manifest.read_bytes()),
                         args.freeze_receipt.read_bytes(),args.ciphertext_root)
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
