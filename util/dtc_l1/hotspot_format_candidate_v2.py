#!/usr/bin/env python3
"""Offline candidate for one fixed Hotspot member, conditional on source profile.

Default: report only. --candidate-output writes a NEW derived file; never edits
the original, main parser, running binaries, registry or admission holds.
Passing checks qualifies this candidate model, not immutable capture identity.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import tempfile

def require(condition, detail="Fixed Hotspot source-profile contract failed"):
    if not condition:
        raise ValueError(detail)


MEMBER_SHA = 'ea268780903d10f61a36634bf90f8b00b7e160c1e0703d345efd4ab3e9c3f1b8'
SASS_SHA = '079d8b4d07c53f4c7bae0a9a9f484ceb2ff8eb3ad7487e1128eb68373472ec06'
EXPECTED = {'0180':1364, '0190':1364, '0290':1364, '02a0':1364, '0ab0':58652, '0ac0':58652}
SHARED_OFFSETS = {'0290':0, '02a0':1024, '0ab0':2048, '0ac0':0}


def frozen(base, stride, lanes):
    previous = lanes[0]-1
    gap = False
    values = []
    for lane in lanes:
        gap |= lane != previous+1
        values.append(0 if gap else base+(lane-lanes[0])*stride)
        previous = lane
    return values


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--member',type=Path,required=True)
    ap.add_argument('--profile-validation',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--candidate-output',type=Path)
    a = ap.parse_args()
    profile = json.loads(a.profile_validation.read_text())
    require(profile['status']=='PASS_CANDIDATE_SOURCE_PROFILE_NOT_IMMUTABLE_CAPTURE_RECEIPT', 'Fixed Hotspot source-profile contract failed')
    require(profile['member_sha256']==MEMBER_SHA and profile['source_profile_sass_sha256']==SASS_SHA, 'Fixed Hotspot source-profile contract failed')
    require(profile['counts']['records']==13169524 and profile['counts']['active_instructions']==377291004, 'Fixed Hotspot source-profile contract failed')
    require(not profile['failures'], 'Fixed Hotspot source-profile contract failed')
    require(a.member.stat().st_size==1041309456, 'Fixed Hotspot source-profile contract failed')
    require(a.report.resolve()!=a.member.resolve(), 'Fixed Hotspot source-profile contract failed')
    require(not a.report.exists() and a.member.resolve().parent not in a.report.resolve().parents, 'Fixed Hotspot source-profile contract failed')
    if a.candidate_output:
        dest = a.candidate_output.resolve()
        require(not dest.exists() and a.member.resolve().parent not in dest.parents, 'Fixed Hotspot source-profile contract failed')
        require(dest!=a.report.resolve(), 'Fixed Hotspot source-profile contract failed')
        dest.parent.mkdir(parents=True,exist_ok=True)
        temp = tempfile.NamedTemporaryFile(mode='wb',dir=dest.parent,prefix='.hotspot-candidate-',delete=False)
    else:
        temp = None
    original = hashlib.sha256()
    candidate = hashlib.sha256()
    counts = Counter()
    changed_lanes = Counter()
    try:
        with a.member.open('rb') as f:
            for line in f:
                original.update(line)
                output = line
                # Limit parsing and transformations to the six proven delta PCs.
                prefix = line.split(maxsplit=5)
                if len(prefix)==6 and prefix[4].decode(errors='replace') in EXPECTED:
                    t=line.split();pc=t[4].decode();warp=int(t[3]);mask=int(t[5],16)
                    lanes=[s for s in range(32) if mask>>s&1]
                    j=7+int(t[6]);nsrc=int(t[j+1]);width_index=j+2+nsrc;mode_index=width_index+1
                    require(t[width_index]==b'4', 'Fixed Hotspot source-profile contract failed')
                    mode=int(t[mode_index])
                    if lanes:
                        if pc in SHARED_OFFSETS:
                            require(mode in [0,1], 'Fixed Hotspot source-profile contract failed')
                            values=[(warp*32+s)*4+SHARED_OFFSETS[pc] for s in lanes]
                            if mode==1:
                                base=int(t[mode_index+1],16);stride=int(t[mode_index+2]);before=frozen(base,stride,lanes)
                            else:
                                before=[int(v,16) for v in t[mode_index+1:]]
                                require(before==values, 'Fixed Hotspot source-profile contract failed')
                        else:
                            require(mode==0, 'Fixed Hotspot source-profile contract failed')
                            raw=[int(v,16) for v in t[mode_index+1:]]
                            before=raw[:len(lanes)]
                            require(len(raw) in [32,len(lanes)], 'Fixed Hotspot source-profile contract failed')
                            values=[raw[s] for s in lanes] if len(raw)==32 else raw
                        if before!=values:
                            counts[pc]+=1
                            changed_lanes[pc]+=sum(v!=w for v,w in zip(before,values))
                            output=b' '.join(t[:mode_index]+[b'0']+[f'0x{v:016x}'.encode() for v in values])+b' \n'
                            # Explicit mode0 round-trip is checked against values
                            # derived independently from source/raw lane vectors.
                            parsed=output.split()
                            require(int(parsed[mode_index])==0, 'Fixed Hotspot source-profile contract failed')
                            require([int(v,16) for v in parsed[mode_index+1:]]==values, 'Fixed Hotspot source-profile contract failed')
                candidate.update(output)
                if temp:
                    temp.write(output)
        require(original.hexdigest()==MEMBER_SHA, 'Fixed Hotspot source-profile contract failed')
        require(dict(counts)==EXPECTED, dict(counts))
        require(sum(counts.values())==122760 and sum(changed_lanes.values())==2944024, 'Fixed Hotspot source-profile contract failed')
        if temp:
            temp.close()
            # Exclusive destination publication; an existing file is never replaced.
            import os
            os.link(temp.name,dest)
            Path(temp.name).unlink()
        receipt=dict(status='OFFLINE_SOURCE_PROFILE_CANDIDATE_ONLY_NOT_ADMITTED',
                     original_member=str(a.member), original_sha256=original.hexdigest(),
                     candidate_member=str(a.candidate_output) if temp else None,
                     candidate_sha256=candidate.hexdigest(), changed_records=dict(counts),
                     changed_lanes=dict(changed_lanes),
                     profile_validation_sha256=hashlib.sha256(a.profile_validation.read_bytes()).hexdigest(),
                     source_profile_sass_sha256=SASS_SHA,
                     original_parser_changed=False, original_trace_changed=False,
                     hold_released=False, capture_binary_identity='NOT_ESTABLISHED_REQUIRES_REVIEW')
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt),flush=True)
    finally:
        if temp:
            temp.close()
            Path(temp.name).unlink(missing_ok=True)


if __name__=='__main__':
    main()
