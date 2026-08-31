#!/usr/bin/env python3
"""CSV-only 100%-composition redraw of the five WBUF=8 blocker classes."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT.parents[0]/'PAPER_FIGURES_DRAFT_v3'/'plotting_tables'/'FIG2_L2_STRUCTURAL_BLOCKING_PAPER_DRAFT.csv'
ORDER=['BlackScholes','dwt2d','convolutionSeparable','mergeSort','sad','spmv','transpose','scan','FWT_7_21','cfd_097k','btree','gemm']
GROUPS=[(0,1,'Streaming / Spatial'),(1,8,'Low Temporal Reuse'),(8,12,'Reuse Rich')]
NAMES=['SET_ASSOC','MSHR_META','MISSQ_LOWER','WB_PATH','OTHER']; COLORS=['#c74c4c','#4f7fb8','#73a85f','#8c6baa','#9b9b9b']; FONT=ImageFont.load_default()
def main():
 ROOT.joinpath('figures').mkdir(parents=True,exist_ok=True);ROOT.joinpath('plotting_tables').mkdir(exist_ok=True)
 rows=list(csv.DictReader(INPUT.open())); data={r['workload']:r for r in rows}; plot=[]
 for w in ORDER:
  r=data[w]; total=sum(int(r[n]) for n in NAMES); q={'workload':w,'blocking_cycles_total':total}
  for n in NAMES:q[n]=int(r[n]);q[n+'_fraction_of_blocked_cycles']=int(r[n])/total if total else 0.0
  plot.append(q)
 with (ROOT/'plotting_tables'/'FIG2_L2_BLOCKER_COMPOSITION_100PCT_PAPER_DRAFT.csv').open('w',newline='') as f:
  out=csv.DictWriter(f,fieldnames=list(plot[0]));out.writeheader();out.writerows(plot)
 w,h=1700,800;x0,y0,pw,ph=105,630,1510,490;bar=65;step=pw/len(plot);xs=[x0+step*(i+.5) for i in range(len(plot))]
 im=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><rect width="100%" height="100%" fill="white"/>']
 for i,(n,c) in enumerate(zip(NAMES,COLORS)):
  x=245+i*190;svg.append(f'<rect x="{x}" y="27" width="14" height="14" fill="{c}" stroke="#333" stroke-width="0.5"/><text x="{x+20}" y="39" font-family="sans-serif" font-size="12">{n}</text>');dr.rectangle((x,27,x+14,41),fill=c,outline=(51,51,51));dr.text((x+20,28),n,fill='black',font=FONT)
 svg += [f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-ph}" stroke="black" stroke-width="1.5"/>',f'<line x1="{x0}" y1="{y0}" x2="{x0+pw}" y2="{y0}" stroke="black" stroke-width="1.5"/>','<text x="28" y="420" font-family="sans-serif" font-size="16" transform="rotate(-90 28 420)">Composition of blocked cycles (%)</text>']
 for p in range(0,101,20):
  y=y0-ph*p/100;svg.append(f'<line x1="{x0}" y1="{y}" x2="{x0+pw}" y2="{y}" stroke="#d0d0d0" stroke-dasharray="5,5"/><text x="{x0-10}" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="12">{p}</text>');dr.line((x0,y,x0+pw,y),fill=(208,208,208));dr.text((x0-28,y-5),str(p),fill='black',font=FONT)
 for x,r in zip(xs,plot):
  y=y0
  for n,c in zip(NAMES,COLORS):
   hh=ph*r[n+'_fraction_of_blocked_cycles'];y-=hh;svg.append(f'<rect x="{x-bar/2}" y="{y}" width="{bar}" height="{hh}" fill="{c}" stroke="#333" stroke-width="0.35"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(51,51,51))
  svg.append(f'<text x="{x}" y="{y0+20}" text-anchor="end" font-family="sans-serif" font-size="12" transform="rotate(-25 {x} {y0+20})">{r["workload"]}</text>');dr.text((x-27,y0+10),r['workload'][:14],fill='black',font=FONT)
 for a,b,label in GROUPS:
  mid=(xs[a]+xs[b-1])/2;svg.append(f'<text x="{mid}" y="{y0+130}" text-anchor="middle" font-family="sans-serif" font-size="14">{label}</text>');dr.text((mid-len(label)*3,y0+123),label,fill='black',font=FONT)
  if b<len(plot):
   x=(xs[b-1]+xs[b])/2;svg.append(f'<line x1="{x}" y1="110" x2="{x}" y2="{y0+95}" stroke="#999" stroke-dasharray="4,4"/>');dr.line((x,110,x,y0+95),fill=(153,153,153))
 svg.append('</svg>');(ROOT/'figures'/'FIG2_L2_BLOCKER_COMPOSITION_100PCT_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(ROOT/'figures'/'FIG2_L2_BLOCKER_COMPOSITION_100PCT_PAPER_DRAFT.png')
if __name__=='__main__':main()
