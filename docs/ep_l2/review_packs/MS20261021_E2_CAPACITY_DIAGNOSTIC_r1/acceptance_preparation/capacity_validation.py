"""Draft pure validator for NEW capacity diagnostic normalized records.

No simulator, file I/O, registry/controller mutation, legacy validator import,
qualification grant or old-runtime projection. A2 output schema is not yet
released: native parser adaptation and E binding remain required.
"""
AUTHORITY='49343880865edb22a17523790fc32dd55975966c'
LEGACY_MAIN61='61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5'
SOURCE_KEYS=('core_source_commit','framework_source_commit','binary_sha256')
ZERO=('live_descriptors','live_line_mshrs','live_wad','pending_lower_reads',
      'pending_returns','pending_responses','transient_payloads')
SLICE_ZERO=('reserved','read_refs','wb_live','wb_slots','bank_pending',
 'descriptor_used','line_mshr_used','wad_live','pending_lower_reads',
 'pending_returns','pending_responses','resident_pending','bypass_live')
ROLES=('RESIDENT_OR_FILL','BYPASS','WB_STAGED')

def require(ok,message):
    if not ok:raise ValueError(message)

def integer(value):return type(value) is int and value>=0

def capacity_label(records,resources,master):
    """Classify named enlarged vector only; missing coverage remains UNKNOWN."""
    if master==0:return {'label':'FINITE_OFF_BASELINE','near_unbounded':False}
    missing=[];binding=[];ratios=[]
    for sid,row in records.items():
        for name in resources:
            r=row['resources'][name];cap=r['capacity']
            covered=r.get('counter_covered') is True and r.get('full_input_scope') is True
            if not covered or not integer(r.get('highwater')) or not integer(r.get('capacity_refusals')):
                missing.append({'slice':int(sid),'resource':name});continue
            high,refusal=r['highwater'],r['capacity_refusals']
            require(high<=cap,'capacity highwater exceeds actual bound: '+name)
            ratios.append(high/cap)
            if refusal or 2*high>cap:
                binding.append({'slice':int(sid),'resource':name,'capacity':cap,
                                'highwater':high,'capacity_refusals':refusal})
    # Known binding suffices for large-finite even if some other counters unknown.
    label='LARGE_FINITE' if binding else ('UNKNOWN' if missing else 'OPERATIONALLY_NEAR_UNBOUNDED_NAMED_VECTOR')
    return {'label':label,'near_unbounded':not(binding or missing),
      'binding_resources':binding,'unknown_coverage':missing,
      'maximum_measured_highwater_fraction':max(ratios) if ratios else None,
      'scope':'Named enlarged vector only; not infinite simulator or hardware upper bound',
      'criterion':'All named enlarged capacities: capacity_refusals=0 AND measured highwater<=50%; all coverage/full-input scope proven'}

