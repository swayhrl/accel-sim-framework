#!/usr/bin/env python3
import sys
p=sys.argv[1]; target=int(sys.argv[2]); prefix='ROUTEB_CENSUS_LAUNCH grid_launch_id='
rows=[]
for line in open(p,errors='replace'):
    if not line.startswith(prefix): continue
    nav=int(line[len(prefix):].split(' ',1)[0]); fn=line.split(' function=',1)[1].rsplit(' grid=',1)[0]
    rows.append((nav,fn,line.rstrip()))
target_row=next(r for r in rows if r[0]==target); exact=target_row[1]
matches=[r for r in rows if r[1]==exact]
ordinal=next(i for i,r in enumerate(matches) if r[0]==target)
print(ordinal); print(target_row[2]); print(len(matches))
