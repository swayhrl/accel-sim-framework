"""Separate Stage2 files; immutable initial Shared source paths are read only."""
from pathlib import Path
O=Path(__file__).parent
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
OLD=A/'agents/E/cpu_shared_timeslice_strict_v1'
def one(text,a,b):
 assert text.count(a)==1,(a[:80],text.count(a));return text.replace(a,b)
s=(OLD/'resource_extra_strict.py').read_text()
s=one(s," assert c in design['initial_scope']['allowed_cohorts']and design['initial_scope']['max_shared_running']==1,'Only initial exact1 qualified'", " assert cfg['qualification_stage']=='AFTER_NATURAL_SHARED_CANARY'and cfg['max_shared_running']==1,'Stage2 exact engineering scope only'\n first=snap['fresh_preflights'][0]\n extension=lib.validate_scope_certificate(cfg,authority,first['scope_extension_approval_utf8'],first['scope_extension_source_artifacts_utf8'])\n assert c in extension['allowed_cohorts']and set(cfg['allowed_cohorts'])==set(extension['allowed_cohorts']),'Real Stage2 certificate scope'\n for p in snap['fresh_preflights']:\n  assert p['scope_extension_approval_utf8']==first['scope_extension_approval_utf8']and p['scope_extension_source_artifacts_utf8']==first['scope_extension_source_artifacts_utf8'],'Stage2 certificate witnesses differ'")
s=one(s," first=snap['fresh_preflights'][0]", " first=snap['fresh_preflights'][0]\n assert snap['scope_extension_approval_utf8']==first['scope_extension_approval_utf8']and snap['scope_extension_source_artifacts_utf8']==first['scope_extension_source_artifacts_utf8'],'Resource top/captured proof certificate mismatch'")
(O/'resource_extra_strict.py').write_text(s)
s=(OLD/'bpf_extra_strict.py').read_text()
s=one(s,'def normalize_contract(document,root,source_sha256,qualification_only=False):','def normalize_contract(document,root,source_sha256,qualification_only=False,cfg=None):')
s=one(s," design=read(DESIGN_PATH);allowed=design['initial_scope']['allowed_cohorts']\n require(len(allowed)==1 and design['initial_scope']['max_shared_running']==1,'Initial exact1 only')", " require(cfg is not None,'Stage2 captured config required')\n approval=validate_stage2_approval(cfg)\n allowed=approval['allowed_cohorts']\n require(set(allowed)==set(document['scope_cohorts'])and len(allowed)==4,'Only original four engineering identities')")
s=one(s,"resource_configuration_sha256=cfg['resource_configuration_sha256'],design_contract_sha256=DESIGN_SHA)","resource_configuration_sha256=cfg['resource_configuration_sha256'],design_contract_sha256=DESIGN_SHA,scope_extension_approval_sha256=cfg['scope_extension_approval_sha256'])")
s=one(s," require(set(cfg['modes'])==set(read(DESIGN_PATH)['initial_scope']['allowed_cohorts'])and cfg['modes'][c]=='DEFAULT_CONTROL','Initial SharedCPU exact1 control mode')", " approval=validate_stage2_approval(cfg)\n require(cfg['modes']==approval['modes']and c in cfg['modes'],'Only Stage2 original four requested modes')\n require(utfsha(snap['scope_extension_approval_utf8'])==cfg['scope_extension_approval_sha256'],'Stage2 approval snapshot')")
import hashlib
resource_sha=hashlib.sha256((O/'resource_extra_strict.py').read_bytes()).hexdigest()
(O/'bpf_extra_strict.py').write_text(s+"\nSTAGE2_RESOURCE_EXTRA_SHA="+repr(resource_sha)+'\n'+(O/'mixed_generation_gate.py').read_text())
# The source-generation-aware consumer is generated separately below.
