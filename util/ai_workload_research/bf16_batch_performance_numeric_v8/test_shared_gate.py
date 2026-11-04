"""V5 shared-gate policy unit tests, no real campaign lock/admin/network/CUDA calls."""
import unittest,os
from unittest.mock import patch
from types import SimpleNamespace as NS
from shared_gate import SharedClient
def who(pid):return dict(pid=pid,uid=1004,start_ticks=str(pid+1),boot_id="boot",executable="/usr/bin/python3.12")
def client():
    c=SharedClient.__new__(SharedClient);c.claimant=who(os.getpid());c.request_id="mine";c.baseline=None;c.latest=None
    c.cfg=dict(lock="FAKE_ONLY");c.s=dict(owner=who(100))
    c.value=dict(reservation=dict(request_id="mine",owner=c.claimant,pause_new_work=True),state="GPU_RESERVED_FOR_AI_ARCH",kernel_holders=[dict(identity=c.claimant)],completed_scopes=7,last_quiescence=dict(finished_unix=10),observed_compute_processes=[dict(pid=100)],run_nonce="nonce",owner=who(100),queue_counts=[0,1],last_profile_checked_unix=99,loaded_function_hashes={"a":"hash"},loaded_modules={"b":"hash"})
    c.get=lambda:c.value
    return c
def row():return dict(external_gpu_pids=[100,200],unqualified_external_gpu_pids=[100],known_own_pids=[os.getpid()])
class SharedTests(unittest.TestCase):
    def test_resident_is_specific_class_not_blanket_whitelist(self):
        c=client()
        with patch("shared_gate.kernel_holders",return_value=[os.getpid()]):
            r=c.check(row());self.assertEqual(r["unqualified_external_gpu_pids"],[]);self.assertEqual(r["verified_gated_resident_pids"],[100])
            r=row();r["unqualified_external_gpu_pids"].append(300);r=c.check(r);self.assertEqual(r["unqualified_external_gpu_pids"],[300])
    def test_wrong_actual_lock_holder_rejected(self):
        c=client()
        with patch("shared_gate.kernel_holders",return_value=[999]):
            with self.assertRaises(RuntimeError):c.check(row())
    def test_reservation_request_or_claimant_change_rejected(self):
        for mode in ["request","owner"]:
            c=client()
            if mode=="request":c.value["reservation"]["request_id"]="other"
            else:c.value["reservation"]["owner"]=who(999)
            with self.assertRaises(RuntimeError):c.check(row())
    def test_scope_count_change_rejected(self):
        c=client()
        with patch("shared_gate.kernel_holders",return_value=[os.getpid()]):
            c.check(row());c.value["completed_scopes"]+=1
            with self.assertRaises(RuntimeError):c.check(row())
    def test_unknown_compute_rejected(self):
        c=client();c.value["observed_compute_processes"].append(dict(pid=888))
        with patch("shared_gate.kernel_holders",return_value=[os.getpid()]):
            with self.assertRaises(RuntimeError):c.check(row())
    def test_no_delete_foreign_reservation(self):
        c=client();calls=[]
        def api(method,path,*a,**kw):
            calls.append(method);return dict(reservation=dict(request_id="other",owner=who(999))),{}
        c.api=api;result=c.release();self.assertFalse(result["released"]);self.assertEqual(calls,["GET"])
    def test_cleanup_own_reservation(self):
        c=client();calls=[]
        def api(method,path,*a,**kw):
            calls.append(method)
            return (dict(reservation=dict(request_id="mine",owner=c.claimant)) if method=="GET" else dict(reservation={},ownership_granted=False)),{}
        c.api=api;self.assertTrue(c.release()["released"]);self.assertEqual(calls,["GET","DELETE"])
if __name__=="__main__":unittest.main(verbosity=2)
