#!/usr/bin/env python3
"""Verify Root's closed current-binary attestation joins; never read binary bodies."""
import hashlib,pathlib
from collections import defaultdict
from audit_common_v1 import need
ATTEST_SHA='6eea0372813e8d102a042601cfc7bedcf3f269effc5ebdc63c5af7bc4c99ad78'
def check_binary_attestation(reader,path,scope_rows,pinned_sha=ATTEST_SHA,scope_sha='b48a9007274459184c332b77f10784c1fbb8b1c1df213543c65d18a4d8e5327a'):
 need(hashlib.sha256(reader.bytes(path)).hexdigest()==pinned_sha,'BINARY_ATTESTATION_PIN_CHANGED')
 att=reader.obj(path);expected=defaultdict(set)
 need(att.get('schema')=='EXACT161_CURRENT_BINARY_READONLY_ATTESTATION_V1','WRONG_BINARY_ATTESTATION_SCHEMA')
 for row in scope_rows:
  need(isinstance(row.get('argv'),list) and row['argv'],'SCOPE_BINARY_PATH_MISSING')
  expected[(row['argv'][0],row['binary_sha256'])].add(row['queue_id'])
 seen=set();ids=[]
 for row in att['rows']:
  key=(row['path'],row['expected_sha256']);need(key in expected and key not in seen,'BINARY_PATH_SHA_PAIR_UNKNOWN_OR_DUPLICATE',key);seen.add(key)
  need(row.get('status')=='MATCH_CLOSED_CURRENT_BINARY' and row.get('actual_sha256')==key[1],'BINARY_ATTESTATION_MISMATCH',key)
  need(row.get('before')==row.get('after') and row['before']['size']==row['bytes']>0,'BINARY_ATTESTATION_NOT_CLOSED',key)
  group=row['source_ids'];need(len(group)==len(set(group)) and set(group)==expected[key],'BINARY_SOURCE_ID_JOIN_MISMATCH',key)
  need(pathlib.Path(row['resolved_path']).is_absolute(),'INVALID_ATTESTED_RESOLVED_PATH')
  ids.extend(group)
 need(seen==set(expected),'BINARY_ATTESTATION_MISSING_PAIR')
 need(len(ids)==len(set(ids))==161,'BINARY_ATTESTATION_NOT_EXACT161')
 need(att.get('closed') is True and att.get('no_GPU') is True and att.get('no_CUDA_init_or_product_execution') is True and att.get('source_files_modified') is False,'BINARY_ATTESTATION_SCOPE_OR_PERMISSION')
 need(att.get('scope_sha256')==scope_sha,'BINARY_ATTESTATION_SCOPE_MISMATCH')
 return {'exact_binary_path_sha_pairs':len(seen),'exact_ids':len(ids),'independent_metadata_reopen':True,'binary_bodies_rehashed_by_checker':0,'root_attestation_sha256':pinned_sha}
