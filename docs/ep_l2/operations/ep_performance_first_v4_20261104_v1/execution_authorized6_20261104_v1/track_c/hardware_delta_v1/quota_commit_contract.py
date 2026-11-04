"""Bounded proposed hardware transaction contract, independent of production bf4.
No Trace, ELF, native entry, budget, subprocess or model execution facilities.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Row:
    state: str = 'EMPTY'
    incarnation: int = 0
    payload_id: int = -1
    payload_generation: int = 0
    readers: int = 0

@dataclass(frozen=True)
class Op:
    row: int
    kind: str
    expected_incarnation: int
    expected_payload_generation: int
    new_payload_id: int = -1
    new_payload_generation: int = 0
    resources_reserved: bool = True

class QuotaCommit:
    """K row lanes, nonoverlapped READ then COMMIT, one count write/COMMIT.
    All selected candidates share one exact base revision. This is a proposed
    batch interface; it is NOT an adapter that changes production semantics.
    """
    def __init__(self, rows, cap, lanes=2):
        if not 0 <= cap <= len(rows) <= 128 or lanes not in (1,2):
            raise ValueError('bounded geometry')
        self.rows=tuple(rows); self.cap=cap; self.lanes=lanes
        self.count=sum(r.state=='CLEAN' for r in rows)
        if self.count > cap: raise ValueError('initial occupancy exceeds cap')
        self.revision=0; self.cycle=0; self.pending=None; self.acks=0
        self.metrics=dict(row_reads=0,row_writes=0,count_reads=0,count_writes=0,
                          read_beats=0,commit_beats=0,blocked_commit_beats=0,
                          committed_transitions=0,quota_blocks=0,port_blocks=0)

    def visible(self):
        return self.rows,self.count,self.revision,self.acks

    def _next(self, op, row):
        if not op.resources_reserved: return None,'RESOURCES_NOT_RESERVED'
        if (op.expected_incarnation,op.expected_payload_generation)!=(row.incarnation,row.payload_generation):
            return None,'STALE_IDENTITY'
        k=op.kind
        if k in ('clean_install','dirty_install'):
            if row.state not in ('EMPTY','CLEAN','WB_COMPLETE') or row.readers:
                return None,'ROW_NOT_RECLAIMABLE'
            if k=='clean_install' and self.cap==0: return None,'CLEAN_DISABLED'
            if op.new_payload_id < 0 or op.new_payload_generation <= 0:
                return None,'INVALID_NEW_PAYLOAD_IDENTITY'
            return Row('CLEAN' if k=='clean_install' else 'WB_STAGED',row.incarnation+1,
                       op.new_payload_id,op.new_payload_generation,0),'OK'
        if k in ('reclaim','promote'):
            if row.state not in ('CLEAN','WB_COMPLETE') or row.readers:
                return None,'PINNED_OR_MANDATORY'
            return Row(incarnation=row.incarnation+1),'OK'
        if k=='wb_accept':
            return (replace(row,state='WB_INFLIGHT'),'OK') if row.state=='WB_STAGED' else (None,'WRONG_WB_STATE')
        if k=='wb_done':
            return (replace(row,state='WB_COMPLETE'),'OK') if row.state=='WB_INFLIGHT' else (None,'WRONG_WB_STATE')
        if k=='read_begin':
            return (replace(row,readers=row.readers+1),'OK') if row.state!='EMPTY' else (None,'EMPTY_READ')
        if k=='read_end':
            return (replace(row,readers=row.readers-1),'OK') if row.readers>0 else (None,'NO_READ_LEASE')
        return None,'UNKNOWN_OPERATION'

    def prepare(self, ops, expected_revision):
        """READ beat: accept <=K row-unique transitions. No visible mutation.
        Prefix admission deliberately does not bypass an early +1 using a later
        -1: this safe bubble is explicit, and requires no lookahead reorder.
        """
        self.cycle+=1
        if self.pending is not None: return dict(status='BACKPRESSURE_PENDING',accepted=[],results=[])
        if len(ops)>self.lanes:
            self.metrics['port_blocks']+=1
            return dict(status='BACKPRESSURE_ROW_PORT_BOUND',accepted=[],results=[])
        if expected_revision!=self.revision:
            return dict(status='STALE_BATCH_REVISION',accepted=[],results=[])
        self.metrics['read_beats']+=1; self.metrics['count_reads']+=1
        seen=set(); projected=self.count; accepted=[]; results=[]
        for op in ops:
            if not 0<=op.row<len(self.rows):
                results.append('INVALID_ROW');continue
            if op.row in seen:
                results.append('BACKPRESSURE_SAME_ROW');continue
            seen.add(op.row);self.metrics['row_reads']+=1
            old=self.rows[op.row];new,why=self._next(op,old)
            if new is None: results.append(why);continue
            delta=int(new.state=='CLEAN')-int(old.state=='CLEAN')
            if not 0<=projected+delta<=self.cap:
                self.metrics['quota_blocks']+=1;results.append('BACKPRESSURE_QUOTA');continue
            projected+=delta;accepted.append((op,old,new,delta));results.append('PREPARED')
        if accepted:
            self.pending=dict(revision=self.revision,transitions=tuple(accepted),count=projected,
                              net_delta=projected-self.count,read_cycle=self.cycle)
        return dict(status='PREPARED' if accepted else 'NO_GRANTS',
                    accepted=[x[0].row for x in accepted],results=results,
                    net_delta=projected-self.count)

    def commit(self, downstream_ready=True):
        """COMMIT beat: all prepared row writes and one count write atomic.
        Backpressure and stale revision cause no visible mutation or ack.
        Each supplied wait beat is a charged contract cycle, not a time reading.
        """
        self.cycle+=1
        if self.pending is None:return dict(status='NO_PENDING',committed=0)
        if not downstream_ready:
            self.metrics['blocked_commit_beats']+=1
            return dict(status='BACKPRESSURE_DOWNSTREAM',committed=0)
        p=self.pending
        if p['revision']!=self.revision:
            self.pending=None;return dict(status='STALE_COMMIT_REVISION',committed=0)
        if any(self.rows[op.row]!=old for op,old,new,delta in p['transitions']):
            self.pending=None;return dict(status='STALE_COMMIT_ROW',committed=0)
        updated=list(self.rows)
        for op,old,new,delta in p['transitions']:updated[op.row]=new
        # All validation precedes this single architectural commit point.
        self.rows=tuple(updated);self.count=p['count']
        n=len(p['transitions']);self.revision+=n;self.acks+=n
        self.metrics['row_writes']+=n;self.metrics['count_writes']+=1
        self.metrics['commit_beats']+=1;self.metrics['committed_transitions']+=n
        self.pending=None
        assert self.count==sum(r.state=='CLEAN' for r in self.rows)
        return dict(status='COMMITTED',committed=n,net_delta=p['net_delta'],cycle=self.cycle)

class RoundRobinHeads:
    """Six existing producer HEAD references, no implemented queue allocation.
    At most K heads are attempted per READ beat, even if validation later blocks.
    Advance after attempted selection so a quota-blocked producer cannot freeze
    all producers. Holding the transaction blocks all new READ beats.
    """
    def __init__(self, producers=6):self.producers=producers;self.cursor=0
    def select(self, heads, lanes=2):
        if len(heads)!=self.producers or lanes not in (1,2):raise ValueError('geometry')
        picks=[]
        for offset in range(self.producers):
            i=(self.cursor+offset)%self.producers
            if heads[i] is not None:
                picks.append((i,heads[i]))
                if len(picks)==lanes:break
        if picks:self.cursor=(picks[-1][0]+1)%self.producers
        return picks
