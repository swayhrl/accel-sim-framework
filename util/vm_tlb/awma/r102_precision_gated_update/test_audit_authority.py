#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from audit_authority import positions

class AuthorityAuditTests(unittest.TestCase):
    def test_ordered_fragments(self):
        self.assertEqual(positions('a xx b yy c',['a','b','c']),[0,5,10])
    def test_missing_fragment_fails(self):
        with self.assertRaises(AssertionError): positions('a c',['a','b','c'])
    def test_reversed_fragment_fails(self):
        with self.assertRaises(AssertionError): positions('b a',['a','b'])

if __name__=='__main__':unittest.main()
