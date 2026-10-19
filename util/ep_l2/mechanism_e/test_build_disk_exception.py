"""User-authorized bounded named-build exception; no compiler or simulator."""
import copy
import unittest
from unittest.mock import patch
import coordinator as c
import test_coordinator as fixtures


class NamedBuildDiskTests(unittest.TestCase):
    setUp=fixtures.ControlTests.setUp
    save=fixtures.ControlTests.save
    read=fixtures.ControlTests.read

    def envelope(self):
        self.identity_build={'core':'1'*40,'framework':'2'*40,'vendor':'3'*40,
                             'build_entry_sha256':'4'*64,'build_directory':str(self.root/'build')}
        record={'status':'READY','campaign_id':c.CAMPAIGN,'host':c.socket.gethostname(),
          'boot_id':self.ledger['boot_id'],'expires_unix':c.time.time()+300,
          'user_instruction':'稍微低于48G没关系，你先启动，我会清理。',
          'source_identity':self.identity_build,'api_sha256':c.digest(c.__file__),
          'output_directory':str(self.root/'build'),'cpu_units':2,'memory_bytes':8*c.GIB,
          'growth_bytes':c.GIB,'result_growth_bytes':128*2**20,
          'disk_floor_bytes':47*c.GIB,'monitor_reserve_bytes':128*2**20}
        self.ledger['disk_authorizations']={'one':record};self.live['disk_free_bytes']=48*c.GIB+256*2**20;self.save()
        return record

    def reserve(self,**kw):
        params={'disk_authorization_id':'one','build_identity':self.identity_build};params.update(kw)
        return self.coord.reserve_work('A','build',2,8*c.GIB,c.GIB,self.root/'build',128*2**20,**params)

    def test_named_build_may_draw_only_its_reserved_growth_below48(self):
        self.envelope();result=self.reserve();self.assertEqual(result['disk_floor_bytes'],47*c.GIB)
        self.assertEqual(self.read()['hosts'],self.data['hosts'])
        self.assertEqual(self.coord.snapshot()['disk_authorizations']['one']['status'],'CONSUMED')

    def test_default_build_still48(self):
        self.envelope()
        with self.assertRaisesRegex(ValueError,'workspace'):
            self.coord.reserve_work('A','build',2,8*c.GIB,c.GIB,self.root/'build',128*2**20)

    def test_token_not_replayed(self):
        self.envelope();self.reserve()
        with self.assertRaisesRegex(ValueError,'used'):self.reserve()

    def test_wrong_source_rejected(self):
        self.envelope()
        with self.assertRaisesRegex(ValueError,'source/entry'):self.reserve(build_identity={'core':'9'*40})

    def test_expired_rejected(self):
        record=self.envelope();record['expires_unix']=0;self.save()
        with self.assertRaisesRegex(ValueError,'expired'):self.reserve()

    def test_wrong_host_rejected(self):
        record=self.envelope();record['host']='other';self.save()
        with self.assertRaisesRegex(ValueError,'host/boot'):self.reserve()

    def test_wrong_output_budget_rejected(self):
        record=self.envelope();record['growth_bytes']+=1;self.save()
        with self.assertRaisesRegex(ValueError,'paths/resources'):self.reserve()

    def test_competing_lease_rejected(self):
        self.envelope();self.data['resource_leases']['other']=fixtures.ControlTests.row(self);self.save()
        with self.assertRaisesRegex(ValueError,'competing'):self.reserve()

    def test_monitor_margin_is_required(self):
        record=self.envelope();record['monitor_reserve_bytes']=0;self.save()
        with self.assertRaisesRegex(ValueError,'overshoot'):self.reserve()

    def test_peak_plus_margin_cannot_be_waived(self):
        self.envelope();self.live['disk_free_bytes']=48*c.GIB
        with self.assertRaisesRegex(ValueError,'monitor reserve'):self.reserve()

    def test_no_wholesale_lower_floor(self):
        record=self.envelope();record['disk_floor_bytes']=45*c.GIB;self.save()
        with self.assertRaisesRegex(ValueError,'derive from exact'):self.reserve()

    def test_stale_helper_authorization_rejected(self):
        record=self.envelope();record['api_sha256']='0'*64;self.save()
        with self.assertRaisesRegex(ValueError,'stale E API'):self.reserve()

    def test_exception_blocks_competing_heavy_admission(self):
        self.envelope();self.reserve();d=self.read()
        with self.assertRaisesRegex(ValueError,'exclusive task-scoped'):c.policy_v2.global_gate(d,'test',1,c.GIB)

    def test_build_exception_cannot_be_application_floor(self):
        with self.assertRaisesRegex(ValueError,'only selected A build'):
            c.resource_gate(self.data,'simulation',1,c.GIB,c.GIB,self.live,self.usage,disk_floor_bytes=46*c.GIB)

    def repair(self):
        record=self.envelope();parent=copy.deepcopy(record)
        parent.update(status='CONSUMED',growth_bytes=3*c.GIB,result_directory=str(self.root/'old_result'),
                      disk_floor_bytes=45*c.GIB,lease_id='prior')
        self.ledger['disk_authorizations']['parent']=parent
        record.update(parent_authorization_id='parent',disk_draw_bytes=3*c.GIB,disk_floor_bytes=45*c.GIB,
                      repair_scope='TEST_OR_ENTRY_ONLY_PRODUCTION_UNCHANGED',
                      result_directory=str(self.root/'new_result'),
                      inherited_artifacts=[{'path':str(self.bin),'sha256':c.digest(self.bin)}])
        self.data['resource_leases']['prior']={'status':'RELEASED','host':c.socket.gethostname()}
        self.live['disk_free_bytes']=47*c.GIB;self.save();return record,parent

    def test_repair_reserves_only_new_growth_with_original_draw(self):
        self.repair();row=self.reserve()
        self.assertEqual(row['disk_growth_bytes'],c.GIB);self.assertEqual(row['disk_draw_bytes'],3*c.GIB)
        self.assertEqual(self.read()['resource_leases']['prior']['status'],'RELEASED')

    def test_repair_cannot_expand_original_draw(self):
        record,parent=self.repair();record['disk_draw_bytes']+=1;self.save()
        with self.assertRaisesRegex(ValueError,'enlarge original'):self.reserve()

    def test_repair_requires_retired_parent(self):
        self.repair();self.data['resource_leases']['prior'].update(status='RESERVED',cpu_units=2,memory_bytes=c.GIB);self.save()
        with self.assertRaisesRegex(ValueError,'competing|retired parent'):self.reserve()

    def test_repair_preserves_inherited_binary_identity(self):
        self.repair();self.bin.write_text('retained artifact modified')
        with self.assertRaisesRegex(ValueError,'retained repair artifact changed'):self.reserve()

    def test_repair_cannot_extend_original_expiry(self):
        record,parent=self.repair();record['expires_unix']=parent['expires_unix']+1;self.save()
        with self.assertRaisesRegex(ValueError,'extend parent expiry'):self.reserve()


if __name__=='__main__':unittest.main()
