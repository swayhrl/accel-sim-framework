"""Pure configuration transformations. No simulator or model-launch imports.

generate(base_config_texts, 'E384') -> (texts, manifest)
generate(base_config_texts, {'entries':384,'merge':8}) -> (...)
Only the last effective occurrence of each changed option is replaced.
P0 is byte-preserving. Caller owns scientific registration and admission.
"""
import hashlib,json,re

BASE={'entries':192,'merge':4,'miss_queue':32,'frfcfs':64}
PROFILES={'P0':{},'E384':{'entries':384},'E768':{'entries':768},
 'M8':{'merge':8},'M16':{'merge':16},'Q64':{'miss_queue':64},
 'Q128':{'miss_queue':128},'F128':{'frfcfs':128},'F256':{'frfcfs':256}}
L2='-gpgpu_cache:dl2'
FR='-gpgpu_frfcfs_dram_sched_queue_size'
BASE_L2='S:128:128:16,L:B:m:L:L,A:192:4,32:0,32'
FIXED={'-gpgpu_clock_domains':'1410.0:1410.0:1410.0:850.0',
 '-gpgpu_n_mem':'20','-gpgpu_n_sub_partition_per_mchannel':'2',
 '-gpgpu_dram_partition_queues':'64:64:64:64',
 '-gpgpu_dram_return_queue_size':'192','-gpgpu_dram_scheduler':'1'}
PAT=re.compile(r'^(\s*)(-[^\s#]+)([ \t]+)([^#\r\n]*?)([ \t]*)(\r?\n)?$')

def effective_options(texts):
    options={}
    for text in texts:
        for line in text.splitlines():
            body=line.split('#',1)[0].strip()
            if not body: continue
            key,_,value=body.partition(' ')
            if '\t' in key: key,value=body.split(None,1)
            if key.startswith('-'):options[key]=value.strip()
    return options

def _replace_last(texts,key,value):
    hits=[]
    split=[t.splitlines(keepends=True) for t in texts]
    for i,lines in enumerate(split):
        for j,line in enumerate(lines):
            m=PAT.match(line)
            if m and m.group(2)==key:hits.append((i,j,m))
    if not hits:raise ValueError('Missing registered base option '+key)
    i,j,m=hits[-1]
    split[i][j]=m.group(1)+key+m.group(3)+value+m.group(5)+(m.group(6) or '')
    return [''.join(lines) for lines in split]

def normalize(profile):
    if isinstance(profile,str):
        if profile not in PROFILES:raise ValueError('Unknown profile '+profile)
        override=PROFILES[profile]
    elif isinstance(profile,dict):override=profile
    else:raise TypeError('profile must be name or factor dict')
    if set(override)-set(BASE):raise ValueError('Unsupported parameter family')
    p=dict(BASE)
    for key,value in override.items():
        if type(value) is not int or value<BASE[key] or value>2147483647:
            raise ValueError('Invalid finite expansion '+key)
        p[key]=value
    if p['entries']>1073741823:raise ValueError('2*num_entries constructor overflow guard')
    return p

def resource_cost(p):
    """Logical slot capacities, NOT a physical byte/area model or eager RSS."""
    banks=40;controllers=20
    return {'l2_data_bytes':banks*128*128*16,'l2_banks':banks,
     'mshr_address_entries_total':banks*p['entries'],
     'mshr_request_references_upper_bound':banks*p['entries']*p['merge'],
     'miss_queue_request_slots_total':banks*p['miss_queue'],
     'frfcfs_request_slots_total':controllers*p['frfcfs'],
     'shared_credit_limit_per_controller':p['frfcfs']+192-(2-1),
     'private_credits_per_controller':2,
     'credit_coupling':'shared=FRFCFS+DRAMreturn-(subpartitions-1); write split disabled',
     'physical_area_or_bytes':'UNKNOWN: request metadata, pointer/list/map overhead and hardware encoding not modeled'}

def generate(base_config_texts,profile='P0'):
    texts=list(base_config_texts)
    if not texts or any(type(t) is not str for t in texts):raise ValueError('Config text list required')
    before=effective_options(texts)
    if before.get(L2)!=BASE_L2 or before.get(FR)!='64':raise ValueError('Not the accepted P0 L2/FRFCFS base')
    for k,v in FIXED.items():
        if before.get(k)!=v:raise ValueError('Fixed baseline mismatch '+k)
    if before.get('-dram_seperate_write_queue_enable','0')!='0':raise ValueError('Write split must remain disabled')
    p=normalize(profile)
    targets={L2:f"S:128:128:16,L:B:m:L:L,A:{p['entries']}:{p['merge']},{p['miss_queue']}:0,32",FR:str(p['frfcfs'])}
    expected={k:v for k,v in targets.items() if before[k]!=v}
    for key,value in expected.items():texts=_replace_last(texts,key,value)
    after=effective_options(texts)
    actual={k:v for k,v in after.items() if before.get(k)!=v}
    if actual!=expected or set(after)!=set(before):raise AssertionError('Non-target option changed')
    # CH/DH L1, all clock/address-map/timing and every non-target effective option retained.
    manifests={'schema':'DTC_L2_MLP_CONFIG_TRANSFORM_V1','profile':profile,'parameters':p,
     'changed_options':{k:{'before':before[k],'after':v} for k,v in actual.items()},
     'config_sha256_before':[hashlib.sha256(t.encode()).hexdigest() for t in base_config_texts],
     'config_sha256_after':[hashlib.sha256(t.encode()).hexdigest() for t in texts],
     'effective_options':after,'logical_resource_cost':resource_cost(p),
     'baseline_all_non_target_options_equal':True,'model_launches':0}
    return texts,manifests

def stage2_templates():
    # Candidate templates only. Activation requires completed whole-suite single-factor evidence.
    return {'E384_M8':{'entries':384,'merge':8},'E768_M16':{'entries':768,'merge':16},
     'E384_Q64':{'entries':384,'miss_queue':64},'E768_Q128':{'entries':768,'miss_queue':128},
     'E384_F128':{'entries':384,'frfcfs':128},'E768_F256':{'entries':768,'frfcfs':256},
     'M8_Q64':{'merge':8,'miss_queue':64},'M8_F128':{'merge':8,'frfcfs':128},
     'E384_M8_Q64_F128':{'entries':384,'merge':8,'miss_queue':64,'frfcfs':128}}

if __name__=='__main__':
    import argparse,pathlib
    ap=argparse.ArgumentParser();ap.add_argument('--base-dir',required=True);ap.add_argument('--profile',default='P0');ap.add_argument('--output-dir',required=True)
    a=ap.parse_args();base=pathlib.Path(a.base_dir);out=pathlib.Path(a.output_dir);out.mkdir(parents=True,exist_ok=False)
    paths=sorted(base.glob('config-*.config'));t,m=generate([p.read_text() for p in paths],json.loads(a.profile) if a.profile.startswith('{') else a.profile)
    for p,s in zip(paths,t):(out/p.name).write_text(s,encoding='utf-8',newline='')
    (out/'TRANSFORM.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
