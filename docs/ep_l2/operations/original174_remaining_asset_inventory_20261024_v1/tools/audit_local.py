from pathlib import Path
import subprocess,json,csv,hashlib,datetime
W=Path(subprocess.check_output(['git','-C',str(Path(__file__).parent),'rev-parse','--show-toplevel']).decode().strip())
R=W/'docs/ep_l2/operations/original174_remaining_asset_inventory_20261024_v1'
R.mkdir(parents=True,exist_ok=True)
P=Path('D:/repo/tmp/original174_remaining_asset_inventory_20261024_v1');P.mkdir(parents=True,exist_ok=True)
def git(*args):return subprocess.check_output(['git','-C',str(W),*args])
def save(name,x):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def obj(commit,path):return git('show',commit+':'+path)
def remote(alias,code,timeout=90):
 r=subprocess.run(['ssh','-o','BatchMode=yes',alias,'nice -n 19 ionice -c 3 python3 -B -'],input=code.encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace')[-2000:])
 return json.loads(r.stdout)
if __name__=='__main__':
 c='474dc4613c6bd65de9431198caf9263df67dac7a'; prefix='docs/ep_l2/operations/global_cold_census_20261019_source/'
 for name in ['SOURCE_COLD_CENSUS_ROOT_LEDGER.csv','SOURCE_COLD_CENSUS_TOP20.csv','SOURCE_COLD_CENSUS_PROJECT_SUMMARY.csv','SOURCE_COLD_CENSUS_SCAN_COVERAGE.json','SOURCE_ROOT_DATA_BOUNDED_SIDECAR.json','SOURCE_COLD_CENSUS_C2P_BREAKDOWN.csv','SOURCE_C16_PACKAGE_DUPLICATE_EVIDENCE.json']:
  (P/name).write_bytes(obj(c,prefix+name))
 for name in ['SOURCE_COLD_CENSUS_ROOT_LEDGER.csv','SOURCE_COLD_CENSUS_TOP20.csv']:
  rows=list(csv.DictReader((P/name).open(encoding='utf-8-sig')));print(name,len(rows));print(json.dumps(rows[:3],indent=2)[:4500])
 print((P/'SOURCE_COLD_CENSUS_SCAN_COVERAGE.json').read_text()[:2500])

