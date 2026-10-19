import hashlib,os,pathlib,tempfile,unittest
import tls_v10_one_shot_stage_recovery as recovery
from tls_v10_p9_exact_window_runner import Hold

class ExactStageRecovery(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.d=pathlib.Path(self.t.name);self.p=self.d/'range-0000.bin';self.p.write_bytes(b'fixture');os.chmod(self.p,0o600)
        self.rows=[dict(relative_path='data',offset=0,length=7,source_identity={'fixture':True},original_sha256='a'*64)]
        self.sha=[hashlib.sha256(b'fixture').hexdigest()]
    def test_complete_stage_verified_without_write(self):
        before=self.p.stat();e=recovery.verify_complete_stage(self.d,self.rows,self.sha)
        self.assertEqual(e[0]['chunk_sha256'],self.sha[0]);self.assertEqual(self.p.stat(),before)
    def test_short_stage_refused(self):
        self.p.write_bytes(b'short')
        with self.assertRaises(Hold):recovery.verify_complete_stage(self.d,self.rows,self.sha)
    def test_wrong_sha_refused(self):
        with self.assertRaises(Hold):recovery.verify_complete_stage(self.d,self.rows,['0'*64])
    def test_extra_path_refused(self):
        (self.d/'extra').write_text('x')
        with self.assertRaises(Hold):recovery.verify_complete_stage(self.d,self.rows,self.sha)
    def test_symlink_refused(self):
        self.p.unlink();self.p.symlink_to('/dev/null')
        with self.assertRaises(Hold):recovery.verify_complete_stage(self.d,self.rows,self.sha)
    def test_hardlink_refused(self):
        alias=self.d.parent/(self.d.name+'-alias');os.link(self.p,alias)
        try:
            with self.assertRaises(Hold):recovery.verify_complete_stage(self.d,self.rows,self.sha)
        finally:alias.unlink()

class FollowupAuthority(unittest.TestCase):
    def setUp(self):
        self.binding=dict(window_id='TLS_V10_P9_PUBLIC_B0013',plan_batch_index=12,txid=recovery.r.old.TXID,selector_sha256=recovery.r.old.SELECTOR,source_root=recovery.r.old.SOURCE_ROOT,canonical_manifest_sha256=recovery.r.old.MANIFEST_SHA256)
        self.source=dict(canonical_approval_commit=recovery.CANONICAL_AMENDMENT,source_adopts_exact_commit=True)
        self.target=dict(canonical_approval_commit=recovery.CANONICAL_AMENDMENT,status='S_AND_T_SAME_CANONICAL_USER_APPROVAL_COMMIT_ADOPTED')
    def check(self):return recovery.check_followup_binding(self.binding,self.source,self.target)
    def test_same_approval_frozen_followup(self):self.check()
    def test_wrong_source_adoption(self):
        self.source['canonical_approval_commit']='0'*40
        with self.assertRaises(Hold):self.check()
    def test_wrong_target_adoption(self):
        self.target['status']='NOT_ADOPTED'
        with self.assertRaises(Hold):self.check()
    def test_not_original_followup(self):
        for window in ['TLS_V10_P9_PUBLIC_B0009','TLS_V10_P9_PUBLIC_B0034','C16_B0013']:
            self.binding['window_id']=window
            with self.assertRaises(Hold):self.check()
    def test_changed_transaction(self):
        self.binding['txid']='0'*64
        with self.assertRaises(Hold):self.check()

if __name__=='__main__':unittest.main()
