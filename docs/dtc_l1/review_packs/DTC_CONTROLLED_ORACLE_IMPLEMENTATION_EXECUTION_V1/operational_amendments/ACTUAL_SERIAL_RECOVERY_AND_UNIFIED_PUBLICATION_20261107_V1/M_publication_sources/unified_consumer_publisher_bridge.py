"""Read-only bridge matching the existing publisher snapshot API."""
import importlib.util,json,hashlib
from pathlib import Path
ADAPTER_PATH='/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/M_clean_successor_unified_consumer_v2/oracle_unified_roots_consumer.py'
ADAPTER_SHA256='4388a852d49319735a6fee2a82ba8b628f666aa4e71f8bbb6ce3e9b34e303c23'
def snapshot(bindings_path,matrix_path,out_dir):
 p=Path(ADAPTER_PATH)
 if hashlib.sha256(p.read_bytes()).hexdigest()!=ADAPTER_SHA256:raise ValueError('REVIEWED_ADAPTER_PIN_DRIFT')
 cfg=json.loads(Path(bindings_path).read_bytes())
 if Path(cfg['fixed_matrix']['path']).resolve()!=Path(matrix_path).resolve():raise ValueError('WRONG_PUBLISHER_FIXED_MATRIX')
 spec=importlib.util.spec_from_file_location('readonly_unified_adapter',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m.snapshot_once(bindings_path,out_dir)
