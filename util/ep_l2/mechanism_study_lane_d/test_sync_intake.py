"""Analysis integrity checks with synthetic receipts, never application results."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import sync_intake as intake
import enrich_ro_evidence

class AnalysisIntegrity(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.identity = dict(core_source_commit='core', framework_source_commit='fw',
                             binary_sha256='binary', trace_content_sha256='trace',
                             epoch_range=dict(scope='full_application', epochs='all'), workload='fixture',
                             runtime_config_sha256='config')
        self.a = self.receipt('a', 100); self.b = self.receipt('b', 120)
        self.pair = dict(status='CURRENT_ACCEPTED', baseline_attempt_id='a', variant_attempt_id='b',
                         mechanism='W', comparison_group='fixture-only', nonresearch_config_equal=True)
    def receipt(self, name, cycles):
        r = dict(attempt_id=name, identity=copy.deepcopy(self.identity), status='COMPLETE_VALID',
                 independent_acceptance='PASS', complete_input_verified=True,
                 cycles=cycles, instructions=1000)
        return r
    def refs(self):
        rows = {}
        for r in [self.a, self.b]:
            p = self.root/(r['attempt_id']+'.json'); p.write_text(json.dumps(r))
            rows[r['attempt_id']] = dict(path=str(p), sha256=intake.digest(p), identity=r['identity'])
        return rows
    def ledger(self):
        return dict(campaign_id=intake.CAMPAIGN, authority_commit=intake.AUTHORITY, owner='E',
                    accepted_pairs={'p':self.pair}, accepted_results=self.refs())
    def test_missing_is_unknown_observed_zero_stays_zero(self):
        self.b['mechanism_metrics'] = {'trigger':0}
        row = intake.analyze_pair('p', self.pair, self.refs())
        self.assertEqual(row['trigger'], '0')
        self.assertEqual(row['bottleneck'], 'UNKNOWN')
        del self.b['cycles']
        row = intake.analyze_pair('p', self.pair, self.refs())
        self.assertEqual(row['variant_cycles'], 'UNKNOWN')
        self.assertEqual(row['baseline_over_variant'], 'UNKNOWN')
    def test_cross_binary_is_rejected(self):
        self.b['identity']['binary_sha256'] = 'different'
        with self.assertRaisesRegex(ValueError, 'cross-source/binary'):
            intake.analyze_pair('p', self.pair, self.refs())
    def test_negative_effect_retained(self):
        row = intake.analyze_pair('p', self.pair, self.refs())
        self.assertEqual(row['cycles_baseline_minus_variant'], -20)
        self.assertAlmostEqual(row['baseline_over_variant'], 100/120)
    def test_config_scope_cannot_be_inferred(self):
        self.pair.pop('nonresearch_config_equal')
        row = intake.analyze_pair('p', self.pair, self.refs())
        self.assertEqual(row['baseline_over_variant'], 'UNKNOWN')
        self.assertEqual(row['status'], 'E_ACCEPTED_PENDING_D_CONFIG_SCOPE')
    def test_idempotent_and_withdrawal_keeps_history(self):
        ledger = self.ledger(); out = self.root/'analysis'
        first = intake.sync(ledger, out)
        second = intake.sync(ledger, out)
        self.assertEqual(len(first['history']), len(second['history']))
        self.assertEqual(second['status'], 'NO_NEW_ACCEPTED_PAIR')
        ledger['accepted_pairs']['p'] = {'status':'WITHDRAWN'}
        third = intake.sync(ledger, out)
        self.assertEqual(third['D_analyzed_pairs'], 0)
        self.assertEqual(len(third['history']), 2)
        self.assertEqual(third['history'][0]['cycles_baseline_minus_variant'], -20)
    def test_old_campaign_and_short_fragment_rejected(self):
        ledger = self.ledger(); ledger['campaign_id'] = 'OLD_R19'
        with self.assertRaises(ValueError): intake.sync(ledger, self.root/'old')
        self.b['identity']['epoch_range']['scope'] = 'SCREEN_ONLY'
        with self.assertRaisesRegex(ValueError, 'screen/synthetic'):
            intake.analyze_pair('p', self.pair, self.refs())
    def test_exact_E_source_profiles_and_scope_are_retained(self):
        for r, profile in [(self.a, 'U'), (self.b, 'U_VICTIM_CLEAN_ONLY')]:
            r.update(profile=profile, source_identity=dict(core_source_commit='core',
                     framework_source_commit='fw', vendor_pybind11_commit='vendor', binary_sha256='binary'),
                     selection_id='D_V1_fixture', comparison_invariants_sha256='same',
                     qualification_id='q', labels={'diagnostic':False, 'subset':'CLEAN_ONLY', 'oracle':False})
        self.b['mechanism_metrics']={'actual_victim_hits':0, 'lower_read_bytes':32}
        row = intake.analyze_pair('p', self.pair, self.refs())
        self.assertEqual(row['vendor'], 'vendor')
        self.assertEqual(row['variant_profile'], 'U_VICTIM_CLEAN_ONLY')
        self.assertEqual(json.loads(row['variant_labels'])['subset'], 'CLEAN_ONLY')
        self.assertEqual(json.loads(row['variant_mechanism_metrics'])['actual_victim_hits'], 0)
        self.assertEqual(row['trigger'], 'UNKNOWN')  # No invented mapping from flat fields.
        self.b['source_identity']['vendor_pybind11_commit']='different'
        with self.assertRaisesRegex(ValueError, 'comparison boundary'):
            intake.analyze_pair('p', self.pair, self.refs())
    def test_embedded_E_pair_endpoint_cannot_silently_rebind(self):
        refs = self.refs()
        self.pair['endpoints']={side:dict(refs[key], attempt_id=key)
                              for side,key in [('left','a'),('right','b')]}
        intake.analyze_pair('p', self.pair, refs)
        self.b['cycles']=110
        with self.assertRaisesRegex(ValueError, 'endpoint pointer changed'):
            intake.analyze_pair('p', self.pair, self.refs())
    def test_RO_input_property_does_not_create_L2_pressure_or_cross_input(self):
        candidate=self.root/'candidate.json';candidate.write_text('{}')
        item={'workload':'fixture','matching_trace_hashes':['right-trace'],
              'candidate_path':str(candidate),'candidate_sha256':intake.digest(candidate),
              'scope':'TRACE_MODEL_CLOSED_WORLD','certified_lines':7,'certified_read_lane_references':11}
        before={'workload':'fixture','trace':'right-trace','cycles':123,'R_tag_all_pending':'NO'}
        wrong=dict(before,trace='other-input')
        rows=enrich_ro_evidence.enrich([copy.deepcopy(before),wrong],{'inputs':[item]})
        self.assertEqual(rows[0]['RO_certified_lines'],7)
        self.assertEqual(rows[0]['RO_native_blocked_request_intersection'],'UNKNOWN')
        self.assertEqual(rows[0]['cycles'],123)
        self.assertEqual(rows[0]['R_tag_all_pending'],'NO')
        self.assertEqual(rows[1]['RO_certified_lines'],'UNKNOWN')
        candidate.write_text('{"changed":true}')
        with self.assertRaisesRegex(ValueError,'changed full-input'):
            enrich_ro_evidence.enrich([copy.deepcopy(before)],{'inputs':[item]})

if __name__ == '__main__': unittest.main()
