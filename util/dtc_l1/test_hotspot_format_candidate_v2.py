#!/usr/bin/env python3
"""Refusal tests for offline candidate boundaries; no real trace is accessed."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CandidateGuards(unittest.TestCase):
    def test_refusals_with_and_without_python_optimization(self):
        script=Path(__file__).with_name('hotspot_format_candidate_v2.py')
        with tempfile.TemporaryDirectory(prefix='hotspot-candidate-guard-') as tmp:
            root=Path(tmp);raw=root/'raw';raw.mkdir()
            member=raw/'kernel-1.traceg'
            # Sparse placeholder: guard tests must reject before scanning it.
            with member.open('wb') as f:
                f.truncate(1041309456)
            profile=root/'profile.json'
            data=dict(status='PASS_CANDIDATE_SOURCE_PROFILE_NOT_IMMUTABLE_CAPTURE_RECEIPT',
                      member_sha256='ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8',
                      source_profile_sass_sha256='079d8b4d07c53f4c7bae0a9a9f484ceb2ff8eb3ad7487e1128eb68373472ec06',
                      counts=dict(records=13169524,active_instructions=377291004),failures=[])
            profile.write_text(json.dumps(data))
            wrong_profile=root/'wrong-profile.json';data['source_profile_sass_sha256']='0'*64
            wrong_profile.write_text(json.dumps(data))
            existing=root/'existing.traceg';existing.write_bytes(b'preserve existing output\n')
            wrong_member=root/'wrong-member.traceg';wrong_member.write_bytes(b'wrong input\n')
            for optimized in [False,True]:
                prefix=[sys.executable]+(['-O'] if optimized else [])+[str(script)]
                common=['--member',str(member),'--profile-validation',str(profile)]
                cases=[
                    ('existing_output',common+['--candidate-output',str(existing),'--report',str(root/'existing-report.json')]),
                    ('raw_output',common+['--candidate-output',str(raw/'new.traceg'),'--report',str(root/'raw-output-report.json')]),
                    ('raw_report',common+['--report',str(raw/'new-report.json')]),
                    ('same_output_and_report',common+['--candidate-output',str(root/'same.traceg'),'--report',str(root/'same.traceg')]),
                    ('wrong_member',['--member',str(wrong_member),'--profile-validation',str(profile),'--report',str(root/'wrong-member-report.json')]),
                    ('wrong_profile',['--member',str(member),'--profile-validation',str(wrong_profile),'--report',str(root/'wrong-profile-report.json')]),
                ]
                for name,args in cases:
                    with self.subTest(case=name,optimized=optimized):
                        result=subprocess.run(prefix+args,capture_output=True,timeout=5)
                        self.assertNotEqual(result.returncode,0)
                        self.assertIn(b'ValueError',result.stderr)
            self.assertEqual(existing.read_bytes(),b'preserve existing output\n')
            self.assertEqual(sorted(p.name for p in raw.iterdir()),['kernel-1.traceg'])
            self.assertFalse(any(root.glob('*report.json')))
            self.assertFalse((root/'same.traceg').exists())


if __name__=='__main__':
    unittest.main(verbosity=2)
