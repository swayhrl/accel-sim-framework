#!/usr/bin/env python3
"""Fail-closed Stage-6 aggregation and portable SVG/PNG figure generation.

The input is one parser-produced ON directory per required workload.  This
script deliberately revalidates manifests and exclusive accounting before it
emits a paper-facing table or figure.  It uses only the standard library and
Pillow so the review artifact is reproducible on the runner image.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as err:
    raise SystemExit("Pillow is required to create PNG review figures: %s" % err)

WORKLOADS = ("scan", "vectorAdd_4M", "convolutionSeparable", "spmv",
             "FWT_7_21", "cfd_097k", "dwt2d", "sad", "btree", "gemm")
BINS = ("<=8", "9-16", "17-32", "33-64", "65-128", "129-256",
        "257-512", "513-1024", ">1024")
CATS = ("set_assoc", "mshr_meta", "missq_lower", "wb_path", "other")
COLORS = ("#4C78A8", "#72B7B2", "#F58518", "#E45756", "#54A24B",
          "#B279A2", "#FF9DA6", "#9D755D", "#BAB0AC")
CAT_COLORS = {"set_assoc": "#4C78A8", "mshr_meta": "#F58518",
              "missq_lower": "#E45756", "wb_path": "#72B7B2",
              "other": "#B279A2"}

def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)

def write_tsv(path, rows):
    fields = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
        writer.writeheader(); writer.writerows(rows)

def number(value):
    return float(value) if value not in ("", "NA", None) else math.nan

def integer(value):
    return int(value)

def svg_text(x, y, value, size=13, anchor="start", weight="normal"):
    return '<text x="%.1f" y="%.1f" text-anchor="%s" font-family="Arial,sans-serif" font-size="%d" font-weight="%s">%s</text>' % (x, y, anchor, size, weight, escape(str(value)))

def svg_rect(x, y, w, h, color, stroke="none"):
    return '<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="%s"/>' % (x, y, w, h, color, stroke)

def save_svg_png(stem, width, height, svg_lines, painter):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (width, height, width, height),
           svg_rect(0, 0, width, height, "white")]
    svg.extend(svg_lines); svg.append("</svg>")
    stem.with_suffix(".svg").write_text("\n".join(svg) + "\n")
    image = Image.new("RGB", (width, height), "white")
    painter(ImageDraw.Draw(image))
    image.save(stem.with_suffix(".png"))

def font(size, bold=False):
    candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else ""),
                  "/usr/share/fonts/truetype/liberation2/LiberationSans%s.ttf" % ("-Bold" if bold else "-Regular")]
    for candidate in candidates:
        if Path(candidate).exists(): return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()

def draw_label(draw, xy, text, size=13, fill="black", anchor="la", bold=False):
    draw.text(xy, str(text), font=font(size, bold), fill=fill, anchor=anchor)

def make_fig1(rows, out):
    width, height, left, right, top, bottom = 1500, 760, 90, 30, 100, 180
    plot_w, plot_h = width-left-right, height-top-bottom
    svg = [svg_text(width/2, 36, "Figure 1. Exact bounded L2 reuse-distance distribution", 22, "middle", "bold"),
           svg_text(width/2, 62, "Frontend L2 demand references; epoch-local, 128-B distinct-block stack distance", 14, "middle"),
           '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black"/>' % (left, top+plot_h, left+plot_w, top+plot_h),
           '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black"/>' % (left, top, left, top+plot_h)]
    canvas = []
    for tick in range(0, 101, 20):
        y = top + plot_h - plot_h*tick/100
        svg += ['<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#dddddd"/>' % (left, y, left+plot_w, y), svg_text(left-10, y+5, "%d%%" % tick, 12, "end")]
    for idx, row in enumerate(rows):
        x = left + plot_w*(idx+.5)/len(rows); bar_w=plot_w/len(rows)*.65; cursor=top+plot_h
        for bi, key in enumerate(BINS):
            h=plot_h*number(row[key]); cursor-=h; svg.append(svg_rect(x-bar_w/2,cursor,bar_w,h,COLORS[bi]))
        svg.append(svg_text(x, top+plot_h+20, row["workload"], 12, "end").replace('text-anchor="end"','text-anchor="end" transform="rotate(-35 %.1f %.1f)"' % (x, top+plot_h+20)))
    for bi, key in enumerate(BINS):
        lx=left+(bi%5)*260; ly=height-85+(bi//5)*28
        svg += [svg_rect(lx,ly-12,16,16,COLORS[bi]), svg_text(lx+22,ly,key,12)]
    svg.append(svg_text(23, top+plot_h/2, "fraction of reuse instances", 13, "middle").replace('text-anchor="middle"','text-anchor="middle" transform="rotate(-90 23 %.1f)"' % (top+plot_h/2)))
    def painter(d):
        draw_label(d,(width/2,36),"Figure 1. Exact bounded L2 reuse-distance distribution",22,anchor="ma",bold=True); draw_label(d,(width/2,62),"Frontend L2 demand references; epoch-local, 128-B distinct-block stack distance",14,anchor="ma")
        d.line((left,top,left,top+plot_h),fill="black");d.line((left,top+plot_h,left+plot_w,top+plot_h),fill="black")
        for tick in range(0,101,20):
            y=top+plot_h-plot_h*tick/100;d.line((left,y,left+plot_w,y),fill="#dddddd");draw_label(d,(left-10,y),"%d%%"%tick,12,anchor="ra")
        for idx,row in enumerate(rows):
            x=left+plot_w*(idx+.5)/len(rows);bw=plot_w/len(rows)*.65;cur=top+plot_h
            for bi,key in enumerate(BINS):
                h=plot_h*number(row[key]);cur-=h;d.rectangle((x-bw/2,cur,x+bw/2,cur+h),fill=COLORS[bi])
            draw_label(d,(x,top+plot_h+20),row["workload"],12,anchor="ra")
        for bi,key in enumerate(BINS):
            lx=left+(bi%5)*260;ly=height-85+(bi//5)*28;d.rectangle((lx,ly-12,lx+16,ly+4),fill=COLORS[bi]);draw_label(d,(lx+22,ly),key,12,anchor="la")
        draw_label(d,(23,top+plot_h/2),"fraction of reuse instances",13,anchor="ma")
    save_svg_png(out / "FIG1_L2_REUSE_DISTANCE_STACKED", width, height, svg, painter)

def make_fig2(rows, out):
    width,height,left,right,top,bottom=1500,760,90,30,100,180; pw,ph=width-left-right,height-top-bottom
    svg=[svg_text(width/2,36,"Figure 2. Exclusive primary frontend demand-miss admission blockers (WBUF=8)",22,"middle","bold"),svg_text(width/2,62,"Source-ordered classification; each eligible blocked cycle has at most one primary blocker",14,"middle"),'<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black"/>'%(left,top+ph,left+pw,top+ph),'<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black"/>'%(left,top,left,top+ph)]
    for tick in range(0,101,20):
        y=top+ph-ph*tick/100;svg += ['<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#dddddd"/>'%(left,y,left+pw,y),svg_text(left-10,y+5,"%d%%"%tick,12,"end")]
    for i,row in enumerate(rows):
        x=left+pw*(i+.5)/len(rows);bw=pw/len(rows)*.65;cur=top+ph;den=integer(row["projected_blocked_miss_admission_cycles"])
        for cat in CATS:
            h=ph*(integer(row[cat])/den if den else 0);cur-=h;svg.append(svg_rect(x-bw/2,cur,bw,h,CAT_COLORS[cat]))
        svg.append(svg_text(x,top+ph+20,row["workload"],12,"end").replace('text-anchor="end"','text-anchor="end" transform="rotate(-35 %.1f %.1f)"'%(x,top+ph+20)))
    for i,cat in enumerate(CATS):
        lx=left+i*245;ly=height-55;svg += [svg_rect(lx,ly-12,16,16,CAT_COLORS[cat]),svg_text(lx+22,ly,cat.upper(),12)]
    def painter(d):
        draw_label(d,(width/2,36),"Figure 2. Exclusive primary frontend demand-miss admission blockers (WBUF=8)",22,anchor="ma",bold=True);draw_label(d,(width/2,62),"Source-ordered classification; each eligible blocked cycle has at most one primary blocker",14,anchor="ma")
        d.line((left,top,left,top+ph),fill="black");d.line((left,top+ph,left+pw,top+ph),fill="black")
        for tick in range(0,101,20):
            y=top+ph-ph*tick/100;d.line((left,y,left+pw,y),fill="#dddddd");draw_label(d,(left-10,y),"%d%%"%tick,12,anchor="ra")
        for i,row in enumerate(rows):
            x=left+pw*(i+.5)/len(rows);bw=pw/len(rows)*.65;cur=top+ph;den=integer(row["projected_blocked_miss_admission_cycles"])
            for cat in CATS:
                h=ph*(integer(row[cat])/den if den else 0);cur-=h;d.rectangle((x-bw/2,cur,x+bw/2,cur+h),fill=CAT_COLORS[cat])
            draw_label(d,(x,top+ph+20),row["workload"],12,anchor="ra")
        for i,cat in enumerate(CATS):
            lx=left+i*245;ly=height-55;d.rectangle((lx,ly-12,lx+16,ly+4),fill=CAT_COLORS[cat]);draw_label(d,(lx+22,ly),cat.upper(),12,anchor="la")
    save_svg_png(out / "FIG2_L2_BLOCKING_BREAKDOWN_WBUF8",width,height,svg,painter)

def make_fig2s(rows, out):
    width,height,left,right,top,bottom=1500,760,90,30,100,180;pw,ph=width-left-right,height-top-bottom
    maximum=max(integer(r["wbuf_trace_projected_would_block_cycles"]) for r in rows) or 1
    ymax=10**math.ceil(math.log10(maximum)); ymax=max(ymax, maximum*1.1)
    svg=[svg_text(width/2,36,"Figure 2S. Trace-projected WBUF capacity-pressure sensitivity",22,"middle","bold"),svg_text(width/2,62,"Same workload run; C=4/8/16 are shadow capacity views, not performance counterfactuals",14,"middle"),'<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black"/>'%(left,top+ph,left+pw,top+ph),'<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="black"/>'%(left,top,left,top+ph)]
    for tick in range(0,6):
        v=ymax*tick/5;y=top+ph-ph*tick/5;svg += ['<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#dddddd"/>'%(left,y,left+pw,y),svg_text(left-10,y+5,"%.0f"%v,12,"end")]
    caps=("4","8","16")
    for i,w in enumerate(WORKLOADS):
        group=[r for r in rows if r["workload"]==w];x=left+pw*(i+.5)/len(WORKLOADS);bw=pw/len(WORKLOADS)*.18
        for j,cap in enumerate(caps):
            row=next(r for r in group if r["wbuf_capacity"]==cap);h=ph*integer(row["wbuf_trace_projected_would_block_cycles"])/ymax;svg.append(svg_rect(x+(j-1)*bw-bw/2,top+ph-h,bw,h,COLORS[j]))
        svg.append(svg_text(x,top+ph+20,w,12,"end").replace('text-anchor="end"','text-anchor="end" transform="rotate(-35 %.1f %.1f)"'%(x,top+ph+20)))
    for j,cap in enumerate(caps):
        lx=left+j*170;ly=height-55;svg += [svg_rect(lx,ly-12,16,16,COLORS[j]),svg_text(lx+22,ly,"WBUF=%s"%cap,12)]
    def painter(d):
        draw_label(d,(width/2,36),"Figure 2S. Trace-projected WBUF capacity-pressure sensitivity",22,anchor="ma",bold=True);draw_label(d,(width/2,62),"Same workload run; C=4/8/16 are shadow capacity views, not performance counterfactuals",14,anchor="ma")
        d.line((left,top,left,top+ph),fill="black");d.line((left,top+ph,left+pw,top+ph),fill="black")
        for tick in range(6):
            v=ymax*tick/5;y=top+ph-ph*tick/5;d.line((left,y,left+pw,y),fill="#dddddd");draw_label(d,(left-10,y),"%.0f"%v,12,anchor="ra")
        for i,w in enumerate(WORKLOADS):
            group=[r for r in rows if r["workload"]==w];x=left+pw*(i+.5)/len(WORKLOADS);bw=pw/len(WORKLOADS)*.18
            for j,cap in enumerate(("4","8","16")):
                row=next(r for r in group if r["wbuf_capacity"]==cap);h=ph*integer(row["wbuf_trace_projected_would_block_cycles"])/ymax;d.rectangle((x+(j-1)*bw-bw/2,top+ph-h,x+(j-1)*bw+bw/2,top+ph),fill=COLORS[j])
            draw_label(d,(x,top+ph+20),w,12,anchor="ra")
        for j,cap in enumerate(("4","8","16")):
            lx=left+j*170;ly=height-55;d.rectangle((lx,ly-12,lx+16,ly+4),fill=COLORS[j]);draw_label(d,(lx+22,ly),"WBUF=%s"%cap,12,anchor="la")
    save_svg_png(out / "FIG2S_WBUF_4_8_16_SENSITIVITY",width,height,svg,painter)

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",required=True,type=Path);ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--framework-commit",required=True);ap.add_argument("--core-commit",required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True);fig=args.out/"figures";fig.mkdir(exist_ok=True)
    tables={"motivation_summary":[],"reuse_distance":[],"reuse_coverage":[],"blocking_breakdown":[],"wbuf_sensitivity":[],"post_eviction_reuse":[],"wbuf_lifetime":[]}; raw_index=[];status=[]
    for workload in WORKLOADS:
        source=args.root/workload/"on";manifest=json.loads((source/"manifest.json").read_text())
        if manifest.get("workload")!=workload or manifest.get("framework_commit")!=args.framework_commit or manifest.get("core_commit")!=args.core_commit: raise SystemExit("provenance mismatch for "+workload)
        for table in tables:
            rows=read_csv(source/(table+".csv")); tables[table].extend(rows)
        summary=tables["motivation_summary"][-1]
        if integer(summary["wb_packets_created"]) != integer(summary["wb_packets_lower_accepted"]) or integer(summary["wb_active_at_snapshot"]): raise SystemExit("open terminal WBUF lifecycle for "+workload)
        for cap in ("4","8","16"):
            subset=[r for r in tables["blocking_breakdown"] if r["workload"]==workload and r["wbuf_capacity"]==cap][0]
            if sum(integer(subset[x]) for x in CATS)!=integer(subset["projected_blocked_miss_admission_cycles"]): raise SystemExit("nonexclusive blockers for "+workload+" WBUF="+cap)
        raw=source/"raw.log"; raw_index.append({"workload":workload,"raw_log":str(raw),"sha256":sha256(raw),"bytes":raw.stat().st_size,"framework_commit":args.framework_commit,"core_commit":args.core_commit})
        status.append({"workload":workload,"status":"COMPLETE_VALID","parser_schema":"EPL2MOTV1","raw_log_sha256":manifest["source_log_sha256"],"terminal_wbuf_outstanding":summary["wb_packets_created"] if False else "0"})
    for name,rows in tables.items(): write_csv(args.out/(name+".csv"),rows)
    write_tsv(args.out/"RAW_LOG_INDEX.tsv",raw_index);write_csv(args.out/"WORKLOAD_STATUS.csv",status)
    reuse=tables["reuse_distance"];block=[r for r in tables["blocking_breakdown"] if r["wbuf_capacity"]=="8"]
    for row in block:
        denom=integer(row["projected_blocked_miss_admission_cycles"]);rate=integer(row["other"])/denom if denom else 0
        if rate>0.02: print("REVIEW_REQUIRED OTHER %.4f workload=%s"%(rate,row["workload"]))
    make_fig1(reuse,fig);make_fig2(block,fig);make_fig2s(tables["wbuf_sensitivity"],fig)
    (args.out/"aggregation_manifest.json").write_text(json.dumps({"framework_commit":args.framework_commit,"core_commit":args.core_commit,"workloads":list(WORKLOADS),"figures":[p.name for p in sorted(fig.iterdir())]},indent=2)+"\n")
    print("MOTIVATION_AGGREGATION_PASS workloads=%d output=%s"%(len(WORKLOADS),args.out))

if __name__=="__main__": main()
