"""Retain original scientific intake; additionally bind unused runtime revisions."""
import pathlib,importlib.util
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
original=load('unchanged_whole_input_spec_producer','sweep_admission.py');oldnative=load('unchanged_original_scientific_authority','sweep_native.py');effective=load('effective_observational_spec_producer','sweep_cap1m_specs.py')
grouped_candidates=original.grouped_candidates
def admit(key,native):
 result=original.admit(key,oldnative)
 return effective.register_input(result,native) if result['state']=='ADMITTED_FULL_INPUT' else result
