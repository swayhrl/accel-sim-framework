"""Synthetic metadata/resource-boundary qualification; no model launch."""
import copy,importlib.util,pathlib,unittest
P=pathlib.Path(__file__).with_name('aefair_result_gate_v2.py')
s=importlib.util.spec_from_file_location('candidate_gate',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Qualification(unittest.TestCase):
 def fixture(self):return {'registered_future_requests':{m.REQUEST:{'state':'RUNNING','reserved_write_bytes':805306368},'closed':{'state':'CLOSED'},'peer':{'state':'ARMED','reserved_write_bytes':123456}}}
 def test_current_peer_and_unknown_headroom(self):
  b=m.peer_basis(self.fixture());self.assertEqual(b['other_outstanding_write_reservations_bytes'],m.GIB+123456);self.assertEqual(b['own_reservation_bytes_preserved'],m.GIB)
 def test_active_missing_reservation_rejected(self):
  r=self.fixture();del r['registered_future_requests']['peer']['reserved_write_bytes']
  with self.assertRaises(RuntimeError):m.peer_basis(r)
 def test_negative_reservation_rejected(self):
  r=self.fixture();r['registered_future_requests']['peer']['reserved_write_bytes']=-1
  with self.assertRaises(RuntimeError):m.peer_basis(r)
 def test_boolean_reservation_rejected(self):
  r=self.fixture();r['registered_future_requests']['peer']['reserved_write_bytes']=True
  with self.assertRaises(RuntimeError):m.peer_basis(r)
 def test_own_above_preserved_cap_rejected(self):
  r=self.fixture();r['registered_future_requests'][m.REQUEST]['reserved_write_bytes']=m.GIB+1
  with self.assertRaises(RuntimeError):m.peer_basis(r)
 def test_all_terminal_peer_states(self):
  for state in ['CLOSED','COMPLETE','STOP_UNACCEPTED']:
   r=self.fixture();r['registered_future_requests']['peer']={'state':state};self.assertEqual(m.peer_basis(r)['other_outstanding_write_reservations_bytes'],m.GIB)
 def test_same_floor_and_own_reserve_boundary(self):
  b=m.peer_basis(self.fixture());required=b['disk_floor_bytes_preserved']+b['monitor_bytes_preserved']+b['own_reservation_bytes_preserved']+b['other_outstanding_write_reservations_bytes']+16*1024**2
  self.assertEqual(required,9*m.GIB+144*1024**2+123456)
  self.assertFalse(required-1>=required);self.assertTrue(required>=required)
 def test_explicit_override_cannot_lower_current_requirement(self):
  class Outbox:
   def gate(self,reservation=0,other_reservation=None):return {'other':other_reservation}
  old=m.current_basis;m.current_basis=lambda:m.peer_basis(self.fixture())
  try:
   o=Outbox();m.bind_gate(o)
   with self.assertRaises(RuntimeError):o.gate(other_reservation=0)
  finally:m.current_basis=old
if __name__=='__main__':unittest.main(verbosity=2)
