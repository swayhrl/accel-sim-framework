"""Small frozen-evidence manifest assembler. No scientific side effects."""
import argparse,pathlib,json,hashlib
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops/revision16';receipt=O/'R16_TWO_SCOPE_METADATA_FREEZE_RECEIPT_V1.json';h=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();r=json.loads(receipt.read_bytes())
assert h(receipt)=='45a67468080f5ad65286479a7d1c90b6af071aeae776043b05920d733e279e93'
p=argparse.ArgumentParser();p.add_argument('--lava-proof',type=P,required=True);p.add_argument('--late-proof',type=P,required=True);p.add_argument('--resource-proof',type=P,required=True);p.add_argument('--lava-resource-proof',type=P,required=True);a=p.parse_args()
files=[{'path':str(receipt),'sha256':h(receipt)},{'path':r['preimage_manifest_path'],'sha256':r['preimage_manifest_sha256']}];scopes={}
for root,meta in r['final'].items():
 for x in meta.values():files.append(x)
 key='DTC_AE_LAVAMEM_REPAIR_20261026_V2' if root.endswith('validation_lava_memory_v2') else 'DTC_AE_LATE_FAILURE_REPAIR_20261026_V1'
 scopes[key]={'plan_path':meta['plan']['path'],'profile_path':meta['profile']['path']}
files.extend(r['unchanged_source_pins'])
proofs=[{'kind':kind,'path':str(path),'sha256':h(path)} for kind,path in [('LAVA_DEEP_PRE_POPEN',a.lava_proof),('LATE_DEEP_PRE_POPEN',a.late_proof),('FOUR_SCOPE_RESOURCES_AND_METADATA',a.resource_proof),('LAVA_RESOURCES_AND_METADATA',a.lava_resource_proof)]]
out=O/'R16_FROZEN_EVIDENCE_MANIFEST_V1.json'
with out.open('x') as f:json.dump(dict(frozen_files=files,CPU_proofs=proofs,scopes=scopes),f,indent=2);f.write('\n')
print(json.dumps({'manifest':str(out),'sha256':h(out)}))
