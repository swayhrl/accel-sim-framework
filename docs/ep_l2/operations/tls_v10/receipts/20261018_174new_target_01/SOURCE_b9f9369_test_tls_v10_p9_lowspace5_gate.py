import unittest
from dataclasses import replace
import tls_v10_copy_only16g_gate as original
import tls_v10_copy_only20g_gate as frozen
import tls_v10_p9_lowspace5_gate as gate


class GateTests(unittest.TestCase):
    def call(self, item=None, **changes):
        args=dict(window=28, action='ack-publish',
                  predicted_growth_bytes=gate.TEMP_RESERVE,
                  growth_sample_age_seconds=0)
        args.update(changes)
        return gate.evaluate(item or original.policy_input(
            workspace_available_bytes=6*frozen.GIB), **args)

    def test_positive_original16_hold_new5_pass(self):
        item=original.policy_input(workspace_available_bytes=6*frozen.GIB)
        self.assertEqual(original.evaluate(item)['decision'], 'RESOURCE_HOLD')
        self.assertEqual(self.call(item)['decision'], 'POLICY_ELIGIBLE_NOT_READY')
        self.assertFalse(self.call(item)['source_unlink_authorized'])

    def test_all_remaining_actions(self):
        for n in range(29,34):
            for a in ['prepare','stage','publish','ack-prepare','ack-publish']:
                self.assertEqual(self.call(window=n,action=a)['reasons'],[])

    def test_scope_counterexamples(self):
        for n,a in [(27,'ack-publish'),(28,'stage'),(34,'stage'),(29,'delete')]:
            self.assertEqual(self.call(window=n,action=a)['decision'],'RESOURCE_HOLD')
        for fields in [dict(source_root='/workspace/EP-L2'),dict(group='OTHER24'),
                       dict(txid='0'*64),dict(source_namespace='wrong'),
                       dict(operation='UNLINK'),dict(source_unlink_requested=True)]:
            item=original.policy_input(workspace_available_bytes=6*frozen.GIB,**fields)
            self.assertEqual(self.call(item)['decision'],'RESOURCE_HOLD')

    def test_floor_and_projection(self):
        for size in [5*frozen.GIB-1,5*frozen.GIB,5*frozen.GIB+gate.TEMP_RESERVE]:
            self.assertEqual(self.call(original.policy_input(workspace_available_bytes=size))['decision'],'RESOURCE_HOLD')
        self.assertEqual(self.call(predicted_growth_bytes=2*frozen.GIB)['decision'],'RESOURCE_HOLD')
        self.assertEqual(self.call(predicted_growth_bytes=0)['decision'],'RESOURCE_HOLD')

    def test_original_guards_unchanged(self):
        for fields in [dict(share_available_bytes=40*frozen.GIB-1),
                       dict(memory_available_bytes=64*frozen.GIB),
                       dict(cgroup_headroom_bytes=None),dict(lane_runs_clear=False),
                       dict(lane_leases_clear=False),dict(candidate_root_idle=False),
                       dict(scheduled_readers_clear=False),dict(physical_scan_complete=False),
                       dict(sole_source_sender=False),dict(sole_target_receiver=False),
                       dict(snapshot_age_seconds=31),dict(first_source_sha_refreshed=False),
                       dict(target_request_present_and_exact=False),
                       dict(planned_rate_bytes_per_second=30*frozen.MIB+1),
                       dict(planned_bridge_staged_bytes=256*frozen.MIB+1)]:
            self.assertEqual(self.call(original.policy_input(workspace_available_bytes=6*frozen.GIB,**fields))['decision'],'RESOURCE_HOLD',fields)
        self.assertEqual(self.call(buffer_bytes=frozen.MIB+1)['decision'],'RESOURCE_HOLD')
        self.assertEqual(self.call(growth_sample_age_seconds=31)['decision'],'RESOURCE_HOLD')

    def test_growth_never_credits_reclamation(self):
        self.assertEqual(gate.growth_reserve(6*frozen.GIB,7*frozen.GIB,10),gate.TEMP_RESERVE)
        self.assertEqual(gate.growth_reserve(7*frozen.GIB,6*frozen.GIB,10),24*frozen.GIB)
        for seconds in [0,31]:
            with self.assertRaises(ValueError):gate.growth_reserve(1,1,seconds)


if __name__=='__main__':unittest.main()
