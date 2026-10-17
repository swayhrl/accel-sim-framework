"""Compile the manuscript with BibTeX in a new scratch directory; no simulation."""
import argparse,os,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);ap.add_argument('--tex-deps',type=Path);a=ap.parse_args()
P=Path(__file__).resolve().parent;T=a.output_dir.resolve();T.mkdir(parents=True,exist_ok=False);N='EP_L2_EN_v7';env=dict(os.environ)
search=str(P)+'//:'
if a.tex_deps:
 deps=str(a.tex_deps.resolve())+'//:';search=deps+search
 for key in ['TFMFONTS','VFFONTS','T1FONTS','ENCFONTS','TEXFONTMAPS','BSTINPUTS']:env[key]=deps+env.get(key,'')
env['TEXINPUTS']=str(T)+'//:'+search+env.get('TEXINPUTS','');env['BIBINPUTS']=str(P)+'//:'+env.get('BIBINPUTS','')
wrapper=T/'build.tex';wrapper.write_text('\\pdfmapfile{+newtx.map}\n\\input{'+str(P/(N+'.tex'))+'}\n')
def latex(n):
 with (T/f'pass{n}.stdout').open('w') as out:subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-no-shell-escape','-no-mktex=pk','-no-mktex=tfm','-jobname='+N,'-output-directory='+str(T),str(wrapper)],cwd=P,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=45,check=True)
latex(1)
with (T/'bibtex.stdout').open('w') as out:subprocess.run(['bibtex',N],cwd=T,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=20,check=True)
latex(2);latex(3)
print(T/(N+'.pdf'))
