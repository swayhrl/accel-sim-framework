"""Plot functions called only with points returned by a registered independent intake handler."""
from pathlib import Path
import csv,json
VIEWS=('ideal_potential','limitation_removal','finite_configuration','structure','cost_timing')
def plot_points(view,points,out):
 if view not in VIEWS:raise ValueError('Unknown view')
 if any(not p.get('intake_receipt_sha256') or not p.get('current_target_binding') for p in points):raise ValueError('Derived points need traceable independently rechecked receipts')
 out=Path(out)
 if not points:return
 # An absent metric remains absent; it is never replaced with zero.
 actual=[p for p in points if p.get('value') is not None]
 if not actual:return
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(7.25,2.6))
 labels=[p['label'] for p in actual];values=[p['value'] for p in actual]
 ax.bar(range(len(values)),values,color=['#187d8d' if x>=0 else '#ac4d40' for x in values])
 ax.set_xticks(range(len(labels)),labels,rotation=25,ha='right');ax.set_ylabel(actual[0]['declared_metric']);ax.set_title(view.replace('_',' '))
 # No stacked cycle decomposition or automatic mixed-profile mean.
 fig.tight_layout();fig.savefig(out/(view+'.pdf'));plt.close(fig)
 with (out/(view+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(actual[0]),lineterminator='\n');w.writeheader();w.writerows(actual)
