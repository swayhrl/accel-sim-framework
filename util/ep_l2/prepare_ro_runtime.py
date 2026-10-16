#!/usr/bin/env python3
"""Bind frozen RO inputs to Core runtime flags; never runs or qualifies a simulator.

Full trace identity must additionally be checked by the Lane 5 runner at launch.
This tool consumes the existing preflight receipt, preserving its whole-commandlist
scope and coverage. It never re-parses/re-certifies the five frozen trace inputs.
"""
import argparse
import hashlib
import json
from pathlib import Path


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare(binding, manifest, ranges, output, detach, bypass):
    b=json.loads(binding.read_text());m=json.loads(manifest.read_text())
    if b['schema_version']!='EP_L2_RO_INPUT_BINDING_V1' or b['status']!='ORACLE_INPUT_VERIFIED_NOT_RUNTIME_QUALIFICATION':
        raise ValueError('not a verified input receipt')
    for key,value in [('epoch','whole_commandlist'),('scope','TRACE_MODEL_CLOSED_WORLD'),('address_domain','CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS')]:
        if b[key]!=value or m[key]!=value:raise ValueError('unsupported oracle scope: '+key)
    if m['unresolved_opcodes'] or m['schema']!='EP_L2_RO_ORACLE_V1':raise ValueError('uncertain certificate')
    if digest(manifest)!=b['oracle_manifest_sha256']:raise ValueError('manifest identity mismatch')
    if digest(ranges)!=b['certified_ranges_sha256'] or digest(ranges)!=m['artifacts']['certified_ranges.csv']:
        raise ValueError('range identity mismatch')
    for p in [manifest,ranges]:
        if any(c.isspace() for c in str(p.resolve())):raise ValueError('option parser path contains whitespace')
    output.mkdir(parents=True,exist_ok=False)
    config={
        'gpgpu_ep_l2_ro_tag_detach':int(detach),
        'gpgpu_ep_l2_ro_line_mshr_bypass':int(bypass),
        'gpgpu_ep_l2_ro_ranges':str(ranges.resolve()),
        'gpgpu_ep_l2_ro_ranges_sha256':digest(ranges),
        'gpgpu_ep_l2_ro_manifest':str(manifest.resolve()),
        'gpgpu_ep_l2_ro_manifest_sha256':digest(manifest),
        'gpgpu_ep_l2_ro_scope':'TRACE_MODEL_CLOSED_WORLD'}
    (output/'ro.config').write_text(''.join(f'-{k} {v}\n' for k,v in config.items()))
    receipt=dict(schema='EP_L2_RO_RUNTIME_CONFIG_V1',status='PREPARED_NOT_RUNTIME_QUALIFIED',
        input_binding_sha256=digest(binding),oracle_manifest_sha256=digest(manifest),
        certified_ranges_sha256=digest(ranges),runtime_ro_config_sha256=digest(output/'ro.config'),
        trace_content_sha256=b['trace_content_sha256'],commandlist_sha256=m['commandlist_sha256'],
        oracle_input_coverage=dict(unique_lines=b['eligible_unique_lines'],read_lane_references=b['eligible_read_lane_references']),
        epoch=b['epoch'],scope=b['scope'],features=dict(ro_tag_detach=bool(detach),ro_line_mshr_bypass=bool(bypass)),
        launch_gate='Lane5 verifies exact full trace content, source/binary/ordered complete config plus latest CURRENT_ACCEPTED scientific qualification; newer withdrawal overrides old immutable qualification and COMPLETE_VALID',
        required_repair_gates=['physical_bank_clock','memcpy_payload_identity'],
        scientific_acceptance='PENDING_LANE5_CURRENT_ACCEPTED',
        runtime_counters='accepted_global_reads, accepted_oracle_candidates, accepted_ro; requests at L2, distinct from input lane references')
    (output/'RUNTIME_CONFIG_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--binding',type=Path,required=True);p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--ranges',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--detach',type=int,choices=[0,1],required=True);p.add_argument('--bypass',type=int,choices=[0,1],required=True)
    a=p.parse_args();print(json.dumps(prepare(a.binding,a.manifest,a.ranges,a.output,a.detach,a.bypass)))


if __name__=='__main__':main()
