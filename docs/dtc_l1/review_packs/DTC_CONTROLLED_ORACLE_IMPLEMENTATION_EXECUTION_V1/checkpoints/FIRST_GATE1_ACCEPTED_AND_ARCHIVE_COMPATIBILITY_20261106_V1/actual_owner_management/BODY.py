import sys,os,json,hashlib,importlib.util,traceback
assert os.getpid()==1498278
assert int(open('/proc/self/stat').read().rsplit(')',1)[1].split()[19])==977758783
assert sys.modules['threading'].current_thread()is sys.modules['threading'].main_thread()
assert hashlib.sha256(open('/root/data/dtc_controlled_oracle_20261106_v1/control/postprocess_approval_alias_management_v1/oracle_postprocess_alias.py','rb').read()).hexdigest()=='5525945a40de4b28a9c28382bdb5829747d277413518f7250c74606c78c8c3f3'
try:
 _opa_spec=importlib.util.spec_from_file_location('dtc_oracle_closed_archive_alias_v1','/root/data/dtc_controlled_oracle_20261106_v1/control/postprocess_approval_alias_management_v1/oracle_postprocess_alias.py');_opa_module=importlib.util.module_from_spec(_opa_spec);sys.modules[_opa_spec.name]=_opa_module;_opa_spec.loader.exec_module(_opa_module)
 _opa_ack=_opa_module.install()
 with open('/root/data/dtc_controlled_oracle_20261106_v1/control/postprocess_approval_alias_management_v1/INSTALL_ACK.fixed.json','x')as _opa_h:json.dump(_opa_ack,_opa_h,sort_keys=True,indent=2);_opa_h.flush();os.fsync(_opa_h.fileno())
except BaseException:
 with open('/root/data/dtc_controlled_oracle_20261106_v1/control/postprocess_approval_alias_management_v1/INSTALL_ERROR.fixed.json','x')as _opa_h:json.dump(dict(traceback=traceback.format_exc(),no_blind_retry=True),_opa_h,sort_keys=True,indent=2);_opa_h.flush();os.fsync(_opa_h.fileno())
