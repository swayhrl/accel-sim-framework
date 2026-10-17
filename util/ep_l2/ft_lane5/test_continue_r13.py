"""Only new continuation guards; no historical suite or production execution."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import continue_r13 as event
import qualify_r0_1 as qualify


class ContinueGuards(unittest.TestCase):
    def test_before600s_refuses_without_live_or_network(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_lane5_continue_test_') as raw:
            root = Path(raw);(root/'contract.json').write_text('{}')
            (root/'EVENT_000.json').write_text(json.dumps({'checked_at_unix': time.time()}))
            with patch.object(event, 'live') as live, patch.object(event, 'command') as cmd:
                with self.assertRaisesRegex(ValueError, 'minimum600s'): event.observe(root/'contract.json', root)
                live.assert_not_called();cmd.assert_not_called()

    def test_expired_observes_without_network_or_any_dispatch(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_lane5_continue_test_') as raw:
            root = Path(raw);(root/'contract.json').write_text(json.dumps({'deadline_utc':'PAST','deadline_unix':0}))
            with patch.object(event, 'live', return_value={}), patch.object(event, 'command') as cmd, contextlib.redirect_stdout(io.StringIO()):
                result = event.observe(root/'contract.json', root)
                self.assertEqual(result['status'], 'CONTINUE_WINDOW_EXPIRED_NO_NEW_DEPENDENCY_EXECUTION');cmd.assert_not_called()
                self.assertFalse(result['authorization_or_lease_claim'])

    def test_clock_counterexample_is_rejected(self):
        case={'case':'physical_clock_1_16_4096','argv':['a','b','1','16','4096'],'required_clock':{'offset':4096}}
        text='FT real partition lower-full/WBUF/WAD/set_done mode=1 C=16 peak=16 PASS\nCLOCK_AUDIT|offset=4096|violations=1|max_grants_per_physical_bank_cycle=2'
        with self.assertRaisesRegex(ValueError,'Physical bank clock'):qualify.check_directed_log(case,text)

    def test_clock_wrong_offset_is_rejected(self):
        case={'case':'physical_clock_1_16_4096','argv':['a','b','1','16','4096'],'required_clock':{'offset':4096}}
        text='FT real partition lower-full/WBUF/WAD/set_done mode=1 C=16 peak=16 PASS\nCLOCK_AUDIT|offset=0|violations=0|max_grants_per_physical_bank_cycle=1'
        with self.assertRaisesRegex(ValueError,'Physical bank clock'):qualify.check_directed_log(case,text)

    def test_prefill_generic_pass_is_insufficient(self):
        with self.assertRaisesRegex(ValueError,'host prefill'):qualify.check_directed_log({'case':'host_prefill_1_16'},'FT_HOST_PREFILL_PRODUCTION_SUITE PASS')

    def test_engineering_status_never_qualifies(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_lane5_continue_test_') as raw:
            p=Path(raw)/'receipt.json';p.write_text(json.dumps({'owner':'lane1','release':'R0.1','status':'COMPLETE_ENGINEERING_ONLY'}))
            with patch.object(qualify,'git',return_value=p.read_bytes()):
                with self.assertRaisesRegex(ValueError,'No official'):qualify.audit_producer(p,'0'*40,'docs/report.json')

    def test_engineering_root_cannot_be_renamed_as_formal(self):
        with tempfile.TemporaryDirectory(prefix='ep_l2_lane5_continue_test_') as raw:
            p=Path(raw)/'receipt.json';p.write_text(json.dumps({'owner':'lane1','release':'R0.1','status':'PRODUCER_TESTS_PASS_NOT_INDEPENDENTLY_QUALIFIED','compiler_started':True,'independent_qualification':False,'build':'/workspace/build/ep-l2-ft20261017-lane1-r0-1-engineering-pilot01','binary':'/workspace/build/ep-l2-ft20261017-lane1-r0-1-engineering-pilot01/accel-sim.out'}))
            with patch.object(qualify,'git',return_value=p.read_bytes()):
                with self.assertRaisesRegex(ValueError,'Foreign/engineering'):qualify.audit_producer(p,'0'*40,'docs/report.json')


if __name__ == '__main__':unittest.main()
