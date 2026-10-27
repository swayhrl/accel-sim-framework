import pathlib,importlib.util,argparse,json
P=pathlib.Path;D=P('/root/data/dtc_failure_repair_20261025_v1/ops/r20_archive_namespace_fix_20261027_v1')
ap=argparse.ArgumentParser();ap.add_argument('--cohort',required=True);args=ap.parse_args();s=importlib.util.spec_from_file_location('verified_namespace_reconciliation',D/'namespace_fix.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);p=m.plan();outbox=m.corrected_outbox(m.load('read_only_corrected_outbox',P(p['outbox_path'])),p);proof=outbox.verify(args.cohort);print(json.dumps(proof,indent=2))
