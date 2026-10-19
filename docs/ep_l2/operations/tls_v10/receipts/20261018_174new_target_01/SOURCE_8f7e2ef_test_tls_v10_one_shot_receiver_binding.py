import unittest
from tls_v10_p9_exact_window_runner import _receiver_name_allowed

class OneShotReceiverBinding(unittest.TestCase):
    def setUp(self):
        self.window='TLS_V10_P9_PUBLIC_B0010'
        self.binding=dict(target_receiver_preflight_name=self.window+'_TARGET_METADATA_PREFLIGHT_COPY16_ONE_SHOT_20261019.json',
            one_shot_coordination_commit='3a7ea422d3f4301688bd3cb7bcf4431b97f08e90',
            target_request_git_commit='3bb823e362c3ae96a25e70cb762398355fbd1c3b',
            target_request_sha256='938c536b731e9584ea91840cfb1062191025019ec2b85fd5244b5f955e696991',
            target_receiver_preflight_git_commit='10263bccb2257f14209c1a0fc1f67dcd2b293d67',
            target_receiver_preflight_sha256='a220032309caad16fc9e55634be742368ec9b073b4a84da98861da8cb96ad134')
    def test_exact_append_only_refresh_accepted(self):
        self.assertTrue(_receiver_name_allowed(self.binding,self.window))
    def test_each_pin_mutation_rejected(self):
        for key in self.binding:
            changed=dict(self.binding);changed[key]+='x'
            self.assertFalse(_receiver_name_allowed(changed,self.window))
    def test_foreign_window_rejected(self):
        self.assertFalse(_receiver_name_allowed(self.binding,'TLS_V10_P9_PUBLIC_B0011'))
    def test_original_filename_semantics_preserved(self):
        self.assertTrue(_receiver_name_allowed({'target_receiver_preflight_name':'TLS_V10_P9_PUBLIC_B0004_TARGET_METADATA_PREFLIGHT_COPY16.json'},'TLS_V10_P9_PUBLIC_B0004'))

if __name__=='__main__':unittest.main()
