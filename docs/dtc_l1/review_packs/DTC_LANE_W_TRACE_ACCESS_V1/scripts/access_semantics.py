"""Pure CPU analysis helpers for the frozen version-0/version-3 trace contract.

No filesystem, network, subprocess, simulator, decoder modification or value
inference. Accepts one supplied record. This is an independent analysis
consumer, not a replacement for the frozen simulator parser.
"""
from dataclasses import dataclass
import re

U64_MAX = (1 << 64) - 1


class ContractGap(ValueError):
    """Fields cannot be interpreted without extending the reviewed contract."""


@dataclass(frozen=True)
class Record:
    cta: tuple
    warp: int
    ordinal: int
    pc: int
    opcode: str
    mask: int
    trace_width: int
    width: int
    address_mode: object
    lanes: tuple
    access_class: str


def opcode_width(opcode):
    # trace_parser.cc:61: first decimal token or U<decimal>, else 4 bytes.
    for token in opcode.split('.'):
        if re.fullmatch(r'[0-9]+', token):
            bits = int(token)
            break
        if re.fullmatch(r'U[0-9]+', token):
            bits = int(token[1:])
            break
    else:
        return 4
    if bits < 8 or bits % 8 or bits > 128:
        raise ContractGap('UNREVIEWED_OPCODE_WIDTH')
    return bits // 8


def classify(opcode, skip_l1=False):
    tokens=opcode.split('.')
    base=tokens[0]
    if base in ('ATOM','ATOMG','RED'):
        return 'ATOMIC'
    if base=='LDG':
        bypass=skip_l1 or 'BYPASS' in tokens or ('STRONG' in tokens and 'GPU' in tokens)
        return 'BYPASS_GLOBAL_LOAD' if bypass else 'CACHEABLE_GLOBAL_LOAD'
    if base=='STG':
        return 'ORDINARY_STORE'
    if base in ('LDS','STS'):
        return 'SHARED'
    if base in ('LDL','STL'):
        return 'LOCAL'
    if base in ('MEMBAR','FENCE'):
        return 'FENCE'
    if base=='BAR':
        return 'CTA_BARRIER'
    if base.startswith(('LD','ST','ATOM','RED','UTMA','UBLK')):
        raise ContractGap('UNREVIEWED_MEMORY_OPCODE')
    return 'NON_MEMORY'


def frozen_base_stride(mask, base, stride):
    """Match frozen consumer for diagnostics, including the known mask-gap bug.

    scan decoding below rejects mask gaps; these zeros must not enter alias sets.
    """
    result=[0]*32
    first=False
    last=False
    address=base
    for lane in range(32):
        active=bool(mask & (1<<lane))
        if active and not first:
            first=True
            result[lane]=base
        elif first and not last:
            if active:
                address=(address+stride)&U64_MAX
                result[lane]=address
            else:
                last=True
    return tuple(result)


