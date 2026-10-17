"""r19 positive config admission; existing runner/V2/registry remain authoritative."""
import hashlib
import json
from pathlib import Path
import shlex

from registry import canonical

EXPERIMENT = 'EPL2_DOWNSTREAM_HEADROOM_R19'
COORDINATION = '28e8fce027046643b909c58469e9c7697522a3df'
BINARY = '23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee'
H0 = {'B16_BANKED':'29995661b72e911af344e99759bfe1fef5b899abfa245fcb73cb6accbbcd256f',
      'U_WB16':'5d4dd9034439ece4d170a762ebd1b47972dac2f364e32d845df4e638c1496b3c'}
Q4 = {'-gpgpu_dram_partition_queues':'64:512:256:64',
      '-gpgpu_frfcfs_dram_sched_queue_size':'512', '-gpgpu_dram_return_queue_size':'768'}
OVERRIDES = {'Q4':Q4, 'D4':{**Q4,'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:3400.0'},
             'D2':{**Q4,'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:1700.0'},
             'D8':{**Q4,'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:6800.0'},
             'L25':{**Q4,'-gpgpu_clock_domains':'1132.0:1132.0:1132.0:3400.0','-dram_latency':'25'}}
# LOWER_CEILING deliberately absent: separate path qualification required.


def require(ok, reason):
    if not ok: raise ValueError(reason)


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def options(paths):
    """Native one-value option syntax, quoted multiline timing values preserved."""
    out={}
    for path in paths:
        tokens=shlex.split(Path(path).read_text(),comments=True)
        require(len(tokens)%2==0,'Unsupported non-pair config syntax')
        for key,value in zip(tokens[::2],tokens[1::2]):
            require(key.startswith('-') and key!='-config','Nested/non-option config token')
            out[key]=value
    return out


def validate(spec,release,configs,assets):
    binding=release.get('downstream_config_qualification')
    if binding is None:
        if spec['identity']['binary_sha256']==BINARY:
            require(not spec.get('experiment_id') and not spec.get('regime'), 'Diagnostic requires independently qualified condition envelope')
            require(spec['identity']['runtime_config_sha256']==H0.get(spec.get('mode')), 'Unknown runtime config outside H0 whitelist')
        return None
    require(digest(binding['path'])==binding['sha256'],'Condition qualification changed')
    m=json.loads(Path(binding['path']).read_text())
    require(m['status']=='INDEPENDENT_CONFIG_PASS' and m['coordination_commit']==COORDINATION,'Unqualified r19 condition')
    require(spec.get('experiment_id')==m['experiment_id']==EXPERIMENT,'Wrong experiment grouping')
    regime=spec.get('regime');require(regime==m['regime'] and regime in OVERRIDES,'Unknown/mismatched condition')
    for name in ('core_source_commit','framework_source_commit','binary_sha256'):
        require(m['identity'][name]==spec['identity'][name],'Condition source/binary mismatch')
    require(spec['identity']['binary_sha256']==BINARY,'New runtime requires new independent science')
    require(len(configs)>5 and [r['name'] for r in configs]==['config-'+str(i)+'.config' for i in range(len(configs))],'Config order/name changed')
    row=m['modes'][spec['mode']]
    require(row['ordered_configs']==configs and row['auxiliary_assets']==assets and row['environment']==spec.get('environment',{}),'Condition assets/environment differ')
    require(row['runtime_config_sha256']==spec['identity']['runtime_config_sha256'],'Condition runtime hash differs')
    base={'ordered_configs':configs[:5],'auxiliary_assets':assets,'environment':spec.get('environment',{})}
    require(hashlib.sha256(canonical(base)).hexdigest()==H0[spec['mode']],'Frozen H0 base altered')
    baseopts=options([r['path'] for r in spec['configs'][:5]])
    extra=options([r['path'] for r in spec['configs'][5:]])
    require(extra==OVERRIDES[regime],'Overlay changes forbidden/missing field')
    effective=options([r['path'] for r in spec['configs']])
    require(effective=={**baseopts,**OVERRIDES[regime]}==row['effective_options'],'Effective config not the exact qualified overlay')
    require(effective.get('-dram_latency','100')==('25' if regime=='L25' else '100'),'Fixed interface latency changed')
    require(effective.get('-gpgpu_simple_dram_model','0')=='0','Unqualified simple DRAM path')
    for evidence in m['evidence']:
        require(digest(evidence['path'])==evidence['sha256'],'Affected production/independent evidence changed')
    require(m['evidence'],'Missing affected production evidence')
    return {'experiment_id':EXPERIMENT,'regime':regime,'condition_qualification_sha256':binding['sha256'],
            'runtime_config_sha256':row['runtime_config_sha256'],'effective_options_sha256':hashlib.sha256(canonical(effective)).hexdigest()}
