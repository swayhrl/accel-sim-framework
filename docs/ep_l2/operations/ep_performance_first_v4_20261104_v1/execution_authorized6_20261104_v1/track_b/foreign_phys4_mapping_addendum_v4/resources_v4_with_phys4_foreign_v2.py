"""Main-consumable V4 resource helper plus one strictly mapped foreignfirst4.
Default API only reads. Preserves prior exact3 new request map/admit/forecast.
"""
from pathlib import Path
import hashlib,importlib.util
HERE=Path(__file__).resolve().parent
MAIN=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/main/qualified_resources_v4/resources_v4.py');MAIN_SHA='ee5cc3ba4c49ed95a1ac110e52dc0123d8f90c4a166da4f3ca00bc0e01b73303'
MAPPER=HERE/'strict_phys4_foreign_mapper_v2.py';MAPPER_SHA='798703945fa39110267cdc877edb941b9dc8c46d333a48d202476743a542004f'
PINS=HERE/'EXACT_FOREIGN_AUTHORITY_SOURCE_PINS.json';PINS_SHA='af0b0995aa41df17be091898aba91553faa3423fe92c313d522da3ca2d8a4ad9'
def load(n,p,h):
 if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('qualified resource dependency drift '+str(p))
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def shared():
 main=load('unchanged_Main_V4_resource_helper',MAIN,MAIN_SHA);mapper=load('strict_foreign_PHYS4_only_mapper',MAPPER,MAPPER_SHA)
 if hashlib.sha256(PINS.read_bytes()).hexdigest()!=PINS_SHA:raise ValueError('foreign mapping authority pins drift')
 return main,mapper.attach(main.shared())
def snapshot(request):
 main,resource=shared()
 main.need(request in main.NEW_SCOPES,'outside exact V4 resource scopes')
 s=resource.snapshot(request);main.need(s.get('current_request')==request,'snapshot request mismatch')
 s['V4_private_scope_map']={k:str(v)for k,v in main.NEW_SCOPES.items()};s['V4_resource_mapping_is_not_science_authorization']=True;s['strict_foreign_PHYS4_mapping_added']=True
 return s
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 main=load('unchanged_Main_V4_resource_admission',MAIN,MAIN_SHA)
 return main.admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):
 main=load('unchanged_Main_V4_resource_forecast',MAIN,MAIN_SHA)
 return main.forecast(input_id,history,policy=policy)