def decode_record(line, version, lineinfo, cta, warp, ordinal, skip_l1=False):
    if version not in (0,3) or lineinfo not in (0,1):
        raise ContractGap('UNREVIEWED_VERSION_OR_LINEINFO')
    words=line.split()
    pos=0

    def take():
        nonlocal pos
        if pos>=len(words):
            raise ContractGap('TRUNCATED_RECORD')
        value=words[pos]
        pos+=1
        return value

    def integer(base=10):
        word=take()
        try:
            return int(word,base)
        except ValueError as exc:
            raise ContractGap('INVALID_INTEGER') from exc

    if version<3:
        old_cta=tuple(integer() for _ in range(3))
        old_warp=integer()
        if old_cta!=tuple(cta) or old_warp!=warp:
            raise ContractGap('LEGACY_CTA_WARP_DISAGREE_WITH_BLOCK_HEADER')
    if lineinfo:
        integer()  # Source line number is not an execution-order field.
    pc=integer(16)
    mask=integer(16)
    if not 0<=pc<=U64_MAX or not 0<=mask<(1<<32):
        raise ContractGap('PC_OR_MASK_OUT_OF_RANGE')
    nd=integer()
    if not 0<=nd<=1:  # trace_parser.h MAX_DST
        raise ContractGap('UNREVIEWED_DEST_COUNT')
    for _ in range(nd):
        if not re.fullmatch(r'(?:R|UR|P|UP)[0-9]+',take()):
            raise ContractGap('UNREVIEWED_REGISTER')
    opcode=take()
    ns=integer()
    if not 0<=ns<=4:  # trace_parser.h MAX_SRC
        raise ContractGap('UNREVIEWED_SOURCE_COUNT')
    for _ in range(ns):
        if not re.fullmatch(r'(?:R|UR|P|UP)[0-9]+',take()):
            raise ContractGap('UNREVIEWED_REGISTER')
    cls=classify(opcode,skip_l1)
    trace_width=integer()
    if trace_width<0:
        raise ContractGap('NEGATIVE_TRACE_WIDTH')
    mode=None
    width=0
    lanes=[]
    if trace_width:
        if cls in ('NON_MEMORY','CTA_BARRIER','FENCE'):
            raise ContractGap('UNCLASSIFIED_MEMORY_RECORD')
        width=opcode_width(opcode)
        mode=integer()
        active=[i for i in range(32) if mask & (1<<i)]
        if mode==0:
            addresses=[integer(16) for _ in active]
        elif mode==1:
            base=integer(16)
            stride=integer()
            if not -(1<<31)<=stride<(1<<31):
                raise ContractGap('STRIDE_OUTSIDE_FROZEN_INT32')
            if active and active!=list(range(active[0],active[-1]+1)):
                raise ContractGap('SPARSE_MASK_BASE_STRIDE_PRODUCER_CONTRACT_UNAVAILABLE')
            addresses=[base+i*stride for i in range(len(active))]
        elif mode==2:
            base=integer(16)
            addresses=[base] if active else []
            for _ in active[1:]:
                delta=integer()
                if not -(1<<63)<=delta<(1<<63):
                    raise ContractGap('DELTA_OUTSIDE_FROZEN_INT64')
                addresses.append(addresses[-1]+delta)
        else:
            raise ContractGap('UNREVIEWED_ADDRESS_MODE')
        for lane,address in zip(active,addresses):
            if not 0<=address<=U64_MAX or address+width-1>U64_MAX:
                raise ContractGap('ADDRESS_OVERFLOW_NO_SILENT_WRAP')
            lanes.append((lane,address))
    elif cls in ('CACHEABLE_GLOBAL_LOAD','BYPASS_GLOBAL_LOAD','ORDINARY_STORE','ATOMIC','SHARED','LOCAL'):
        raise ContractGap('MEMORY_OPCODE_WITHOUT_ADDRESS_FIELDS')
    # Frozen parser attempts an immediate with default zero, including when the
    # token is absent. Never interpret or retain that token as a load value.
    if len(words)-pos>1:
        raise ContractGap('UNREVIEWED_TRAILING_FIELDS')
    return Record(tuple(cta),warp,ordinal,pc,opcode,mask,trace_width,width,mode,tuple(lanes),cls)


def line_masks(record):
    """line -> (exact 128-bit byte mask, four-bit 32B sector mask)."""
    output={}
    for _,address in record.lanes:
        remaining=record.width
        while remaining:
            line=address & ~127
            offset=address-line
            count=min(remaining,128-offset)
            bm=((1<<count)-1)<<offset
            output[line]=output.get(line,0)|bm
            address+=count
            remaining-=count
    return {line:(bm,sum(1<<s for s in range(4) if (bm>>(32*s))&((1<<32)-1)))
            for line,bm in output.items()}


class WarpWriteHistory:
    """Intra-warp record-order candidates; no cross-warp time interpretation."""
    def __init__(self):
        self.writes={}
        self.last_ordinal={}

    def observe(self, record):
        identity=(record.cta,record.warp)
        if record.ordinal<=self.last_ordinal.get(identity,-1):
            raise ContractGap('NONMONOTONIC_INTRA_WARP_RECORD_ORDINAL')
        self.last_ordinal[identity]=record.ordinal
        candidates=[]
        if record.access_class=='CACHEABLE_GLOBAL_LOAD':
            for line,(bm,_) in line_masks(record).items():
                for write_pc,(write_bm,write_ordinal) in self.writes.get((identity,line),{}).items():
                    overlap=bm&write_bm
                    candidates.append(dict(write_pc=write_pc,read_pc=record.pc,line=line,
                        line_alias=True,byte_overlap=bool(overlap),overlap_byte_count=overlap.bit_count(),
                        last_contributing_write_record_ordinal=write_ordinal,read_record_ordinal=record.ordinal,
                        ordering='SAME_WARP_TRACE_RECORD_ORDER_ONLY',actual_happens_before='UNAVAILABLE',
                        actual_value='UNAVAILABLE'))
        elif record.access_class in ('ORDINARY_STORE','ATOMIC'):
            for line,(bm,_) in line_masks(record).items():
                seen=self.writes.setdefault((identity,line),{})
                old,_=seen.get(record.pc,(0,-1))
                # Union masks can span several instances of the same write PC;
                # ordinal is the last contributing record, not exact-pair time.
                seen[record.pc]=(old|bm,record.ordinal)
        return candidates
