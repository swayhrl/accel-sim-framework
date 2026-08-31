#!/usr/bin/env python3
"""Fail-closed aggregate and two-panel figure generator for frozen EPL2SRV1 rows."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BINS=("<=8","9-16","17-32","33-64","65-128","129-256","257-512","513-1024","1025-2048","2049-4096",">4096")
KEYS=("sector_reuse_le8","sector_reuse_9_16","sector_reuse_17_32","sector_reuse_33_64","sector_reuse_65_128","sector_reuse_129_256","sector_reuse_257_512","sector_reuse_513_1024","sector_reuse_1025_2048","sector_reuse_2049_4096","sector_reuse_gt4096")
PRODUCTS=("motivation_summary.csv","reuse_distance.csv","reuse_coverage.csv","blocking_breakdown.csv","wbuf_lifetime.csv","wbuf_sensitivity.csv","post_eviction_reuse.csv")
COUNTS=("total_sector_reference_events","new_sector_on_new_line_events","new_sector_on_seen_line_events","temporal_sector_reuse_instances","unique_sector_identities","unique_sectors_reused_at_least_once","one_touch_unique_sectors",*KEYS)

def fail(s): raise SystemExit("FAIL-CLOSED: "+s)
def js(p):
 try: return json.loads(p.read_text())
 except Exception as e: fail(f"invalid JSON {p}: {e}")
def sha(p):
 h=hashlib.sha256()
 with p.open("rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()
def one(p):
 try: rows=list(csv.DictReader(p.open(newline="")))
 except OSError as e: fail(f"unreadable CSV {p}: {e}")
 if len(rows)!=1: fail(f"expected one row: {p}")
 return rows[0]
def eq(a,b,label):
 if a!=b: fail(f"{label}: expected {b!r}, got {a!r}")
def num(r,k,n):
 try: return int(r[k])
 except Exception as e: fail(f"invalid {k} for {n}: {e}")
def write(p,rows):
 if not rows: fail("empty aggregate")
 with p.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=sorted({k for r in rows for k in r}));w.writeheader();w.writerows(rows)

def validate(spec,c):
 n=spec["workload"]; root=Path(spec["on_result_dir"])
 if not root.is_dir(): fail(f"missing result {n}: {root}")
 status=js(root/"run_status.json"); campaign=js(root.parents[2]/"campaign_manifest.json")
 sm=js(root/"sector"/"manifest.json"); mm=js(root/"motivation"/"manifest.json")
 s=one(root/"sector"/"sector_reuse_summary.csv"); d=one(root/"sector"/"sector_reuse_distance.csv"); co=one(root/"sector"/"sector_reuse_coverage.csv"); m=one(root/"motivation"/"motivation_summary.csv")
 eq(status.get("status"),"COMPLETE_VALID",f"status {n}"); eq(status.get("workload"),n,f"status workload {n}"); eq(status.get("mode"),"on",f"mode {n}")
 eq(campaign.get("schema"),["EPL2MOTV1","EPL2SRV1"],f"campaign schema {n}")
 for k,v in (("core_commit",c["core_commit"]),("framework_commit",c["runtime_framework_commit"]),("config_sha256",c["config_sha256"])):
  eq(campaign.get(k),v,f"campaign {k} {n}");eq(status.get(k),v,f"status {k} {n}");eq(sm.get(k),v,f"sector {k} {n}");eq(mm.get(k),v,f"motivation {k} {n}")
 eq(sm.get("schema_version"),"EPL2SRV1",f"sector schema {n}");eq(mm.get("schema_version"),"EPL2MOTV1",f"motivation schema {n}")
 for r,label in ((s,"summary"),(d,"distance"),(co,"coverage"),(m,"motivation")): eq(r.get("workload"),n,f"{label} workload {n}")
 trace=Path(status.get("trace_id",""));eq(str(trace),spec["trace_id"],f"trace identity {n}")
 if not trace.is_file(): fail(f"trace absent {n}")
 eq(status.get("trace_kernelslist_sha256"),spec["trace_kernelslist_sha256"],f"trace status SHA {n}");eq(sha(trace),spec["trace_kernelslist_sha256"],f"trace filesystem SHA {n}")
 raw=status.get("raw_log_sha256");eq(sm.get("source_log_sha256"),raw,f"sector/raw pairing {n}");eq(mm.get("source_log_sha256"),raw,f"motivation/raw pairing {n}");eq(sha(root/"raw.log"),raw,f"raw digest {n}")
 for k in COUNTS: s[k]=num(s,k,n)
 total=s["total_sector_reference_events"]
 if s["new_sector_on_new_line_events"]+s["new_sector_on_seen_line_events"]+s["temporal_sector_reuse_instances"]!=total: fail(f"classification closure {n}")
 if sum(s[k] for k in KEYS)!=s["temporal_sector_reuse_instances"]: fail(f"distance closure {n}")
 for b,k in zip(BINS,KEYS):
  if num(d,k,n)!=s[k]: fail(f"distance CSV mismatch {n}/{b}")
 if num(co,"total_sector_reference_events",n)!=total: fail(f"coverage total mismatch {n}")
 eligible=num(m,"eligible_demand_references",n)
 if eligible<=0: fail(f"nonpositive eligible demand references {n}")
 s["eligible_demand_references"]=eligible;s["sector_events_per_demand_reference"]=total/eligible
 ref=Path(spec["motivation_reference"])
 for f in PRODUCTS:
  if not (root/"motivation"/f).is_file() or not (ref/f).is_file(): fail(f"missing Motivation compatibility product {n}/{f}")
  if sha(root/"motivation"/f)!=sha(ref/f): fail(f"Motivation compatibility mismatch {n}/{f}")
 return s,d,co,m

def fig(svg,png,rows):
 w,h=2200,1280; x0=115; span=1980; bar=max(18,min(46,(span//len(rows))-10));gap=(span-bar*len(rows))/len(rows)
 a=(("#9ecae1",(158,202,225)),("#74c476",(116,196,118)),("#756bb1",(117,107,177))); b=("#f7fbff","#deebf7","#c6dbef","#9ecae1","#6baed6","#4292c6","#2171b5","#084594","#fdae6b","#e6550d","#a63603")
 im=Image.new("RGB",(w,h),"white");dr=ImageDraw.Draw(im);ft=ImageFont.load_default();dr.text((40,25),"FIG1V2: spatial continuation is distinct from true 32-B sector temporal reuse",fill="black",font=ft);dr.text((70,95),"Panel A: locality type over all sector-reference events",fill="black",font=ft);dr.text((70,695),"Panel B: true-temporal reuse distance conditional on temporal reuse (N/A = NO TEMPORAL REUSE)",fill="black",font=ft)
 out=['<svg xmlns="http://www.w3.org/2000/svg" width="2200" height="1280"><rect width="100%" height="100%" fill="white"/><text x="40" y="48" font-family="sans-serif" font-size="30">FIG1V2: spatial continuation is distinct from true 32-B sector temporal reuse</text><text x="70" y="120" font-family="sans-serif" font-size="24" font-weight="bold">A. Locality type over all sector-reference events</text><text x="70" y="720" font-family="sans-serif" font-size="24" font-weight="bold">B. True-temporal reuse distance, conditional on temporal reuse</text>']
 for i,r in enumerate(rows):
  x=x0+i*(bar+gap); y=540
  for key,(sc,pc) in zip(("new_sector_on_new_line_events","new_sector_on_seen_line_events","temporal_sector_reuse_instances"),a):
   hh=420*r[key]/r["total_sector_reference_events"];y-=hh;out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar}" height="{hh:.1f}" fill="{sc}"/>');dr.rectangle((int(x),int(y),int(x+bar),int(y+hh)),fill=pc)
  out.append(f'<text x="{x+bar/2:.1f}" y="558" font-family="sans-serif" font-size="10" transform="rotate(-55 {x+bar/2:.1f} 558)">{r["workload"]}</text>');dr.text((int(x),548),r["workload"][:14],fill="black",font=ft)
  y=1140;t=r["temporal_sector_reuse_instances"]
  if not t: out.append(f'<rect x="{x:.1f}" y="1136" width="{bar}" height="4" fill="#bdbdbd"/><text x="{x+bar/2:.1f}" y="1128" text-anchor="middle" font-family="sans-serif" font-size="9">N/A</text>');dr.rectangle((int(x),1136,int(x+bar),1140),fill=(189,189,189));dr.text((int(x),1120),"N/A",fill="black",font=ft)
  else:
   for k,c in zip(KEYS,b):
    hh=420*r[k]/t;y-=hh;out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar}" height="{hh:.1f}" fill="{c}"/>');dr.rectangle((int(x),int(y),int(x+bar),int(y+hh)),fill=c)
  out.append(f'<text x="{x+bar/2:.1f}" y="1158" font-family="sans-serif" font-size="10" transform="rotate(-55 {x+bar/2:.1f} 1158)">{r["workload"]}</text>');dr.text((int(x),1148),r["workload"][:14],fill="black",font=ft)
 out.append('<text x="70" y="590" font-family="sans-serif" font-size="15">blue=cold/new-line; green=spatial continuation; purple=true temporal reuse</text><text x="70" y="1190" font-family="sans-serif" font-size="15">Exact 11 bins remain authoritative in CSV. Orange bins are &gt;1024; N/A is never normalized as a full bar.</text></svg>');dr.text((70,580),"blue=cold/new-line; green=spatial continuation; purple=true temporal reuse",fill="black",font=ft);dr.text((70,1180),"Exact 11 bins retained in CSV; orange bins are >1024; N/A is never normalized.",fill="black",font=ft)
 svg.write_text("\n".join(out));im.save(png)

def supplemental(svg,png,rows):
 im=Image.new("RGB",(1800,620),"white");dr=ImageDraw.Draw(im);ft=ImageFont.load_default();dr.text((40,25),"FIG1S: line reuse versus true sector temporal reuse",fill="black",font=ft);out=['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="620"><rect width="100%" height="100%" fill="white"/><text x="40" y="45" font-family="sans-serif" font-size="28">FIG1S: line reuse versus true sector temporal reuse</text>']
 for i,r in enumerate(rows):
  x=150+i*110
  for dx,v,c in ((0,float(r["line_reuse_fraction"]),"#3182bd"),(42,float(r["sector_temporal_reuse_fraction"]),"#756bb1")):
   y=520-380*v;out.append(f'<rect x="{x+dx}" y="{y:.1f}" width="34" height="{380*v:.1f}" fill="{c}"/>');dr.rectangle((x+dx,int(y),x+dx+34,520),fill=c)
  out.append(f'<text x="{x+38}" y="550" text-anchor="middle" font-family="sans-serif" font-size="12">{r["workload"]}</text>');dr.text((x,540),r["workload"][:13],fill="black",font=ft)
 out.append('<text x="150" y="595" font-family="sans-serif" font-size="16">blue=line-level reuse fraction; purple=true sector temporal-reuse fraction</text></svg>');dr.text((150,590),"blue=line-level reuse fraction; purple=true sector temporal-reuse fraction",fill="black",font=ft);svg.write_text("\n".join(out));im.save(png)

def main():
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);p.add_argument("--formal-spec",type=Path,required=True);a=p.parse_args()
 if a.out.exists(): fail(f"refusing to overwrite output root: {a.out}")
 c=js(a.formal_spec)
 for k in ("schema","core_commit","runtime_framework_commit","config_sha256","expected_workloads","rows"):
  if k not in c: fail(f"formal spec missing {k}")
 eq(c["schema"],"EPL2SRV1","formal spec schema"); names=[r.get("workload") for r in c["rows"]]
 if len(names)!=len(set(names)): fail("duplicate workload")
 if len(names)!=len(c["expected_workloads"]) or set(names)!=set(c["expected_workloads"]): fail("exact formal workload set failure")
 a.out.mkdir(parents=True);ss=[];dd=[];cc=[];ll=[];rr=[]
 for spec in c["rows"]:
  s,d,co,m=validate(spec,c);ss.append(s);dd.append(d);cc.append(co);n=spec["workload"];ll.append({"workload":n,"line_reuse_fraction":int(m["reuse_instances"])/int(m["eligible_demand_references"]),"sector_temporal_reuse_fraction":s["sector_temporal_reuse_fraction"],"spatial_new_sector_fraction":s["spatial_new_sector_fraction"],"one_touch_sector_fraction":s["one_touch_sector_fraction"]});rr.append({"workload":n,"eligible_demand_references":s["eligible_demand_references"],"total_sector_reference_events":s["total_sector_reference_events"],"sector_events_per_demand_reference":s["sector_events_per_demand_reference"]})
 for rows,fn in ((ss,"sector_reuse_summary.csv"),(dd,"sector_reuse_distance.csv"),(cc,"sector_reuse_coverage.csv"),(ll,"line_vs_sector_reuse.csv"),(rr,"demand_sector_ratio.csv")): write(a.out/fn,rows)
 (a.out/"aggregation_manifest.json").write_text(json.dumps({"schema":"EPL2SRV1","formal_spec_sha256":sha(a.formal_spec),"inputs":c["rows"],"count_aggregation":True,"fail_closed":True},indent=2,sort_keys=True)+"\n")
 f=a.out/"figures";f.mkdir();fig(f/"FIG1V2_L2_SECTOR_TEMPORAL_REUSE.svg",f/"FIG1V2_L2_SECTOR_TEMPORAL_REUSE.png",ss);supplemental(f/"FIG1S_LINE_VS_SECTOR_REUSE.svg",f/"FIG1S_LINE_VS_SECTOR_REUSE.png",ll)
if __name__=="__main__": main()
