#!/usr/bin/env python3
"""Independent abstract lifetime oracle; not a SASS value or timing simulator.

`qualified` is an abstract source-selected LDST request predicate, not a claim
about a production store/atomic/fence trigger. IO refs below are shadow refs;
this IO model does not supply the missing production orphan mechanism.
Lane V contract: 26abd496417d9392245052e54fbd9ba27c6ffd96.
"""
import argparse
import copy
import json
import sys
from pathlib import Path


class Reject(Exception):
    pass


class Model:
    def __init__(self, mode, enabled=True, lines=2, slots=3):
        self.mode, self.enabled = mode, enabled
        self.phys = [dict(generation=0, allocated=False, tag=False, line=None,
                          refs=[], expected=0, received=0, values={}) for _ in range(lines)]
        self.slots = [dict(generation=0, uid=None) for _ in range(slots)]
        self.entries, self.tags, self.handles = {}, {}, {}
        self.memory, self.bank_cycle, self.banks = {}, -1, set()
        self.frees = 0

    def identity(self, handle):
        ident = self.handles[handle]
        p = self.phys[ident[0]]
        if not p['allocated'] or p['generation'] != ident[1]:
            raise Reject('stale_generation')
        return p

    def release(self, p):
        assert p['allocated'] and not p['tag'] and not p['refs']
        assert p['received'] == p['expected']
        p.update(allocated=False, expected=0, received=0, values={})
        self.frees += 1

    def ready(self, uid):
        e = self.entries[uid]
        return all(self.phys[i]['received'] & mask == mask for i, mask in e['refs'].items())

    def apply(self, e):
        op = e['op']
        if op == 'admit':
            uid = e['uid']
            assert uid not in self.entries
            slot = next((i for i, s in enumerate(self.slots) if s['uid'] is None), None)
            if slot is None:
                return 'pib_full'
            s = self.slots[slot]
            s.update(uid=uid, generation=s['generation'] + 1)
            self.entries[uid] = dict(slot=slot, refs={})
            return 'admitted'
        if op == 'access':
            uid, line = e['uid'], e.get('line', 0)
            mask = 15 if self.mode in ('IO', 'OO') else e.get('mask', 15)
            owner = self.entries[uid]
            if line in self.tags:
                i = self.tags[line]
                p = self.phys[i]
                result = 'valid_hit' if p['received'] & mask == mask else 'pending_hit'
            else:
                i = next((i for i, p in enumerate(self.phys) if not p['allocated']), None)
                if i is None:
                    return 'no_free_line'
                p = self.phys[i]
                p.update(generation=p['generation'] + 1, allocated=True, tag=True,
                         line=line, refs=[], expected=0, received=0, values={})
                self.tags[line] = i
                result = 'new_miss'
            if uid not in p['refs']:
                p['refs'].append(uid)
            p['expected'] |= mask
            owner['refs'][i] = owner['refs'].get(i, 0) | mask
            if 'handle' in e:
                self.handles[e['handle']] = (i, p['generation'])
            return result
        if op == 'invalidate':
            if not self.enabled or not e.get('qualified', True):
                return 'suppressed'
            i = self.tags.pop(e.get('line', 0), None)
            if i is None:
                return 'absent'
            p = self.phys[i]
            p['tag'] = False
            if not p['refs'] and p['expected'] == p['received']:
                self.release(p)
            return 'invalidated'
        if op == 'fill':
            p = self.identity(e['handle'])
            bit = 1 << e['sector'] if 0 <= e['sector'] < 4 else 0
            if not bit or not p['expected'] & bit:
                raise Reject('unrequested_sector')
            if p['received'] & bit:
                raise Reject('duplicate_sector')
            p['received'] |= bit
            # A supplied value is a shadow token chosen by the input, not hardware data.
            p['values'][e['sector']] = e.get('value', self.memory.get(p['line'], 0))
            return 'filled'
        if op == 'retire':
            uid = e['uid']
            if self.mode == 'IO' and uid != next(iter(self.entries)):
                return 'fifo_blocked'
            if not self.ready(uid):
                return 'not_ready'
            owner = self.entries.pop(uid)
            self.slots[owner['slot']]['uid'] = None
            for i in owner['refs']:
                p = self.phys[i]
                p['refs'].remove(uid)
                if not p['tag'] and not p['refs']:
                    self.release(p)
            return 'retired'
        if op == 'tag':
            cycle, bank = e['cycle'], e.get('line', 0) % 4
            if cycle != self.bank_cycle:
                self.bank_cycle, self.banks = cycle, set()
            if bank in self.banks:
                return 'bank_busy'
            self.banks.add(bank)
            return 'tag_granted'
        if op == 'write':
            self.memory[e.get('line', 0)] = e['value']
            return 'shadow_written'
        if op == 'shadow_read':
            p = self.identity(e['handle'])
            value = p['values'].get(e.get('sector', 0))
            return 'potential_stale' if value != self.memory.get(p['line'], 0) else 'matches'
        raise ValueError(op)

    def invariant(self):
        for i, p in enumerate(self.phys):
            refs = sorted(uid for uid, owner in self.entries.items() if i in owner['refs'])
            assert sorted(p['refs']) == refs
            assert p['allocated'] or (not p['tag'] and not refs)
            assert p['received'] & ~p['expected'] == 0
            if p['tag']:
                assert self.tags[p['line']] == i
        for line, i in self.tags.items():
            assert self.phys[i]['allocated'] and self.phys[i]['tag'] and self.phys[i]['line'] == line

    def snapshot(self):
        return dict(allocated=sum(p['allocated'] for p in self.phys),
                    tags=sorted(self.tags), refs=sum(len(p['refs']) for p in self.phys),
                    occupancy=len(self.entries), frees=self.frees,
                    ready=sorted(uid for uid in self.entries if self.ready(uid)),
                    physical=copy.deepcopy(self.phys), slots=copy.deepcopy(self.slots))


