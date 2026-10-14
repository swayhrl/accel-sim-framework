import json,pathlib,time
from budget_io import ROOT,download
url='https://ann-benchmarks.com/glove-100-angular.hdf5';size=485413888;etag='"9ef1a69a639809d4ae43efd5e6707fa1-58"'
try:
 receipt=download(url,ROOT/'downloads/glove-100-angular.hdf5',size,kind='data',headers={'Range':f'bytes=0-{size-1}','If-Match':etag})
 assert receipt['etag']==etag and receipt['content_range']==f'bytes 0-{size-1}/{size}'
 receipt['status']='PASS';(ROOT/'data_download_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('DATA_DOWNLOADED',receipt,flush=True)
except Exception as e:
 (ROOT/'data_download_failure.json').write_text(json.dumps({'error':repr(e),'epoch':time.time()}));raise
