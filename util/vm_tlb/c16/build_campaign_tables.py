#!/usr/bin/env python3
"""Deterministic CPU-only generator for C16 measurement-campaign design TSVs."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


QWEN='https://huggingface.co/Qwen/Qwen2.5-3B-Instruct'
QWEN_AWQ='https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-AWQ'
OLMOE='https://huggingface.co/allenai/OLMoE-1B-7B-0125-Instruct'
GRANITE='https://huggingface.co/ibm-granite/granite-3.1-1b-a400m-instruct'
VLLM='https://docs.vllm.ai/en/latest/models/supported_models/'
WIKITEXT='https://huggingface.co/datasets/Salesforce/wikitext'
PG19='https://github.com/google-deepmind/pg19'
NSYS='https://docs.nvidia.com/nsight-systems/UserGuide/'
NCU='https://docs.nvidia.com/nsight-compute/ProfilingGuide/'
CUDA='https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__EVENT.html'


def write(path: Path, fields: list[str], rows: list[dict]) -> None:
    if not rows:
        raise AssertionError(f'empty {path.name}')
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n',extrasaction='raise')
        w.writeheader()
        for row in rows:
            if set(row)!=set(fields):
                raise AssertionError((path.name,set(fields)-set(row),set(row)-set(fields)))
            w.writerow(row)


def rows(fields: str, values: list[tuple]) -> tuple[list[str],list[dict]]:
    names=fields.split('|')
    out=[]
    for value in values:
        if len(value)!=len(names):
            raise AssertionError((fields,len(names),len(value),value))
        out.append(dict(zip(names,value)))
    return names,out


def build(out: Path) -> None:
    out.mkdir(parents=True,exist_ok=True)
    f,r=rows('axis_group|axis_id|levels_or_requirement|selected_coverage|reason_or_boundary',[
        ('WORKLOAD','MODEL_STRUCTURE','dense;MoE','dense Qwen;MoE OLMoE and Granite','Two structures without a Cartesian sweep'),
        ('WORKLOAD','REPRESENTATION','BF16/FP16;W4/AWQ;FP8 conditional','BF16;official W4/AWQ','FP8 not selected until SM89 runtime and numerical semantics are qualified'),
        ('WORKLOAD','PHASE','prefill;decode','both','One dense prefill control plus decode-focused discovery'),
        ('WORKLOAD','BATCH_EFFECTIVE_M','batch1;small;medium','B1;B4;B16 with effective M measured','Transition is a supply-control ladder; no unverified backend threshold claim'),
        ('WORKLOAD','CONTEXT','short;long','512 and 16384 token proposals','Long stress is a pre-registered holdout; exact capacity must qualify'),
        ('WORKLOAD','OPERATOR_FAMILY','projection;attention;routing/expert;norm/elementwise;KV','whole-run inventory then selected critical windows','No local kernel can bypass whole-run time weighting'),
        ('WORKLOAD','RUNTIME_BACKEND','mature fused;quantized;fused MoE','pinned vLLM-class native backend to qualify','Eager/reference fallback is not the sole strong baseline'),
        ('WORKLOAD','PLATFORM','109 RTX4080 SM89 first','109 only proposed','No Hopper/Blackwell gain transplanted to Ada'),
        ('OBSERVABLE','CRITICAL_PATH','legal wall union;launch/sync gaps;operator/phase weights','Tier0 NSYS/NVTX plus native timing','Summed kernel durations are not wall union'),
        ('OBSERVABLE','COMPUTE','CTA/waves;active warps;tile fill;stalls','Tier0 launch geometry;Tier1 selected utilization','CTA count is not saturation'),
        ('OBSERVABLE','MEMORY','requested/useful;L1/TEX;L2;DRAM;stalls','Tier1 targeted NCU after weight gate','Traffic does not imply time or duplicate fill'),
        ('OBSERVABLE','TRANSLATION','page set;TLB;PTW;blocked time','TO_BE_QUALIFIED;no proxy promotion','VA page proxy cannot replace TLB timing'),
        ('OBSERVABLE','CHRONOLOGY','same-process order;producer-consumer;reuse','Tier0 kernel/NVTX timeline;Tier2 only after oracle gate','Independent static-shard replay cannot supply natural chronology'),
        ('OBSERVABLE','MOE_SPECIFIC','routing;expert sequence;turnover;shared/routed','Tier0 natural routing IDs;Tier2 address sequence conditional','No generic expert-locality mechanism from routing alone'),
    ])
    write(out/'PROBLEM_COVERAGE_TAXONOMY.tsv',f,r)

    f,r=rows('point_id|structure|representation|phase|batch|context_tokens|operator_coverage|candidate_model|backend_gate|platform|question_ids|scientific_role|whole_run_parent',[
        ('MP01','dense','BF16','prefill','1','512','attention;projection;FFN;norm','Qwen/Qwen2.5-3B-Instruct','SB01_TO_BE_QUALIFIED','109_SM89','DQ1;DQ3;DQ4','discovery','natural_request_prefill'),
        ('MP02','dense','BF16','decode','1','512','projection;attention;KV;FFN','Qwen/Qwen2.5-3B-Instruct','SB01_TO_BE_QUALIFIED','109_SM89','DQ1;DQ2;DQ3;DQ4','discovery','natural_request_decode_D0_D31'),
        ('MP03','dense','BF16','decode','4','512','projection;attention;KV;FFN','Qwen/Qwen2.5-3B-Instruct','SB01_TO_BE_QUALIFIED','109_SM89','DQ2;DQ3','transition','natural_request_decode_D0_D31'),
        ('MP04','dense','BF16','decode','16','512','projection;attention;KV;FFN','Qwen/Qwen2.5-3B-Instruct','SB01_TO_BE_QUALIFIED','109_SM89','DQ2','holdout','natural_request_decode_D0_D31'),
        ('MP05','dense','W4_AWQ','decode','1','512','quantized projection;attention;KV','Qwen/Qwen2.5-3B-Instruct-AWQ','SB02_TO_BE_QUALIFIED','109_SM89','DQ2;DQ3','control','natural_request_decode_D0_D31'),
        ('MP06','MoE','BF16','decode','1','512','router;routed/shared expert;attention;KV','allenai/OLMoE-1B-7B-0125-Instruct','SB03_TO_BE_QUALIFIED','109_SM89','DQ1;DQ2;DQ4','discovery','natural_request_decode_D0_D31'),
        ('MP07','MoE','BF16','decode','1','512','router;expert;attention;KV','ibm-granite/granite-3.1-1b-a400m-instruct','SB04_TO_BE_QUALIFIED','109_SM89','DQ4','holdout','natural_request_decode_D0_D31'),
        ('MP08','dense','BF16','decode','1','16384','attention;KV;projection;FFN','Qwen/Qwen2.5-3B-Instruct','SB01_TO_BE_QUALIFIED','109_SM89','DQ3;DQ4;SQ_TRANSLATION_AUTHORITY_ONLY','holdout','natural_request_decode_D0_D31'),
    ])
    for coverage_row in r:
        if coverage_row['point_id']=='MP07':
            coverage_row['question_ids']='DQ1;DQ2;DQ4'
        if coverage_row['point_id']=='MP08':
            coverage_row['question_ids']='DQ1;DQ3;DQ4;SQ_TRANSLATION_AUTHORITY_ONLY'
    write(out/'WORKLOAD_COVERAGE_MATRIX.tsv',f,r)

    point_fields='point_id|scientific_role|model_class|candidate_model|model_revision|structure|precision|runtime_backend|phase|batch_effective_M|context_tokens|natural_input_source|operator_scope|why_this_point_exists|question_ids|tier0_observables|tier1_if_admitted|tier2_if_admitted|strong_baseline_id|oracle_id|stop_rule_id|estimated_gpu_active_min|asset_status|local_scope|whole_run_parent|correctness_gate'.split('|')
    common_t0='model/backend/kernel identity;token and shape correctness;NVTX/NSYS wall union;native CUDA-event duration;launch gaps'
    common_t1='selected NCU launch/active-warps/stall and L1-L2-DRAM service groups only after point gate;separate profile duration'
    common_t2='question-specific object-bound warp/address chronology only after project review'
    points=[
        dict(point_id='MP01',scientific_role='discovery',model_class='modern_dense',candidate_model='Qwen/Qwen2.5-3B-Instruct',model_revision='TO_BE_QUALIFIED',structure='dense',precision='BF16',runtime_backend='SB01_PIN_REQUIRED',phase='prefill',batch_effective_M='B1;M=512 token tile-dependent',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_A_PIN_AND_SHA_REQUIRED',operator_scope='prefill attention+projection+FFN',why_this_point_exists='anchors phase and whole-run timing before local diagnosis',question_ids='DQ1;DQ3;DQ4',tier0_observables=common_t0,tier1_if_admitted=common_t1,tier2_if_admitted=common_t2,strong_baseline_id='SB01',oracle_id='OQ1;OQ3;OQ4',stop_rule_id='ST_DQ1;ST_DQ3;ST_DQ4',estimated_gpu_active_min='2',asset_status='NEW_ASSET_REQUIRED',local_scope='prefill attention/projection/FFN critical windows',whole_run_parent='natural_request_prefill',correctness_gate='exact prompt and tokens;shape/order;BF16 tolerance pinned'),
        dict(point_id='MP02',scientific_role='discovery',model_class='modern_dense',candidate_model='Qwen/Qwen2.5-3B-Instruct',model_revision='TO_BE_QUALIFIED',structure='dense',precision='BF16',runtime_backend='SB01_PIN_REQUIRED',phase='decode',batch_effective_M='B1;projection_M=1',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_A_PIN_AND_SHA_REQUIRED',operator_scope='decode projection+attention+KV+FFN',why_this_point_exists='small-M natural decode anchor and critical-path parent',question_ids='DQ1;DQ2;DQ3;DQ4',tier0_observables=common_t0,tier1_if_admitted=common_t1,tier2_if_admitted=common_t2,strong_baseline_id='SB01',oracle_id='OQ1;OQ2;OQ3;OQ4',stop_rule_id='ST_DQ1;ST_DQ2;ST_DQ3;ST_DQ4',estimated_gpu_active_min='2',asset_status='NEW_ASSET_REQUIRED',local_scope='decode projection/attention/FFN critical windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='exact prompt and D0-D31 tokens;shape/order;BF16 tolerance pinned'),
        dict(point_id='MP03',scientific_role='transition',model_class='modern_dense',candidate_model='Qwen/Qwen2.5-3B-Instruct',model_revision='TO_BE_QUALIFIED',structure='dense',precision='BF16',runtime_backend='SB01_PIN_REQUIRED',phase='decode',batch_effective_M='B4;effective_M_measured',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_A_PIN_AND_SHA_REQUIRED',operator_scope='decode projection+attention+KV',why_this_point_exists='predefined middle batch point;not a claimed backend threshold',question_ids='DQ2;DQ3',tier0_observables=common_t0,tier1_if_admitted=common_t1,tier2_if_admitted='warp geometry only if material unexplained transition and review',strong_baseline_id='SB01',oracle_id='OQ2;OQ3',stop_rule_id='ST_DQ2;ST_DQ3',estimated_gpu_active_min='2',asset_status='NEW_ASSET_REQUIRED',local_scope='decode projection/attention windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='batch-specific D0-D31 tokens and row mapping exact;shape/order pinned'),
        dict(point_id='MP04',scientific_role='holdout',model_class='modern_dense',candidate_model='Qwen/Qwen2.5-3B-Instruct',model_revision='TO_BE_QUALIFIED',structure='dense',precision='BF16',runtime_backend='SB01_PIN_REQUIRED',phase='decode',batch_effective_M='B16;effective_M_measured',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_B_SEALED_PIN_AND_SHA_REQUIRED',operator_scope='decode projection+attention+KV',why_this_point_exists='batch/shape holdout not used to select low-M threshold',question_ids='DQ2',tier0_observables=common_t0,tier1_if_admitted='only frozen DQ2 metric subset after discovery gate',tier2_if_admitted='no default Tier2;separate review',strong_baseline_id='SB01',oracle_id='OQ2',stop_rule_id='ST_DQ2',estimated_gpu_active_min='2',asset_status='NEW_ASSET_REQUIRED',local_scope='decode projection/attention windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='sealed prompt IDs and batch-specific D0-D31 tokens;shape/order pinned'),
        dict(point_id='MP05',scientific_role='control',model_class='modern_dense_lowbit',candidate_model='Qwen/Qwen2.5-3B-Instruct-AWQ',model_revision='TO_BE_QUALIFIED',structure='dense',precision='W4_AWQ',runtime_backend='SB02_PIN_AND_SEMANTIC_GATE_REQUIRED',phase='decode',batch_effective_M='B1;projection_M=1',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_A_PIN_AND_SHA_REQUIRED',operator_scope='quantized projection+attention+KV',why_this_point_exists='same family representation control;cross-representation not single-variable A/B',question_ids='DQ2;DQ3',tier0_observables=common_t0+';quantization schema',tier1_if_admitted=common_t1+';quantized kernel identity',tier2_if_admitted='no dequant-cache trace;only question-approved object-bound trace',strong_baseline_id='SB02',oracle_id='OQ2;OQ3',stop_rule_id='ST_DQ2;ST_DQ3',estimated_gpu_active_min='3',asset_status='NEW_ASSET_REQUIRED',local_scope='quantized projection/attention windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='AWQ qweight/qzeros/scales/group semantics;pre-frozen numerical tolerance;token and shape/order gate'),
        dict(point_id='MP06',scientific_role='discovery',model_class='moe_family_A',candidate_model='allenai/OLMoE-1B-7B-0125-Instruct',model_revision='TO_BE_QUALIFIED',structure='MoE',precision='BF16',runtime_backend='SB03_PIN_AND_FUSED_GATE_REQUIRED',phase='decode',batch_effective_M='B1;per_expert_M_measured',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_A_PIN_AND_SHA_REQUIRED',operator_scope='natural routing+expert+attention+KV',why_this_point_exists='same-process MoE chronology and operator-weight discovery;not old selected shard',question_ids='DQ1;DQ2;DQ4',tier0_observables=common_t0+';natural per-token expert IDs and order',tier1_if_admitted=common_t1+';only selected expert kernel',tier2_if_admitted='object-bound expert/page chronology only if oracle and review pass',strong_baseline_id='SB03',oracle_id='OQ1;OQ2;OQ4',stop_rule_id='ST_DQ1;ST_DQ2;ST_DQ4',estimated_gpu_active_min='3',asset_status='ASSET_AVAILABLE_ACCEPTED_PRIOR_ARTIFACT_ONLY',local_scope='router/expert and adjacent producer-consumer windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='exact routing/token sequence;shared versus routed expert;shape/order pinned'),
        dict(point_id='MP07',scientific_role='holdout',model_class='moe_family_B',candidate_model='ibm-granite/granite-3.1-1b-a400m-instruct',model_revision='TO_BE_QUALIFIED',structure='MoE',precision='BF16',runtime_backend='SB04_PIN_AND_FUSED_GATE_REQUIRED',phase='decode',batch_effective_M='B1;per_expert_M_measured',context_tokens='512',natural_input_source='WIKITEXT103_TRAIN_A_PIN_AND_SHA_REQUIRED',operator_scope='natural routing+expert+attention+KV',why_this_point_exists='independent MoE family holdout preselected before OLMoE results',question_ids='DQ4',tier0_observables=common_t0+';natural per-token expert IDs and order',tier1_if_admitted='frozen DQ4 selected metrics only after discovery gate',tier2_if_admitted='no default Tier2;separate review',strong_baseline_id='SB04',oracle_id='OQ4',stop_rule_id='ST_DQ4',estimated_gpu_active_min='3',asset_status='NEW_ASSET_REQUIRED',local_scope='router/expert and adjacent producer-consumer windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='exact routing/token sequence;shape/order;BF16 tolerance pinned'),
        dict(point_id='MP08',scientific_role='holdout',model_class='modern_dense_long_context',candidate_model='Qwen/Qwen2.5-3B-Instruct',model_revision='TO_BE_QUALIFIED',structure='dense',precision='BF16',runtime_backend='SB01_PIN_AND_CONTEXT_GATE_REQUIRED',phase='decode',batch_effective_M='B1;projection_M=1',context_tokens='16384',natural_input_source='PG19_VALIDATION_SEALED_BOOK_PIN_AND_SHA_REQUIRED',operator_scope='attention+KV+projection+FFN',why_this_point_exists='independent long-context stress/holdout;translation only conditional authority question',question_ids='DQ3;DQ4;SQ_TRANSLATION_AUTHORITY_ONLY',tier0_observables=common_t0+';KV growth and context identity',tier1_if_admitted='frozen DQ3 selected memory-service subset;no unverified TLB counter',tier2_if_admitted='translation only if Ada observable proven and separate review',strong_baseline_id='SB01',oracle_id='OQ3;OQ4;TRANSLATION_ORACLE_AUTHORITY_REQUIRED',stop_rule_id='ST_DQ3;ST_DQ4;ST_TRANSLATION',estimated_gpu_active_min='3',asset_status='NEW_ASSET_REQUIRED',local_scope='decode attention/KV and adjacent operator windows',whole_run_parent='natural_request_decode_D0_D31',correctness_gate='sealed PG19 book/excerpt;exact D0-D31 tokens;context and KV shape/order pinned'),
    ]
    for point in points:
        point['asset_status']={'NEW_ASSET_REQUIRED':'ASSET_MISSING',
                               'ASSET_AVAILABLE_ACCEPTED_PRIOR_ARTIFACT_ONLY':'ASSET_AVAILABLE'}[point['asset_status']]
        if point['point_id']=='MP04':
            point['natural_input_source']='WIKITEXT103_TRAIN_A_ANCHOR_PLUS_B_SEALED_PIN_AND_SHA_REQUIRED'
        if point['point_id']=='MP07':
            point['question_ids']='DQ1;DQ2;DQ4'
            point['oracle_id']='OQ1;OQ2;OQ4'
            point['stop_rule_id']='ST_DQ1;ST_DQ2;ST_DQ4'
            point['why_this_point_exists']='preselected independent MoE family for whole-run;small-M;chronology transfer'
            point['tier1_if_admitted']='only frozen DQ1/DQ2/DQ4 metric subset after discovery gate'
        if point['point_id']=='MP08':
            point['question_ids']='DQ1;DQ3;DQ4;SQ_TRANSLATION_AUTHORITY_ONLY'
            point['oracle_id']='OQ1;OQ3;OQ4;TRANSLATION_ORACLE_AUTHORITY_REQUIRED'
            point['stop_rule_id']='ST_DQ1;ST_DQ3;ST_DQ4;ST_TRANSLATION'
            point['why_this_point_exists']='preselected long-context timing/service/chronology holdout;translation remains authority-only'
    write(out/'MEASUREMENT_POINT_PLAN.tsv',point_fields,points)

    f,r=rows('question_id|required_observable|cheapest_legal_tool|tier|admission_gate|caution|source_url',[
        ('DQ1','whole-run request/phase/kernel interval union;launch gaps','NSYS/NVTX plus native CUDA events','Tier0','all identity-qualified points','Do not sum module durations into wall time',NSYS),
        ('DQ2','CTA/grid/waves per SM;effective M;useful tile fill','source audit plus NSYS launch geometry','Tier0','material whole-run operator weight','CTA supply is not occupancy or saturation',NSYS),
        ('DQ2','selected active warps and stall mix for weighted kernel','targeted NCU metric set TO_BE_QUALIFIED','Tier1','at most three preselected points','Profile duration not native wall time; replay may perturb cache',NCU),
        ('DQ3','requested/useful bytes and L1/TEX-L2-DRAM selected service','source layout audit then targeted NCU','Tier1','Tier0 exposes a weighted candidate','Exact metric names and replay mode must be qualified on Ada',NCU),
        ('DQ4','same-process operator/expert order;producer-consumer windows','NSYS/NVTX plus low-overhead router IDs','Tier0','routing IDs must preserve correctness','Chronology not inferable from independent shard replay',NSYS),
        ('DQ4','object-bound VA/page or tile-ready chronology','question-bound trace instrumentation TO_BE_QUALIFIED','Tier2','positive oracle plus project review','No default NVBit or page trace',NSYS),
        ('SQ_TRANSLATION_AUTHORITY_ONLY','TLB/PTW service and translation-caused blocked time','Ada tool capability audit TO_BE_QUALIFIED','pre-Tier1 authority','no proxy substitution','If unavailable retain UNKNOWN and STOP translation claim',NCU),
        ('ALL','source shape/dataflow;kernel/backend identity','pinned source/static audit','Tier0 CPU','all points','Do not infer exact runtime backend from public docs alone',VLLM),
        ('ALL','same-stream kernel timing and event protocol','CUDA event plus NSYS correlation','Tier0','correctness pass','Native timing distinct from NCU profile kernel duration',CUDA),
    ])
    write(out/'OBSERVABLE_TO_TOOL_MAP.tsv',f,r)

    f,r=rows('baseline_id|applies_to|candidate_backend|strong_software_requirement|qualify_before_109|fallback_rule|comparison_boundary|source_url',[
        ('SB01','MP01;MP02;MP03;MP04;MP08','pinned vLLM native Qwen2 path TO_BE_QUALIFIED','fused attention/MLP and mature launch path;CUDA Graph control where legal','pin exact model/runtime/revision on SM89;verify kernel inventory and tokens','drop affected point if only eager/reference or OOM','same-runtime batch/context comparisons;no local mechanism',VLLM),
        ('SB02','MP05','pinned vLLM AWQ/Marlin or equally mature semantic-equivalent backend TO_BE_QUALIFIED','native tuned W4 kernel with accepted qweight/qzeros/scales/group semantics;merged projection where supported','prove exact checkpoint format and numeric correctness on SM89','drop W4 point if only weak AutoAWQ path or semantic mismatch','CROSS_RUNTIME_STRONG_BASELINE if backend differs from BF16;not strict single-variable A/B',QWEN_AWQ),
        ('SB03','MP06','pinned optimized OLMoE fused-MoE path TO_BE_QUALIFIED','no slow per-expert eager fallback;natural routing and shared/routed distinction','pin runtime source/binary;check VRAM and correctness','drop OLMoE point if fused path unavailable','old isolated expert replay is provenance not a whole-run strong baseline',OLMOE),
        ('SB04','MP07','pinned optimized GraniteMoE path TO_BE_QUALIFIED','native fused/grouped expert implementation;no reference-only fallback','pin model/runtime revision;verify kernel inventory and correctness','drop holdout and block MoE generalization if unavailable','distinct model family is pre-frozen holdout not post-hoc control',GRANITE),
    ])
    write(out/'STRONG_SOFTWARE_BASELINES.tsv',f,r)

    f,r=rows('question_id|oracle_id|legal_oracle_or_authority|tier0_minimum|tier1_or_tier2_gate|stop_rule_id|stop_condition|holdout',[
        ('DQ1','OQ1','zero local-operator or launch-gap time using correlated wall intervals;Amdahl-style upper ceiling only','native wall union and parent request window','Tier1 only if weighted contribution material','ST_DQ1','STOP if local wall weight <0.03 or zero-cost whole-run ceiling <0.02 incremental gain;do not sum kernels','MP07 for MoE family;MP08 for context'),
        ('DQ2','OQ2','ORACLE_AUTHORITY_REQUIRED for exact under-supplied time;zero-cost weighted kernel only a pre-gate ceiling','B1/B4 launch geometry;native durations;whole-run f','Tier1 for at most three points if transition persists under SB01/SB02/SB03','ST_DQ2','STOP if matched B4/B16 removes >=0.85 of local gap or B16 holdout lacks predicted direction or correctness fails','MP04 sealed B16;MP07 MoE family'),
        ('DQ3','OQ3','ORACLE_AUTHORITY_REQUIRED for exact service-time removal;zero-cost weighted operator is only pre-gate ceiling','wall-weight and source bytes/layout','selected NCU if f>=0.05 and zero-cost ceiling >=0.02;Tier2 only if service exposure remains material','ST_DQ3','STOP if only traffic changes without native timing exposure or if memory-service denominator cannot be attributed','MP08 sealed long context;MP05 representation control'),
        ('DQ4','OQ4','ORACLE_AUTHORITY_REQUIRED for perfect handoff or expert turnover;need exact critical-path window and legal software baseline','same-process NVTX kernel/routing chronology and parent wall union','Tier2 only after explicit handoff/turnover oracle and project review','ST_DQ4','STOP if handoff/turnover is not on critical path or fused/grouped baseline removes >=0.85 gap or holdout fails','MP07 sealed Granite family;MP08 sealed context'),
        ('SQ_TRANSLATION_AUTHORITY_ONLY','OTLB','ORACLE_AUTHORITY_REQUIRED: direct translation service/blocked-time observable on Ada','page footprint and same-process sequence only;never equate VA proxy with TLB time','no Tier1/Tier2 translation until tool capability and zero-time fraction are proven','ST_TRANSLATION','STOP and preserve TRANSLATION_TIME_HEADROOM_UNKNOWN if TLB/PTW/blocked-time attribution unavailable','MP08 reserved context only;no promotion without independent validation'),
    ])
    write(out/'ORACLE_AND_STOP_RULES.tsv',f,r)

    f,r=rows('closed_direction|historical_status|overlap_question|OVERLAPS_CLOSED_DIRECTION|forbidden_reopening|exception_gate',[
        ('selective_residency_M1F','CLOSED','DQ3','PARTIAL','do not rename memory traffic as a residency mechanism','new platform/capacity identity plus measured whole-run headroom'),
        ('cache_aware_splitK','CLOSED_BY_GROUPED_CTA','DQ2','PARTIAL','no split/GROUP_M sweep to seek a positive','new residual after verified grouped strong baseline only'),
        ('dequant_result_cache','CLOSED_BY_STRICT_IDENTITY_HEADROOM','DQ2;DQ3','PARTIAL','no new conversion cache from W4 counters','new strict conversion identity and material legal oracle'),
        ('FFN_materialization','CLOSED_AS_MAIN_OPPORTUNITY','DQ4','PARTIAL','no idealized hidden-state removal claim','new natural critical-path handoff and strong fused baseline'),
        ('plain_gate_up_concurrency','CLOSED_NEGATIVE_NATIVE','DQ4','PARTIAL','no naive two-stream overlap mechanism','new identity with positive heldout whole-run residual only'),
        ('plain_merged_gate_up_novelty','CLOSED_STRONG_SOFTWARE','DQ4','PARTIAL','do not claim plain merge as novelty','compare against semantic-matched merged software baseline'),
        ('generic_Ada_W4_flat_GEMM','CLOSED_MULTIVIEW','DQ2;DQ3','PARTIAL','no generic occupancy/W4 kernel story from one counter','new identity and decomposed cause with whole-run weight'),
        ('replacement_policy_predictor','CLOSED_PASCAL_GATE','DQ3','PARTIAL','no cache-policy proposal from miss or traffic ratios','service-specific residual after strong software and timing oracle'),
        ('DeepSeek_exact_reread','SOFTWARE_KERNEL_SHAPE_OBSERVATION_ONLY','NONE_EXCLUDED','YES','do not promote 50% logical reread into L2/DRAM/time claim','archive only;not a measurement target'),
        ('generic_translation_TLB_current_C16','NO_CURRENT_PROBLEM_QUALIFIED','SQ_TRANSLATION_AUTHORITY_ONLY','YES','no page-proxy timing inference or 109 translation capture','new same-process timing authority and separate approval'),
        ('generic_MoE_expert_locality','NOT_QUALIFIED_WITHOUT_MATCHED_RESIDUAL','DQ4','PARTIAL','routing or page-set change alone is not a cache mechanism','critical-path turnover plus fused/grouped baseline and heldout residual'),
    ])
    write(out/'CLOSED_DIRECTION_GUARD.tsv',f,r)

    f,r=rows('requirement_id|candidate_or_source|asset_status|runtime_status|before_any_native_execution|failure_action|source_url',[
        ('MODEL_DENSE_BF16','Qwen/Qwen2.5-3B-Instruct','ASSET_MISSING','TO_BE_QUALIFIED','NEW_ASSET_REQUIRED;pin exact model revision/tokenizer/license;dry source/runtime/VRAM and backend audit','drop MP01-MP04/MP08 if unavailable',QWEN),
        ('MODEL_DENSE_W4','Qwen/Qwen2.5-3B-Instruct-AWQ','ASSET_MISSING','TO_BE_QUALIFIED','NEW_ASSET_REQUIRED;verify same family checkpoint AWQ schema and tuned SM89 backend correctness','drop MP05 if semantics/backend fail',QWEN_AWQ),
        ('MODEL_MOE_A','allenai/OLMoE-1B-7B-0125-Instruct','ASSET_AVAILABLE','TO_BE_QUALIFIED','accepted prior asset/artifact only;pin whole-run strong fused backend and VRAM;old isolated replay insufficient','drop MP06 if unavailable',OLMOE),
        ('MODEL_MOE_B','ibm-granite/granite-3.1-1b-a400m-instruct','ASSET_MISSING','TO_BE_QUALIFIED','NEW_ASSET_REQUIRED;pin GraniteMoE runtime and strong expert kernel on SM89','drop MP07 and MoE generalization if unavailable',GRANITE),
        ('INPUT_SHORT','WikiText-103 raw natural prose','ASSET_MISSING','not_applicable','NEW_INPUT_FREEZE_REQUIRED;pin dataset revision;disjoint train A/B IDs;tokenize per model;record UTF8 SHA','do not choose prompts after observing output',WIKITEXT),
        ('INPUT_LONG','PG-19 validation natural long book','ASSET_MISSING','not_applicable','NEW_INPUT_FREEZE_REQUIRED;pin book ID/excerpt/license/UTF8 SHA before data;confirm 16K token feasibility','drop MP08 if context invalid',PG19),
        ('RUNTIME','vLLM native kernels on 109 SM89','RUNTIME_UNQUALIFIED','TO_BE_QUALIFIED','pin source/build/CUDA versions;kernel inventory;no fallback reference','do not execute affected point',VLLM),
        ('FP8','conditional representation not selected','MODEL_NOT_SELECTED','RUNTIME_UNQUALIFIED','prove SM89/runtime numerics and real strong path in later design revision','do not add FP8 point by default',VLLM),
        ('TRANSLATION_TOOL','direct Ada TLB/PTW/blocked-time metric path','MODEL_NOT_SELECTED','TO_BE_QUALIFIED','audit exact observable availability and validity;VA proxy insufficient','keep UNKNOWN and no translation promotion',NCU),
    ])
    write(out/'ASSET_AND_RUNTIME_REQUIREMENTS.tsv',f,r)


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,default=Path('docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_MEASUREMENT_CAMPAIGN_DESIGN_174NEW_V1'))
    args=p.parse_args()
    build(args.out)
    print('generated 8 campaign TSVs deterministically')


if __name__=='__main__':
    main()
