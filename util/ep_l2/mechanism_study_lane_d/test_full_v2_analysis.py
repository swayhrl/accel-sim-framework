"""Synthetic D display integrity tests; never native correctness evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import full_v2_analysis as a
import sync_intake as i

class FullV2(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.source={'core_source_commit':'c','framework_source_commit':'f','vendor_pybind11_commit':'v','binary_sha256':'b'}
        self.ledger={'owner':'E','campaign_id':a.CAMPAIGN,'authority_commit':a.AUTH,'actual_starts':0,
          'qualifications':{},'accepted_results':{},'accepted_pairs':{}}
        self.binding={'owner':'E','authority':a.AUTH,'qualification_id':'q','source_identity':self.source,
          'fixed_policy_sha256':'1'*64,'full_victim_semantics':'CLEAN_DIRTY_PENDING_INFLIGHT',
          'condition_profiles':{r['condition_id']:r['profile'] for r in a.matrix()},'pairs':{}}
        q={'qualified_by':'E','campaign_id':a.CAMPAIGN,'status':'INDEPENDENTLY_QUALIFIED',
           'source_identity':self.source,'supported_profiles':list({r['profile'] for r in a.matrix()})}
        p=self.root/'q.json';p.write_text(json.dumps(q))
        self.ledger['qualifications']['q']={'path':str(p),'sha256':i.digest(p),'qualification':q}
    def pair(self,w,left='S',right='F',cycles=(100,120)):
        cmp=next(r for r in a.comparisons() if r['workload']==w and r['left']==f'V2_{w}_{left}' and r['right']==f'V2_{w}_{right}')
        pid=cmp['comparison_id'];ids=[]
        for n,prof,cycle in [('l',left,cycles[0]),('r',right,cycles[1])]:
            ident=dict(self.source,trace_content_sha256=w,epoch_range={'scope':'full_application','epochs':'all'},
                       workload=w,runtime_config_sha256=prof)
            ident.pop('vendor_pybind11_commit')
            key=w+'_'+prof
            r={'attempt_id':key,'identity':ident,'status':'COMPLETE_VALID','independent_acceptance':'PASS',
               'complete_input_verified':True,'cycles':cycle,'instructions':1000,'profile':prof,
               'source_identity':copy.deepcopy(self.source),'qualification_id':'q'}
            p=self.root/(key+'.json');p.write_text(json.dumps(r))
            self.ledger['accepted_results'][key]={'path':str(p),'sha256':i.digest(p),'identity':ident};ids.append(key)
        self.ledger['accepted_pairs'][pid]={'status':'CURRENT_ACCEPTED','baseline_attempt_id':ids[0],
          'variant_attempt_id':ids[1],'nonresearch_config_equal':True,'comparison_group':w}
        self.binding['pairs'][pid]={'pair_id':pid,'left':cmp['left'],'right':cmp['right']}
        return pid
    def test_matrix_unique32_reuses14_anchors_and40_is_total(self):
        m=a.matrix();self.assertEqual(len(m),32);self.assertEqual(len({r['condition_id'] for r in m}),32)
        self.assertEqual(sum(r['group']=='MAIN' for r in m),14)
        self.assertTrue(all(r['total_payload_slots']==1168 and r['ops_per_bank_physical_cycle']==1 for r in m))
    def test_no_data_is_unknown_no_normalized_fake_baseline(self):
        r=a.views(self.ledger,None)
        self.assertEqual(len(r['coverage']),14);self.assertEqual(r['summary']['seven_input_geomean_S_over_F'],'UNKNOWN')
        self.assertTrue(all(x['cycles']=='UNKNOWN' for x in r['coverage']))
    def test_negative_and_missing_causal_metrics_stay_visible_no_partial_mean(self):
        self.pair('sad');r=a.views(self.ledger,self.binding)
        self.assertAlmostEqual(r['main'][0]['ratio_left_over_right'],100/120)
        self.assertEqual(r['main'][0]['cycles_left_minus_right'],-20)
        self.assertEqual(r['main'][0]['trigger'],'UNKNOWN')
        self.assertEqual(r['summary']['seven_input_geomean_S_over_F'],'UNKNOWN')
        self.assertAlmostEqual(r['summary']['current_accepted_subset_geomean_S_over_F'],100/120)
        self.assertEqual(r['summary']['current_accepted_subset_members'],['sad'])
        self.assertTrue(r['summary']['subset_mean_is_not_complete_seven_mean'])
    def test_full_seven_common_release_geomean(self):
        for w in a.WORKLOADS:self.pair(w,cycles=(100,125))
        self.assertAlmostEqual(a.views(self.ledger,self.binding)['summary']['seven_input_geomean_S_over_F'],.8)
    def test_clean_only_cannot_be_full(self):
        self.pair('sad');self.binding['full_victim_semantics']='CLEAN_ONLY'
        r=a.views(self.ledger,self.binding);self.assertEqual(r['summary']['current_accepted_main_pairs'],0)
    def test_different_final_binary_pair_does_not_enter_main(self):
        self.pair('sad');self.binding['source_identity']=dict(self.source,binary_sha256='different')
        r=a.views(self.ledger,self.binding);self.assertEqual(r['summary']['current_accepted_main_pairs'],0)
    def test_one_other_binary_cannot_complete_seven(self):
        for w in a.WORKLOADS:self.pair(w,cycles=(100,80))
        for name in ['btree_S','btree_F']:
            ref=self.ledger['accepted_results'][name];p=Path(ref['path']);r=json.loads(p.read_text())
            r['source_identity']['binary_sha256']='other';r['identity']['binary_sha256']='other'
            p.write_text(json.dumps(r));ref.update(sha256=i.digest(p),identity=r['identity'])
        r=a.views(self.ledger,self.binding)
        self.assertEqual(r['summary']['current_accepted_main_pairs'],6)
        self.assertEqual(r['summary']['seven_input_geomean_S_over_F'],'UNKNOWN')
    def test_withdrawal_immediately_removes_value(self):
        pid=self.pair('sad');self.assertEqual(a.views(self.ledger,self.binding)['summary']['current_accepted_main_pairs'],1)
        self.ledger['accepted_pairs'][pid]['status']='WITHDRAWN_SCIENTIFIC_HOLD'
        r=a.views(self.ledger,self.binding);self.assertEqual(r['summary']['current_accepted_main_pairs'],0)
        self.assertEqual(r['main'][0]['ratio_left_over_right'],'UNKNOWN')
    def test_current_qualification_hold_refuses_even_stale_current_pair(self):
        self.pair('sad');self.ledger['scientific_holds']={'q':{'status':'ACTIVE'}}
        self.assertEqual(a.views(self.ledger,self.binding)['summary']['current_accepted_main_pairs'],0)
    def test_input_hold_keeps_seven_denominator_and_preserves_DWT(self):
        for w in a.WORKLOADS:self.pair(w,cycles=(100,80))
        r=a.views(self.ledger,self.binding,{'btree':{'status':'HOLD','reason':'NONZERO_MASK_FULL32'}})
        self.assertEqual(r['summary']['current_accepted_main_pairs'],6)
        self.assertEqual(r['summary']['required_main_pairs'],7)
        self.assertEqual(r['summary']['seven_input_geomean_S_over_F'],'UNKNOWN')
        btree=next(v for v in r['main'] if v['workload']=='btree')
        dwt=next(v for v in r['main'] if v['workload']=='dwt2d')
        self.assertEqual(btree['status'],'HOLD_INPUT_SCIENTIFIC_SCOPE')
        self.assertEqual(btree['cycles_left'],'UNKNOWN')
        self.assertEqual(dwt['status'],'E_ACCEPTED_D_ANALYZED')
    def test_reversed_mapping_not_favorable_reciprocal(self):
        pid=self.pair('sad');m=self.binding['pairs'][pid];m['left'],m['right']=m['right'],m['left']
        self.assertEqual(a.views(self.ledger,self.binding)['summary']['current_accepted_main_pairs'],0)
    def test_unqualified_profile_and_missing_config_equality_hold(self):
        pid=self.pair('sad');self.binding['condition_profiles']['V2_sad_F']='CLEAN_ONLY'
        self.assertEqual(a.views(self.ledger,self.binding)['summary']['current_accepted_main_pairs'],0)
        self.binding['condition_profiles']['V2_sad_F']='F';self.ledger['accepted_pairs'][pid].pop('nonresearch_config_equal')
        self.assertEqual(a.views(self.ledger,self.binding)['summary']['current_accepted_main_pairs'],0)

    def direct(self):
        for ref in self.ledger['qualifications'].values():
            q=ref['qualification'];q['full_system_v2']={'authority_commit':a.AUTH,
              'fixed_policy':True,'victim_scope':'CLEAN_DIRTY_PENDING_INFLIGHT'}
            Path(ref['path']).write_text(json.dumps(q));ref['sha256']=i.digest(ref['path'])
        return a.accepted_display_binding(self.ledger,'b')

    def test_direct_E_profiles_support_distinct_endpoint_qualification_revisions(self):
        self.pair('convolutionSeparable')
        ref=copy.deepcopy(self.ledger['qualifications']['q']);p=self.root/'q2.json'
        p.write_text(json.dumps(ref['qualification']));ref.update(path=str(p),sha256=i.digest(p))
        self.ledger['qualifications']['q2']=ref
        ep=self.ledger['accepted_results']['convolutionSeparable_F'];r=json.loads(Path(ep['path']).read_text())
        r['qualification_id']='q2';Path(ep['path']).write_text(json.dumps(r));ep['sha256']=i.digest(ep['path'])
        binding=self.direct();result=a.views(self.ledger,binding)
        self.assertEqual(result['summary']['current_accepted_main_pairs'],1)
        self.assertLess(result['main'][3]['ratio_left_over_right'],1) # unfavorable remains visible
        self.ledger['scientific_holds']={'qualification:q2':{'status':'REVIEW_REQUIRED'}}
        self.assertEqual(a.views(self.ledger,binding)['summary']['current_accepted_main_pairs'],0)

    def test_direct_projection_withdrawal_and_missing_full_scope(self):
        pid=self.pair('sad');binding=self.direct()
        self.assertEqual(a.views(self.ledger,binding)['summary']['current_accepted_main_pairs'],1)
        self.ledger['accepted_pairs'][pid]['status']='WITHDRAWN'
        self.assertIsNone(a.accepted_display_binding(self.ledger,'b'))
        self.assertEqual(a.views(self.ledger,binding)['summary']['current_accepted_main_pairs'],0)
        self.ledger['accepted_pairs'][pid]['status']='CURRENT_ACCEPTED'
        q=self.ledger['qualifications']['q'];q['qualification'].pop('full_system_v2')
        Path(q['path']).write_text(json.dumps(q['qualification']));q['sha256']=i.digest(q['path'])
        self.assertEqual(a.views(self.ledger,binding)['summary']['current_accepted_main_pairs'],0)

    def test_mechanism_peaks_not_summed_and_missing_not_zero(self):
        rows={str(n):{'resource':{'peak_transactions':n+1,'query_count':2}} for n in range(64)}
        metric={'full_mechanism_records':{'readonly':rows}}
        p={'pair_id':'x','workload':'x','baseline_mechanism_metrics':'UNKNOWN',
           'variant_mechanism_metrics':json.dumps(metric)}
        table={r['metric']:r for r in a.mechanism_table(p)}
        self.assertEqual(table['peak_transactions_max_across_slices']['F'],64)
        self.assertEqual(table['peak_transactions_min_across_slices']['F'],1)
        self.assertEqual(table['query_count']['F'],128)
        self.assertEqual(table['query_count']['S'],'UNKNOWN')

    def test_cost_observation_uses_last_snapshot_and_exact_raw_hash(self):
        pid=self.pair('sad');pair=self.ledger['accepted_pairs'][pid]
        row={'pair_id':pid,'workload':'sad'}
        for side,key in [('baseline',pair['baseline_attempt_id']),('variant',pair['variant_attempt_id'])]:
            row[side+'_attempt_id']=key;root=self.root/key;root.mkdir()
            log=root/'raw.log'
            counters=['frontend_cam_queries','completion_cam_queries','indexed_wb_accept','indexed_rollback',
                      'native_install_commits','native_promotion_commits']
            log.write_text(''.join('EPL2TVDV3|METADATA_COST|slice='+str(n)+'|'+
                '|'.join(k+'='+str(value) for k in counters)+'\n' for value in [5,7] for n in range(64)))
            ref=self.ledger['accepted_results'][key];p=Path(ref['path']);r=json.loads(p.read_text())
            r['raw_log_sha256']=i.digest(log);p.write_text(json.dumps(r));ref['sha256']=i.digest(p)
        rows,proof=a.terminal_cost_observations(self.ledger,row,self.root)
        self.assertEqual(rows[0]['F'],64*7)
        self.assertEqual(len(proof['variant']['records']),64)
        (self.root/pair['variant_attempt_id']/'raw.log').write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed accepted raw'):
            a.terminal_cost_observations(self.ledger,row,self.root)

if __name__=='__main__':unittest.main()
