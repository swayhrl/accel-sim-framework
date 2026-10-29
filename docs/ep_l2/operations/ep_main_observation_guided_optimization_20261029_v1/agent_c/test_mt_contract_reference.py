import unittest
from mt_contract_reference import RequestReference, AddressUnionReference, readiness, rate


class ContractTests(unittest.TestCase):
    def test_default_off(self):
        r = RequestReference(); r.observe(1, 0, 0, 'first_head', 1, is_new=True)
        self.assertEqual((r.records, dict(r.counts)), ({}, {}))

    def test_boundaries_and_retry(self):
        r = RequestReference(True)
        for b, t in [('ingress_child', 3), ('queue_enter', 8), ('first_head', 12),
                     ('first_head', 18), ('admission', 20)]:
            r.observe(1, 0, 0, b, t, is_new=True)
        self.assertEqual([r.counts[b] for b in ('ingress_child','queue_enter','first_head','admission')], [1]*4)
        self.assertEqual(r.duration(1, 0, 'queue_enter', 'first_head'), 4)
        self.assertEqual(r.duration(1, 0, 'ingress_child', 'first_head'), 9)
        self.assertEqual(r.counts['new_unique'], 1)

    def test_successor_can_arrive_before_head_releases(self):
        r = RequestReference(True)
        r.observe(1, 0, 0, 'first_head', 5)
        r.observe(2, 0, 0, 'ingress_child', 6)
        r.observe(2, 0, 0, 'first_head', 20)
        self.assertEqual(r.duration(2, 0, 'ingress_child', 'first_head'), 14)

    def test_first_new_versus_ever_full(self):
        r = RequestReference(True)
        r.observe(1, 0, 0, 'first_head', 1, is_new=True, reserved=7)
        for t in (3, 3, 4):
            r.observe(1, 0, 0, 'first_head', t, is_new=True, reserved=8,
                      structural=1, policy_enabled=False, tag_denied=True)
        self.assertEqual(r.counts['first_new_R8'], 0)
        self.assertEqual(r.counts['ever_full_unique'], 1)
        self.assertEqual(r.counts['full_structural_checks'], 3)
        self.assertEqual(r.counts['full_structural_policy_on_checks'], 0)
        self.assertEqual(len(r.records[(1,0)]['denied_ticks']), 2)

    def test_full_without_structural_or_unknown(self):
        r = RequestReference(True)
        for uid, c in [(1, 0), (2, None)]:
            r.observe(uid, 0, 0, 'first_head', 1, is_new=True, reserved=8, structural=c)
        self.assertEqual(r.counts['full_structural_checks'], 0)
        self.assertEqual(r.counts['full_structural_unknown_checks'], 1)

    def test_generation_and_epoch(self):
        r = RequestReference(True)
        r.observe(1, 0, 1, 'ingress_child', 0)
        r.observe(1, 1, 2, 'ingress_child', 1)
        self.assertEqual(r.counts['ingress_child'], 2)
        with self.assertRaises(ValueError): r.observe(1, 0, 2, 'admission', 2)

    def test_cross_clock(self):
        r = RequestReference(True)
        r.observe(1, 0, 0, 'ingress_child', 100, 'CORE')
        r.observe(1, 0, 0, 'first_head', 50, 'L2')
        with self.assertRaises(ValueError): r.duration(1, 0, 'ingress_child','first_head')

    def test_same_tick_order_and_sector_split(self):
        r = RequestReference(True)
        for uid in (1, 2):
            for b in ('ingress_child', 'queue_enter', 'first_head'):
                r.observe(uid, 0, 0, b, 4)
        self.assertEqual(r.counts['ingress_child'], 2)
        self.assertEqual(r.duration(1, 0, 'ingress_child', 'first_head'), 0)

    def test_overflow_invalidates(self):
        r = RequestReference(True, 1)
        for uid in (1,2): r.observe(uid, 0, 0, 'first_head', 0)
        self.assertFalse(r.valid)
        self.assertEqual(r.counts['overflow'], 1)

    def test_sector_readiness(self):
        a = readiness(1, 1, 3, True)
        self.assertTrue(a['ready_only_drain'])
        self.assertTrue(a['line_has_issued_not_ready'])
        self.assertFalse(a['required_not_ready'])
        b = readiness(2, 1, 3, True)
        self.assertTrue(b['required_issued_not_ready'])
        self.assertFalse(readiness(2, 1, 3, False)['required_not_ready'])

    def test_address_union_not_sum(self):
        r = AddressUnionReference()
        r.set_refs(128, 2, 3, 2, 3)
        r.set_refs(256, 0, 0, 0, 1)
        self.assertEqual(r.occupancy(), (1, 1, 1, 2))
        r.set_refs(128, 0, 0, 0, 0)
        self.assertEqual(r.occupancy(), (0, 0, 0, 1))

    def test_address_overflow_unknown(self):
        r = AddressUnionReference(1)
        r.set_refs(128,1,0,1,0);r.set_refs(256,0,1,0,1)
        self.assertIsNone(r.occupancy())

    def test_matching_rate_population(self):
        p = ('first_head', 'global_demand_read', 'new', 'uid_generation')
        self.assertEqual(rate(3, 4, p, p), .75)
        self.assertIsNone(rate(0, 0, p, p))
        with self.assertRaises(ValueError): rate(3, 4, p, ('ingress_child',)+p[1:])


if __name__ == '__main__': unittest.main(verbosity=2)
