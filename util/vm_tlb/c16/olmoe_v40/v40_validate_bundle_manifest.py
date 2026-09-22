#!/usr/bin/env python3
"""Producer-side use of the receiver's strict Pipeline V1 manifest validator."""
import argparse,json,sys
from pathlib import Path
REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-v40-publish-109-v1')
sys.path.insert(0,str(REPO/'util/vm_tlb/c16/data_plane'))
from receiver_common import validate_manifest,enumerate_regular_artifacts,sha256_file
TOKEN='5d05e7cb6f5f89dda4feff7aded76f27e9630b57d527526812accf9db329ecc5'
RECEIPT='1773bcad6b2ebd6206f96be4b25c268dd316bad1978588530e550459f807e7fb'
def main():
 p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 manifest=json.loads((a.bundle/'RUN_MANIFEST.json').read_text());validate_manifest(manifest)
 if manifest['input']['token_ids_sha256_or_semantic_hash']!=TOKEN or manifest['input']['receipt_sha256']!=RECEIPT:raise SystemExit('input binding')
 if manifest['artifacts']!=enumerate_regular_artifacts(a.bundle):raise SystemExit('artifact inventory')
 if a.output.exists():raise SystemExit('receipt exists')
 a.output.write_text(json.dumps({'status':'PASS_SHARED_PIPELINE_V1_MANIFEST_VALIDATION','run_id':manifest['run_id'],'manifest_sha256':sha256_file(a.bundle/'RUN_MANIFEST.json'),'input_token_ids_sha256':TOKEN,'input_receipt_sha256':RECEIPT,'artifact_count':len(manifest['artifacts'])},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
