#!/usr/bin/env python3
"""Independent reopening of original job and frozen exact identity/profile projection."""
import ast,hashlib,pathlib,json
from audit_common_v1 import need,canonical
def verify_identity_inputs(reader,result,row,admission,allow,require_projection=True):
 refs=result.get('inputs',[])+result.get('evidence',[])
 candidates=[x for x in refs if x['sha256']==row['job_sha256']]
 need(bool(candidates),'ORIGINAL_JOB_PREIMAGE_NOT_REOPENED')
 job=reader.refobj(candidates[0]);task=job.get('task',{})
 need(task.get('binary_sha256')==row['binary_sha256'] and task.get('argv')==row['argv'],'JOB_PREIMAGE_BINARY_OR_ARGV_CHANGED')
 if not require_projection:return
 source=reader.bytes(allow['path']).decode();tree=ast.parse(source)
 assignments={target.id:node.value for node in tree.body if isinstance(node,ast.Assign) for target in node.targets if isinstance(target,ast.Name)}
 need('INDEX_SHA' in assignments,'APPROVED_METADATA_ADAPTER_LACKS_AUTHORITY_PIN')
 index_sha=ast.literal_eval(assignments['INDEX_SHA']);need(isinstance(index_sha,str) and len(index_sha)==64,'INVALID_AUTHORITY_INDEX_PIN')
 names={node.args[0].value for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='with_name' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str) and node.args[0].value.startswith('FROZEN_AUTHORITY_INDEX')}
 need(len(names)==1,'AMBIGUOUS_AUTHORITY_INDEX_PATH')
 path=pathlib.Path(allow['path']).with_name(next(iter(names)))
 found=[x for x in refs if x['path']==str(path) and x['sha256']==index_sha]
 need(len(found)==1,'FROZEN_AUTHORITY_INDEX_NOT_REOPENED')
 index=reader.refobj(found[0]);item=index['rows'][admission['row_index']]
 need(item['queue_id']==row['queue_id'] and item['frozen_row_sha256']==canonical(row),'AUTHORITY_INDEX_ROW_CHANGED')
 projection_ref=item['projection_ref'];need(projection_ref in refs,'EXACT_AUTHORITY_PROJECTION_NOT_REOPENED')
 projection=reader.refobj(projection_ref);need(projection['scope_row']==row,'AUTHORITY_SCOPE_ROW_CHANGED')
 ir=projection['identity_row'];pr=projection['profile_row']
 need(ir['queue_id']==pr['queue_id']==row['queue_id'],'IDENTITY_PROFILE_WRONG_QUEUE')
 need(ir['job_evidence']['sha256']==pr['job_evidence']['sha256']==row['job_sha256'],'PROFILE_JOB_SHA_CHANGED')
 expected_path=ir['job_evidence']['snapshot']
 need(any(x['path']==expected_path and x['sha256']==row['job_sha256'] for x in candidates),'ORIGINAL_JOB_WRONG_SNAPSHOT_PATH')
 original=reader.obj(expected_path);need(original==job,'ORIGINAL_JOB_SNAPSHOT_MISMATCH')
 scientific=ir['scientific_identity']
 need(scientific['binary_sha256']==pr['binary_sha256']==row['binary_sha256'] and scientific['argv']==pr['argv']==row['argv'],'DECLARED_PROFILE_BINARY_ARGV_MISMATCH')
 legacy=hashlib.sha256(json.dumps(scientific,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 need(legacy==ir['scientific_identity_sha256']==row['declared_identity_sha256'],'DECLARED_IDENTITY_DIGEST_CHANGED')
 need(pr['profile_families']==row['profile_families_nonexclusive'],'PROFILE_FAMILY_MISMATCH')
 mapper=projection.get('mapper_row')
 if mapper:need(mapper['id']==row['queue_id'] and mapper['binary_sha256']==row['binary_sha256'],'MAPPER_PROJECTION_IDENTITY_MISMATCH')
