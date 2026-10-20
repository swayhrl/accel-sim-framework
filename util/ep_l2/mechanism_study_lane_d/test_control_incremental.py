"""Display integrity only. These synthetic records are not simulator evidence."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import full_v2_analysis as a
import sync_intake as i
import control_incremental as c
import test_full_v2_analysis as fixtures


class Controls(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.FullV2();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.ledger=self.fixture.ledger;self.binding=self.fixture.binding;self.root=self.fixture.root
        self.main=self.fixture.pair('convolutionSeparable',cycles=(100,101))
        self.plan={'source_identity':self.fixture.source,'profiles':[]}
    def add(self,profile,cycles=105,anchor='F'):
        w='convolutionSeparable';aid=w+'_'+anchor;cid=w+'_'+profile
        ref=self.ledger['accepted_results'][aid];r=copy.deepcopy(i.pointer(ref))
        r.update(attempt_id=cid,profile=profile,cycles=cycles);r['identity']['runtime_config_sha256']=profile
        p=self.root/(cid+'.json');p.write_text(json.dumps(r))
        cref={'path':str(p),'sha256':i.digest(p),'identity':r['identity']}
        self.ledger['accepted_results'][cid]=cref
        pid='CONTROL_'+profile
        self.ledger['accepted_pairs'][pid]={'status':'CURRENT_ACCEPTED','baseline_attempt_id':aid,
          'variant_attempt_id':cid,'nonresearch_config_equal':True,
          'endpoints':{'left':dict(ref,attempt_id=aid),'right':dict(cref,attempt_id=cid)}}
        e=dict(workload=w,profile=profile,control_pair_id=pid,condition_id='V2_'+w+'_'+profile,
          anchor_attempt_id=aid,anchor_profile=anchor,anchor_receipt_sha256=ref['sha256'],qualification_id='q',
          identity=copy.deepcopy(r['identity']),selection_id='UNKNOWN',comparison_invariants_sha256='UNKNOWN',execution_authority='TEST')
        self.plan['profiles'].append(e);return pid,e
    def result(self):return a.control_views(self.ledger,self.binding,self.plan)
    def test_first_control_is_analyzed_without_waiting_for_all(self):
        self.add('W_ONLY',99,'S');pid,_=self.add('F_MINUS_V');del self.ledger['accepted_pairs'][pid]
        r=self.result();self.assertEqual([x['status'] for x in r['controls']],['E_ACCEPTED_D_ANALYZED','PENDING_E_ACCEPTANCE'])
        self.assertEqual(r['controls'][0]['control_minus_anchor_cycles'],-1)
        self.assertEqual(r['RO_cycle_interaction_C11_minus_C10_minus_C01_plus_C00'],'UNKNOWN')
    def test_main_withdrawal_removes_all_controls_and_derived_values(self):
        self.add('W_ONLY',anchor='S');self.ledger['accepted_pairs'][self.main]['status']='WITHDRAWN'
        r=self.result();self.assertFalse(r['points']);self.assertTrue(all(x['status']=='D_DISPLAY_HOLD' for x in r['controls']))
        self.assertTrue(all(x['cycles_right']=='UNKNOWN' for x in r['contrasts']))
    def test_control_withdrawal_removes_current_contrast(self):
        pid,_=self.add('F_MINUS_V');self.ledger['accepted_pairs'][pid]['status']='WITHDRAWN'
        self.assertEqual(self.result()['controls'][0]['status'],'D_DISPLAY_HOLD')
    def test_different_config_is_not_the_prepared_condition(self):
        _,e=self.add('F_MINUS_V');e['identity']['runtime_config_sha256']='other'
        self.assertEqual(self.result()['controls'][0]['status'],'D_DISPLAY_HOLD')
    def test_wrong_frozen_anchor_is_held(self):
        _,e=self.add('F_MINUS_V');e['anchor_receipt_sha256']='other'
        self.assertEqual(self.result()['controls'][0]['status'],'D_DISPLAY_HOLD')
    def test_control_qualification_not_inherited_from_main(self):
        _,e=self.add('F_MINUS_V');e['qualification_id']='different'
        self.assertEqual(self.result()['controls'][0]['status'],'D_DISPLAY_HOLD')
    def test_current_qualification_hold_removes_controls(self):
        self.add('F_MINUS_V');self.ledger['scientific_holds']={'q':{'status':'ACTIVE'}}
        self.assertFalse(self.result()['points'])
    def test_negative_effect_preserved_and_four_corner_signed_interaction(self):
        for p,v in [('F_MINUS_R',110),('WV_T',108),('WV_M',103)]:self.add(p,v)
        r=self.result();self.assertEqual(r['RO_grid'],dict(F_MINUS_R=110,WV_T=108,WV_M=103,F=101))
        self.assertEqual(r['RO_cycle_interaction_C11_minus_C10_minus_C01_plus_C00'],0)
        self.assertEqual(r['controls'][0]['control_minus_anchor_cycles'],9)
    def test_outside_scope_pair_is_not_projected(self):
        self.add('F_MINUS_V');self.ledger['accepted_pairs']['SAD_W_ONLY']={'status':'CURRENT_ACCEPTED'}
        self.assertEqual(len(self.result()['controls']),1)
    def test_cache_reuses_hash_bound_observation_without_raw_scan(self):
        obs={'path':'/notread/attempt/raw.log','sha256':'raw','frames':[]}
        p=self.root/'OBSERVATIONS_attempt.json';p.write_text(json.dumps(obs))
        (self.root/'FILES_SHA256.json').write_text(json.dumps({p.name:i.digest(p)}))
        with patch.object(c.detail,'observe',side_effect=AssertionError('must not scan accepted anchor again')):
            value,prov=c.cached_observation(dict(attempt_id='attempt',workload='w',profile='S'),{'raw_log_sha256':'raw'},[self.root],self.root)
        self.assertEqual(value,obs);self.assertEqual(prov['mode'],'HASH_BOUND_SNAPSHOT_REUSED')
    def test_arbitrary_control_kernel_labels_close_without_being_called_S_F(self):
        obs={}
        for prof,n,tail in [('W_ONLY',100,9),('F',90,12)]:
            obs[('x',prof)]={'frames':[{'kernel_name':'k','gpu_sim_cycle':n,'gpu_tot_sim_cycle':n,
              'counter_snapshot_delta':{},'raw_clock_line':1},{'kernel_name':'','gpu_sim_cycle':0,
              'gpu_tot_sim_cycle':n+tail,'counter_snapshot_delta':{},'raw_clock_line':2}]}
        row=dict(workload='x',left='W_ONLY',right='F',left_attempt='a',right_attempt='b',cycles_left=109,cycles_right=102,cycles_right_minus_left=-7)
        joined=c.timing_for_contrast(row,obs)
        self.assertEqual(sum(r['right_minus_left_cycles'] for r in joined),-7)
        self.assertEqual(joined[0]['left_gpu_sim_cycle'],100)
        self.assertFalse(any(k.startswith('S_') or k.startswith('F_') for k in joined[0]))
        row['cycles_right']=101
        with self.assertRaisesRegex(ValueError,'terminal clock'):c.timing_for_contrast(row,obs)

if __name__=='__main__':unittest.main()
