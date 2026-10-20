import copy
import unittest
from p9_source_stage_guard import verify_stage, POLICY_SHA, COPY5, GIB, MIB


class SignedSourceStageTests(unittest.TestCase):
    def setUp(self):
        self.s = dict(workspace_available_bytes=7*GIB, share_available_bytes=41*GIB,
                      snapshot_age_seconds=1, staged_physical_bytes=128*MIB,
                      growth_sample=dict(first_available_bytes=7*GIB,
                                         last_available_bytes=7*GIB, interval_seconds=2),
                      decision=dict(decision='POLICY_ELIGIBLE_NOT_READY', reasons=[],
                                    effective_workspace_floor_bytes=5*GIB,
                                    policy_id=COPY5, source_unlink_authorized=False,
                                    control_write_reserve_bytes=32*MIB,
                                    projection_horizon_seconds=120,
                                    predicted_external_growth_bytes=256*MIB,
                                    actual_workspace_available_bytes=7*GIB,
                                    projected_workspace_available_bytes=7*GIB-288*MIB))

    def call(self, s=None, wid='TLS_V10_P9_PUBLIC_B0029', pin=POLICY_SHA):
        return verify_stage(wid, s or self.s, copy5_policy_sha=pin)

    def test_exact_five_receive_windows(self):
        for n in range(29,34):
            self.assertEqual(self.call(wid='TLS_V10_P9_PUBLIC_B%04d'%n), 5*GIB)

    def test_no_authority_or_wrong_scope(self):
        for pin in [None, '0'*64]:
            with self.assertRaises(AssertionError): self.call(pin=pin)
        for wid in ['TLS_V10_P9_PUBLIC_B0028','TLS_V10_P9_PUBLIC_B0034','EP_L2_B0029']:
            with self.assertRaises(AssertionError): self.call(wid=wid)

    def test_policy_tampering(self):
        changes = [('policy_id','OTHER'), ('source_unlink_authorized',True),
                   ('control_write_reserve_bytes',0), ('projection_horizon_seconds',1),
                   ('predicted_external_growth_bytes',0), ('reasons',['HOLD']),
                   ('effective_workspace_floor_bytes',4*GIB),
                   ('actual_workspace_available_bytes',8*GIB),
                   ('projected_workspace_available_bytes',8*GIB)]
        for k,v in changes:
            s=copy.deepcopy(self.s);s['decision'][k]=v
            with self.assertRaises(AssertionError, msg=k):self.call(s)

    def test_growth_and_current_guards(self):
        s=copy.deepcopy(self.s);s['growth_sample']['first_available_bytes']=8*GIB
        with self.assertRaises(AssertionError):self.call(s)
        for k,v in [('share_available_bytes',40*GIB-1), ('snapshot_age_seconds',31),
                    ('staged_physical_bytes',256*MIB+1), ('workspace_available_bytes',5*GIB-1)]:
            s=copy.deepcopy(self.s);s[k]=v
            with self.assertRaises(AssertionError,msg=k):self.call(s)

    def test_original16_compatibility_without_copy5_authority(self):
        s=copy.deepcopy(self.s);s['decision']['effective_workspace_floor_bytes']=16*GIB
        s['workspace_available_bytes']=18*GIB
        s['decision']['projected_workspace_available_bytes']=17*GIB
        self.assertEqual(self.call(s,pin=None),16*GIB)


if __name__ == '__main__': unittest.main()
