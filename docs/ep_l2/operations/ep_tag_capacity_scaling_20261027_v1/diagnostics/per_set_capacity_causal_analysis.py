#!/usr/bin/env python3
"""Offline identical-population per-set occupancy/episode identity; no probability inference."""
import pathlib,json,csv,statistics
P=pathlib.Path;J=P('/root/data/ep_tag_capacity_scaling_20261027_v1')
def stats(v):
 v=sorted(v);return {'min':min(v),'max':max(v),'mean':sum(v)/len(v),'p50':v[len(v)//2],'p95':v[min(len(v)-1,int(len(v)*.95))]}
def main():
 out=[]
 for p in sorted((J/'analysis').glob('EP_TAGFLOW*.json')):
  d=json.loads(p.read_bytes());rows=d['LIFE']['per_physical_set'];table=[]
  for r in rows:
   c=r['counters'];t=r['observed_L2_ticks'];assert c['LEFT']==c['RIGHT']==0,'censor-free identity cannot be assumed';assert c['ENTER']==c['CLOSED_NEW']+c['CLOSED_RE']==c['EXIT'];assert r['weighted_reserved_Tag_L2_ticks']==c['SUM_NEW']+c['SUM_RE'];assert sum(r['incarnation']['new_unique_reserved_joint'])==c['NEW_UNIQUE'];assert c['NEW_UNIQUE']==c['CLOSED_NEW']
   # Same physical slice/set and exact closed-new/reentry episode populations.
   lam_new=c['CLOSED_NEW']/t;life_new=c['SUM_NEW']/c['CLOSED_NEW']if c['CLOSED_NEW']else 0;lam_re=c['CLOSED_RE']/t;life_re=c['SUM_RE']/c['CLOSED_RE']if c['CLOSED_RE']else 0;observed=r['weighted_reserved_Tag_L2_ticks']/t
   assert abs(lam_new*life_new+lam_re*life_re-observed)<1e-12
   table.append({'slice':r['slice'],'set':r['set'],'observed_L2_ticks':t,'new_unique':c['NEW_UNIQUE'],'new_episode_arrival_per_L2_tick':lam_new,'closed_new_episode_mean_L2_ticks_including_zero':life_new,'reentry_episode_arrival_per_L2_tick':lam_re,'closed_reentry_episode_mean_L2_ticks':life_re,'timeweighted_RESERVED':observed,'event_peak':c['EVENT_PEAK'],'tick_peak':c['TICK_PEAK'],'NEW_UNIQUE_at_full_RESERVED':r['incarnation']['new_unique_reserved_joint'][d['geometry']['ways']]})
  dest=J/'analysis'/(d['cohort']+'.PER_SET_CAUSAL.csv')
  with dest.open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
  a=d['LIFE']['aggregate'];h=a['episodes']['new_allocation']['histogram']['counts'];count=a['episodes']['new_allocation']['closed_count'];positive=count-h[0];sumlife=a['episodes']['new_allocation']['observed_overlap_sum_L2_ticks']
  out.append({'cohort':d['cohort'],'geometry':d['geometry'],'per_set_count':len(table),'exact_per_set_episode_area_identity_pass':True,'new_unique_per_set':stats([r['new_unique']for r in table]),'new_episode_arrival_rate_per_set_per_L2_tick':stats([r['new_episode_arrival_per_L2_tick']for r in table]),'closed_new_episode_lifetime_including_zero_per_set':stats([r['closed_new_episode_mean_L2_ticks_including_zero']for r in table]),'timeweighted_RESERVED_per_set':stats([r['timeweighted_RESERVED']for r in table]),'new_zero_lifetime_episodes':h[0],'new_positive_lifetime_episodes':positive,'new_positive_lifetime_mean_L2_ticks':sumlife/positive if positive else'UNKNOWN','new_unique_reserved_joint':a['new_unique_reserved_joint'],'area_L2_ticks_by_RESERVED':a['area_L2_ticks_by_reserved_tags'],'full_way_NEW_joint_sum':sum(r['NEW_UNIQUE_at_full_RESERVED']for r in table),'scope':'per-set exact occupancy identity plus actual full-way arrival joint; not tail-probability or cross-layer causal inference','per_set_csv':str(dest)})
 (J/'analysis/PER_SET_CAUSAL_SUMMARY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
