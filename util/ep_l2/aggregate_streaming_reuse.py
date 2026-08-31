#!/usr/bin/env python3
"""Count-aggregate frozen EPL2SRV1 rows and render the review figures."""
import argparse, csv, json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BINS=("<=8","9-16","17-32","33-64","65-128","129-256","257-512","513-1024","1025-2048","2049-4096",">4096")
KEYS=("sector_reuse_le8","sector_reuse_9_16","sector_reuse_17_32","sector_reuse_33_64","sector_reuse_65_128","sector_reuse_129_256","sector_reuse_257_512","sector_reuse_513_1024","sector_reuse_1025_2048","sector_reuse_2049_4096","sector_reuse_gt4096")
COUNTS=("total_sector_reference_events","new_sector_on_new_line_events","new_sector_on_seen_line_events","temporal_sector_reuse_instances","unique_sector_identities","unique_sectors_reused_at_least_once","one_touch_unique_sectors",*KEYS)
def readone(path):
    return next(csv.DictReader(path.open()))
def write(path, rows):
    fields=sorted({k for row in rows for k in row})
    with path.open("w",newline="") as f:
        out=csv.DictWriter(f,fieldnames=fields);out.writeheader();out.writerows(rows)
def ratio(n,d): return n/d if d else "NA"
def svg(path, title, rows, sector=True):
    w,h=1600,640; x0,y0=180,90; bw=80; gap=26
    text=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',f'<rect width="100%" height="100%" fill="white"/><text x="40" y="45" font-family="sans-serif" font-size="28">{title}</text>']
    for i,row in enumerate(rows):
        x=x0+i*(bw+gap); total=int(row["total_sector_reference_events"]); vals=(int(row["new_sector_on_new_line_events"]),int(row["new_sector_on_seen_line_events"]),int(row["temporal_sector_reuse_instances"]))
        colors=("#9ecae1","#74c476","#756bb1"); y=520
        for val,c in zip(vals,colors):
            hh=380*val/total if total else 0;y-=hh;text.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{hh:.1f}" fill="{c}"/>')
        text.append(f'<text x="{x+bw/2}" y="550" text-anchor="middle" font-family="sans-serif" font-size="13" transform="rotate(35 {x+bw/2} 550)">{row["workload"]}</text>')
        text.append(f'<text x="{x+bw/2}" y="{y-8:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">T={float(row["sector_temporal_reuse_fraction"]):.2f}</text>')
    text.append('<text x="180" y="600" font-family="sans-serif" font-size="16" fill="#9ecae1">cold new-line</text><text x="410" y="600" font-family="sans-serif" font-size="16" fill="#74c476">spatial continuation</text><text x="650" y="600" font-family="sans-serif" font-size="16" fill="#756bb1">true temporal reuse</text></svg>')
    path.write_text("\n".join(text))
def png(path, title, rows):
    im=Image.new("RGB",(1600,640),"white");d=ImageDraw.Draw(im);font=ImageFont.load_default();d.text((40,25),title,fill="black",font=font)
    x0=180
    for i,r in enumerate(rows):
        x=x0+i*106; total=int(r["total_sector_reference_events"]); y=520
        for v,c in zip((int(r["new_sector_on_new_line_events"]),int(r["new_sector_on_seen_line_events"]),int(r["temporal_sector_reuse_instances"])),((158,202,225),(116,196,118),(117,107,177))):
            hh=int(380*v/total) if total else 0;y-=hh;d.rectangle((x,y,x+80,y+hh),fill=c)
        d.text((x,540),r["workload"][:12],fill="black",font=font);d.text((x,y-14),"T=%.2f"%float(r["sector_temporal_reuse_fraction"]),fill="black",font=font)
    d.text((180,600),"cold new-line   spatial continuation   true temporal reuse",fill="black",font=font);im.save(path)
