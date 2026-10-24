from pathlib import Path
import json,hashlib,gzip,csv,sys,os,collections,datetime
R=Path('/root/data/shared_sm70_trace_library_20261024_v1');W=Path('/root/data/ep_l2_main_20261023_v1/worktree');NAS=Path('/root/share/mnt164/huangrulin/traces')
O=W/'docs/ep_l2/operations/shared_sm70_trace_library_20261024_v1';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'tools'));import library_copy as e
v=e.v9();catalog=json.loads((NAS/'catalog/CURRENT').read_text());assets=catalog['assets']
assert json.loads((R/'control/CROSS_PROJECT_VALIDATION.json').read_text())['status']=='PASS_CROSS_PROJECT_ALL_ASSET_ACCESS'
restore=json.loads((R/'control/BOUNDED_NATIVE_RESTORE_COMPLETE.json').read_text());assert restore['objects']==len(catalog['objects'])
expected=json.loads((R/'control/INPUT_ALIASES_FROM_AUDIT.json').read_text())
seen={(p.get('host'),p.get('path'),a['extent']) for a in assets for p in a['source_aliases']}
missing=[r for r in expected if (r['host'],r['path'],r['extent']) not in seen];assert not missing,missing
prior=json.loads(Path('/root/data/ep_dtc_trace_migration_20261024_v1/controls/ASSET_CATALOG.json').read_text())['assets']
assert all(any(set(p['aliases']).intersection(a['aliases']) for a in assets) for p in prior)
before=json.loads((R/'control/PROTECTED_PREIMAGE.json').read_text());after={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in before}
tool_changes=[p for p in before if '/tools/' in p or p.endswith('/bin/native') if before[p]!=after[p]];assert not tool_changes
archives=[json.loads(gzip.decompress(p.read_bytes())) for p in sorted((R/'control').glob('ARCHIVE_[0-9]*.json.gz'))]
assert len(archives)==4 and all(a['source_before_after_unchanged'] and a['compressed_bytes_read']==a['archive_identity']['size'] for a in archives)
proof_dir=NAS/'receipts/goal_20261024_v1';proof_dir.mkdir(exist_ok=True)
proof_index=[]
for p in sorted((R/'control').iterdir()):
 if p.is_file() and p.suffix in ['.json','.jsonl','.gz']:
  b=p.read_bytes();name=p.name
  if len(b)>1024**2 and p.suffix!='.gz':b=gzip.compress(b,mtime=0);name+='.gz'
  e.publish_bytes(proof_dir/name,b,v);proof_index.append({'name':name,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
tool_dir=proof_dir/'tools';tool_dir.mkdir(exist_ok=True)
for p in sorted((R/'tools').iterdir()):
 if p.is_file() and p.suffix=='.py':e.publish_bytes(tool_dir/p.name,p.read_bytes(),v)
e.publish_bytes(tool_dir/'zstd',(R/'tools/zstd').read_bytes(),v)
summary={'status':'PASS_COMPLETE_SHARED_ASSET_LIBRARY','catalog_id':catalog['catalog_id'],'registered_input_bundles':len(assets),'unique_content_objects':len(catalog['objects']),'unique_content_bytes':sum(o['size'] for o in catalog['objects'].values()),'all_original_complete_input_aliases_covered':len(expected),'all20_prior_asset_aliases_covered':True,'archive_containers_audited':len(archives),'regular_bundles':sum(a['kind']=='regular' for a in assets),'fraction_bundles':sum(a['kind']=='fraction' for a in assets),'by_suite':dict(collections.Counter(a['suite'] for a in assets)),'public_root':'/root/workspace/assets/traces','public_command':'/root/workspace/assets/bin/trace-assets','all_project_access_verified':True,'full_closed_native_window_restore':restore,'complete_large_dataset_simultaneous_materialization_claimed':False,'source_keep':True,'source_release_bytes':0,'scientific_starts':0,'109_capture_starts':0,'science_qualification_granted':False,'protected_before':before,'protected_after':after,'protected_scientific_tools_unchanged':True,'registry_or_epoch_external_differences':[p for p in before if p not in tool_changes and before[p]!=after[p]],'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(R/'control/FINAL_VALIDATION.json').write_text(json.dumps(summary,indent=2)+'\n');e.publish_bytes(proof_dir/'FINAL_VALIDATION.json',e.canon(summary),v)
for n in ['FINAL_VALIDATION.json','USER_AUTHORIZATION.json','ENGINE_DERIVATION.json','PUBLIC_WRAPPER_QUALIFICATION.json','ZSTD_PROTOCOL_QUALIFICATION.json','NATIVE_BACKEND_QUALIFICATION.json','EXPANDED_FROZEN_BUDGET.json','ARCHIVE_FROZEN_BUDGET.json','LIBRARY_PUBLICATION.json','BOUNDED_NATIVE_RESTORE_COMPLETE.json']:
 (O/n).write_bytes((R/'control'/n).read_bytes())
(O/'PROOF_INDEX.json').write_text(json.dumps(proof_index,indent=2)+'\n')
with (O/'ASSET_INDEX.csv').open('w',newline='') as f:
 fields=['suite','version','program','kind','architecture','bundle_id','kernel_launches','logical_bytes','view_path','source_alias_count']
 out=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');out.writeheader()
 for a in assets:out.writerow({**{k:a[k] for k in fields if k!='source_alias_count'},'source_alias_count':len(a['source_aliases'])})
e.publish_bytes(NAS/'catalog/ASSET_INDEX.csv',(O/'ASSET_INDEX.csv').read_bytes(),v)
archive_rows=[{'path':a['path'],'archive_sha256':a['archive_sha256'],'physical_bytes':a['archive_identity']['size'],'grouped_member_bytes_hashed':a['hashed_member_bytes'],'entries':len(a['members'])} for a in archives]
(O/'ARCHIVE_AUDIT_SUMMARY.json').write_text(json.dumps(archive_rows,indent=2)+'\n')
md=f'''# 174-new跨项目共享trace资产库（2026-10-24）

状态：数据接入、全文件身份校验、跨项目访问和全对象有界本地恢复均完成。科学资格、预算、旧失败/接受记录没有因此提升或覆盖。本Goal未运行模拟器、编译或109采集。

统一入口：`/root/workspace/assets/traces/`；公共命令：`/root/workspace/assets/bin/trace-assets`。同一174-new执行环境中的各项目无需激活EP/DTC环境即可使用。

正式主档：真164 `/home/shared/huangrulin/traces/`。原有20套已验证对象保留原位并接入内容索引；其旧路径和旧查询入口保留。全部原Source保持KEEP，释放0B。

## 交付规模

- 精确输入集合：{len(assets)}，其中常规{summary['regular_bundles']}、裁剪{summary['fraction_bundles']}；不以S/F、工作目录别名或不同项目引用重复计输入。
- 唯一内容文件：{summary['unique_content_objects']}，逻辑内容{summary['unique_content_bytes']:,}B。不同输入可复用同一内容对象；物理NAS占用另含续传块及原有存储副本，不能把此数当成新增物理分配。
- 原账户清点中{len(expected)}条有效输入路径观察全部有公共入口；已有20套资产别名全部覆盖。
- 完整核查四个大型归档，新增有效输入与展开文件去重后登记；无效/冲突/缺失项保留在`quarantine/INPUT_ISSUES.json`，不标为READY。
- 全局目录：`catalog/CURRENT`，内容ID `{catalog['catalog_id']}`；逐输入表见`catalog/ASSET_INDEX.csv`，suite缺口见`catalog/SUITE_COVERAGE.json`。

## 使用

```sh
/root/workspace/assets/bin/trace-assets list
/root/workspace/assets/bin/trace-assets list --suite Parboil
/root/workspace/assets/bin/trace-assets show <bundle-id>
/root/workspace/assets/bin/trace-assets verify <bundle-id>
/root/workspace/assets/bin/trace-assets materialize <bundle-id> --destination /root/data/<project>/NEW-cache --dry-run
```

需要真实物化时显式指定新ABSENT本地目录及字节预算。工具保留共享磁盘余量，拒绝写入公共主档、已有目标或非指定native文件系统。各项目独立热写，不把输出写回公共trace树。

## 验收边界

EP、DTC、C16三个工作目录已分别在无项目激活环境下验证公共目录、所有资产成员读取、完整小输入物化及负面拒绝案例。公共数据接口仅提供查询、校验和显式新本地物化；它不是root用户权限隔离墙，也不是科学启动入口。

每个唯一对象均从164完整读取，经不超过64MiB的本地ext4窗口关闭、重开、重算SHA；累计重建整文件SHA与内容身份一致。受本地空间限制，大输入没有同时完整展开在本地，不能把有界窗口恢复称为大输入完整本地物化。小输入另有完整本地物化回执。

“常规”仍是目录未标记裁剪的资产分类，不新宣称原始捕获完整性或数值正确性；裁剪来源与比例只有可见证据才登记。版本、源参数和历史接受上下文保留，SM70或其他header证据按实际记录；没有改写header或将数据READY变为模拟接受。B+Tree/Scan/SpMV既有HOLD不解除。

完整证据、源全SHA账本、归档索引、传输/恢复回执、工具与私有zstd依赖出处在164 `receipts/goal_20261024_v1/`。Git内保留索引与小型审计材料，大正文保持在164。
'''
(O/'SHARED_TRACE_LIBRARY.md').write_text(md);e.publish_bytes(NAS/'README.md',md.encode(),v)
for p in [R/'tools/trace_assets_public.py',R/'tools/publish_library.py',R/'tools/restore_all_windows.py',R/'tools/build_archive_plan.py',R/'tools/build_expanded_plan.py',R/'tools/library_copy.py']:(O/p.name).write_bytes(p.read_bytes())
(O/'DELIVERY_SHA256.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.iterdir()) if p.is_file() and p.name!='DELIVERY_SHA256.json'},indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ['protected_before','protected_after']}),flush=True)
