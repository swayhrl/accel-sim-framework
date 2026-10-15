"""CPU-only rights-authority audit record; no dataset/installation/GPU operations."""
from evidence import *
import subprocess,re,resource
P=W/'docs/ai_workload_research/runs/AI_ARCH_A59_LICENSE_AUTHORITY_CPU_109_V1';P.mkdir(parents=True,exist_ok=True);(P/'raw').mkdir(exist_ok=True)
def read(n):return json.loads((R/n).read_text())
def clean(s):
 for a,b in [(str(W),'<AUDIT_WORKTREE>'),(str(R),'<AUDIT_OUTPUT>'),('/home/huangrulin','<HOME>')]:s=s.replace(a,b)
 return s
def write(n,x):(P/n).write_text(clean(x if isinstance(x,str) else json.dumps(x,indent=2)+'\n'))
check();requests=list(map(json.loads,(R/'raw/requests.jsonl').read_text().splitlines()));paper=read('raw/upstream_academic_statement.json');relay=read('raw/controller_relay.json');issue=read('sources/ogb_issue_499.json');comments=read('sources/ogb_issue_499_comments.json');assert issue['state']=='open' and not comments
assert issue['author_association'] not in ['OWNER','MEMBER'];assert issue['comments']==0
quote='We have made this dataset available for academic use';assert paper['verified_quote']==quote and paper['full_SHA256']==sha(R/'sources/upstream_author_paper_complete.pdf')
assert 'Multilingual Amazon Reviews Corpus' in (R/'sources/aws_ml_license.txt').read_text();assert 'academic research' in (R/'sources/aws_ml_license.txt').read_text()
ogb=(R/'sources/ogb_fixed_nodeprop.md').read_text();assert '[Amazon license](https://s3.amazonaws.com/amazon-reviews-pds/license.txt)' in ogb
asl=(R/'sources/aws_software_license.html').read_text();assert '3.3' in asl and 'made available' in asl
prior=pathlib.Path('/data/c16/aiarch_a59_graphsage_products_native_109_v1');old_files={str(p):sha(p) for p in [prior/'final_git_readback.json',prior/'g0_receipt.json',prior/'source/original_XML_repository.html']};oldxml=(prior/'source/original_XML_repository.html').read_text();assert 'Amazon-3M' in oldxml and 'Julian15a' in oldxml and 'styles and substitutes' in ' '.join(re.sub('<[^>]+>',' ',oldxml).split()).lower()
# Current run adds only independent files; old execution branch/worktree stays STOP.
oldW=pathlib.Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-a59-graphsage-products-109-v1');old_head=subprocess.check_output(['git','-C',str(oldW),'rev-parse','HEAD'],text=True).strip();assert old_head=='0e52f088d21e0a88ff471cdf5ad76a7a539cf616';assert subprocess.check_output(['git','-C',str(oldW),'status','--porcelain'],text=True)==''
public_issue={'url':issue['html_url'],'number':499,'state':issue['state'],'created_at':issue['created_at'],'updated_at':issue['updated_at'],'author':issue['user']['login'],'author_association':issue['author_association'],'comments_returned':len(comments),'suggested_URL':'https://aws.amazon.com/asl/','interpretation':'issue opener proposes a replacement; no maintainer reply or assignment of that license to ogbn-products was observed','raw_issue_JSON_sha256':sha(R/'sources/ogb_issue_499.json'),'raw_comments_JSON_sha256':sha(R/'sources/ogb_issue_499_comments.json')}
authorities={'OGB_dataset_mapping':{'fixed_commit':'f4c21f16796589fdf18dee00b206e01915cfa564','file':'_docs/datasets/nodeprop.md','blob':'e4feb4017b0eb5e6ed12dc976f8d6eb4d104cf67','dataset':'ogbn-products','license_URL':'https://s3.amazonaws.com/amazon-reviews-pds/license.txt','current_response':403,'source_sha256':sha(R/'sources/ogb_fixed_nodeprop.md')},'upstream_authors_academic_statement':paper,'historical_lineage_support':{'OGB_reference':'XMLRepository + Cluster-GCN','XMLRepository_Amazon3M_references':'Julian15a and Julian15b; the first is Image-based recommendations on styles and substitutes','XML_snapshot_readonly_sha256':old_files[str(prior/'source/original_XML_repository.html')],'ClusterGCN_README_blob':'755077e42059f948ea9b0678ec83ff23e05181cd','qualification':'related upstream academic release verified; exact OGB derivative scope and currently named Amazon grant not established'},'OGB_open_issue':public_issue,'AWS_ML_license':{'URL':'https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt','blob':'11c0e89cc1cf218c6528b9b1d7eca7013eb35cc4','source_sha256':sha(R/'sources/aws_ml_license.txt'),'explicit_scope':'Multilingual Amazon Reviews Corpus','decision':'EXCLUDED_DIFFERENT_CORPUS; no transfer to ogbn-products'},'Amazon_Software_License':{'URL':'https://aws.amazon.com/asl/','source_sha256':sha(R/'sources/aws_software_license.html'),'facts':'defines Software/Work; application requires a notice or included license; section3.3 restricts use to Amazon web services/platforms/applications','decision':'NOT_ESTABLISHED_AS_OGB_LICENSE; issue suggestion is not maintainer confirmation'},'historical_recovery':{'Wayback_CDX':'TIMEOUT','Wayback_snapshot':'TIMEOUT','Wayback_available_API':'TIMEOUT','AWS_official_PDS_doc_path_current':'404 via controller API','AWS_official_PDS_doc_path_history':'empty list for this exact queried path only','global_absence_claim':False}}
write('AUTHORITY_RECORD.json',authorities)
verdict={'status':'AUTHORITY_PARTIAL_OGB_APPLICABILITY_UNRESOLVED','upstream_academic_use_statement':'VERIFIED_PRIMARY_AUTHOR_PAPER','official_AWS_license_text':'FOUND_FOR_ANOTHER_CORPUS_AND_EXCLUDED','exact_named_OGB_license_fulltext':'NOT_RECOVERED_FROM_VERIFIABLE_OFFICIAL_OR_HISTORICAL_SOURCE','maintainer_confirmed_substitute':'NOT_FOUND_IN_QUERIED_ISSUE_OR_FIXED_DOCUMENTATION','A59_scientific_gate':'KEEP_DATA_LICENSE_NO_GO_STOP','native_training':'NOT_RUN','no_claim_of_illegality_or_global_unavailability':True,'no_external_message_sent':True,'no_GPU_task_started':True};write('APPLICABILITY_DECISION.json',verdict)
repairs={'CPU_budget_clock':'Git parent commit time was rejected as a start clock; use initial start-record wall timestamp minus60s conservative setup charge','PDF_bounded_acquisition':'initial2MiB+1byte sentinel capture identified a9307397B document, not a full PDF; preserved prefix, one tail attempt timed out with0bytes; one retry completed conditional206 ETag-matched range, no duplicate prefix download','PDF_text_extraction':'layout extraction initially interleaved columns; independently cropped page2 left column and asserted the exact10-word quote before qualification','source_identity':'all4 controller-relayed Git files recomputed Git blob SHA1 and file SHA256','not_scientific_changes':True};write('ENGINEERING_REPAIRS.json',repairs)
resources=[read('raw/'+n) for n in ['probe_resource_receipt.json','paper_resource_receipt.json','paper_retry1_resource_receipt.json']];node_bytes=sum(x['bytes'] for x in requests);relay_bytes=sum(x['conservative_origin_plus_relay_bytes'] for x in relay['records']);accounted=node_bytes+relay_bytes+2*1024**2;assert accounted<16*1024**2
resource_record={'limits':{'CPU_effective_workers':1,'RAM_bytes':256*1024**2,'metadata_network_bytes':16*1024**2,'new_disk_bytes':32*1024**2,'wall_seconds':1200},'actual':{'node_HTTP_body_bytes':node_bytes,'controller_source_origin_and_relay_accounted_bytes':relay_bytes,'control_search_read_transport_conservative_reserve_bytes':2*1024**2,'total_network_accounted_with_reserve_bytes':accounted,'task_own_disk_allocated_bytes_before_report':check(),'host_free_bytes':shutil.disk_usage(R).free,'CPU_affinity':[0],'sampled_parent_child_RSS_peak_bytes':max(x['peak_sampled_parent_child_RSS_bytes'] for x in resources),'guard_RAM_stop_bytes':240*1024**2,'each_python_RLIMIT_AS_bytes':256*1024**2,'GPU_initialization_and_lock_operations':0,'scientific_graph_download_bytes':0,'dependency_download_install_bytes':0,'training_steps':0,'elapsed_seconds_before_publication':time.time()-read('start.json')['epoch']},'scope':'RSS sampling covers supervised HTTP probe and PDF acquisition/retry; small single-process relay/archive helpers have the same affinity/address-space limit; values are sampled rather than exact instantaneous whole-system peaks','CPU_probe_receipts':resources,'network_reserve_is_not_measured_transfer':True,'original_A59_worktree_HEAD':old_head,'original_A59_worktree_clean':True,'old_readonly_file_SHA256':old_files,'no_old_asset_write_or_system_change':True,'no_future_task':True};write('RESOURCE_RECEIPT.json',resource_record)
manifest=[]
for p in sorted((R/'sources').glob('*')):
 if p.is_file():manifest.append({'private_name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'partial_warning':'bounded prefix only; not completePDF' if p.name=='upstream_author_paper.pdf' else None})
write('SOURCE_MANIFEST.json',{'sources':manifest,'controller_git_sources':relay,'HTTP_requests':requests,'no_full_third_party_PDF_HTML_dataset_in_Git':True})
write('raw/requests.jsonl',(R/'raw/requests.jsonl').read_text());write('raw/controller_relay.json',relay);write('raw/ogb_issue_499_summary.json',public_issue);write('raw/upstream_academic_statement.json',paper)
for name in ['probe_resource_receipt.json','paper_resource_receipt.json','paper_retry1_resource_receipt.json']:write('raw/'+name,read('raw/'+name))
write('REVIEW_REQUEST_DRAFT.md','''# 未发送的单一核实问题

请 OGB 维护者或适当权利人确认：哪份使用条款适用于官方 ogbn-products 的图结构、PCA 特征、标签及划分？原始 McAuley 等作者的学术使用声明是否覆盖这一派生版本及本次本地、有限 GraphSAGE 科研使用？请提供可固定版本的条款/许可记录与适用范围。若建议采用 Amazon Software License，请同时给出将该具体数据集置于该许可下的通知或授权依据。

本文件仅为可审阅草稿；未创建 issue、评论或发送邮件。未恢复 A59，不自动追加另一轮许可搜索或 GPU 工作。
''')
report=f'''# A59 后续｜ogbn-products 许可权威 CPU-only 核查（109 / Lane M）

**裁决：AUTHORITY_PARTIAL_OGB_APPLICABILITY_UNRESOLVED。保留原 A59 的 DATA_LICENSE_NO_GO / STOP，不启动训练。** 本轮取得了原始作者论文的学术使用声明，也排除了两个容易误用的替代许可；尚未获得将可读正式条款明确绑定到官方 ogbn-products 的权威记录。这个结论不表示使用违法、许可被撤销，或所有来源都不存在许可。

用户明确同意本次109独立CPU-only核查。新分支 `hrl/aiarch-a59-license-authority-cpu-109-v1`，固定父提交 `0e52f088d21e0a88ff471cdf5ad76a7a539cf616`；新 worktree/output，原A59工作区和证据只读。预算1worker/RAM256MiB/元数据16MiB/新增盘32MiB/20分钟。没有访问GPU、共享GPU锁、训练、科学图数据或依赖安装。

## 新增证据与适用性

| 证据 | 实际核查结果 | 能证明什么 |
|---|---|---|
| OGB 固定官方文档 | commit `f4c21f16796589fdf18dee00b206e01915cfa564`、blob `e4feb4017b0eb5e6ed12dc976f8d6eb4d104cf67`；仍将 ogbn-products 指向同一 Amazon license.txt | 确认精确数据集与所引用许可入口；入口本轮403 |
| 原始作者论文 | 原文PDF完整{paper['full_bytes']}B，SHA256 `{paper['full_SHA256']}`；本地第2页左栏文字核验 | 明确存在上游学术使用声明，不再只是二手转述 |
| OGB issue #499 | 2025-03-14提交；当前open、评论0；作者关联 `{issue['author_association']}` | 官方项目已有相同断链报告；未见维护者确认替代许可 |
| AWS 官方多语言评论许可 | Git blob `11c0e89cc1cf218c6528b9b1d7eca7013eb35cc4`，真实文本读到 | 明确限定 Multilingual Amazon Reviews Corpus，不能转用到当前产品图 |
| issue提议的 Amazon Software License | 官方页面实际读到软件定义、许可附着条件和3.3条款 | 未找到将该许可附着到ogbn-products的记录；不据此认定替代许可成立 |
| Internet Archive及官方历史路径 | CDX/快照/available API超时；特定AWS PDS文档路径404且该路径历史查询空 | 本轮未恢复精确历史文本；不是全网不存在的证明 |

原始作者的确切10词引文是：

> We have made this dataset available for academic use

来源：[McAuley等原始论文，第2页](https://snap.stanford.edu/data/amazon/productGraph/sigir_draft.pdf)。完整PDF通过初始有界前缀及一次成功的条件Range恢复，ETag、Content-Range和完整字节数核对一致。一次中间TLS超时计入同一轮；原始前缀、失败和修复收据保留，没有将前缀SHA冒充完整文件SHA。最初双栏文字抽取出现混列，已用左栏裁切独立修复并断言引文，再形成最终资格记录。

OGB指向XMLRepository和Cluster-GCN；原A59只读XMLRepository快照中Amazon-3M引用McAuley的2015论文，Cluster-GCN官方README也说明Amazon2M的数据生成来源。这条链支持“相关上游数据由作者公开供学术使用”的事实。它尚未补齐官方ogbn-products全部派生内容的具体适用条款，也没有恢复OGB当前所引用的Amazon许可正文；本轮不把这一差别自行改成科学门PASS。

[OGB #499](https://github.com/snap-stanford/ogb/issues/499)的替代链接来自提问者建议，不是维护者许可决定。[Amazon Software License](https://aws.amazon.com/asl/)具有其自身适用条件，不能因名称含Amazon就推定它覆盖本图。另一方面，[AWS官方多语言评论许可](https://github.com/awslabs/open-data-docs/blob/main/docs/amazon-reviews-ml/license.txt)虽可读，其命名对象与当前任务不同，也未被借用。没有用代码MIT/Apache许可替代数据许可，没有更换图或科学任务。

## 资源与边界

109实际HTTP正文下载 **{node_bytes}B**；已计控制端官方源获取及中转 **{relay_bytes}B**，另计 **2MiB控制端检索/传输保守预留**，合计账户 **{accounted}B**，低于16MiB。论文是文献元数据证据，不是训练输入；图数据、依赖、安装均0。保守预留不是精确实测流量。

CPU固定在核心0、OpenMP/BLAS1；监督采样任务父子RSS峰 **{resource_record['actual']['sampled_parent_child_RSS_peak_bytes']}B**（约{resource_record['actual']['sampled_parent_child_RSS_peak_bytes']/1024**2:.2f}MiB）。各Python地址空间硬限256MiB，监督提前阈值240MiB。RSS为有边界的采样值，不声称系统绝对峰值。源PDF重建时保留前缀、尾段和完整文件，新盘峰仍在32MiB内；归档前当前自有盘 **{resource_record['actual']['task_own_disk_allocated_bytes_before_report']}B**。最终文件/Git增量及时间在远端回读收据再次核验。

原A59 HEAD仍为固定父提交且工作区clean；相关只读文件SHA记录在资源收据中。无旧资产写入，无系统设置修改，没有向第三方发消息。原A59 GPU步骤保持NOT_RUN。

## 唯一下一步与停止决定

本轮自动检索到此收口，不自动创建新的许可Goal或GPU实验。若继续，应由科学协调审查本轮上游学术使用证据，并取得针对 **官方ogbn-products具体派生内容** 的维护者/权利人适用性说明；可直接使用本目录 `REVIEW_REQUEST_DRAFT.md` 的单一问题草稿。草稿未发送，也不表示已取得新许可。

即使后续审查确认数据准入，A59的二进制ABI、强缓存正确性、数值和训练wall仍未验证，不能由本轮文字证据替代。需要按另行明确授权的连续执行范围推进，维持原科学条件和累计资源账。

## 发布

仅推送本独立CPU核查分支，不修改/合并原A59或协调分支。完整论文/HTML等快照保留在私有输出；Git仅含小型权威/适用性判断、原始API/资源收据、SHA与脚本。提交前检查所有SHA/JSON/脚本语法，push后核exact commit/tree/blob/SHA、clean及预算后STOP。
'''
write('FINAL_REPORT.md',report)
files=sorted([p for p in P.rglob('*') if p.is_file() and p.name!='SHA256SUMS']+list((W/'tools/aiarch_a59_license').glob('*.py')));(P/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(W))+'\n' for p in files))
for p in P.rglob('*.json'):json.loads(p.read_text())
for p in (W/'tools/aiarch_a59_license').glob('*.py'):compile(p.read_text(),str(p),'exec')
for p,h in old_files.items():assert sha(pathlib.Path(p))==h
check();print('AUDIT_ARCHIVE_PASS',len(files)+1,'AUTHORITY_PARTIAL_KEEP_STOP','ACCOUNTED_BYTES',accounted,'NEW_DISK',check(),'REMAINING',read('start.json')['deadline_epoch']-time.time())
