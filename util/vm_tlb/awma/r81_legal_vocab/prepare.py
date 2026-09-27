#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.metadata,json,time
from pathlib import Path

import torch
import transformers
import triton
import xgrammar as xgr
from transformers import AutoTokenizer,AutoConfig

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1')
FIXTURE=WT/'util/vm_tlb/awma/r81_legal_vocab/fixture.json'
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
OUT=ROOT/'raw/fixture'
COMPILED=ROOT/'raw/compiled_grammar'
OUT.mkdir(parents=True,exist_ok=True)
COMPILED.mkdir(parents=True,exist_ok=True)

def sha_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def sha_file(path:Path)->str:return sha_bytes(path.read_bytes())
def canonical(value)->bytes:return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()

fixture=json.loads(FIXTURE.read_text())
weight_audit=json.loads((ROOT/'HEAD_WEIGHT_IDENTITY.json').read_text())
assert weight_audit['fp16_cast_matches_accepted_head']
assert fixture['authority_class']=='AUTHORED_QUALIFICATION_FIXTURE_NOT_PRODUCTION_DISTRIBUTION'
assert list(fixture['cohorts'])==['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT']
assert all(len(v)==4 for v in fixture['cohorts'].values())
assert len({r['id'] for group in fixture['cohorts'].values() for r in group})==12
assert len({r['record'] for group in fixture['cohorts'].values() for r in group})==12
assert len({sha_bytes(canonical(r['schema'])) for r in fixture['cohorts']['C0_SHARED_DISCOVERY']})==1
assert len({sha_bytes(canonical(r['schema'])) for r in fixture['cohorts']['C1_HETEROGENEOUS_DISCOVERY']})==4
assert len({sha_bytes(canonical(r['schema'])) for r in fixture['cohorts']['H0_HETEROGENEOUS_HOLDOUT']})==4

tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,padding_side='left')
cfg=AutoConfig.from_pretrained(MODEL,local_files_only=True)
assert cfg.vocab_size==151936 and tok.eos_token_id is not None
tokenizer_info=xgr.TokenizerInfo.from_huggingface(tok,vocab_size=cfg.vocab_size,
                                                   stop_token_ids=[tok.eos_token_id])
compiler=xgr.GrammarCompiler(tokenizer_info,max_threads=4,cache_enabled=True)
unique={}
requests=[]
for cohort,group in fixture['cohorts'].items():
    for row in group:
        sid=sha_bytes(canonical(row['schema']))
        if sid not in unique:unique[sid]=row['schema']
        input_ids=tok.apply_chat_template([{'role':'user','content':row['prompt']}],
            add_generation_prompt=True,tokenize=True)
        if not isinstance(input_ids,list) or not input_ids:raise ValueError('chat template failed')
        requests.append({'cohort':cohort,'request_id':row['id'],
          'record_sha256':sha_bytes(row['record'].encode()),
          'prompt_sha256':sha_bytes(row['prompt'].encode()),
          'schema_sha256':sid,
          'input_ids':input_ids,
          'input_token_count':len(input_ids),
          'input_ids_sha256':sha_bytes(canonical(input_ids))})

compile_rows=[]
for sid,schema in unique.items():
    start=time.perf_counter_ns()
    compiled=compiler.compile_json_schema(schema,strict_mode=True,any_whitespace=True)
    elapsed_ms=(time.perf_counter_ns()-start)/1e6
    serialized=compiled.serialize_json()
    path=COMPILED/f'{sid}.json'
    path.write_text(serialized)
    compile_rows.append({'schema_sha256':sid,'compiler_ms':elapsed_ms,
        'compiled_json_sha256':sha_file(path),'compiled_bytes':path.stat().st_size,
        'strict_mode':True,'any_whitespace':True})

