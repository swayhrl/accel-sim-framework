#!/usr/bin/env python3
"""CSV-only structural-blocking redraw using the v6 nonzero workload roster."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT.parents[0]/'PAPER_FIGURES_DRAFT_v3'/'plotting_tables'/'FIG2_L2_STRUCTURAL_BLOCKING_PAPER_DRAFT.csv'
ORDER=['dwt2d','convolutionSeparable','spmv','scan','FWT_7_21','cfd_097k','btree']
NAMES=['SET_ASSOC','MSHR_META','MISSQ_LOWER','WB_PATH','OTHER'];COLORS=['#c74c4c','#4f7fb8','#73a85f','#8c6baa','#9b9b9b'];FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def ft(n=15): return ImageFont.truetype(FONT,n)
def main():
 out=ROOT/'figures';tab=ROOT/'plotting_tables';out.mkdir(parents=True,exist_ok=True);tab.mkdir(exist_ok=True)
 data={r['workload']:r for r in csv.DictReader(SRC.open())};rows=[data[x] for x in ORDER]
 with (tab/'FIG2_L2_STRUCTURAL_BLOCKING_NONZERO_CN.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 W,H=1180,680;x0,y0,pw,ph=120,535,980,395;bar=80;step=pw/len(rows);xs=[x0+step*(i+.5) for i in range(len(rows))]
 im=Image.new('RGB',(W,H),'white');dr=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="100%" height="100%" fill="white"/>']
 for i,(n,c) in enumerate(zip(NAMES,COLORS)):
  x=105+i*190;svg.append(f'<rect x="{x}" y="30" width="15" height="15" fill="{c}" stroke="#333"/><text x="{x+21}" y="43" font-family="sans-serif" font-size="13">{n}</text>');dr.rectangle((x,30,x+15,45),fill=c,outline=(51,51,51));dr.text((x+21,27),n,fill='black',font=ft(13))
 svg += [f'<rect x="{x0}" y="{y0-ph}" width="{pw}" height="{ph}" fill="none" stroke="black" stroke-width="1.5"/>',f'<text x="30" y="340" font-family="Noto Sans CJK SC, sans-serif" font-size="16" transform="rotate(-90 30 340)">L2 准入阻塞周期占比（占合格 miss-admission 周期）</text>']
 for p in range(0,81,20):
  y=y0-ph*p/80;svg.append(f'<line x1="{x0}" y1="{y}" x2="{x0+pw}" y2="{y}" stroke="#777" stroke-dasharray="6,5"/><text x="{x0-12}" y="{y+5}" text-anchor="end" font-family="sans-serif" font-size="14">{p}</text>');dr.line((x0,y,x0+pw,y),fill=(119,119,119));dr.text((x0-35,y-7),str(p),fill='black',font=ft(13))
 for x,r in zip(xs,rows):
  y=y0
  for n,c in zip(NAMES,COLORS):
   hh=ph*float(r[n+'_fraction_of_eligible'])/0.8;y-=hh;svg.append(f'<rect x="{x-bar/2}" y="{y}" width="{bar}" height="{hh}" fill="{c}" stroke="#222" stroke-width="0.45"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(34,34,34))
  rate=float(r['overall_blocking_rate']);svg.append(f'<text x="{x}" y="{y-9}" text-anchor="middle" font-family="sans-serif" font-size="13">{rate:.1%}</text><text x="{x}" y="{y0+25}" text-anchor="middle" font-family="sans-serif" font-size="13">{r["workload"]}</text>');dr.text((x-18,y-20),f'{rate:.1%}',fill='black',font=ft(13));dr.text((x-28,y0+11),r['workload'],fill='black',font=ft(12))
 svg.append('<text x="120" y="625" font-family="Noto Sans CJK SC, sans-serif" font-size="14">每个色块均以合格 miss-admission 周期为分母；总柱高与柱顶百分比为整体 L2 准入阻塞率。</text></svg>');dr.text((120,610),'每个色块均以合格 miss-admission 周期为分母；总柱高与柱顶百分比为整体 L2 准入阻塞率。',fill='black',font=ft(14))
 (out/'FIG2_L2_STRUCTURAL_BLOCKING_NONZERO_CN_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(out/'FIG2_L2_STRUCTURAL_BLOCKING_NONZERO_CN_PAPER_DRAFT.png')
if __name__=='__main__':main()
