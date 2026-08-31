#!/usr/bin/env python3
"""Reference-style CSV-only redraw of five-class blocked-cycle composition."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT.parents[0]/'PAPER_FIGURES_DRAFT_v4'/'plotting_tables'/'FIG2_L2_BLOCKER_COMPOSITION_100PCT_PAPER_DRAFT.csv'
ORDER=['BlackScholes','dwt2d','convolutionSeparable','mergeSort','sad','spmv','transpose','scan','FWT_7_21','cfd_097k','btree','gemm']
GROUPS=[(0,1,'Streaming / Spatial'),(1,8,'Low Temporal Reuse'),(8,12,'Reuse Rich')]
NAMES=['SET_ASSOC','MSHR_META','MISSQ_LOWER','WB_PATH','OTHER']; COLORS=['#285394','#f1ead0','#a61c4c','#6e9d5b','#8a8a8a']; FONT=ImageFont.load_default()
def main():
 out=ROOT/'figures';tab=ROOT/'plotting_tables';out.mkdir(parents=True,exist_ok=True);tab.mkdir(exist_ok=True)
 data={r['workload']:r for r in csv.DictReader(SRC.open())}; rows=[data[w] for w in ORDER]
 with (tab/'FIG2_L2_BLOCKER_COMPOSITION_REFERENCE_STYLE.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 W,H=1480,720;x0,y0,pw,ph=130,565,1260,405;bar=62;step=pw/len(rows);xs=[x0+step*(i+.5) for i in range(len(rows))]
 im=Image.new('RGB',(W,H),'white');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><defs><pattern id="noblock" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="8" fill="#f2f2f2"/><line x1="0" y1="0" x2="0" y2="8" stroke="#aaa" stroke-width="2"/></pattern></defs><rect width="100%" height="100%" fill="white"/>']
 # boxed horizontal legend, matching the supplied compact reference style
 lx=145
 for i,(n,c) in enumerate(zip(NAMES,COLORS)):
  x=lx+i*190;svg.append(f'<rect x="{x}" y="31" width="15" height="15" fill="{c}" stroke="#333"/><text x="{x+21}" y="43" font-family="sans-serif" font-size="13">{n}</text>');dr.rectangle((x,31,x+15,46),fill=c,outline=(51,51,51));dr.text((x+21,32),n,fill='black',font=FONT)
 svg += [f'<rect x="{x0}" y="{y0-ph}" width="{pw}" height="{ph}" fill="none" stroke="black" stroke-width="1.5"/>',f'<text x="32" y="{y0-ph/2}" font-family="sans-serif" font-size="17" transform="rotate(-90 32 {y0-ph/2})">Composition among blocked cycles (%)</text>']
 for p in range(0,101,20):
  y=y0-ph*p/100;svg.append(f'<line x1="{x0}" y1="{y}" x2="{x0+pw}" y2="{y}" stroke="#777" stroke-width="1" stroke-dasharray="6,5"/><text x="{x0-14}" y="{y+5}" text-anchor="end" font-family="sans-serif" font-size="14">{p}</text>');dr.line((x0,y,x0+pw,y),fill=(119,119,119),width=1);dr.text((x0-36,y-5),str(p),fill='black',font=FONT)
 for x,r in zip(xs,rows):
  total=int(r['blocking_cycles_total']); y=y0
  if not total:
   svg.append(f'<rect x="{x-bar/2}" y="{y0-ph}" width="{bar}" height="{ph}" fill="url(#noblock)" stroke="#777"/><text x="{x}" y="{y0-ph/2}" text-anchor="middle" font-family="sans-serif" font-size="11">No blocking</text>');dr.rectangle((x-bar/2,y0-ph,x+bar/2,y0),outline=(119,119,119));dr.text((x-bar/2,y0-ph/2),'N/A',fill='black',font=FONT)
  else:
   for n,c in zip(NAMES,COLORS):
    hh=ph*float(r[n+'_fraction_of_blocked_cycles']);y-=hh;svg.append(f'<rect x="{x-bar/2}" y="{y}" width="{bar}" height="{hh}" fill="{c}" stroke="#222" stroke-width="0.45"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(34,34,34))
  svg.append(f'<text x="{x}" y="{y0+24}" text-anchor="middle" font-family="sans-serif" font-size="12">{r["workload"]}</text>');dr.text((x-25,y0+13),r['workload'][:14],fill='black',font=FONT)
 for a,b,label in GROUPS:
  mid=(xs[a]+xs[b-1])/2;svg.append(f'<text x="{mid}" y="{y0+112}" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">{label}</text>');dr.text((mid-len(label)*3,y0+103),label,fill='black',font=FONT)
  if b<len(rows):
   x=(xs[b-1]+xs[b])/2;svg.append(f'<line x1="{x}" y1="{y0-ph}" x2="{x}" y2="{y0+68}" stroke="#777" stroke-width="1" stroke-dasharray="5,4"/>');dr.line((x,y0-ph,x,y0+68),fill=(119,119,119),width=1)
 svg.append('</svg>');(out/'FIG2_L2_BLOCKER_COMPOSITION_REFERENCE_STYLE_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(out/'FIG2_L2_BLOCKER_COMPOSITION_REFERENCE_STYLE_PAPER_DRAFT.png')
if __name__=='__main__':main()
