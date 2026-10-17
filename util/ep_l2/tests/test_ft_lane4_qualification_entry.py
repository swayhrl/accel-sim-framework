"""Failure at directed-test entry must precede a lease or compiler process."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import test_ft_lane4_production as entry


class QualificationEntry(unittest.TestCase):
    def arguments(self,root):
        return ['qualification','--core',str(root/'core'),'--build',str(root/'build'),
                '--build-manifest',str(root/'manifest.json'),'--out',str(root/'out'),
                '--include-host-prefill']

    def test_registry_hash_mismatch_rejects_before_any_metadata_or_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with patch.object(sys,'argv',self.arguments(root)), \
                 patch.object(entry.ft_lane4_lane5_tools,'digest',return_value='0'*64), \
                 patch.object(entry.subprocess,'run',side_effect=AssertionError('process must not start')):
                with self.assertRaisesRegex(ValueError,'registry client changed'):entry.main()
            self.assertFalse((root/'out').exists())

    def test_missing_link_manifest_never_acquires_shared_lease(self):
        # A synthetic API traps any reservation. No real registry is replaced.
        class API:
            @staticmethod
            def Registry(*args):raise AssertionError('lease must not be attempted')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'manifest.json').write_text(json.dumps({'core_source_commit':'1'*40}))
            with patch.object(sys,'argv',self.arguments(root)), \
                 patch.object(entry.ft_lane4_lane5_tools,'load',return_value=({},API,None)), \
                 patch.object(entry.subprocess,'run') as source_check:
                with self.assertRaises(FileNotFoundError):entry.main()
                source_check.assert_called_once()
            self.assertFalse((root/'out').exists())


if __name__=='__main__':unittest.main()
