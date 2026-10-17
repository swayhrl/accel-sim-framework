"""Recompute complete r19 diagnostic groups from existing current V2; never accepts results."""
import argparse
import json
import math
from pathlib import Path
import subprocess

from acceptance import CLIENT,MANIFEST,load_current_authority,current_manifest,require_current_result
from registry import write_json
from run import digest,require
from campaign_r0 import csv_write
from headroom_config import EXPERIMENT,H0

REPO=Path(__file__).resolve().parents[3]
WORKLOADS=('convolutionSeparable','FWT_7_21')
MODES=('B16_BANKED','U_WB16')
H0_PRESSURE=REPO/'docs/ep_l2/review_packs/FT20261017_LANE5_R19_INPUT_PRESSURE_PREPARATION_r1'


def published_json(path,publication):
    path=Path(path);relative=str(path.relative_to(REPO));raw=path.read_bytes()
    require(raw==subprocess.check_output(['git','show',publication+':'+relative],cwd=REPO),'Derived data differs from current published tree '+relative)
    return json.loads(raw)


def collect(regimes):
    state=load_current_authority();ledger=current_manifest(state);pointer=json.loads(CLIENT.read_text())['scientific_acceptance'];pub=pointer['publication_commit']
    require((REPO/MANIFEST).read_bytes()==subprocess.check_output(['git','show',pub+':'+MANIFEST],cwd=REPO),'Current ledger not exact published tree')
    groups={};pairs=[];pressure=[]
    for regime in regimes:
        group=[]
        for workload in WORKLOADS:
            measured=[];baseline=[]
            for mode in MODES:
                now=[r for r in ledger['rows'] if r.get('experiment_id')==EXPERIMENT and r.get('regime')==regime and r['workload']==workload and r['mode']==mode]
                require(len(now)==1 and now[0]['scientific_acceptance']=='CURRENT_ACCEPTED','Incomplete same-condition diagnostic group '+regime+'/'+workload+'/'+mode)
                row=now[0];require_current_result(row['identity'],row['raw_log_sha256'],row['observed_cycles'],row['instructions'],state)
                old=[r for r in ledger['rows'] if not r.get('experiment_id') and r['workload']==workload and r['mode']==mode and r['runtime_config_sha256']==H0[mode] and r['scientific_acceptance']=='CURRENT_ACCEPTED']
                require(len(old)==1,'Missing unique accepted H0 reference');old=old[0]
                for field in ('core_source_commit','framework_source_commit','binary_sha256','trace_content_sha256','instructions'):
                    require(row[field]==old[field],'H0/diagnostic scope mismatch '+field)
                require_current_result(old['identity'],old['raw_log_sha256'],old['observed_cycles'],old['instructions'],state)
                review=REPO/row['independent_review']['path'];require(digest(review)==row['independent_review']['sha256'],'Independent review changed');published_json(review,pub)
                pack=review.parent;data=published_json(pack/(mode+'_PRESSURE.json'),pub);h0=published_json(H0_PRESSURE/(workload+'_'+mode+'_H0_PRESSURE.json'),pub)
                for label,source,item in ((regime,data,row),('H0',h0,old)):
                    pressure.append({'experiment_id':EXPERIMENT,'regime':label,'workload':workload,'mode':mode,'run_key':item['run_key'],'cycles':item['observed_cycles'],'raw_log_sha256':item['raw_log_sha256'],**source['aggregate'],**{'FT_'+k:v for k,v in source['FT_staging'].items()}})
                measured.append(row);baseline.append(old)
            b,u=measured;hb,hu=baseline;sh=b['observed_cycles']/u['observed_cycles'];s0=hb['observed_cycles']/hu['observed_cycles']
            pair={'experiment_id':EXPERIMENT,'regime':regime,'workload':workload,'C_B_H0':hb['observed_cycles'],'C_U_H0':hu['observed_cycles'],'C_B_h':b['observed_cycles'],'C_U_h':u['observed_cycles'],'S_H0':s0,'S_h':sh,'J_h':sh/s0,'delta_B_h_minus_H0':b['observed_cycles']-hb['observed_cycles'],'delta_U_h_minus_H0':u['observed_cycles']-hu['observed_cycles'],'B_run_key':b['run_key'],'U_run_key':u['run_key'],'B_config_sha256':b['runtime_config_sha256'],'U_config_sha256':u['runtime_config_sha256'],'trace_content_sha256':b['trace_content_sha256']}
            group.append(pair);pairs.append(pair)
        require(len(group)==2,'No partial diagnostic mean')
        groups[regime]={'predeclared_workloads':list(WORKLOADS),'pairs':2,'diagnostic_geomean_S_h':math.exp(sum(math.log(r['S_h']) for r in group)/2),'diagnostic_geomean_J_h':math.exp(sum(math.log(r['J_h']) for r in group)/2),'H0_five_workload_mean_unchanged':1.0016002037656606}
    return {'status':'COMPLETE_CURRENT_ACCEPTED_DIAGNOSTIC_GROUPS_ONLY','experiment_id':EXPERIMENT,'checked_current_authority':state['binding'],'current_publication':pub,'groups':groups,'paired_rows':pairs,'pressure_rows':list({(p['regime'],p['workload'],p['mode'],p['run_key']):p for p in pressure}.values()),'limits':['Same-condition S and interaction J only; no cross-condition EP-L2 speedup.','H0 all5 and old withdrawals retained; no new group replaces original0.16%.','Raw event/density/issue-opportunity/DRAM-tick measures separate; no additive GPU stalls or C1 headroom attribution.','Diagnostic means cover only the two predeclared workloads, no statistical significance or hardware-frequency claim.']}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--regimes',nargs='+',choices=('D4','Q4','D2','D8','L25'),default=['D4','Q4']);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    require(not a.out.exists(),'Frozen summary revision exists');report=collect(a.regimes);a.out.mkdir(parents=True)
    csv_write(a.out/'PAIRED_INTERACTION.csv',report['paired_rows']);csv_write(a.out/'PRESSURE_COMPARE.csv',report['pressure_rows']);write_json(a.out/'SUMMARY.json',report)
    print(json.dumps({'status':report['status'],'groups':report['groups']}))
if __name__=='__main__':main()
