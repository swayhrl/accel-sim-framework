#!/usr/bin/env python3
"""CSV-only, reproducible paper-style redraw for the Streaming-Reuse draft."""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT.parents[0] / "DRAFT_FIGURES_CHECKPOINT_r1" / "plotting_tables"
OUT = ROOT / "figures"; TABLES = ROOT / "plotting_tables"
ORDER = ["vectorAdd_4M", "BlackScholes", "dwt2d", "convolutionSeparable", "mergeSort", "sad", "spmv", "transpose", "scan", "FWT_7_21", "cfd_097k", "btree", "gemm"]
GROUPS = [(0, 2, "Streaming / Spatial"), (2, 9, "Low Temporal Reuse"), (9, 13, "Reuse Rich")]
BINS = ["<=8", "9-16", "17-32", "33-64", "65-128", "129-256", "257-512", "513-1024", "1025-2048", "2049-4096", ">4096"]
BIN_COLORS = ["#1f5a85", "#2d78a8", "#4d97bc", "#77b3ca", "#9bc9d6", "#c1d9da", "#eadba6", "#f4be72", "#ea944e", "#cf6534", "#9f3d28"]
LOCAL_COLORS = ["#8fbcd4", "#6cae83", "#7c6aa7"]
BLOCK_COLORS = ["#c74c4c", "#4f7fb8", "#73a85f", "#8c6baa", "#9b9b9b"]
FONT = ImageFont.load_default()

def read(name):
    with (INPUT / name).open(newline="") as f: return list(csv.DictReader(f))
def num(x): return float(x)
def write(name, rows):
    with (TABLES / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;")

def base_svg(w, h): return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>']
def axis(svg, dr, x0, y0, width, height, ylabel, ymax=1.0):
    svg += [f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0-height}" stroke="black" stroke-width="1.5"/>', f'<line x1="{x0}" y1="{y0}" x2="{x0+width}" y2="{y0}" stroke="black" stroke-width="1.5"/>', f'<text x="28" y="{y0-height/2}" font-family="sans-serif" font-size="16" transform="rotate(-90 28 {y0-height/2})">{esc(ylabel)}</text>']
    for p in range(0, 101, 20):
        y=y0-height*p/100; svg.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+width}" y2="{y:.1f}" stroke="#d0d0d0" stroke-dasharray="5,5"/>'); svg.append(f'<text x="{x0-10}" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{p}</text>'); dr.line((x0,y,x0+width,y),fill=(208,208,208),width=1); dr.text((x0-28,y-5),str(p),fill="black",font=FONT)
def legend(svg, dr, items, colors, x=145, y=32, step=145):
    for i,(label,color) in enumerate(zip(items,colors)):
        xx=x+i*step; svg.append(f'<rect x="{xx}" y="{y-10}" width="14" height="14" fill="{color}" stroke="#333" stroke-width="0.5"/><text x="{xx+20}" y="{y+1}" font-family="sans-serif" font-size="12">{esc(label)}</text>'); dr.rectangle((xx,y-10,xx+14,y+4),fill=color,outline=(51,51,51)); dr.text((xx+20,y-9),label,fill="black",font=FONT)
def groups(svg, dr, xs, y, n):
    for a,b,label in GROUPS:
        mid=(xs[a]+xs[b-1])/2; svg.append(f'<text x="{mid:.1f}" y="{y}" text-anchor="middle" font-family="sans-serif" font-size="14">{label}</text>'); dr.text((mid-len(label)*3,y-7),label,fill="black",font=FONT)
        if b<n: x=(xs[b-1]+xs[b])/2; svg.append(f'<line x1="{x:.1f}" y1="110" x2="{x:.1f}" y2="{y-34}" stroke="#999" stroke-dasharray="4,4"/>'); dr.line((x,110,x,y-34),fill=(153,153,153),width=1)

