"""Strict prepared closure; no qualification is granted here."""
import pathlib,json,hashlib,os
ALG='0f2a6d35e5f2547aa284a075a02fae1b981483d9b10614f6275697368ef513a4'
IO='19a5274933da2ec0c83852ac7d87bddcff3b3fdd70d47d0d51769266fe93116e'
def check(source,row,hashfile):
 source=pathlib.Path(source).resolve()
 receipt=json.loads((source.parent/'PREPARED.json').read_text())
 assert receipt['status']=='PREPARED_VALIDATED_NOT_PUBLISHED' and receipt['scope_row']==row
 assert receipt['prepared_root']==str(source)
 assert receipt['generator_sha256']==ALG and receipt['IO_adapter_sha256']==IO
 assert receipt['source_KEEP'] is True and receipt['release_bytes']==0 and receipt['scientific_qualification_granted'] is False
 paths={}
 for x in receipt['files']:
  rel=pathlib.PurePosixPath(x['path'])
  assert not rel.is_absolute() and '..' not in rel.parts and str(rel)==x['path'] and x['path'] not in paths
  paths[x['path']]=x
 tree=list(source.rglob('*'));assert not any(p.is_symlink() for p in tree)
 actual={str(p.relative_to(source)) for p in tree if p.is_file()}
 assert actual==set(paths),'extra/missing prepared member'
 for name,x in paths.items():
  p=source/name
  assert p.stat().st_size==x['bytes'] and hashfile(p)==x['sha256'],'changed prepared member'
 asset=json.loads((source/'ASSET.json').read_text());proof=json.loads((source/'DERIVED_VALIDATION.json').read_text())
 assert asset['asset_id']==row['derived_asset_id'] and asset['parent_asset_id']==row['parent_asset_id']
 assert asset['parent_commit_sha256']==row['parent_commit_sha256'] and asset['parent_manifest_sha256']==row['parent_manifest_sha256']
 assert asset['generator_sha256']==ALG and asset['kind']=='DERIVED_COMPLETE_CTA_TRACE'
 assert proof['status']=='COMPLETE_CTA_PARENT_MEMBER_EQUALITY_PASS' and proof['all_selected_warps_complete'] and proof['full_xz_crc_and_eof']
 return receipt
