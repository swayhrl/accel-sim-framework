"""V3 admission-policy CPU tests; supplement unchanged V2 snapshot/lifecycle coverage."""
import unittest
from types import SimpleNamespace as NS
from desktop_policy import apply_desktop_policy,admit_low_activity,runtime_activity
from resource_monitor import enforce_snapshot,MonitorStop
from supervisor import Supervisor
from test_supervision import FakeNV,FakePS,info,services,config

def evidence():
    user=dict(pid=30,ppid=90,uids=[120]*4,comm="Xorg",cgroup="display.scope",start_ticks=123)
    service=dict(pid=90,ppid=1,uids=[0]*4,comm="gdm3",cgroup="/system.slice/gdm.service",start_ticks=50)
    proof=dict(fingerprint=user,classification="VERIFIED_DESKTOP_SERVICE_IDENTITY_ACTIVITY_PENDING",ancestry_fingerprints=[user,service],service_MainPID=90)
    return {"30":proof},{30:user,90:service}
def cfg(name):
    c=config("v3_"+name)
    catalog,ident=evidence()
    c.update(desktop_identity_catalog=catalog,desktop_external_vram_bytes_max=512*1024**2,baseline_activity_samples_max=3,baseline_activity_window_seconds_max=5,baseline_GPU_utilization_pct_max=5,runtime_desktop_SM_utilization_pct_max=5)
    return c,ident
def external_row(mem=100):
    return dict(gpu_processes=[dict(pid=30,usedGpuMemory=mem)],external_gpu_pids=[30],unknown_gpu_pids=[],invalid_pid_rows=[],monitor_gaps=[],own_NVML_bytes=0,own_tree_RSS_bytes=100,own_new_disk_bytes=100,held_seconds=1,goal_elapsed_seconds=1)
