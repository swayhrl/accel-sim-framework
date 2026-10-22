import copy,unittest
from math_audit import audit_math,AuditError
from test_controls import scope,oldcounts
class AbsentProjection(unittest.TestCase):
 def test_actual_equal_nonzero_absent(self):
  d=scope();d['absent']=17;self.assertEqual(audit_math(d,oldcounts(d))['status'],'MATH_VALID_NOT_QUALIFICATION')
 def test_old_absent_overcount_rejected(self):
  d=scope();c=oldcounts(d);c['head_absent_cycles']=1
  with self.assertRaises(AuditError):audit_math(d,c)
 def test_old_absent_undercount_rejected(self):
  d=scope();d['absent']=1;c=oldcounts(d);c['head_absent_cycles']=0
  with self.assertRaises(AuditError):audit_math(d,c)
 def test_old_absent_bool_rejected(self):
  d=scope();c=oldcounts(d);c['head_absent_cycles']=False
  with self.assertRaises(AuditError):audit_math(d,c)
 def test_absent_missing_not_zero(self):
  d=scope();c=oldcounts(d);del c['head_absent_cycles']
  with self.assertRaises(KeyError):audit_math(d,c)
