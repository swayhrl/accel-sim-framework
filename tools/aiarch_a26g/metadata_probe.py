#!/usr/bin/env python3
"""CPU-only bounded source/HTTP metadata reads. Never imports ML or GPU libraries."""
import argparse,datetime,hashlib,json,pathlib,time,urllib.request,urllib.error,signal

def run(url, method='GET', limit=2*1024*1024, headers=None):
    started=time.monotonic(); record={'url':url,'method':method,'limit_bytes':limit,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    data=b''
    def expire(signum,frame): raise RuntimeError('overall HTTP deadline 25 seconds')
    previous=signal.signal(signal.SIGALRM,expire);signal.setitimer(signal.ITIMER_REAL,25)
    try:
        req=urllib.request.Request(url,method=method,headers={'User-Agent':'AIARCH-A26G-source-qualification/1.0',**(headers or {})})
        with urllib.request.urlopen(req,timeout=45) as r:
            record.update(status=r.status,headers={k:v for k,v in r.headers.items() if k.lower() in {'content-type','content-length','content-range','accept-ranges','last-modified','etag','content-disposition'}},final_url=r.url.split('?')[0])
            if method!='HEAD':
                chunks=[]; remaining=limit
                while remaining:
                    chunk=r.read(min(remaining,65536))
                    if not chunk: break
                    chunks.append(chunk); remaining-=len(chunk)
                data=b''.join(chunks); record['read_limit_reached']=len(data)==limit
    except urllib.error.HTTPError as e:
        record.update(status=e.code,error_type='HTTPError'); data=e.read(min(limit,65536))
    except Exception as e:
        record.update(error_type=type(e).__name__,error=str(e))
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
    record.update(received_body_bytes=len(data),body_sha256=hashlib.sha256(data).hexdigest(),wall_seconds=time.monotonic()-started)
    return record,data

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('destination');p.add_argument('--head',action='store_true');p.add_argument('--limit',type=int,default=2*1024*1024);p.add_argument('--range');a=p.parse_args()
    rec,data=run(a.url,'HEAD' if a.head else 'GET',a.limit,{'Range':a.range} if a.range else None)
    dst=pathlib.Path(a.destination);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data);dst.with_suffix(dst.suffix+'.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
