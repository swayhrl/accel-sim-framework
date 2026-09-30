#!/usr/bin/env python3
"""CPU-only, deterministic Round16 Lane F predecision review files."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-vla-rtc-vjp-boundary-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1'
LEROBOT=ROOT/'source/lerobot';REPAIRED=ROOT/'source/lerobot_repaired';KINETIX=ROOT/'source/kinetix'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def git(*args):return subprocess.check_output(['git',*map(str,args)],text=True).strip()

def main():
    rtc_rel='src/lerobot/policies/rtc/modeling_rtc.py'
    smol_rel='src/lerobot/policies/smolvla/modeling_smolvla.py'
    assert git('-C',LEROBOT,'rev-parse','HEAD')=='e0d50211ef236143ae867228662b7dfaba554f02'
    assert git('-C',KINETIX,'rev-parse','HEAD')=='9296f31d62d5bfeb5779dcb2f9bcf71ca37f448b'
    assert git('-C',LEROBOT,'rev-parse',f'HEAD:{rtc_rel}')=='24f0c6a5bf994da0794e6e758ee5561e717d2817'
    assert git('-C',LEROBOT,'rev-parse',f'HEAD:{smol_rel}')=='cbea888a8f4e414498b8f12c1cc3f8499ac3191b'
    assert git('-C',KINETIX,'rev-parse','HEAD:src/model.py')=='9e04c86cd3b26e33627128032aa8e98bc6f7de70'
    assert sha(LEROBOT/rtc_rel)=='6d8b1ffef42c42c5315660e8d59068617e57e3054336f7f9baf379667f6671b2'
    assert sha(REPAIRED/rtc_rel)=='48c69b9397eac3b3d8b0c77985c88abc0a5a965a0da2adb6a9852d0c7e6ec71d'
    assert sha(ROOT/'assets/model/model.safetensors')=='9a9f6413e42c0f332fccbce9a0dc796af2790f82cf002f791cdbf7e01e1afca8'
    assert git('-C',REPAIRED,'diff','--numstat',rtc_rel)=='1\t1\t'+rtc_rel
    model_api=json.loads((ROOT/'raw/f1/model_api.json').read_text())
    base_api=json.loads((ROOT/'raw/f1/base_vlm_api.json').read_text())
    dataset_api=json.loads((ROOT/'raw/f1/dataset_api.json').read_text())
    assert model_api['sha']=='31d453f7edd78c839a8bbc39744a292686daf0de'
    assert base_api['sha']=='7b375e1b73b11138ff12fe22c8f2822d8fe03467'
    assert dataset_api['sha']=='a1aaacb7f6cd6ee5fb43120f673cebb0cfea7dd4'
    verification=json.loads((ROOT/'raw/f1/metadata_inspection.json').read_text())
    source={
      'stage':'AWMA_VLA_RTC_VJP_BOUNDARY_109_V1',
      'execution_start_head':'6586b2530c38ccd3e7aa620e14990f0c1274bbef',
      'lerobot':{'repo':'https://github.com/huggingface/lerobot','commit':git('-C',LEROBOT,'rev-parse','HEAD'),
          'rtc_blob':git('-C',LEROBOT,'rev-parse',f'HEAD:{rtc_rel}'),
          'smolvla_blob':git('-C',LEROBOT,'rev-parse',f'HEAD:{smol_rel}'),
          'rtc_upstream_sha256':sha(LEROBOT/rtc_rel),
          'rtc_repaired_sha256':sha(REPAIRED/rtc_rel),
          'repair_patch_sha256':sha(WT/'util/vm_tlb/awma/vla_rtc_vjp_boundary/REFERENCE_REPAIR.diff'),
          'repair_scope':'move x_t.requires_grad_(True) before denoiser call; exactly one semantic source repair'},
      'kinetix_reference_only':{'repo':'https://github.com/Physical-Intelligence/real-time-chunking-kinetix',
          'commit':git('-C',KINETIX,'rev-parse','HEAD'),
          'model_blob':git('-C',KINETIX,'rev-parse','HEAD:src/model.py'),
          'readme_blob':git('-C',KINETIX,'rev-parse','HEAD:README.md'),
          'expert_or_dataset_downloaded':False},
      'smolvla_libero':{'repo':'lerobot/smolvla_libero','revision':model_api['sha'],
          'checkpoint_sha256':sha(ROOT/'assets/model/model.safetensors'),
          'checkpoint_bytes':(ROOT/'assets/model/model.safetensors').stat().st_size},
      'base_vlm_config_processor_only':{'repo':'HuggingFaceTB/SmolVLM2-500M-Video-Instruct',
          'revision':base_api['sha'],'base_weights_downloaded':False},
      'dataset':{'repo':'lerobot/libero','revision':dataset_api['sha']},
      'all_asset_files_verified_by_canonical_tree':verification['verified_downloads'],
      'transport':'hf-mirror.com pinned resolve URLs; exact Git blob/LFS OIDs verified; direct huggingface.co timed out on node109',
    }
    (PACK/'SOURCE_IDENTITY.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n')
    upstream=list(csv.DictReader((ROOT/'raw/f0/upstream_canary.tsv').open(),delimiter='\t'))
    repaired=list(csv.DictReader((ROOT/'raw/f0/repaired_canary.tsv').open(),delimiter='\t'))
    assert len(upstream)==len(repaired)==9
    assert all(x['identity_only_pass']=='True' and x['full_jacobian_pass']=='False' for x in upstream)
    assert all(x['identity_only_pass']=='False' and x['full_jacobian_pass']=='True' for x in repaired)
    with (PACK/'VJP_SEMANTIC_CANARY.tsv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(upstream[0]),delimiter='\t',lineterminator='\n')
        writer.writeheader();writer.writerows(upstream+repaired)
    (PACK/'REFERENCE_REPAIR.md').write_text(
        '# Single RTC reference-semantic repair\n\n'
        'Pinned LeRobot RTC source computes `v_t` before `x_t.requires_grad_(True)`. Under the exact wrapper and outer `torch.no_grad()` inference context, `v(x)=2x` gave identity-only VJP in all 9 CPU cases (three shapes × three nondegenerate times); it gave the full `(1-2t)*error` VJP in 0/9. This is `UPSTREAM_RTC_VJP_SEMANTIC_GAP_OBSERVED`.\n\n'
        'The sole reference repair moves `x_t.requires_grad_(True)` immediately before `original_denoise_step_partial(x_t)` inside the existing `torch.enable_grad()` block. No formula, weights, schedule, denoising step, or model source changes. The repaired exact module passed the full analytic VJP in 9/9 and identity-only in 0/9. Its SHA and patch hash are in `SOURCE_IDENTITY.json`; the literal patch is `util/vm_tlb/awma/vla_rtc_vjp_boundary/REFERENCE_REPAIR.diff`. Repaired-vs-upstream timing is never treated as speedup.\n\n'
        'The first real-model observation hook was placed on an expert layer wrapper that this source never invokes; that instrumentation attempt failed only its hook assertion. Moving the hook to the actual expert q_proj submodule left model semantics unchanged. The successful real-model canary observed 10 VJPs, 10 action-output backward hooks and 10 expert-q_proj backward hooks, frozen parameter gradients, and detached prefix outputs. This was a probe correction, not a second reference repair.\n')
    freeze=json.loads((ROOT/'raw/f1/window_freeze.json').read_text())
    discovery=json.loads((ROOT/'raw/f1/discovery_observations_receipt.json').read_text())
    preprocess=json.loads((ROOT/'raw/f1/preprocess_cpu_receipt.json').read_text())
    admission=json.loads((ROOT/'raw/f1/model_admission_cpu.json').read_text())
    graph=json.loads((ROOT/'raw/f0/real_model_graph_canary.json').read_text())
    input_receipt={'model_revision':model_api['sha'],'dataset_revision':dataset_api['sha'],
      'base_vlm_config_processor_revision':base_api['sha'],
      'checkpoint_sha256':source['smolvla_libero']['checkpoint_sha256'],
      'window_freeze':freeze,'discovery_observation_receipt':discovery,
      'preprocessor_frame0_tensor_identity':preprocess,
      'strict_model_and_processor_cpu_admission':admission,
      'real_model_vjp_graph_canary':graph,
      'validation_episode_status':'B_SEALED; no B values selected, inspected or timed; shared Parquet/video files physically include B',
      'no_demonstration_actions_used_as_previous_chunk':True,
      'delay_frames_frozen_after_one_reference_canary':graph['inference_delay_frames']}
    (PACK/'INPUT_RECEIPT.json').write_text(json.dumps(input_receipt,indent=2,sort_keys=True)+'\n')
    print('PRELIMINARY_REVIEW_BUILT')

if __name__=='__main__':main()
