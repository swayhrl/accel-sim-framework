#!/usr/bin/python3
"""Only new Lane6/V2 bridge tests; not reruns of Lane5's 62 or Lane6 r3's 30 tests."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import current_pair_intake as bridge

REPO=Path(__file__).resolve().parents[4]


def packet(n=1):
    q={'status':'INDEPENDENTLY_QUALIFIED','core_source_commit':'1'*40,'framework_source_commit':'2'*40,'binary_sha256':'3'*64,
       'gates':{k:{'status':'PASS','production_driven':True} for k in ['bank_service','finite_wbuf','mode_legality','old_all_off_equivalence','requester_exact_once','resource_closure','sector_reference_data','stale_fill','wb_lifecycle','physical_bank_clock','memcpy_payload_identity']}}
    api=bridge.vendor_api();runs=[]
    for w in ['convolutionSeparable','FWT_7_21','cfd_097k','vectorAdd_4M','sad'][:n]:
        for mode in ['B16_BANKED','U_WB16']:
            ident={k:q[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']}
            ident.update(workload=w,runtime_config_sha256=('4' if mode=='B16_BANKED' else '5')*64,trace_content_sha256='6'*64,
                epoch_range={'scope':'full_application','epochs':'all'},termination_contract={'normal_exit':True,'hardware_drained':True},
                feature_vector={'finite_wbuf':True,'unified_wb':mode=='U_WB16','ro':False,'tvd':False,'adaptive_policy':False,'wbuf_entries':16,'payload_capacity_per_slice':1168,'bank_count':4,'ops_per_bank_cycle':1},
                ideal_vector={'wb':False,'meta':False,'read_hit':False})
            runs.append({'identity':ident,'run_key':api.run_key(ident),'workload':w,'mode':mode,'status':'COMPLETE_VALID','raw_log_sha256':'7'*64,'summary':{'cycles':100 if mode=='B16_BANKED' else 125,'instructions':1000},'effective_base_config_sha256':'8'*64,
                'validation':{k:True for k in ['normal_exit','parser_success','sector_version_reference','requester_exact_once','payload_identity','terminal_clean','wb_milestone_closure']},'numeric_payload_validation':'UNAVAILABLE_SASS_DATALESS'})
    q['qualified_feature_vectors']=[r['identity']['feature_vector'] for r in runs[:2]]
    return {'evidence_kind':'FUNCTIONAL_IMPLEMENTATION','qualification':q,'runs':runs}


def state(p,mutate=None,proof_changed=False):
    api=bridge.vendor_api();proof=b'{"synthetic_only":true}'
    rows=[]
    for r in p['runs']:
        rows.append({**{k:r['identity'][k] for k in ['core_source_commit','framework_source_commit','binary_sha256','runtime_config_sha256','trace_content_sha256','workload']},
            'identity':r['identity'],'run_key':r['run_key'],'raw_log_sha256':r['raw_log_sha256'],'observed_cycles':r['summary']['cycles'],'instructions':r['summary']['instructions'],
            'mode':r['mode'],'original_terminal_status':r['status'],'scientific_acceptance':'CURRENT_ACCEPTED'})
    manifest={'schema_version':api.SCHEMA,'generation':3,'revision':'SYNTHETIC_V2_BRIDGE_ONLY','authority':{'lane_id':5,'framework_branch':api.BRANCH},
        'rows':rows,'withdrawn_releases':[],'launch_authorizations':[],'supersession_evidence':[{'path':'docs/ep_l2/review_packs/SYNTHETIC_ONLY/proof.json','sha256':hashlib.sha256(proof).hexdigest()}]}
    if mutate:mutate(manifest)
    raw=json.dumps(manifest,sort_keys=True).encode();binding={'kind':'FETCHED_GITHUB_BRANCH','publication_commit':'a'*40,'manifest_sha256':hashlib.sha256(raw).hexdigest(),'generation':3,'revision':manifest['revision']}
    return api.bind_manifest(raw,binding,lambda path:b'tampered' if proof_changed else proof)


class V2BridgeChecks(unittest.TestCase):
    def context(self,s):
        with patch.object(bridge,'live_head',return_value='a'*40):return bridge.bridge(REPO,s)
    def summarize(self,p,s):
        c=self.context(s)
        with patch.object(bridge,'live_head',return_value='a'*40):return bridge.legacy_modules(REPO)[2].summarize(p,c)
    def test_native_current_accepted_v2_row_can_feed_r3_validator(self):
        p=packet();r=self.summarize(p,state(p));self.assertEqual(r['pairs'][0]['speedup'],.8);self.assertIsNone(r['whole_group_geomean'])
    def test_all_five_current_pairs_required_for_geomean(self):
        p=packet(5);r=self.summarize(p,state(p));self.assertTrue(r['complete']);self.assertAlmostEqual(r['whole_group_geomean'],.8)
    def test_future_withdrawn_release_not_in_r3_hardcoded_list_is_denied(self):
        p=packet();s=state(p,lambda m:m['withdrawn_releases'].append({**{k:p['runs'][0]['identity'][k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},'reason':'new independent counterexample'}))
        with self.assertRaisesRegex(ValueError,'qualification withdrawn'):self.summarize(p,s)
    def test_rebinding_newer_revocation_vetoes_prior_accepted_packet(self):
        p=packet();self.summarize(p,state(p));new=state(p,lambda m:m['rows'][0].update(scientific_acceptance='SUSPENDED_NEW_COUNTEREXAMPLE'))
        with self.assertRaisesRegex(ValueError,'suspended'):self.summarize(p,new)
    def test_complete_identity_mutation_is_not_hidden_by_flat_fields(self):
        p=packet();s=state(p);bad=copy.deepcopy(p['runs'][0]);bad['identity']['epoch_range']['epochs']='subset'
        with self.assertRaises(ValueError):self.context(s).check_run(bad)
    def test_unknown_identity_field_is_not_rekeyed(self):
        p=packet();p['runs'][0]['identity']['alias']='bad'
        with self.assertRaisesRegex(ValueError,'extra identity'):state(p)
    def test_proof_tamper_fails_before_any_summary(self):
        with self.assertRaisesRegex(ValueError,'evidence changed'):state(packet(),proof_changed=True)
    def test_state_mutation_after_binding_rejected(self):
        p=packet();s=state(p);s['manifest']['rows'][0]['observed_cycles']=1
        with self.assertRaisesRegex(ValueError,'state mutated'):self.context(s)
    def test_remote_advance_and_unavailable_deny_emission(self):
        c=self.context(state(packet()))
        with patch.object(bridge,'live_head',return_value='b'*40),self.assertRaisesRegex(ValueError,'advanced'):c.assert_fresh()
        with patch.object(bridge.subprocess,'check_output',side_effect=OSError('offline')),self.assertRaisesRegex(ValueError,'no cached fallback'):bridge.fetch_state(REPO)
    def test_launch_authorization_does_not_preaccept_result(self):
        p=packet();s=state(p,lambda m:m.update(rows=[],launch_authorizations=[{'status':'CURRENT_QUALIFIED_FOR_LAUNCH'}]))
        with self.assertRaisesRegex(ValueError,'acceptance row missing'):self.summarize(p,s)
    def test_raw_metrics_mode_mismatch_rejected(self):
        p=packet();s=state(p)
        for field,value in [('raw_log_sha256','9'*64),('summary',{'cycles':101,'instructions':1000}),('mode','U_WB16')]:
            bad=copy.deepcopy(p['runs'][0]);bad[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.context(s).check_run(bad)
    def test_repaired_eleven_gate_requirement_still_enforced(self):
        p=packet();del p['qualification']['gates']['memcpy_payload_identity']
        with self.assertRaisesRegex(ValueError,'Missing repaired'):self.summarize(p,state(p))

if __name__=='__main__':unittest.main(verbosity=2)
