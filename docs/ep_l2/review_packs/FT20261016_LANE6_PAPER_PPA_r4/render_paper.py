#!/usr/bin/python3
"""Render a readable four-page Chinese working draft, not a certified venue template."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import subprocess
import sys
from xml.sax.saxutils import escape


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--reportlab-path',type=Path);args=parser.parse_args()
    if args.reportlab_path:sys.path.insert(0,str(args.reportlab_path.resolve()))
    import reportlab
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,Table,TableStyle,PageBreak,FrameBreak
    here=Path(__file__).resolve().parent;out=args.output_dir.resolve();assert not out.exists(),'New output revision required';out.mkdir(parents=True)
    cjk='/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
    latin='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    pdfmetrics.registerFont(TTFont('CJK',cjk));pdfmetrics.registerFont(TTFont('Latin',latin))
    font_size,leading=10.4,14.4
    body=ParagraphStyle('body',fontName='CJK',fontSize=font_size,leading=leading,wordWrap='CJK',spaceAfter=5,firstLineIndent=font_size)
    heading=ParagraphStyle('heading',parent=body,fontSize=11.1,leading=15.6,spaceBefore=6,spaceAfter=5,firstLineIndent=0)
    sub=ParagraphStyle('sub',parent=body,fontSize=10.4,leading=14.4,spaceBefore=4,spaceAfter=4,firstLineIndent=0)
    table_style=ParagraphStyle('table',parent=body,fontSize=8.8,leading=11.7,spaceAfter=0,firstLineIndent=0)
    note=ParagraphStyle('note',parent=body,fontSize=8.5,leading=11.5,firstLineIndent=0)
    from fontTools.ttLib import TTFont as FontInfo
    latin_chars=set(FontInfo(latin).getBestCmap());cjk_chars=set(FontInfo(cjk).getBestCmap())
    def rich(text):
        # Embed real TrueType CJK and Latin subsets; all text remains searchable.
        chunks=[]
        for char in text:
            font='Latin' if ord(char) in latin_chars else 'CJK'
            assert ord(char) in (latin_chars if font=='Latin' else cjk_chars),('Missing glyph',char,hex(ord(char)))
            if chunks and chunks[-1][0]==font:chunks[-1][1]+=char
            else:chunks.append([font,char])
        return ''.join('<font name="'+font+'">'+escape(chars)+'</font>' for font,chars in chunks)
    def paragraph(text,style=body):return Paragraph(rich(text),style)
    width,height=612,792;margin=43;gap=17;column=(width-2*margin-gap)/2;bottom=39;top=44;available=height-top-bottom
    title='EP-L2：以生命周期解耦实现原位写回与等预算数据池共享'
    def decorate(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#7b8790'));canvas.setLineWidth(.35);canvas.line(margin,height-28,width-margin,height-28)
        canvas.setFont('Latin',7);canvas.drawString(margin,height-22,'EP-L2 | research working draft | provisional four-page layout')
        canvas.drawRightString(width-margin,22,str(doc.page));canvas.restoreState()
    doc=BaseDocTemplate(str(out/'paper_4page.pdf'),pagesize=(width,height),title=title,author='EP-L2 Research',pageCompression=1,invariant=1)
    frames=[Frame(margin,bottom,column,available,id='left',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),Frame(margin+column+gap,bottom,column,available,id='right',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)]
    doc.addPageTemplates(PageTemplate(id='two-columns',frames=frames,onPage=decorate))
    md=(here/'PAPER_DRAFT_ZH_V4.md').read_text();pages=re.split(r'<!-- PAGE [1-4] -->',md)[1:];assert len(pages)==4
    story=[];usage=[]
    for page_num,page in enumerate(pages,1):
        elements=[]
        if page_num==1:elements.append(paragraph(title,ParagraphStyle('title',parent=heading,fontSize=13,leading=18,spaceAfter=10)))
        lines=page.strip().splitlines();i=0
        while i<len(lines):
            line=lines[i].strip()
            if line.startswith('|'):
                rows=[]
                while i<len(lines) and lines[i].strip().startswith('|'):
                    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                    if not all(re.fullmatch(r'[-: ]+',c) for c in cells):rows.append([paragraph(c,table_style) for c in cells])
                    i+=1
                table=Table(rows,colWidths=[column*.29,column*.71],hAlign='LEFT')
                table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('LINEABOVE',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,0),(-1,0),.35,colors.black),('LINEBELOW',(0,-1),(-1,-1),.5,colors.black)]))
                elements.extend([table,Spacer(1,6)]);continue
            if line.startswith('### '):elements.append(paragraph(line[4:],sub))
            elif line.startswith('## '):elements.append(paragraph(line[3:],heading))
            elif line:elements.append(paragraph(line))
            i+=1
        if page_num==2:
            slot=Table([[paragraph('F1／机制示意槽位：Tag退出、WB_STAGED、lower_accept、set_done分别标记；数据承载与排序状态单独画线。本文已有生命周期表；此处不放性能曲线。',note)]],colWidths=[column])
            slot.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.45,colors.HexColor('#7b8790')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));elements.append(slot)
        if page_num==3:
            slot=Table([[paragraph('F2／主结果与归因槽位：五点配对、copy、capacity pressure、lower与cycles。当前正式配对为0；不画虚构柱形、加速数字或均值。',note)]],colWidths=[column])
            slot.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.45,colors.HexColor('#7b8790')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));elements.append(slot)
        def measure(item):
            _,h=item.wrap(column,available);return h+item.getSpaceBefore()+item.getSpaceAfter()
        heights=[measure(e) for e in elements];total=sum(heights)
        candidates=[(max(sum(heights[:j]),sum(heights[j:])),j) for j in range(1,len(elements)) if not isinstance(elements[j-1],Paragraph) or elements[j-1].style not in [heading,sub]]
        _,split=min(candidates)
        left,right=sum(heights[:split]),sum(heights[split:])
        assert max(left,right)<=available,('Page overflow: edit prose/table before shrinking font',page_num,left,right,available)
        story.extend(elements[:split]);story.append(FrameBreak());story.extend(elements[split:])
        if page_num<4:story.append(PageBreak())
        usage.append({'page':page_num,'estimated_left_height_pt':round(left,2),'estimated_right_height_pt':round(right,2),'available_height_pt':available,'balanced_occupied_fraction':round(total/(2*available),3)})
    doc.build(story)
    info=subprocess.check_output(['pdfinfo',str(out/'paper_4page.pdf')]).decode();n=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1));assert n==4,info
    text=subprocess.check_output(['pdftotext','-layout',str(out/'paper_4page.pdf'),'-']).decode();(out/'paper_4page.txt').write_text(text)
    fonts=[{'path':f,'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()} for f in [cjk,latin]]
    result={'status':'PASS_LAYOUT_PENDING_VISUAL_INSPECTION','pages':n,'pdf_bytes':(out/'paper_4page.pdf').stat().st_size,'pdf_sha256':hashlib.sha256((out/'paper_4page.pdf').read_bytes()).hexdigest(),'source_md_sha256':hashlib.sha256((here/'PAPER_DRAFT_ZH_V4.md').read_bytes()).hexdigest(),'renderer':'ReportLab '+reportlab.Version,'fonts':fonts,'font_size_pt':font_size,'leading_pt':leading,'column_width_pt':column,'page_usage':usage,'venue_template_verified':False,'scope':'Low-resource document rendering; not a simulator or production build'}
    (out/'LAYOUT_VALIDATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result))

if __name__=='__main__':main()