def temporal_distance(A, B):
    amap={r['workload']:r for r in A}; bmap={}
    for r in B: bmap.setdefault(r['workload'],[]).append(r)
    w,h=1780,820;x0,y0,pw,ph=105,650,1590,500; bar=58; step=pw/len(ORDER); xs=[x0+step*(i+.5) for i in range(len(ORDER))]
    im=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(im);svg=base_svg(w,h);legend(svg,dr,BINS,BIN_COLORS,x=130,y=37,step=140);axis(svg,dr,x0,y0,pw,ph,'Fraction of temporal reuse (%)')
    for x,name in zip(xs,ORDER):
        a=amap[name]; temp=num(a['true_temporal_sector_reuse_events']);
        if not temp:
            svg.append(f'<rect x="{x-bar/2:.1f}" y="{y0-ph}" width="{bar}" height="{ph}" fill="#fafafa" stroke="#bbb" stroke-dasharray="3,3"/><text x="{x:.1f}" y="{y0-ph/2}" text-anchor="middle" font-family="sans-serif" font-size="11">No temporal</text><text x="{x:.1f}" y="{y0-ph/2+14}" text-anchor="middle" font-family="sans-serif" font-size="11">reuse</text>'); dr.rectangle((x-bar/2,y0-ph,x+bar/2,y0),outline=(187,187,187));dr.text((x-bar/2,y0-ph/2),'N/A',fill='black',font=FONT)
        else:
            y=y0
            by={q['distance_bin']:q for q in bmap[name]}
            for label,c in zip(BINS,BIN_COLORS):
                hh=ph*num(by[label]['conditional_fraction']); y-=hh; svg.append(f'<rect x="{x-bar/2:.1f}" y="{y:.1f}" width="{bar}" height="{hh:.1f}" fill="{c}" stroke="#333" stroke-width="0.35"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(51,51,51))
            svg.append(f'<text x="{x:.1f}" y="{y-9:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">T={num(a["temporal_fraction"]):.2f}</text>');dr.text((x-18,y-19),f'T={num(a["temporal_fraction"]):.2f}',fill='black',font=FONT)
        svg.append(f'<text x="{x:.1f}" y="{y0+20}" text-anchor="end" font-family="sans-serif" font-size="12" transform="rotate(-25 {x:.1f} {y0+20})">{name}</text>');dr.text((x-25,y0+10),name[:14],fill='black',font=FONT)
    groups(svg,dr,xs,y0+135,len(ORDER)); svg.append('<text x="70" y="88" font-family="sans-serif" font-size="17">(a)</text></svg>');dr.text((70,76),'(a)',fill='black',font=FONT)
    (OUT/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(OUT/'FIG1_L2_TEMPORAL_REUSE_DISTANCE_PAPER_DRAFT.png')

def locality(A):
    amap={r['workload']:r for r in A};w,h=1780,820;x0,y0,pw,ph=105,650,1590,500;bar=58;step=pw/len(ORDER);xs=[x0+step*(i+.5) for i in range(len(ORDER))];labs=['Cold new-line sector','Spatial continuation','True temporal sector reuse']
    im=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(im);svg=base_svg(w,h);legend(svg,dr,labs,LOCAL_COLORS,x=230,y=37,step=225);axis(svg,dr,x0,y0,pw,ph,'Fraction of sector references (%)')
    for x,name in zip(xs,ORDER):
        a=amap[name]; y=y0
        for key,c in zip(['cold_fraction','spatial_fraction','temporal_fraction'],LOCAL_COLORS):
            hh=ph*num(a[key]);y-=hh;svg.append(f'<rect x="{x-bar/2:.1f}" y="{y:.1f}" width="{bar}" height="{hh:.1f}" fill="{c}" stroke="#333" stroke-width="0.35"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(51,51,51))
        svg.append(f'<text x="{x:.1f}" y="{y0+20}" text-anchor="end" font-family="sans-serif" font-size="12" transform="rotate(-25 {x:.1f} {y0+20})">{name}</text>');dr.text((x-25,y0+10),name[:14],fill='black',font=FONT)
    groups(svg,dr,xs,y0+135,len(ORDER));svg.append('<text x="70" y="88" font-family="sans-serif" font-size="17">(b)</text></svg>');dr.text((70,76),'(b)',fill='black',font=FONT)
    (OUT/'FIG1S_L2_LOCALITY_TYPE_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(OUT/'FIG1S_L2_LOCALITY_TYPE_PAPER_DRAFT.png')

def blocking(F):
    fmap={r['workload']:r for r in F};w,h=1780,820;x0,y0,pw,ph=105,650,1590,500;bar=58;step=pw/len(ORDER);xs=[x0+step*(i+.5) for i in range(len(ORDER))];labs=['SET_ASSOC','MSHR_META','MISSQ_LOWER','WB_PATH','OTHER']
    im=Image.new('RGB',(w,h),'white');dr=ImageDraw.Draw(im);svg=base_svg(w,h);legend(svg,dr,labs,BLOCK_COLORS,x=270,y=37,step=180);axis(svg,dr,x0,y0,pw,ph,'L2 admission blocked cycles (%)')
    for x,name in zip(xs,ORDER):
        r=fmap[name];y=y0
        for key,c in zip(labs,BLOCK_COLORS):
            hh=ph*num(r[key+'_fraction_of_eligible']);y-=hh;svg.append(f'<rect x="{x-bar/2:.1f}" y="{y:.1f}" width="{bar}" height="{hh:.1f}" fill="{c}" stroke="#333" stroke-width="0.35"/>');dr.rectangle((x-bar/2,y,x+bar/2,y+hh),fill=c,outline=(51,51,51))
        rate=num(r['overall_blocking_rate']);svg.append(f'<text x="{x:.1f}" y="{y-9:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{rate:.1%}</text><text x="{x:.1f}" y="{y0+20}" text-anchor="end" font-family="sans-serif" font-size="12" transform="rotate(-25 {x:.1f} {y0+20})">{name}</text>');dr.text((x-18,y-19),f'{rate:.1%}',fill='black',font=FONT);dr.text((x-25,y0+10),name[:14],fill='black',font=FONT)
    groups(svg,dr,xs,y0+135,len(ORDER));svg.append('</svg>');(OUT/'FIG2_L2_STRUCTURAL_BLOCKING_PAPER_DRAFT.svg').write_text('\n'.join(svg));im.save(OUT/'FIG2_L2_STRUCTURAL_BLOCKING_PAPER_DRAFT.png')

def main():
    OUT.mkdir(parents=True,exist_ok=True);TABLES.mkdir(exist_ok=True)
    A,B,S,F=[read(x) for x in ['FIG1V2_PANEL_A.csv','FIG1V2_PANEL_B.csv','FIG1S_LINE_VS_SECTOR.csv','FIG2_WBUF8_BLOCKING.csv']]
    for name,rows in [('FIG1_L2_TEMPORAL_REUSE_DISTANCE_PAPER_DRAFT.csv',[r for w in ORDER for r in B if r['workload']==w]),('FIG1S_L2_LOCALITY_TYPE_PAPER_DRAFT.csv',[next(r for r in A if r['workload']==w) for w in ORDER]),('FIG2_L2_STRUCTURAL_BLOCKING_PAPER_DRAFT.csv',[next(r for r in F if r['workload']==w) for w in ORDER])]: write(name,rows)
    temporal_distance(A,B); locality(A); blocking(F)
if __name__=='__main__': main()
