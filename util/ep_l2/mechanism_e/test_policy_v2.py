"""Affected V2 boundaries only. Synthetic controls are not native correctness."""
import copy
import hashlib
import json
import unittest
import subprocess
from unittest.mock import patch
from pathlib import Path
import coordinator as c
import policy_v2 as p
import test_coordinator as fixtures


class V2Tests(unittest.TestCase):
    setUp=fixtures.ControlTests.setUp
    save=fixtures.ControlTests.save
    read=fixtures.ControlTests.read

    def adopt(self):
        self.ledger.update(t0_unix=1792414193,actual_starts=0,screen_maximum=6)
        p.amend(self.ledger,1792420000)
        self.save()

    def test_amend_preserves_t0_and_every_attempt(self):
        self.ledger.update(t0_unix=1792414193,actual_starts=1,screen_maximum=6)
        self.ledger['attempts']=[{'actual_start':True,'state':'FAILED','budget_bucket':'victim'}]
        old=copy.deepcopy(self.ledger)
        self.save();result=self.coord.adopt_v2();new=self.coord.snapshot()
        self.assertEqual(result['remaining_start_capacity'],39)
        for key in ('attempts','t0_unix','qualifications','accepted_results','accepted_pairs','input_selections'):
            self.assertEqual(old[key],new[key])
        self.assertEqual(self.read()['campaigns'],self.data['campaigns'])
        self.assertFalse(self.coord.adopt_v2()['changed'])

    def test_count_mismatch_cannot_be_erased(self):
        self.ledger.update(actual_starts=1,screen_maximum=6)
        with self.assertRaisesRegex(ValueError,'recount mismatch'):p.amend(self.ledger,1792420000)

    def test_v2_not_40_additional(self):
        self.adopt()
        self.ledger['attempts']=[{'actual_start':True,'state':'FAILED'} for _ in range(40)]
        self.save()
        with self.assertRaisesRegex(ValueError,'40 actual'):self.coord.reserve_application(self.spec)

    def test_39_plus_reservation_fills_40(self):
        self.adopt()
        self.ledger['attempts']=[{'actual_start':True,'state':'FAILED'} for _ in range(39)]+[
            {'actual_start':False,'state':'RESERVED'}]
        c.counts(self.ledger);self.assertEqual(self.ledger['remaining_start_capacity'],0)

    def test_v2_41_rejected(self):
        self.adopt();self.ledger['maximum_actual_starts']=41;self.save()
        with self.assertRaisesRegex(ValueError,'budget/deadline'):self.coord.snapshot()

    def test_old_bucket_consumes_contingency(self):
        self.assertEqual(p.charged_bucket({'budget_bucket':'victim'},p.RESERVATIONS),'contingency')
        self.assertEqual(sum(p.RESERVATIONS.values()),40)

    def test_remote_build_cpu_counts_globally(self):
        self.data['resource_leases']['remote']={'host':'174-new','status':'RUNNING','cpu_units':8,'memory_bytes':8*c.GIB}
        with self.assertRaisesRegex(ValueError,'global shared CPU'):p.global_gate(self.data,'build',2,8*c.GIB)

    def test_remote_ram_counts_globally(self):
        self.data['resource_leases']['remote']={'host':'174-new','status':'RUNNING','cpu_units':2,'memory_bytes':32*c.GIB}
        with self.assertRaisesRegex(ValueError,'global shared memory'):p.global_gate(self.data,'test',1,c.GIB)

    def test_remote_simulations_share_four_slots(self):
        self.data['runs']={str(i):{'host':'174-new','status':'RUNNING','cpu_units':1,'memory_bytes':c.GIB} for i in range(4)}
        with self.assertRaisesRegex(ValueError,'global shared simulator'):p.global_gate(self.data,'simulation',1,c.GIB)

    def test_no_second_authority_on_remote_host(self):
        with patch.object(c.socket,'gethostname',return_value='174-new'):
            with self.assertRaisesRegex(ValueError,'central dispatcher'):
                with self.coord.registry.locked():pass

    def full_q(self):
        return {'supported_profiles':{key:{'research_switches':dict(zip(('W','V','T','M'),v))} for key,v in p.SWITCHES.items()},
          'full_system_v2':{'authority_commit':p.AUTHORITY,'fixed_policy':True,
          'victim_scope':'CLEAN_DIRTY_PENDING_INFLIGHT','resource_budget':{'data_slots':1168,'line_bytes':128,
          'resident_tags':1024,'banks':4,'bank_ops':1,'descriptors':512,'line_mshrs':128,'shared_wad_tvd':128},
          'minus_w_preserves_vr_and_static16_copy':True},
          'gates':{g:{'status':'PASS','production_driven':True,'evidence_path':str(self.bin),
                     'evidence_sha256':c.digest(self.bin)} for g in p.COMBINATION_GATES|{
                         'full_data_free_finite_residual_service','fixed_victim_equal_budget_and_cost'}}}

    def test_combination_control_accepts_complete_gate_binding(self):
        p.combination_qualification(self.full_q(),c.digest)

    def test_module_pass_not_combination_pass(self):
        q=self.full_q();q['gates']['shared_payload_lifecycle']['production_driven']=False
        with self.assertRaisesRegex(ValueError,'native combination'):p.combination_qualification(q,c.digest)

    def test_clean_only_cannot_be_full(self):
        q=self.full_q();q['full_system_v2']['victim_scope']='CLEAN_ONLY'
        with self.assertRaisesRegex(ValueError,'CLEAN_ONLY'):p.combination_qualification(q,c.digest)

    def test_full_profile_cannot_skip_new_qualification(self):
        q=self.full_q();del q['full_system_v2']
        with self.assertRaisesRegex(ValueError,'combination qualification'):p.combination_qualification(q,c.digest)

    def test_fake_minus_w_rejected(self):
        q=self.full_q();q['supported_profiles']['F_MINUS_W']['research_switches']['V']=0
        with self.assertRaisesRegex(ValueError,'ablation semantics'):p.combination_qualification(q,c.digest)

    def test_dependent_minus_w_explicitly_unsupported(self):
        q=self.full_q();q['full_system_v2']['minus_w_preserves_vr_and_static16_copy']=False
        with self.assertRaisesRegex(ValueError,'DEPENDENT_CONTROL_UNSUPPORTED'):p.combination_qualification(q,c.digest)

    def env(self):
        candidate={'campaign_id':c.CAMPAIGN,'authority_commit':p.AUTHORITY,
          'host_identity':{'hostname':'174-new','boot_id':'remote-boot'}}
        review={'reviewed_by':'E','independent_observation':True,'candidate_sha256':hashlib.sha256(
          json.dumps(candidate,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
          'measured_unix':1000,'expires_unix':1300,'host_identity':candidate['host_identity'],
          'physical_backing_verified':True,'physical_storage_identity':'independent-device-proof',
          'effective_memory_available_bytes':160*c.GIB,'effective_cpu_units':4,
          'share_available_bytes':41*c.GIB,'evidence':[{'path':str(self.bin),'sha256':c.digest(self.bin)}],
          'write_filesystems':[{'writable':True,'free_inodes':10000,'peak_growth_bytes':10*c.GIB,
              'available_bytes':80*c.GIB,'quota_available_bytes':80*c.GIB,'pending_growth_bytes':2*c.GIB}]}
        for key in ('quota_verified','write_probe_fsynced','all_write_destinations_closed',
                    'input_config_oracle_identity_closed','compiler_vendor_libraries_recorded',
                    'io_owner_coordination_pass','authorized_dispatch_entry_verified'):review[key]=True
        return candidate,review

    def test_environment_review_is_not_lease(self):
        candidate,review=self.env()
        result=p.environment_review(candidate,review,'old-physical-device',1100,c.digest)
        self.assertEqual(result['status'],'ENVIRONMENT_REVIEW_PASS_NOT_A_LEASE')
        self.assertEqual(self.read()['resource_leases'],{})

    def test_changed_hostname_not_physical_independence(self):
        candidate,review=self.env();review['physical_storage_identity']='old-physical-device'
        with self.assertRaisesRegex(ValueError,'alias'):p.environment_review(candidate,review,'old-physical-device',1100,c.digest)

    def test_remote_quota_cannot_sum_other_filesystems(self):
        candidate,review=self.env();review['write_filesystems'][0]['quota_available_bytes']=55*c.GIB
        with self.assertRaisesRegex(ValueError,'per-filesystem'):p.environment_review(candidate,review,'old',1100,c.digest)

    def test_f_candidate_without_independent_e_review_rejected(self):
        candidate,review=self.env();review['independent_observation']=False
        with self.assertRaisesRegex(ValueError,'independent E'):p.environment_review(candidate,review,'old',1100,c.digest)

    def test_stale_environment_not_admission(self):
        candidate,review=self.env()
        with self.assertRaisesRegex(ValueError,'stale'):p.environment_review(candidate,review,'old',1301,c.digest)

    def test_missing_remote_dispatcher_not_admission(self):
        candidate,review=self.env();review['authorized_dispatch_entry_verified']=False
        with self.assertRaisesRegex(ValueError,'dispatch'):p.environment_review(candidate,review,'old',1100,c.digest)

    def binding_fixture(self):
        root=self.root/'published';root.mkdir();directory=root/'util/mechanism_e';directory.mkdir(parents=True)
        api=directory/'coordinator.py';api.write_text('# frozen control API\n')
        helper=directory/'policy_v2.py';helper.write_text('# frozen policy\n')
        subprocess.run(['git','init','-q',str(root)],check=True)
        subprocess.run(['git','add','.'],cwd=root,check=True)
        subprocess.run(['git','-c','user.name=E control test','-c','user.email=e-control@example.invalid',
                        'commit','-qm','fixture'],cwd=root,check=True)
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
        contract={'authority_commit':p.AUTHORITY,'resource_lease_api_sha256':c.digest(api),
          'source_publication_commit':commit,'execution_worktree':str(root),
          'source_files':{str(x.relative_to(root)):c.digest(x) for x in (api,helper)}}
        path=self.root/'client.json';path.write_text(json.dumps(contract))
        return api,helper,path,contract

    def test_client_binds_real_git_source_commit(self):
        api,helper,path,contract=self.binding_fixture()
        with patch.object(c,'__file__',str(api)):
            self.assertEqual(c.verify_extension_binding(path),contract['source_publication_commit'])

    def test_unpublished_helper_hash_cannot_bypass_source_binding(self):
        api,helper,path,contract=self.binding_fixture();helper.write_text('# unpublished helper change\n')
        contract['source_files'][str(helper.relative_to(api.parents[2]))]=c.digest(helper)
        path.write_text(json.dumps(contract))
        with patch.object(c,'__file__',str(api)):
            with self.assertRaisesRegex(ValueError,'publication mismatch'):c.verify_extension_binding(path)

    def test_missing_helper_manifest_rejected(self):
        api,helper,path,contract=self.binding_fixture();contract['source_files'].pop(str(helper.relative_to(api.parents[2])))
        path.write_text(json.dumps(contract))
        with patch.object(c,'__file__',str(api)):
            with self.assertRaisesRegex(ValueError,'manifest incomplete'):c.verify_extension_binding(path)

    def test_f_data_free_needs_own_native_gate(self):
        q=self.full_q();q['gates']['full_data_free_finite_residual_service']['status']='NOT_RUN'
        with self.assertRaisesRegex(ValueError,'profile-specific native gate'):p.combination_qualification(q,c.digest)

    def test_physical_device_proof_cannot_be_hostname_only(self):
        candidate,review=self.env();review['physical_backing_verified']=False
        with self.assertRaisesRegex(ValueError,'physical independence'):p.environment_review(candidate,review,'old',1100,c.digest)

    def test_frozen_d32_schema_and_fixed_victim_encoding(self):
        path=Path(__file__).resolve().parents[3]/'docs/ep_l2/review_packs/MS20261019_E_FULL_SYSTEM_V2_r1/D_publication/MATRIX_32.json'
        matrix=json.loads(path.read_text());p.validate_matrix(matrix)
        row=next(r for r in matrix['conditions'] if r['profile']=='F_FIXED_V64')
        self.assertEqual(row['V'],'FIXED64')
        row['V']=1
        with self.assertRaisesRegex(ValueError,'matrix mode mismatch'):p.validate_matrix(matrix)

    def test_new_total_cannot_reuse_tls_output_exception(self):
        self.adopt();self.ledger['additional_results_max_bytes']=16*c.GIB;self.save()
        with self.assertRaisesRegex(ValueError,'output budget'):self.coord.snapshot()


if __name__=='__main__':unittest.main()
