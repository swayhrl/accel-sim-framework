#!/usr/bin/env python3
"""Unregistered pure-CPU strict metadata validator; never opens binary/cubin/trace or invokes tools."""
import hashlib,importlib.util,pathlib,re,collections
BASE_SHA='b59c42354680a49f138e4510b845f1c3292d2137bb0a90cc658a543b6eaf0cb0'
P=pathlib.Path(__file__).with_name('existing_static_reopen_adapter_v1.py')
assert hashlib.sha256(P.read_bytes()).hexdigest()==BASE_SHA,'reviewed base source drift'
SP=importlib.util.spec_from_file_location('reviewed_original_static',P)
BASE=importlib.util.module_from_spec(SP);SP.loader.exec_module(BASE)
def validate_existing_manifest(task,manifest,map_bytes):
 try:result=BASE.validate_existing_manifest(task,manifest,map_bytes)
 except (KeyError,TypeError,ValueError,IndexError,AttributeError) as error:
  return {'status':'HOLD','gate_eligible':False,'validation_errors':['MALFORMED_STATIC_METADATA'],'detail':repr(error),'whole_runtime_or_consumer_qualified':False,'candidate_registered':False}
 # This guard can only retain or reduce eligibility, never promote an original HOLD.
 if not result.get('gate_eligible'):return dict(result,candidate_registered=False)
 checks=[];errors=[]
 def check(name,ok,detail):
  checks.append({'name':name,'passed':bool(ok),'detail':detail})
  if not ok:errors.append(name)
 for image in manifest['cubins']:
  check('strict_JSON_disassembler_exit',type(image.get('nvdisasm_json_exit'))is int and image['nvdisasm_json_exit']==0,'FULL/EMPTY closure labels cannot conceal a failed or absent original JSON tool exit')
  check('strict_cubin_digest_grammar',bool(re.fullmatch('[0-9a-f]{64}',str(image.get('sha256')))),'A64-character label is not necessarily a SHA256 digest')
  check('strict_image_count_types',type(image.get('instructions'))is int and type(image.get('json_instruction_count'))is int,'Reject booleans or coerced JSON numeric fields')
 for row in manifest['instructions']:
  check('strict_SASS_field',isinstance(row.get('sass'),str)and bool(row['sass'].strip())and not any(x in row['sass']for x in '\t\r\n'),'One nonempty TSV field; no extra column/line injection')
 census=task['census'];listed=re.findall(r'^ELF file\s+\d+:\s+(.+)$',census.get('listing',''),re.M)
 check('strict_census_tool_exit',type(census.get('tool_exit'))is int and census['tool_exit']==0,'Independent ELF listing closed successfully')
 check('strict_census_listing_SHA',hashlib.sha256(census.get('listing','').encode()).hexdigest()==census.get('listing_sha256'),'Close raw listing text to its frozen digest')
 check('strict_census_names_count',listed==census.get('cubin_names')and type(census.get('cubin_count'))is int and len(listed)==census['cubin_count'],'Independent raw listing names/count agree')
 out=dict(result);out['checks']=result['checks']+checks;out['validation_errors']=result['validation_errors']+errors
 out['status']='HOLD'if errors else'PASS';out['gate_eligible']=not errors;out['whole_runtime_or_consumer_qualified']=False
 out['candidate_source_sha256']=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
 out['candidate_registered']=False;out['gate_scope']='Existing pinned complete static metadata reopening only; new plans/packets still require independent Root admission'
 return out
