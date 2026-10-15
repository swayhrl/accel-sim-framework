from evidence import *
import subprocess,resource
rows=list(map(json.loads,(R/'raw/requests.jsonl').read_text().splitlines()));first=next(x for x in rows if x['url'].endswith('sigir_draft.pdf'));total=int(first['headers']['Content-Length']);prefix=R/'sources/upstream_author_paper.pdf';n=prefix.stat().st_size;assert n==2097153 and total==9307397
row,tail=fetch(first['url'],'upstream_author_paper.tail',limit=total-n,headers={'Range':f'bytes={n}-{total-1}','If-Match':first['headers']['ETag']})
assert row.get('status')==206 and len(tail)==total-n
h={k.lower():v for k,v in row['headers'].items()};assert h.get('content-range')==f'bytes {n}-{total-1}/{total}' and h.get('etag')==first['headers']['ETag']
full=R/'sources/upstream_author_paper_complete.pdf'
with full.open('wb') as f:f.write(prefix.read_bytes());f.write(tail)
assert full.stat().st_size==total
subprocess.run(['pdftotext','-f','2','-l','2','-layout',str(full),str(R/'sources/upstream_author_page2.txt')],check=True,timeout=20)
txt=(R/'sources/upstream_author_page2.txt').read_text();normalized=' '.join(txt.replace('\u00ad','').split());assert 'We have made this dataset available for aca' in normalized;start=normalized.index('We have made this dataset available');excerpt=normalized[start:start+220]
x={'url':first['url'],'full_bytes':total,'full_SHA256':sha(full),'ETag':h['etag'],'assembly':'previous bounded prefix + one conditional206 range tail; ETag and exact Content-Range match','prefix_bytes':n,'tail_bytes':len(tail),'quote_page_1_based':2,'excerpt':excerpt,'claim':'upstream authors explicitly state availability for academic use; exact OGB derivative/license applicability requires separate binding','RAM_self_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024};(R/'raw/upstream_academic_statement.json').write_text(json.dumps(x,indent=2));print(json.dumps(x),flush=True);check()
