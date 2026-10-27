"""Single-target75/25 aging candidate. No model launch, signals, or auto-install.

Frames contain exact provider values plus verified operational observations.
This module never changes a registered forecast, real claim or scientific spec.
"""
import copy,math,threading
G=1024**3
DEFAULT={'wait_seconds':1800,'large_bytes':8*G,'protect_fraction':.75,'pss_max_age_seconds':60}

def _generation(row):return(row['cohort'],row['uuid'])
def _money(value):return max(0,int(value))

class AgingState:
    def __init__(self,policy=None):
        self.policy=dict(DEFAULT,**(policy or{}));assert self.policy['protect_fraction']==.75
        self.target=None;self.protected=0;self.previous_C=None;self.previous_discount=0
        self.previous_discount_rows={}
        self.last_live={};self.pending_releases={};self.seen_completions=set();self.last_decision=None

    def advance(self,frame):
        p=self.policy;now=frame['now'];budget=frame['budget_bytes'];total=frame['effective_total_growth_bytes'];C=budget-total
        assert budget>=0 and total>=0 and 0<frame['memory_utilization_fraction']<=1
        live={_generation(r):r for r in frame['own_live']};consumed=frame['consumed'];claims=set(frame['claim_cohorts'])
        pending={r['cohort']:r for r in frame['pending']};events=[]
        # Clear only on actual observed generation or terminal closure; a spent
        # uncertain grant is never resubmitted and remains a visible hold.
        if self.target:
            c=self.target['cohort'];spent=consumed.get(c)
            observed=bool(spent and(c,spent['uuid'])in live)
            terminal=bool(spent and spent.get('terminal'))
            if observed or terminal:
                events.append(dict(kind='TARGET_OBSERVED_OR_CLOSED',cohort=c,observed_generation=observed,terminal=terminal))
                self.target=None;self.protected=0;self.pending_releases={}
            elif c in pending:self.target=copy.deepcopy(pending[c])
        if self.target is None:
            active_inputs=set(frame.get('active_input_digests',[]));started=set(frame['started_programs'])
            choices=[r for r in frame['pending']if r['cell']=='DH'and r['profile']=='P0'and r['cost_bytes']>=p['large_bytes']
                and now-r['first_eligible_monotonic']>=p['wait_seconds']and r['cohort']not in consumed
                and r['cohort']not in claims and r['input_digest']not in active_inputs]
            if choices:
                self.target=copy.deepcopy(min(choices,key=lambda r:(r['program']in started,r['first_eligible_monotonic'],r['input_digest'],r['cohort'])))
                self.protected=0;events.append(dict(kind='TARGET_ARMED',cohort=self.target['cohort'],never_started_program=self.target['program']not in started))
        target=self.target;feasibility=None;throttle=False
        accounted=frame.get('accounted_growth_by_cohort',{}).get(target['cohort'],0)if target else 0
        backed=bool(target and(target['cohort']in claims or target['cohort']in consumed)and accounted>=target['cost_bytes'])
        if target:
            witnesses=[r for r in frame['own_live']if r.get('anon_PSS_bytes')is not None and 0<=now-r['PSS_sample_monotonic']<=p['pss_max_age_seconds']]
            released_future=sum(r['effective_future_bytes']for r in witnesses)
            assert released_future<=total,'EFFECTIVE_OWN_GROWTH_EXCEEDS_TOTAL'
            released_anon=sum(min(r['anon_PSS_bytes'],r['RSS_bytes'])for r in witnesses)
            fraction=frame['memory_utilization_fraction'];drain_C=budget+int(fraction*released_anon)-(total-released_future)
            coverage=len(witnesses)==len(frame['own_live'])
            additional_target=0 if backed else target['cost_bytes']
            feasibility=dict(after_own_drain_slack_bytes=drain_C,required_target_bytes=additional_target,
                own_effective_future_removable_bytes=released_future,own_anon_PSS_bytes=released_anon,
                retained_peer_claim_unknown_growth_bytes=total-released_future,full_live_PSS_coverage=coverage,
                witness_count=len(witnesses),feasible=drain_C>=additional_target)
            throttle=feasibility['feasible']
            if not throttle:
                self.protected=0;self.pending_releases={}
                events.append(dict(kind='EXTERNAL_LIMIT_NOT_RESOLVABLE_BY_OWN_DRAIN'if coverage else'INSUFFICIENT_PSS_EVIDENCE_NO_THROTTLE',cohort=target['cohort']))
        # True positive safe-margin movement is reconciled with padding changes.
        # Positive padding expansion cannot masquerade as completion release.
        current_discount=frame.get('total_padding_discount_bytes',0)
        delta_C=0 if self.previous_C is None else C-self.previous_C
        discount_rows=frame.get('padding_discount_by_cohort',{})
        assert sum(discount_rows.values())==current_discount,'PADDING_DISCOUNT_COMPONENTS_REQUIRED'
        padding_expansion=sum(max(0,value-self.previous_discount_rows.get(c,0))for c,value in discount_rows.items())
        positive_budget=max(0,delta_C-padding_expansion)
        negative_budget=max(0,-delta_C)
        # Unaccepted completion-release tokens are not protected yet; intervening
        # new claims/pressure consume them before strict acceptance can use them.
        for k in sorted(self.pending_releases):
            amount=min(negative_budget,self.pending_releases[k]['realized_credit_bytes'])
            self.pending_releases[k]['realized_credit_bytes']-=amount;negative_budget-=amount
        closed={_generation(r):r for r in frame['closures']}
        if target and throttle:
            for k,closure in sorted(closed.items()):
                if k in self.seen_completions:continue
                if not closure['natural_done']:
                    self.pending_releases.pop(k,None);self.seen_completions.add(k);continue
                witness=self.last_live.get(k)
                if witness is None:continue # no retroactive credit for earlier completions
                if k not in self.pending_releases:
                    if now-witness['PSS_sample_monotonic']>p['pss_max_age_seconds']or now-witness['last_live_observation_monotonic']>p['pss_max_age_seconds']:
                        events.append(dict(kind='STALE_RELEASE_WITNESS_NO_CREDIT',cohort=k[0],uuid=k[1]));self.seen_completions.add(k);continue
                    raw=witness['effective_future_bytes']+int(frame['memory_utilization_fraction']*witness['anon_PSS_bytes'])
                    self.pending_releases[k]=dict(raw_release_bytes=raw,realized_credit_bytes=0,
                        raw_release_is_operational_estimate=True,
                        natural_completion_first_seen_monotonic=now,
                        last_effective_future_bytes=witness['effective_future_bytes'],last_anon_PSS_bytes=witness['anon_PSS_bytes'])
            for k,item in sorted(self.pending_releases.items()):
                available=max(0,item['raw_release_bytes']-item['realized_credit_bytes'])
                grant=min(positive_budget,available);item['realized_credit_bytes']+=grant;positive_budget-=grant
            for k,closure in sorted(closed.items()):
                item=self.pending_releases.get(k)
                if item is None or not closure['accepted_strict_archive_restore']:continue
                credit=item['realized_credit_bytes'];increase=min(max(0,target['cost_bytes']-self.protected),int(p['protect_fraction']*credit))
                self.protected+=increase;events.append(dict(kind='STRICT_NATURAL_COMPLETION_CREDIT',cohort=k[0],uuid=k[1],
                    raw_release_bytes=item['raw_release_bytes'],actual_positive_margin_credit_bytes=credit,
                    protected_credit_bytes=increase,unprotected_credit_bytes=credit-increase))
                self.pending_releases.pop(k,None);self.seen_completions.add(k)
        else:
            for k in closed:self.seen_completions.add(k)
        self.protected=min(self.protected,target['cost_bytes'])if target else 0
        # Only healthy actual generations with recent anon-PSS can become future
        # completion witnesses. Heap shrink/padding/external free alone earns0.
        for k,row in live.items():
            if row.get('anon_PSS_bytes')is not None and 0<=now-row['PSS_sample_monotonic']<=p['pss_max_age_seconds']:
                self.last_live[k]=dict(effective_future_bytes=row['effective_future_bytes'],
                    anon_PSS_bytes=min(row['anon_PSS_bytes'],row['RSS_bytes']),
                    PSS_sample_monotonic=row['PSS_sample_monotonic'],last_live_observation_monotonic=now)
            elif k in self.last_live:
                self.last_live[k]['anon_PSS_bytes']=min(self.last_live[k]['anon_PSS_bytes'],row['RSS_bytes'])
                self.last_live[k]['effective_future_bytes']=row['effective_future_bytes']
                self.last_live[k]['last_live_observation_monotonic']=now
        self.previous_C=C;self.previous_discount=current_discount
        self.previous_discount_rows=copy.deepcopy(discount_rows)
        virtual_R=0 if backed else self.protected
        offer=None;allowed=[];phase='NORMAL'
        if target and throttle:
            c=target['cohort'];spent=consumed.get(c)
            if spent:phase='SPENT_UNCERTAIN_NO_RETRY'
            elif c in claims:phase='TARGET_CLAIM_INFLIGHT'
            elif c in pending and C>=target['cost_bytes']:offer=c;phase='TARGET_FIRST_FULL_ORIGINAL_GATES'
            elif c not in pending:phase='TARGET_ZERO_START_DEFER_RESERVATION_RETAINED'
            else:phase='ACCUMULATING_PROTECTED_RELEASE'
            allowed=[r['cohort']for r in frame['pending']if r['cohort']not in consumed and r['cohort']not in claims
                     and r['cohort']!=c and C-r['cost_bytes']>=virtual_R]
        else:
            allowed=[r['cohort']for r in frame['pending']if r['cohort']not in consumed and r['cohort']not in claims]
            if target:phase='OWN_DRAIN_NOT_PROVEN_RELEASE_THROTTLE'
        decision=dict(schema='DTC_SINGLE_TARGET_AGING_DECISION_V1',target=copy.deepcopy(target),protected_bytes=virtual_R,
            saved_protected_credit_bytes=self.protected,target_cost_already_accounted_bytes=accounted,
            virtual_fence_released_due_full_claim=backed,
            current_slack_bytes=C,budget_bytes=budget,effective_total_growth_bytes=total,phase=phase,
            feasibility=feasibility,offer_target_first=offer,backfill_cohorts=allowed,
            new_credit_events=events,positive_margin_budget_after_padding_adjustment=max(0,delta_C-padding_expansion),
            padding_expansion_not_credited_bytes=padding_expansion,
            pending_unaccepted_release_tokens=[dict(cohort=k[0],uuid=k[1],**v)for k,v in self.pending_releases.items()],
            pressure_reasons=frame.get('pressure_reasons',[]),candidate_costs_unmodified=True,
            release_credit_causal_interpretation='bounded operational estimate; simultaneous heap/external changes are not separable; external-only gives no credit',
            canonical_specs_and_claims_mutated=False,healthy_models_continue=True)
        self.last_decision=decision;return decision

