"""Materialize one published frozen project config; no remote operation."""
import argparse,pathlib,subprocess,json,hashlib,base64
V9='docs/ep_l2/operations/174new_to_164_archive_v1/receipts/20261018_storageops_v9_target_01/v9_transaction.py'
def main():
 p=argparse.ArgumentParser();p.add_argument('--project',choices=['EP_L2_E057','DTC_L1_AD_GEMM'],required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--concurrent-write-reservation-bytes',type=int,default=0);a=p.parse_args();r=pathlib.Path(__file__).resolve().parent.parent
 assert not a.output.exists(),'config output must be ABSENT';m=json.loads((r/'manifests'/(a.project+'.json')).read_bytes());owner=(r/'owner_ready'/(a.project+'.json')).read_bytes();assert hashlib.sha256(owner).hexdigest()==m['owner_ready_sha256']
 lib=subprocess.check_output(['git','show','HEAD:'+V9],cwd=r);assert hashlib.sha256(lib).hexdigest()=='6fd13ab5a9df4b2f6cdddcc4c1e09bb34619571efdf3a7578372dc4b776603fe';assert a.concurrent_write_reservation_bytes>=0
 raw=sum(x['size'] for x in m['entries'] if x['type']=='file');allocation=sum(x['allocated'] for x in m['entries'])
 c={'manifest':m,'owner_raw_base64':base64.b64encode(owner).decode(),'v9_base64':base64.b64encode(lib).decode(),'native_reservation_bytes':allocation+320*1024**2,'NAS_reservation_bytes':3*raw+64*1024**2,'concurrent_write_reservation_bytes':a.concurrent_write_reservation_bytes}
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open('xb') as f:f.write((json.dumps(c,indent=2)+'\n').encode())
 print(json.dumps({'project':a.project,'txid':m['txid'],'config':str(a.output),'Source_action':'SOURCE_KEEP','remote_writes':0}))
if __name__=='__main__':main()