def supplemental(svg_path, png_path, rows):
    w,h=1600,640; x0=180; parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="640"><rect width="100%" height="100%" fill="white"/><text x="40" y="45" font-family="sans-serif" font-size="28">FIG1S: line reuse versus true sector temporal reuse</text>']
    im=Image.new("RGB",(w,h),"white");d=ImageDraw.Draw(im);font=ImageFont.load_default();d.text((40,25),"FIG1S: line reuse versus true sector temporal reuse",fill="black",font=font)
    for i,r in enumerate(rows):
        x=x0+i*106; line=float(r['line_reuse_fraction']) if r['line_reuse_fraction']!='NA' else 0; sector=float(r['sector_temporal_reuse_fraction']) if r['sector_temporal_reuse_fraction']!='NA' else 0
        for dx,v,c in ((0,line,'#3182bd'),(42,sector,'#756bb1')):
            hh=380*v;y=520-hh;parts.append(f'<rect x="{x+dx}" y="{y:.1f}" width="34" height="{hh:.1f}" fill="{c}"/>');imc=(49,130,189) if dx==0 else (117,107,177);d.rectangle((x+dx,y,x+dx+34,520),fill=imc)
        parts.append(f'<text x="{x+38}" y="550" text-anchor="middle" font-family="sans-serif" font-size="13">{r["workload"]}</text>');d.text((x,540),r['workload'][:12],fill="black",font=font)
    parts.append('<text x="180" y="600" font-family="sans-serif" font-size="16" fill="#3182bd">line-level reuse fraction</text><text x="500" y="600" font-family="sans-serif" font-size="16" fill="#756bb1">true sector temporal-reuse fraction</text></svg>')
    svg_path.write_text("\n".join(parts));d.text((180,600),"blue: line-level reuse fraction   purple: true sector temporal-reuse fraction",fill="black",font=font);im.save(png_path)
def main():
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);p.add_argument("--input",nargs="+",required=True,help="workload=on-result-directory");a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 summary=[];distance=[];coverage=[];line=[];manifest=[]
 for spec in a.input:
  name,root=spec.split("=",1);root=Path(root); s=readone(root/"sector/sector_reuse_summary.csv");d=readone(root/"sector/sector_reuse_distance.csv");c=readone(root/"sector/sector_reuse_coverage.csv");m=readone(root/"motivation/motivation_summary.csv")
  if s["workload"]!=name or m["workload"]!=name: raise SystemExit("workload mismatch: "+name)
  for k in COUNTS:s[k]=int(s[k])
  if s["new_sector_on_new_line_events"]+s["new_sector_on_seen_line_events"]+s["temporal_sector_reuse_instances"]!=s["total_sector_reference_events"]:raise SystemExit("classification closure: "+name)
  if sum(s[k] for k in KEYS)!=s["temporal_sector_reuse_instances"]:raise SystemExit("distance closure: "+name)
  summary.append(s);distance.append(d);coverage.append(c);line.append({"workload":name,"line_reuse_fraction":ratio(int(m["reuse_instances"]),int(m["eligible_demand_references"])),"sector_temporal_reuse_fraction":s["sector_temporal_reuse_fraction"],"spatial_new_sector_fraction":s["spatial_new_sector_fraction"],"one_touch_sector_fraction":s["one_touch_sector_fraction"]});manifest.append({"workload":name,"on_result_dir":str(root),"sector_manifest":json.loads((root/"sector/manifest.json").read_text())})
 for rows,name in ((summary,"sector_reuse_summary.csv"),(distance,"sector_reuse_distance.csv"),(coverage,"sector_reuse_coverage.csv"),(line,"line_vs_sector_reuse.csv")):write(a.out/name,rows)
 (a.out/"aggregation_manifest.json").write_text(json.dumps({"schema":"EPL2SRV1","inputs":manifest,"count_aggregation":True},indent=2,sort_keys=True)+"\n")
 fig=a.out/"figures";fig.mkdir(exist_ok=True);svg(fig/"FIG1V2_L2_SECTOR_TEMPORAL_REUSE.svg","FIG1V2: sector temporal reuse",summary);png(fig/"FIG1V2_L2_SECTOR_TEMPORAL_REUSE.png","FIG1V2: sector temporal reuse",summary);supplemental(fig/"FIG1S_LINE_VS_SECTOR_REUSE.svg",fig/"FIG1S_LINE_VS_SECTOR_REUSE.png",line)
if __name__=="__main__":main()
