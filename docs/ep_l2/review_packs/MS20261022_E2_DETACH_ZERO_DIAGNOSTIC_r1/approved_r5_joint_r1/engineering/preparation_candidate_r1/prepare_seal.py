"""Root-only candidate seal builder. Reads metadata only; writes requested /tmp output.
Does not activate source, acquire lease, or change the registry/CLIENT.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
import r5_preparation as p
E=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
P=E/'docs/ep_l2/review_packs/MS20261022_E2_DETACH_ZERO_DIAGNOSTIC_r1'
def ref(path):
 path=Path(path);return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def git(path,*args):return subprocess.check_output(['git','-C',str(path),*args],text=True).strip()
def build(build_spec):
 a=ref(P/'approved_r5_joint_r1/USER_APPROVAL.json');approval=json.loads(Path(a['path']).read_bytes());proposal=ref(E/approval['proposal_ref']['path'])
 core=git(p.CORE_PATH,'rev-parse','HEAD');p.require(core!=p.BASE,'new Core must actually be committed first')
 p.require(not git(p.CORE_PATH,'status','--porcelain','--untracked-files=no'),'tracked new Core must be clean')
 p.require(git(p.FRAMEWORK_PATH,'rev-parse','HEAD')==p.FRAMEWORK and not git(p.FRAMEWORK_PATH,'status','--porcelain','--untracked-files=no'),'frozen runtime Framework source')
 source=ref(build_spec);identity=dict(core_source_commit=core,framework_source_commit=p.FRAMEWORK,vendor_pybind11_commit=p.VENDOR,build_spec_sha256=source['sha256'])
 registry=Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json');raw=registry.read_bytes();d=json.loads(raw);i=d[p.FIELD]
 m=dict(schema='E2_R5_PREPARATION_BUILD_AUTHORITY_V1',status='E2_R5_PREPARATION_SOURCE_SEALED_NO_APP_AUTHORITY',campaign_id=p.CAMPAIGN,baseline_actual_starts=55,approval_ref=a,proposal_ref=proposal,core_worktree=p.CORE_PATH,framework_worktree=p.FRAMEWORK_PATH,output_directory=p.BUILD_PATH,build_identity=identity,build_spec_ref=source,resource_envelope=dict(role='E',kind='build',cpu_max=2,memory_bytes=8*p.GIB,growth_max_bytes=p.GIB,result_growth_bytes=0,workspace_floor_bytes=5*p.GIB,monitor_margin_bytes=2*p.GIB),formal_build_owner='E2_R5_FORMAL_PRODUCER',applications_authorized_by_preparation=0,registration_authorized_by_preparation=False,historical55_seal=p.seal55(d,i),registry_read_sha256=hashlib.sha256(raw).hexdigest(),root_source_publication_remote_readback_required_before_activation=True)
 p.validate_manifest(m);p.quiescent55(m,d,i);return m
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--build-spec',required=True);ap.add_argument('--out',required=True);args=ap.parse_args();out=Path(args.out).resolve();p.require(out.is_relative_to(Path('/tmp')),'candidate builder only writes /tmp; root explicitly relocates final seal');p.require(not out.exists(),'do not overwrite a previous seal');out.write_text(json.dumps(build(args.build_spec),indent=2)+'\n')
