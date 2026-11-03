"""Pure decision math only. Main must verify same-Source/input/mode archive state first."""
def decide(reference_EP_cycles, geometry_EP_cycles, scheduler_EP_cycles):
    r,g,s=reference_EP_cycles,geometry_EP_cycles,scheduler_EP_cycles
    if not all(isinstance(x,int) and not isinstance(x,bool) and x>0 for x in [r,g,s]):
        raise ValueError("positive integer completed EP cycles required")
    release=((100*(r-g)>=r and 100*(r-s)>=r) or
             (100*(r-g)>=3*r and r-s>=0) or
             (100*(r-s)>=3*r and r-g>=0))
    return dict(release_combination_candidate=release,
                geometry_EP_cycle_reduction_fraction=(r-g)/r,
                scheduler_EP_cycle_reduction_fraction=(r-s)/r,
                S_ratio_not_used=True,science_launch_permission=False)
