"""CPU regression: a previous telemetry gap must not mask later fatal resource evidence."""
import unittest,os
from unittest.mock import patch
from types import SimpleNamespace as NS
from supervisor import Supervisor
from resource_monitor import MonitorStop
class TelemetryGuardTests(unittest.TestCase):
    def build(self):
        x=Supervisor.__new__(Supervisor);x.s=NS(nv=None,ps=None,pid=os.getpid(),wall=lambda:100,mono=lambda:1,disk=lambda:1);x.cfg={"goal_start_epoch":0};x.owned={os.getpid()};x.handle=None;x.held=0;x.shared=NS(check=lambda row:row);x.r={"samples":[],"desktop_activity_attribution_gap":True};x.save=lambda:None
        return x
    def invoke(self,raised):
        x=self.build()
        with patch("supervisor.collect_snapshot",return_value={}),patch("supervisor.apply_desktop_policy",side_effect=lambda row,cfg,reader:row),patch("supervisor.enforce_snapshot"),patch("supervisor.runtime_activity",side_effect=raised):
            return x.snapshot("WORKER")
    def test_prior_gap_does_not_mask_high_external_activity(self):
        with self.assertRaises(MonitorStop):
            self.invoke(MonitorStop("GPU_RESOURCE_DEFERRED","Observed desktop GPU activity above frozen interference threshold"))
    def test_specific_attribution_gap_only_is_downgraded(self):
        self.assertEqual(self.invoke(MonitorStop("GPU_RESOURCE_DEFERRED","Desktop activity attribution unavailable during own work")),{})
    def test_unrelated_monitor_error_remains_fatal(self):
        with self.assertRaises(MonitorStop):
            self.invoke(MonitorStop("GPU_RESOURCE_DEFERRED","Unknown GPU process"))
if __name__=="__main__":unittest.main(verbosity=2)