def validate_summary(summary,identity,scope):
    """Validate normalized exact-new-runtime 64-slice terminal + capacity labels.

    scope is a hashed E qualification fragment, not data accepted from raw log:
    schema/authority/source/manifest/full-input/profile exact configurations and
    dimensions. Profiles bind actual native getters and enlarged resource list.
    Durable exit, input SHA, leases, evidence files and spec hashes are separately
    verified by original runner/report, never inferred from this pure summary.
    """
    require(scope.get('schema')=='E2_CAPACITY_VALIDATION_SCOPE_V1','wrong explicit new validation scope')
    require(scope.get('authority_commit')==AUTHORITY,'wrong capacity diagnostic authority')
    require(summary.get('diagnostic_scope')=='CAPACITY_DIAGNOSTIC_V1','not the new diagnostic scope')
    source=scope['source_identity']
    require(all(source.get(k)==identity.get(k) for k in SOURCE_KEYS),'identity differs from new source scope')
    require(source['binary_sha256']!=LEGACY_MAIN61,'old main61 anchor/runtime forbidden')
    profile=summary['profile'];require(profile in scope['profiles'],'unqualified capacity profile')
    p=scope['profiles'][profile];master=p['master'];require(master in (0,1),'invalid master')
    feature=identity['feature_vector'];caps=p['capacities'];config=p['configuration']
    require(all(integer(v) and v>0 for v in caps.values()),'invalid exact finite capacity manifest')
    require(caps['payload_slots_total']==sum(caps[n] for n in ('resident_payload_slots','bypass_payload_slots','wb_payload_slots')),'manifest payload role bounds do not conserve')
    require(config['native_tag_sets']*config['native_tag_ways']==caps['tag_slots'],'manifest native Tag geometry mismatch')
    require(feature['payload_capacity_per_slice']==caps['payload_slots_total'],'identity payload capacity mismatch')
    require(feature['wbuf_entries']==caps['wb_payload_slots'],'identity WB capacity mismatch')
    require(config['ft_mode']==1 and all(config[k]==0 for k in ('W','V','T','M','mq2','rg1','copy_free')),'unsupported traditional-S organization')
    require(config['l2_data_free']==master and config['hardware_P1_throughput_eligible']==1-master,'diagnostic service scope mismatch')
    require(config['bank_count']==4 and config['bank_ops_per_physical_cycle']==1 and config['native_line_bytes']==128 and config['copy_latch_bytes']==128,'unchanged bank/line/copy-latch contract changed')
    require(type(summary['cycles']) is int and summary['cycles']>0,'invalid native cumulative cycles')
    require(summary['instructions']==scope['expected_full_instructions'] and integer(summary['instructions']) and summary['instructions']>0,'incomplete full instructions')
    require(summary['slices']==64 and summary['hardware_drained'] is True,'missing64slice hardware drain')
    require(summary['workload_termination']==identity['termination_contract']==scope['termination_contract'],'termination contract changed')
    require(summary['requester_exact_once_audit'] is True and summary['data_correctness_qualification'] is True,'new source data/exact-once qualification missing')
    for key in ZERO:require(summary[key]==0 and integer(summary[key]),'nonzero/invalid resource '+key)
    require(summary['unique_requesters']==summary['responses'] and integer(summary['responses']),'requester/response mismatch')
    require(summary['wb_created']==summary['wb_lower_accepted']==summary['wb_completed'] and integer(summary['wb_created']),'WB lifecycle incomplete')
    require(set(summary['payload_roles'])==set(ROLES) and all(integer(v) for v in summary['payload_roles'].values()),'invalid payload owner roles')
    require(summary['payload_capacity']==64*caps['payload_slots_total'],'actual global payload capacity mismatch')
    require(integer(summary['payload_free']) and summary['payload_free']+sum(summary['payload_roles'].values())==summary['payload_capacity'],'global payload conservation failure')
    d=summary['capacity_diagnostic']
    require(d['schema']=='E2_CAPACITY_NORMALIZED_TERMINAL_V1','wrong normalized native terminal schema')
    require(d['requested_master']==d['effective_master']==master,'requested/effective master mismatch')
    require(d['capacity_manifest_sha256']==scope['capacity_manifest_sha256'],'wrong frozen common capacity vector')
    require(d['complete_input_scope'] is True,'capacity records do not cover complete input')
    records=d['slices'];require(set(records)=={str(i) for i in range(64)},'missing/unexpected capacity slice')
    totals={'unique_requesters':0,'responses':0,'wb_created':0,'wb_lower_accepted':0,'wb_completed':0,'payload_free':0,**{k:0 for k in ROLES}}
    required_resources=set(caps)
    require(set(p['enlarged_resources'])<=required_resources and (master==0 or bool(p['enlarged_resources'])),'missing named enlarged resource manifest')
    for sid,row in records.items():
        require(row['observed_cycles']==summary['cycles'],'capacity snapshot not final native clock')
        require(row['configuration']==config,'actual slice effective configuration/geometry mismatch')
        r=row['resources'];require(set(r)==required_resources,'resource coverage names differ from frozen vector')
        for name,cap in caps.items():
            v=r[name];require(v['capacity']==cap,'actual per-slice capacity differs: '+name)
            for key in ('highwater','capacity_refusals'):
                require(v.get(key) is None or integer(v[key]),'invalid signed/noninteger capacity counter')
            if integer(v.get('highwater')):require(v['highwater']<=cap,'native highwater exceeds capacity')
            if name in p['drained_resources']:require(v.get('terminal_used')==0 and integer(v['terminal_used']),'native enlarged resource not drained')
        c=row['closure']
        require(all(c[k]==1 for k in ('hardware_drained','requester_exact_once','ownership_consistent','resident_tag_payload_consistent')),'slice native correctness/drain proof failed')
        require(c['payload_double_owner']==0,'payload double owner')
        require(all(c[k]==0 and integer(c[k]) for k in SLICE_ZERO),'slice transient not drained')
        require(c['descriptor_free']==caps['descriptor_entries'],'scaled descriptor free closure mismatch')
        require(c['unique_requesters']==c['responses'],'slice requester exactly once mismatch')
        require(c['wb_created']==c['wb_lower_accepted']==c['wb_completed'],'slice WB lifecycle incomplete')
        roles=c['payload_roles'];require(set(roles)==set(ROLES) and all(integer(v) for v in roles.values()),'slice payload roles invalid')
        require(c['payload_free']+sum(roles.values())==caps['payload_slots_total'],'slice payload roles do not conserve')
        for key in totals:totals[key]+=roles[key] if key in ROLES else c[key]
        service=row['local_service'];require(integer(service['physical_grants']),'invalid physical grants')
        require(all(integer(service[k]) for k in ('logical_copy_reads','logical_copy_writes')),'invalid actual logical copy count')
        exemptions=service['exempt_services']
        require(set(exemptions)=={'response','fill','lower_wb','frontend','copy_read','copy_write'} and all(integer(x) for x in exemptions.values()),'missing actual exempt service counters')
        if master:
            require(service['physical_grants']==0,'masterON consumed physical data-bank grants')
            require(service['logical_copy_reads']==exemptions['copy_read'] and service['logical_copy_writes']==exemptions['copy_write'],'ON copy exempt accounting mismatch')
        else:require(not any(exemptions.values()),'masterOFF still exempts native service')
    for key in totals:
        require(totals[key]==(summary['payload_roles'][key] if key in ROLES else summary[key]),'global/slice aggregate mismatch '+key)
    classification=capacity_label(records,p['enlarged_resources'],master)
    return {'status':'PASS','scope':'Exact newly qualified runtime; full input;64slice closure; cumulative native cycles',
      'diagnostic_partition':'CAPACITY_DIAGNOSTIC','hardware_P1_throughput_eligible':not bool(master),
      'capacity_classification':classification,'does_not_validate':'Durable exit/source file/input/hash/lease closure independently checked by original runner/report; no native data-value qualification inferred from these counters'}