def subset(expected, observed, path=''):
    if isinstance(expected, dict):
        for key, value in expected.items():
            assert key in observed, f'{path}.{key}: missing'
            subset(value, observed[key], path + '.' + key)
    else:
        assert expected == observed, f'{path}: expected {expected!r}, observed {observed!r}'


def run(case, mode, corrupt_expected=False):
    m = Model(mode, **case.get('config', {}))
    observations, checks, rc = [], 0, 0
    for step, e in enumerate(case['events']):
        before = copy.deepcopy(m.__dict__)
        try:
            result, event_rc = m.apply(e), 0
        except Reject as error:
            result, event_rc = str(error), 2
            assert before == m.__dict__, 'rejected event mutated state'
        m.invariant()
        state = m.snapshot()
        observation = dict(step=step, input=e, result=result, exit_code=event_rc, state=state)
        observations.append(observation)
        if 'expect' in e:
            subset(e['expect'], dict(result=result, exit_code=event_rc, state=state))
            checks += 1
        rc = event_rc
    expected = copy.deepcopy(case['expected'])
    if corrupt_expected:
        expected['frees'] = expected.get('frees', m.frees) + 1
    subset(expected, m.snapshot())
    assert rc == case.get('expected_exit_code', 0)
    return dict(id=case['id'], mode=mode, status='REFERENCE_ONLY_PASS',
                expected=case['expected'], expected_exit_code=case.get('expected_exit_code', 0),
                observed=m.snapshot(), exit_code=rc, checkpoint_checks=checks,
                observations=observations, contract_binding='26abd496417d9392245052e54fbd9ba27c6ffd96',
                contract_scope='OO lifetime subset; IO abstract shadow only; timing/value unproven',
                production_evidence=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--case', required=True)
    parser.add_argument('--mode', choices=['IO', 'OO', 'SECTOR_OO'], required=True)
    parser.add_argument('--corrupt-expected', action='store_true')
    args = parser.parse_args()
    case = next(c for c in json.loads(args.cases.read_text())['cases'] if c['id'] == args.case)
    try:
        result = run(case, args.mode, args.corrupt_expected)
        print(json.dumps(result, sort_keys=True))
        return result['exit_code']
    except (AssertionError, KeyError, ValueError) as error:
        print(json.dumps(dict(id=case['id'], mode=args.mode, status='FAIL', error=str(error))))
        return 1


if __name__ == '__main__':
    sys.exit(main())