(OUT/'requests.json').write_text(json.dumps(requests,indent=2,sort_keys=True)+'\n')
tokenizer_serialized=tokenizer_info.serialize_json()
(OUT/'tokenizer_info.json').write_text(tokenizer_serialized)
binding={'stage':'AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1',
 'model':'Qwen/Qwen2.5-0.5B-Instruct',
 'model_revision':'7ae557604adf67be50417f59c2c2f167def9a775',
 'model_weight_sha256':'fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe',
 'model_config_sha256':sha_file(MODEL/'config.json'),
 'native_bf16_tied_head_sha256':weight_audit['head_sha256'],
 'accepted_fp16_cast_head_sha256':weight_audit['fp16_cast_head_sha256'],
 'head_weight_identity_receipt_sha256':sha_file(ROOT/'HEAD_WEIGHT_IDENTITY.json'),
 'model_config_vocab_size':cfg.vocab_size,
 'tokenizer_len':len(tok),'tokenizer_vocab_size':tok.vocab_size,
 'tokenizer_eos_token_id':tok.eos_token_id,
 'tokenizer_pad_token_id':tok.pad_token_id,
 'tokenizer_padding_side':'left',
 'tokenizer_json_sha256':sha_file(MODEL/'tokenizer.json'),
 'tokenizer_info_json_sha256':sha_file(OUT/'tokenizer_info.json'),
 'fixture_sha256':sha_file(FIXTURE),
 'requests_json_sha256':sha_file(OUT/'requests.json'),
 'xgrammar_version':importlib.metadata.version('xgrammar'),
 'xgrammar_wheel_sha256':sha_file(next((ROOT/'wheels').glob('xgrammar-0.2.8-*.whl'))),
 'torch':torch.__version__,'torch_cuda':torch.version.cuda,
 'transformers':transformers.__version__,'triton':triton.__version__,
 'dtype':'torch.bfloat16','max_new_tokens_per_request':128,
 'grammar_backend':'xgrammar GrammarCompiler JSON schema strict_mode=true any_whitespace=true',
 'compiled_grammar_count':len(unique),'compiled_grammar_receipts':compile_rows,
 'no_model_execution_yet':True}
(ROOT/'INPUT_RUNTIME_BINDINGS.json').write_text(json.dumps(binding,indent=2,sort_keys=True)+'\n')
prereg={'stage':'AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1',
 'authority_class':fixture['authority_class'],
 'fixture_sha256':binding['fixture_sha256'],
 'input_runtime_bindings_sha256':sha_file(ROOT/'INPUT_RUNTIME_BINDINGS.json'),
 'request_id_order':{cohort:[r['id'] for r in group] for cohort,group in fixture['cohorts'].items()},
 'schema_ids_and_hashes':{r['request_id']:r['schema_sha256'] for r in requests},
 'input_ids_sha256':{r['request_id']:r['input_ids_sha256'] for r in requests},
 'model_config_vocab_size':cfg.vocab_size,'tokenizer_len':len(tok),
 'dtype':'torch.bfloat16','decoder':'grammar_constrained_greedy_temperature_0',
 'max_new_tokens':128,'natural_eos_and_grammar_completion':True,
 'batch_size':4,'cohorts_discovery':['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY'],
 'cohort_holdout':'H0_HETEROGENEOUS_HOLDOUT',
 'holdout_model_outcome_inspected_before_design':False,
 'arms':{
   'A0_DENSE_VENDOR':'torch.nn.functional.linear full 151936x896, xgrammar bitmask, greedy',
   'A1_DENSE_FUSED':'SM89 Triton tiled FP16 head/mask/argmax; FlashSampling-style greedy adaptation, no full logits buffer',
   'A2_INDEXED_UNION':'Kestrel-style preallocated gather W[U], shared torch linear, per-request validity and ID remap',
   'A3_RAGGED_DIRECT':'Triton direct index loads original W, per-request legal rows, fixed grouping identical masks'},
 'candidate_config':{
   'A1_BLOCK_M':16,'A1_BLOCK_N':128,'A1_BLOCK_K':32,
   'A3_BLOCK_ROWS':32,'A3_BLOCK_D':1024,
   'A2_union_ids_sorted':True,'A3_identical_mask_grouping':True,
   'singleton_no_head_shortcut_all_eligible_arms':True},
 'max_discovery_configurations':8,'formal_warmups':2,'formal_repetitions':7,
 'primary_complete_head_interval':'hidden+current grammar availability through selected token ID',
 'primary_full_generation_interval':'start of fixed B4 generation to all request stop/truncation',
 'head_and_generation_timing_separate':True,
 'compile_cost_reported_separately':True,
 'numerical_contract':'all legal row dependencies intact; exact chosen token and full generated IDs against qualified dense reference; no nonselected top2 gate',
 'empty_support':'correctness/termination, never timed winner',
 'holdout_trigger':'reproducible full-region effect or informative regression not explained by known capabilities',
 'no_parameter_sweep':True}
(ROOT/'PREREGISTRATION.json').write_text(json.dumps(prereg,indent=2,sort_keys=True)+'\n')
print(json.dumps({'requests':len(requests),'unique_schemas':len(unique),
  'model_vocab':cfg.vocab_size,'tokenizer_len':len(tok),'input_binding_sha256':sha_file(ROOT/'INPUT_RUNTIME_BINDINGS.json'),
  'preregistration_sha256':sha_file(ROOT/'PREREGISTRATION.json'),
  'compile_ms_total':sum(r['compiler_ms'] for r in compile_rows)},sort_keys=True))
