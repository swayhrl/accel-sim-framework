"""Pure metrology reference, NOT a simulator observer or qualified Core hook.

Synthetic events only. Bounded Python objects are not a C++ state-size estimate.
No protocol decisions, cache accesses, trace parsing, or simulator libraries.
"""
from collections import Counter

BOUNDARIES = ('ingress_child', 'queue_enter', 'first_head', 'admission')


def readiness(required, ready, issued, live):
    if any(x < 0 or x > 15 for x in (required, ready, issued)) or required == 0:
        raise ValueError('four-sector nonempty required mask expected')
    return {
        'existing_live': live,
        'required_not_ready': live and bool(required & ~ready),
        'required_issued_not_ready': live and bool(required & issued & ~ready),
        'line_has_issued_not_ready': live and bool(issued & ~ready),
        'ready_only_drain': live and not bool(required & ~ready),
    }


def rate(numerator, denominator, numerator_population, denominator_population):
    if numerator_population != denominator_population:
        raise ValueError('boundary/class/eligibility/clock/dedup population mismatch')
    if numerator < 0 or denominator < numerator:
        raise ValueError('invalid subset counts')
    return None if denominator == 0 else numerator / denominator


class RequestReference:
    def __init__(self, enabled=False, capacity=64):
        self.enabled, self.capacity = enabled, capacity
        self.records, self.counts = {}, Counter()
        self.valid = True

    def observe(self, uid, generation, origin_epoch, boundary, tick, clock='L2',
                is_new=False, reserved=0, ways=8, structural=None,
                policy_enabled=False, tag_denied=False):
        if not self.enabled:
            return
        if boundary not in BOUNDARIES or not 0 <= reserved <= ways or ways <= 0:
            raise ValueError('invalid boundary/geometry')
        key = (uid, generation)
        if key not in self.records:
            if len(self.records) == self.capacity:
                self.valid = False
                self.counts['overflow'] += 1
                return
            self.records[key] = {'origin': origin_epoch, 'events': {}, 'first_new': None,
                                 'ever_full': False, 'denied_ticks': set()}
        rec = self.records[key]
        if rec['origin'] != origin_epoch:
            raise ValueError('live UID origin cannot be reset at an epoch boundary')
        if boundary not in rec['events']:
            rec['events'][boundary] = (clock, tick)
            self.counts[boundary] += 1
        if boundary != 'first_head':
            return
        self.counts['head_checks'] += 1
        if not is_new:
            return
        if rec['first_new'] is None:
            rec['first_new'] = (clock, tick)
            self.counts['new_unique'] += 1
            self.counts['first_new_R' + str(reserved)] += 1
        if reserved == ways:
            if not rec['ever_full']:
                rec['ever_full'] = True
                self.counts['ever_full_unique'] += 1
            if structural is None:
                self.counts['full_structural_unknown_checks'] += 1
            elif structural > 0:
                self.counts['full_structural_checks'] += 1
                self.counts['full_structural_policy_on_checks'] += int(policy_enabled)
        if tag_denied:
            rec['denied_ticks'].add((clock, tick))

    def duration(self, uid, generation, start, finish):
        a, b = (self.records[(uid, generation)]['events'][x] for x in (start, finish))
        if a[0] != b[0] or b[1] < a[1]:
            raise ValueError('cross-clock or reversed time cannot be subtracted')
        return b[1] - a[1]


class AddressUnionReference:
    """Event-state reference. Real adapter must use exact producer lifetimes."""
    def __init__(self, capacity=1024):
        self.capacity, self.entries, self.valid = capacity, {}, True

    def set_refs(self, line, normal_pending, ro_pending, normal_live, ro_live):
        refs = (normal_pending, ro_pending, normal_live, ro_live)
        if min(refs) < 0 or normal_pending > normal_live or ro_pending > ro_live:
            raise ValueError('invalid reference counts')
        if not any(refs):
            self.entries.pop(line, None)
        elif line in self.entries or len(self.entries) < self.capacity:
            self.entries[line] = refs
        else:
            self.valid = False

    def occupancy(self):
        if not self.valid:
            return None
        n = sum(v[0] > 0 for v in self.entries.values())
        r = sum(v[1] > 0 for v in self.entries.values())
        union_pending = sum(v[0] > 0 or v[1] > 0 for v in self.entries.values())
        union_live = sum(v[2] > 0 or v[3] > 0 for v in self.entries.values())
        return n, r, union_pending, union_live
