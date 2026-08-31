#!/usr/bin/env python3
"""CSV-only four-bin temporal reuse-distance redraw (v9)."""
import csv
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
B=ROOT.parents[0]/'PAPER_FIGURES_DRAFT_v8'/'plotting_tables'/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_NONZERO_PAPER_DRAFT.csv'
A=ROOT.parents[0]/'DRAFT_FIGURES_CHECKPOINT_r1'/'plotting_tables'/'FIG1V2_PANEL_A.csv'
ORDER=['dwt2d','convolutionSeparable','spmv','scan','FWT_7_21','cfd_097k','btree'];GROUPS=[(0,4,'Low Temporal Reuse'),(4,7,'Reuse Rich')]
CATS=[('≤256',['<=8','9-16','17-32','33-64','65-128','129-256'],'#1f5a85'),('257–512',['257-512'],'#eadba6'),('513–2048',['513-1024','1025-2048'],'#ea944e'),('>2048',['2049-4096','>4096'],'#9f3d28')];FONT=ImageFont.load_default()
def main():
 out=ROOT/'figures';tab=ROOT/'plotting_tables';out.mkdir(parents=True,exist_ok=True);tab.mkdir(exist_ok=True)
 raw=list(csv.DictReader(B.open()));a={r['workload']:r for r in csv.DictReader(A.open())};by={}
 for r in raw:by.setdefault(r['workload'],{})[r['distance_bin']]=r
 rows=[]
 for w in ORDER:
  r={'workload':w,'temporal_reuse_instances':by[w]['<=8']['temporal_reuse_instances'],'T_true_temporal_fraction':a[w]['temporal_fraction']}
  for name,bins,_ in CATS:r[name]=sum(float(by[w][b]['conditional_fraction']) for b in bins)
  rows.append(r)
 with (tab/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_MERGED_PAPER_DRAFT.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 W,H=1180,680;x0,y0,pw,ph=110,535,970,395;bar=84;step=pw/len(rows);xs=[x0+step*(i+.5) for i in range(len(rows))]
 im=Image.new('RGB',(W,H),'white');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/>']
 for i,(n,_,c) in enumerate(CATS):
  x=180+i*190;svg.append(f'<rect x="{x}" y="30" width="15" height="15" fill="{c}" stroke="#333"/><text x="{x+21}" y="43" font-family="sans-serif" font-size="13">{n}</text>');dr.rectangle((x,30,x+15,45),fill=c,outline=(51,51,51));dr.text((x+21,30),n,fill='black',font=FONT)
 svg += [f'<rect x="{x0}" y="{y0-ph}" width="{pw}" height="{ph}" fill="none" stroke="black" stroke-width="1.5"/>',f'<text x="28" y="340" font-family="sans-serif" font-size="16" transform="rotate(-90 28 340)">Fraction of temporal reuse (%)</text>']
 for p in range(0,101,20):
  y=y0-ph*p/100;svg.append(f'<line x1="{x0}" y1="{y}" x2="{x0+pw}" y2="{y}" stroke="#777" stroke-dasharray="6,5"/><text x="{x0-12}" y="{y+5}" text-anchor="end" font-family="sans-serif" font-size="14">{p}</text>');dr.line((x0,y,x0+pw,y),fill=(119,119,119));dr.text((x0-34,y-5),str(p),fill='black',font=FONT)
 for x,r in zip(xs,rows):
  y=y0
  for n,_,c in CATS:
   hh=ph*r[n];y-=hh;svg.append(f'<rect x="{x-bar/2}" y="{y}" width="{bar}" height="{hh}" fill="{c}" stroke="#222" stroke-width="0.45"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(34,34,34))
  svg.append(f'<text x="{x}" y="{y-9}" text-anchor="middle" font-family="sans-serif" font-size="13">T={float(r["T_true_temporal_fraction"]):.2f}</text><text x="{x}" y="{y0+25}" text-anchor="middle" font-family="sans-serif" font-size="13">{r["workload"]}</text>');dr.text((x-19,y-20),f'T={float(r["T_true_temporal_fraction"]):.2f}',fill='black',font=FONT);dr.text((x-28,y0+11),r['workload'],fill='black',font=FONT)
 for aa,bb,label in GROUPS:
  mid=(xs[aa]+xs[bb-1])/2;svg.append(f'<text x="{mid}" y="{y0+112}" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">{label}</text>');dr.text((mid-len(label)*3,y0+103),label,fill='black',font=FONT)
  if bb<len(rows):
   x=(xs[bb-1]+xs[bb])/2;svg.append(f'<line x1="{x}" y1="{y0-ph}" x2="{x}" y2="{y0+68}" stroke="#777" stroke-dasharray="5,4"/>');dr.line((x,y0-ph,x,y0+68),fill=(119,119,119))
 svg.append('</svg>');(out/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_MERGED_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(out/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_MERGED_PAPER_DRAFT.png')
if __name__=='__main__':main()