class DesktopPolicyTests(unittest.TestCase):
    def test_verified_desktop_even_in_compute_list(self):
        c,ids=cfg("compute_desktop");row=apply_desktop_policy(external_row(),c,ids.__getitem__)
        self.assertEqual(row["desktop_identity_matched_pids"],[30]);enforce_snapshot(row,c)
    def test_plain_user_compute_not_exempt(self):
        c,ids=cfg("plain_python");c["desktop_identity_catalog"]={}
        row=apply_desktop_policy(external_row(),c,ids.__getitem__)
        with self.assertRaises(MonitorStop):enforce_snapshot(row,c)
    def test_known_user_pid_reuse_is_not_mislabelled(self):
        c,ids=cfg("user_pid_reuse");c["desktop_identity_catalog"]={}
        c["known_external_classifications"]={"30":"ORDINARY_USER_PROCESS_NOT_DESKTOP"}
        c["known_external_identity_fingerprints"]={"30":dict(ids[30])}
        ids[30]=dict(ids[30]);ids[30]["start_ticks"]+=1
        row=apply_desktop_policy(external_row(),c,ids.__getitem__)
        self.assertEqual(row["external_identity_evidence"][0]["category"],"IDENTITY_CHANGED_OR_REUSED")
        with self.assertRaises(MonitorStop):enforce_snapshot(row,c)
    def test_missing_service_evidence_rejected(self):
        c,ids=cfg("no_service");del c["desktop_identity_catalog"]["30"]["service_MainPID"]
        row=apply_desktop_policy(external_row(),c,ids.__getitem__)
        self.assertEqual(row["unqualified_external_gpu_pids"],[30])
    def test_pid_reuse_or_service_restart_rejected(self):
        for changed in [30,90]:
            c,ids=cfg("reused"+str(changed));ids[changed]=dict(ids[changed]);ids[changed]["start_ticks"]+=1
            row=apply_desktop_policy(external_row(),c,ids.__getitem__)
            with self.assertRaises(MonitorStop):enforce_snapshot(row,c)
    def test_identity_permission_gap_rejected(self):
        c,ids=cfg("permission")
        def reader(pid):raise PermissionError("identity")
        row=apply_desktop_policy(external_row(),c,reader)
        with self.assertRaises(MonitorStop):enforce_snapshot(row,c)
    def test_total_external_vram_cap(self):
        c,ids=cfg("vram")
        for size,okay in [(512*1024**2,True),(512*1024**2+1,False)]:
            row=apply_desktop_policy(external_row(size),c,ids.__getitem__)
            if okay:enforce_snapshot(row,c)
            else:
                with self.assertRaises(MonitorStop):enforce_snapshot(row,c)
    def test_low_activity_three_samples_same_goal_then_spawn(self):
        c,ids=cfg("low");s=services(FakeNV([info(30,100)]));s.read_identity=ids.__getitem__
        sup=Supervisor(c,s);r=sup.run()
        self.assertEqual(r["status"],"NATIVE_BATCH_SENSITIVITY_COMPLETE")
        self.assertEqual(len(r["admission_activity_samples"]),3)
        self.assertEqual(r["environment_classification"],"QUALIFIED_DESKTOP_CO_RESIDENT")
        self.assertEqual(s.counts["spawn"],1);self.assertFalse(r["EXCLUSIVITY_EVIDENCE_COMPLETE"])
    def test_high_baseline_stops_before_model(self):
        c,ids=cfg("high");s=services(FakeNV([info(30,100)]));s.read_identity=ids.__getitem__
        s.nv.nvmlDeviceGetUtilizationRates=lambda h:NS(gpu=6,memory=0)
        r=Supervisor(c,s).run();self.assertEqual(r["status"],"GPU_RESOURCE_DEFERRED");self.assertEqual(s.counts["spawn"],0);self.assertTrue(r["lock_released"])
    def test_unavailable_activity_stops_before_model(self):
        c,ids=cfg("util_unavailable");s=services(FakeNV([info(30,100)]));s.read_identity=ids.__getitem__
        def unsupported(h):raise RuntimeError("not supported")
        s.nv.nvmlDeviceGetUtilizationRates=unsupported
        r=Supervisor(c,s).run();self.assertEqual(r["status"],"GPU_RESOURCE_DEFERRED");self.assertEqual(s.counts["spawn"],0)
    def test_new_unknown_external_rejected(self):
        c,ids=cfg("new_compute");s=services(FakeNV([info(30,100),info(40,100)]));s.read_identity=ids.__getitem__;s.ps.alive.add(40)
        r=Supervisor(c,s).run();self.assertEqual(r["status"],"GPU_RESOURCE_DEFERRED");self.assertEqual(s.counts["spawn"],0)
    def test_bounded_activity_window_no_wait_loop(self):
        c,ids=cfg("time");count=[0]
        def mono():count[0]+=1;return 0 if count[0]==1 else 6
        sup=NS(cfg=c,s=NS(mono=mono),r={},snapshot=lambda p:None,save=lambda:None)
        with self.assertRaisesRegex(MonitorStop,"window"):admit_low_activity(sup)
    def test_runtime_desktop_activity_over_threshold_stops(self):
        c,ids=cfg("runtime_high");nv=FakeNV()
        nv.nvmlDeviceGetProcessUtilization=lambda h,t:[NS(pid=30,smUtil=6,memUtil=1,timeStamp=10)]
        sup=NS(cfg=c,s=NS(nv=nv),handle="fake",r={},save=lambda:None)
        row=dict(phase="WORKER",desktop_identity_matched_pids=[30])
        with self.assertRaises(MonitorStop):runtime_activity(sup,row)
    def test_runtime_attribution_gap_stops_and_preserves_evidence(self):
        c,ids=cfg("runtime_gap");sup=NS(cfg=c,s=NS(nv=FakeNV()),handle="fake",r={},save=lambda:None)
        row=dict(phase="WORKER",desktop_identity_matched_pids=[30])
        with self.assertRaises(MonitorStop):runtime_activity(sup,row)
        self.assertTrue(sup.r["desktop_activity_attribution_gap"]);self.assertIn("UNAVAILABLE",row["desktop_activity_attribution"])
if __name__=="__main__":unittest.main(verbosity=2)
