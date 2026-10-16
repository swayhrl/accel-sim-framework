#!/usr/bin/python3
"""Synthetic consumer tests; no simulator, real result edits or network calls."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import acceptance_gate as gate
from result_intake import summarize, canonical_sha, REQUIRED_GATES, RELEASE_GATES, WORKLOADS, ro_bits
from native_pair_intake import read_native_packet


def sha(b): return hashlib.sha256(b).hexdigest()

def fixture(n=1):
    q = {'status':'INDEPENDENTLY_QUALIFIED','qualified_by':'lane5','evidence_kind':'PRODUCTION_DRIVEN',
         'core_source_commit':'1'*40,'framework_source_commit':'2'*40,'binary_sha256':'3'*64,
         'data_correctness_scope':'SYMBOLIC_32B_SECTOR_VERSIONS_AND_REQUEST_IDENTITY_NOT_NUMERIC_SASS_PAYLOAD'}
    evidence = b'{"synthetic_test_only":true}\n'
    q['gates']={k:{'status':'PASS','production_driven':True,'evidence_path':'docs/ep_l2/synthetic_checks.json','evidence_sha256':sha(evidence)} for k in RELEASE_GATES}
    runs=[]
    for w in WORKLOADS[:n]:
        for mode in ['B16_BANKED','U_WB16']:
            identity={k:q[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']}
            identity.update(workload=w,runtime_config_sha256=('4' if mode=='B16_BANKED' else '5')*64,trace_content_sha256='6'*64,
                epoch_range={'scope':'full_application','epochs':'all'},
                feature_vector={'finite_wbuf':True,'unified_wb':mode=='U_WB16','ro':False,'tvd':False,'adaptive_policy':False,
                    'wbuf_entries':16,'payload_capacity_per_slice':1168,'bank_count':4,'ops_per_bank_cycle':1},
                ideal_vector={'wb':False,'meta':False,'read_hit':False})
            runs.append({'workload':w,'mode':mode,'status':'COMPLETE_VALID','identity':identity,'run_key':canonical_sha(identity),
                'raw_log_sha256':'7'*64,'effective_base_config_sha256':'8'*64,'validation':{k:True for k in REQUIRED_GATES},
                'numeric_payload_validation':'UNAVAILABLE_SASS_DATALESS','summary':{'cycles':100 if mode=='B16_BANKED' else 125,'instructions':1000}})
    q['qualified_feature_vectors']=[r['identity']['feature_vector'] for r in runs[:2]]
    return {'evidence_kind':'FUNCTIONAL_IMPLEMENTATION','qualification':q,'runs':runs}


class Checks(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='ep-l2-lane6-r3-synthetic-')
        self.root=Path(self.tmp.name);self.repo=self.root/'authority';self.repo.mkdir()
        self.git('init','-q');self.git('-c','user.name=Lane6 Synthetic','-c','user.email=test@example.invalid','commit','--allow-empty','-qm','synthetic authority floor')
        self.floor=self.git('rev-parse','HEAD').strip();self.current=self.floor
        self.patcher=patch.object(gate,'remote_head',side_effect=lambda:self.current);self.patcher.start()
        self.floorpatch=patch.object(gate,'AUTHORITY_FLOOR',self.floor);self.floorpatch.start()
        self.packet=fixture();self.prepare(self.packet)

    def tearDown(self):
        self.floorpatch.stop();self.patcher.stop();self.tmp.cleanup()

    def git(self,*args):return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.STDOUT).decode()
    def write(self,path,data):
        dest=self.repo/path;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data if isinstance(data,bytes) else json.dumps(data,sort_keys=True).encode())
    def prepare(self,packet,table_change=None,matrix_change=None):
        rows=[]
        for r in packet['runs']:
            rows.append({**{k:r['identity'][k] for k in gate.IDENTITY_KEYS},'run_key':r['run_key'],'workload':r['workload'],'mode':r['mode'],
                'raw_log_sha256':r['raw_log_sha256'],'observed_cycles':r['summary']['cycles'],'instructions':r['summary']['instructions'],
                'original_terminal_status':r['status'],'scientific_acceptance':'CURRENT_ACCEPTED'})
        self.table={'status':'CURRENT_ACCEPTED','evidence_pack':'docs/ep_l2/review_packs/SYNTHETIC_ONLY','rows':rows}
        self.matrix={'R0.1':{'status':'CURRENT_ACCEPTED','formal_runs':copy.deepcopy(rows),
            'repair_manifest':self.table['evidence_pack']+'/REPAIR_MANIFEST.json'}}
        if table_change:table_change(self.table)
        if matrix_change:matrix_change(self.matrix)
        self.publish()
    def publish(self):
        base=self.table['evidence_pack']
        self.write(base+'/REPAIR_MANIFEST.json',{'test_only':True,'not_actual_qualification':True})
        self.write(base+'/SCIENTIFIC_HOLD.json',{'test_only':True,'historical_revocation':'retained'})
        sums=''.join(sha((self.repo/base/n).read_bytes())+'  '+n+'\n' for n in ['REPAIR_MANIFEST.json','SCIENTIFIC_HOLD.json'])
        self.write(base+'/SHA256SUMS',sums.encode())
        self.write(gate.REPORT+'APPLICATION_ACCEPTANCE.json',self.table);self.write(gate.REPORT+'VALIDATION_MATRIX.json',self.matrix)
        self.packet_path=self.root/'normalized.json';self.packet_path.write_text(json.dumps(self.packet,sort_keys=True))
        self.write('bundle.json',{'normalized_pair_packet_sha256':sha(self.packet_path.read_bytes())})
        self.write(gate.REPORT+'RECEIPT.json',{'lane_id':5,'artifacts':[gate.REPORT+'APPLICATION_ACCEPTANCE.json',base,'bundle.json','native_pair']})
        self.git('add','.');self.git('-c','user.name=Lane6 Synthetic','-c','user.email=test@example.invalid','commit','--allow-empty','-qm','synthetic authority update')
        self.current=self.git('rev-parse','HEAD').strip()
        self.binding={'publication_commit':self.current,'release_key':'R0.1','sha256':{n:sha((self.repo/gate.REPORT/n).read_bytes()) for n in ['APPLICATION_ACCEPTANCE.json','VALIDATION_MATRIX.json','RECEIPT.json']}}
        self.binding['sha256']['supersession_SHA256SUMS']=sha((self.repo/base/'SHA256SUMS').read_bytes())
    def context(self):return gate.load_current_acceptance(self.repo,self.binding)
    def summary(self,p=None):return summarize(p or self.packet,self.context())
    def adapter(self):
        return {'current_acceptance':self.binding,'publication_commit':self.current,'receipt_path':gate.REPORT+'RECEIPT.json',
            'receipt_sha256':sha((self.repo/gate.REPORT/'RECEIPT.json').read_bytes()),'bundle_path':'bundle.json',
            'bundle_sha256':sha((self.repo/'bundle.json').read_bytes()),'packet_file':str(self.packet_path)}
    def plot(self,adapter,out):
        spec=self.root/'adapter.json';spec.write_text(json.dumps(adapter))
        argv=['plot_qualified_pairs.py',str(spec),'--framework-repo',str(self.repo),'--output-dir',str(out)]
        with patch.object(sys,'argv',argv),contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(Path(__file__).with_name('plot_qualified_pairs.py')),run_name='__main__')

    def test_missing_current_context_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'Current acceptance context'):summarize(self.packet)
        with self.assertRaisesRegex(ValueError,'Explicit current'):gate.load_current_acceptance(self.repo,None)
    def test_partial_includes_slowdown_and_no_mean(self):
        s=self.summary();self.assertEqual(s['pairs'][0]['speedup'],.8);self.assertIsNone(s['whole_group_geomean']);self.assertEqual(len(s['unavailable']),8)
    def test_full_cohort_mean_includes_slowdowns(self):
        self.packet=fixture(5);self.prepare(self.packet);s=self.summary();self.assertTrue(s['complete']);self.assertAlmostEqual(s['whole_group_geomean'],.8)
    def test_timeout_preserved_not_zero(self):
        self.packet['runs'][1]['status']='TIMEOUT';self.prepare(self.packet);s=self.summary();self.assertFalse(s['pairs']);self.assertIn('TIMEOUT',[r['status'] for r in s['unavailable']])
    def test_completed_single_side_cannot_hide_revocation(self):
        self.packet['runs'].pop();self.prepare(self.packet,lambda t:t['rows'][0].update(scientific_acceptance='SUSPENDED'))
        with self.assertRaisesRegex(ValueError,'SUSPENDED'):self.summary()
    def test_each_unaccepted_state_rejected(self):
        for state in ['SUSPENDED_MEMCPY_PHYSICAL_CLOCK','NOT_RUN_SCIENTIFIC_HOLD','NOT_RUN','RETRACTED_AS_SCIENTIFIC_RESULT',None]:
            with self.subTest(state=state):
                self.prepare(self.packet,lambda t:t['rows'][0].update(scientific_acceptance=state))
                with self.assertRaisesRegex(ValueError,'SUSPENDED_OR_UNACCEPTED'):self.summary()
    def test_identity_and_raw_mismatches_rejected(self):
        for key in [*gate.IDENTITY_KEYS,'raw_log_sha256','mode','workload']:
            with self.subTest(key=key):
                self.prepare(self.packet,lambda t:t['rows'][0].update({key:'wrong'}))
                with self.assertRaisesRegex(ValueError,'mismatch'):self.summary()
    def test_missing_or_duplicate_row_rejected(self):
        self.prepare(self.packet,lambda t:t['rows'].pop())
        with self.assertRaisesRegex(ValueError,'Missing/duplicate'):self.summary()
        self.prepare(self.packet,lambda t:t['rows'].append(copy.deepcopy(t['rows'][0])))
        with self.assertRaisesRegex(ValueError,'Duplicate/empty'):self.context()
    def test_matrix_suspension_vetoes_accepted_row(self):
        self.prepare(self.packet,matrix_change=lambda m:m['R0.1'].update(status='APPLICATION_QUALIFICATION_SUSPENDED'))
        with self.assertRaisesRegex(ValueError,'matrix is not'):self.summary()
    def test_matrix_row_conflict_vetoes_accepted_row(self):
        self.prepare(self.packet,matrix_change=lambda m:m['R0.1']['formal_runs'][0].update(scientific_acceptance='SUSPENDED'))
        with self.assertRaisesRegex(ValueError,'supersession conflict'):self.summary()
    def test_global_suspension_vetoes_accepted_row(self):
        self.prepare(self.packet,lambda t:t.update(status='SUSPENDED'))
        with self.assertRaisesRegex(ValueError,'not CURRENT_ACCEPTED'):self.summary()
    def test_old_source_or_binary_cannot_be_relabelled(self):
        for field,bad in [('core_source_commit',x) for x in gate.REVOKED_CORE]+[('binary_sha256',x) for x in gate.REVOKED_BINARY]:
            with self.subTest(field=field,bad=bad):
                self.packet=fixture()
                for r in self.packet['runs']:r['identity'][field]=bad;r['run_key']=canonical_sha(r['identity'])
                self.packet['qualification'][field]=bad;self.prepare(self.packet)
                with self.assertRaisesRegex(ValueError,'Revoked R0/R1'):self.summary()
    def test_new_repair_gates_mandatory(self):
        for name in ['physical_bank_clock','memcpy_payload_identity']:
            p=copy.deepcopy(self.packet);del p['qualification']['gates'][name]
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'Missing repaired'):self.summary(p)
    def test_production_gate_and_independent_status_required(self):
        p=copy.deepcopy(self.packet);p['qualification']['gates']['physical_bank_clock']['production_driven']=False
        with self.assertRaisesRegex(ValueError,'gate failure'):self.summary(p)
        p=copy.deepcopy(self.packet);p['qualification']['status']='PRODUCER_READY'
        with self.assertRaisesRegex(ValueError,'not independent'):self.summary(p)
    def test_totals_tamper_rejected(self):
        p=copy.deepcopy(self.packet);p['runs'][0]['summary']['cycles']+=1
        with self.assertRaisesRegex(ValueError,'totals mismatch'):self.summary(p)
    def test_scope_failure_rejected_numeric_absence_allowed(self):
        self.assertEqual(len(self.summary()['pairs']),1)
        p=copy.deepcopy(self.packet);p['runs'][0]['validation']['sector_version_reference']=False
        with self.assertRaisesRegex(ValueError,'Verification failure'):self.summary(p)
    def test_cross_binary_or_ideal_rejected(self):
        for key,value in [('binary_sha256','9'*64),('ideal_vector',{'wb':False,'meta':False,'read_hit':True})]:
            p=copy.deepcopy(self.packet);p['runs'][1]['identity'][key]=value;p['runs'][1]['run_key']=canonical_sha(p['runs'][1]['identity'])
            self.prepare(p)
            with self.assertRaises(ValueError):self.summary(p)
    def test_ro_compatibility_view_keeps_identity(self):
        f=self.packet['runs'][0]['identity']['feature_vector'];original=copy.deepcopy(f);self.assertFalse(ro_bits(f)['ro_tag_detach']);self.assertEqual(f,original)
    def test_stale_publication_rejected(self):
        old=copy.deepcopy(self.binding);self.publish()
        with self.assertRaisesRegex(ValueError,'Stale acceptance'):gate.load_current_acceptance(self.repo,old)
    def test_current_context_rechecks_before_summary(self):
        context=self.context();self.publish()
        with self.assertRaisesRegex(ValueError,'Stale acceptance'):summarize(self.packet,context)
    def test_authority_unavailable_fails_closed(self):
        with patch.object(gate,'remote_head',side_effect=ValueError('Cannot establish current Lane-5 authority; fail closed')):
            with self.assertRaisesRegex(ValueError,'fail closed'):self.context()
    def test_digest_and_supersession_closure_tamper_rejected(self):
        self.binding['sha256']['APPLICATION_ACCEPTANCE.json']='0'*64
        with self.assertRaisesRegex(ValueError,'digest mismatch'):self.context()
        self.publish();base=self.table['evidence_pack'];self.write(base+'/SCIENTIFIC_HOLD.json',b'tampered')
        self.git('add','.');self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','test tamper');self.current=self.git('rev-parse','HEAD').strip();self.binding['publication_commit']=self.current
        with self.assertRaisesRegex(ValueError,'digest mismatch'):self.context()
    def test_missing_supersession_digest_rejected(self):
        del self.binding['sha256']['supersession_SHA256SUMS']
        with self.assertRaisesRegex(ValueError,'supersession checksum'):self.context()
    def test_revocation_floor_ancestor_required(self):
        with patch.object(gate,'AUTHORITY_FLOOR','0'*40),self.assertRaisesRegex(ValueError,'predates mandatory'):self.context()
    def test_plot_then_supersession_refuses_replay_without_output(self):
        out=self.root/'accepted';self.plot(self.adapter(),out);self.assertTrue((out/'WB_PAIRS.pdf').exists())
        old_adapter=self.adapter();self.prepare(self.packet,lambda t:t['rows'][0].update(scientific_acceptance='SUSPENDED'))
        replay=self.root/'replay'
        with self.assertRaisesRegex(ValueError,'Stale acceptance'):self.plot(old_adapter,replay)
        self.assertFalse(replay.exists())
        with self.assertRaisesRegex(ValueError,'SUSPENDED'):self.plot(self.adapter(),replay)
        self.assertFalse(replay.exists())
    def test_final_emission_freshness_change_writes_nothing(self):
        # load: first+last; published-packet: first; summarize: first+last; sixth is emission.
        seq=[self.current]*5+['f'*40]
        out=self.root/'final-ref-changed'
        with patch.object(gate,'remote_head',side_effect=seq),self.assertRaisesRegex(ValueError,'Stale acceptance'):
            self.plot(self.adapter(),out)
        self.assertFalse(out.exists())
    def test_plot_packet_tamper_rejected(self):
        self.packet_path.write_text('{}')
        out=self.root/'tamper'
        with self.assertRaisesRegex(ValueError,'Unbound normalized'):self.plot(self.adapter(),out)
        self.assertFalse(out.exists())
    def test_old_r2_adapter_has_no_implicit_defaults(self):
        with self.assertRaisesRegex(ValueError,'Explicit repaired-release adapter'):read_native_packet(self.repo,{'native_pairs':[]})
    def test_duplicate_failed_input_rejected(self):
        p=copy.deepcopy(self.packet);p['runs'].append(copy.deepcopy(p['runs'][0]));p['runs'][-1]['status']='FAILED'
        with self.assertRaisesRegex(ValueError,'Duplicate workload'):self.summary(p)
    def test_native_repaired_adapter_and_raw_tamper(self):
        import csv
        p=fixture();q=p['qualification'];results=[];specs=[];rows=[];modes={}
        binary=b'synthetic executable';q['binary_sha256']=sha(binary)
        for r in p['runs']:
            data=r['mode'].encode();configs=[{'name':'config-0.config','bytes':len(data),'sha256':sha(data)}]
            traces=[{'name':'kernelslist.g','sha256':'a'*64}]
            ident=r['identity'];ident['binary_sha256']=sha(binary);ident['runtime_config_sha256']=canonical_sha({'ordered_configs':configs,'auxiliary_assets':[],'environment':{}});ident['trace_content_sha256']=canonical_sha(traces)
            r['run_key']=canonical_sha(ident);directory=self.root/r['run_key'];directory.mkdir();(directory/'raw.log').write_bytes(b'synthetic log');(directory/'accel-sim.out').write_bytes(binary);(directory/'config-0.config').write_bytes(data);r['raw_log_sha256']=sha(b'synthetic log')
            summary={**r['summary'],'hardware_drained':True,'slices':64,'requester_exact_once_audit':True,'data_correctness_qualification':True,'wb_created':1,'wb_lower_accepted':1,'wb_completed':1,'payload_free':1168*64,'payload_roles':{},'payload_capacity':1168*64}
            summary.update({k:0 for k in ['live_descriptors','live_line_mshrs','live_wad','pending_lower_reads','pending_returns','pending_responses','transient_payloads']})
            result={'run_key':r['run_key'],'identity':ident,'status':r['status'],'summary':summary,'raw_log_sha256':r['raw_log_sha256'],'allocation':{'result_directory':str(directory)},'audit':{'configs':configs,'traces':traces,'auxiliary_assets':[]},'validation':{'status':'PASS'}}
            results.append(result);specs.append({'identity':ident,'environment':{}})
            row={k:ident[k] for k in gate.IDENTITY_KEYS};row.update(workload=r['workload'],mode=r['mode'],status=r['status'],run_key=r['run_key'],raw_log_sha256=r['raw_log_sha256'],**r['summary']);row.update({k:json.dumps(ident[k]) for k in ['feature_vector','ideal_vector','epoch_range']});rows.append(row)
            modes[r['mode']]={'runtime_config_sha256':ident['runtime_config_sha256'],'ordered_config_manifest':configs,'feature_vector':ident['feature_vector'],'ideal_vector':ident['ideal_vector']}
        qbytes=json.dumps(q,sort_keys=True).encode()
        for result in results:result['audit']['qualified_release_sha256']=sha(qbytes)
        self.write('docs/ep_l2/synthetic_checks.json',b'{"synthetic_test_only":true}\n');self.write('qualification.json',qbytes)
        self.write('producer.json',{**{k:q[k] for k in ['core_source_commit','framework_source_commit','binary_sha256']},'modes':modes})
        self.write('native_pair/PAIR_RECEIPT.json',{'workload':WORKLOADS[0],'results':results,'specs':specs})
        out=io.StringIO();writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows);self.write('native_pair/RESULTS.csv',out.getvalue().encode())
        self.packet=p;self.prepare(p)
        adapter={'current_acceptance':self.binding,'qualification_publication':self.current,'qualification_path':'qualification.json','producer_publication':self.current,'producer_contract_path':'producer.json','native_pairs':[{'publication_commit':self.current,'pair_repository_path':'native_pair'}]}
        context=self.context();packet=read_native_packet(self.repo,adapter,context);self.assertEqual(summarize(packet,context)['pairs'][0]['speedup'],.8)
        Path(results[1]['allocation']['result_directory'],'raw.log').write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'Raw payload mismatch'):read_native_packet(self.repo,adapter,context)

if __name__=='__main__':unittest.main(verbosity=2)
