"""Analysis integrity checks with synthetic receipts, never application results."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import sync_intake as intake

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

if __name__ == '__main__': unittest.main()