class AgingChooser:
    """Post-padding outer fence. Frame/provider I/O supplied by one existing owner."""
    def __init__(self,original,frame_provider,policy=None,journal=None):
        self.original=original;self.frame_provider=frame_provider;self.state=AgingState(policy)
        self.journal=journal;self.lock=threading.RLock();self.calls=0;self.installed=None
        self.wrapper=self.choose

    def choose(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
        with self.lock:
            frame=self.frame_provider(pending,sample,claims,history,previous,policy or{},dispatch_index)
            decision=self.state.advance(frame);self.calls+=1
            if self.journal:self.journal(decision)
            if decision['pressure_reasons']:return None
            if decision['offer_target_first']:
                target=[s for s in pending if s['cohort']==decision['offer_target_first']]
                if target:
                    value=self.original(target,sample,claims,history,previous,policy,dispatch_index)
                    if value is not None:
                        assert value['cohort']==decision['offer_target_first']
                        fresh=self.frame_provider(pending,sample,claims,history,previous,policy or{},dispatch_index)
                        if value['cohort']in fresh['consumed']or value['cohort']in fresh['claim_cohorts']:return None
                        return dict(value,large_job_aging=decision)
            allowed=set(decision['backfill_cohorts']);pool=[s for s in pending if s['cohort']in allowed]
            if not pool:return None
            value=self.original(pool,sample,claims,history,previous,policy,dispatch_index)
            if value is not None:
                assert value['cohort']in allowed
                fresh=self.frame_provider(pending,sample,claims,history,previous,policy or{},dispatch_index)
                if value['cohort']in fresh['consumed']or value['cohort']in fresh['claim_cohorts']:return None
                cost=next(r['cost_bytes']for r in fresh['pending']if r['cohort']==value['cohort'])
                if fresh['budget_bytes']-fresh['effective_total_growth_bytes']-cost<decision['protected_bytes']:return None
                return dict(value,large_job_aging=decision)
            return None

    def install(self,res,owner_assert):
        assert threading.current_thread()is threading.main_thread();owner_assert()
        assert self.installed is None and res.choose_dispatch is self.original
        assert not getattr(res,'DTC_LARGE_JOB_AGING_INSTALLED',False)
        res.choose_dispatch=self.wrapper;res.DTC_LARGE_JOB_AGING_INSTALLED=self;self.installed=res
        return dict(status='INSTALLED_EXISTING_CHOOSER_INSTANCE_ONLY',models_started=0)

    def restore(self,owner_assert):
        assert threading.current_thread()is threading.main_thread();owner_assert()
        res=self.installed;assert res is not None and res.choose_dispatch is self.wrapper
        res.choose_dispatch=self.original;del res.DTC_LARGE_JOB_AGING_INSTALLED;self.installed=None
        return dict(status='RESTORED_PREVIOUS_CHOOSER_INSTANCE',claims_models_and_specs_untouched=True)
