"""Contain the *outermost* PyRun_SimpleString payload before body loading.

No queue or execution on import; the existing a28 inner builder is unchanged.
"""
def build_payload(body_path,body_sha256,error_path):
 return '''try:
 import pathlib as _dtc_shared_p, hashlib as _dtc_shared_h
 _dtc_shared_body_path = _dtc_shared_p.Path(__BODY_PATH_LITERAL__)
 _dtc_shared_body_bytes = _dtc_shared_body_path.read_bytes()
 assert _dtc_shared_h.sha256(_dtc_shared_body_bytes).hexdigest() == __BODY_SHA_LITERAL__, 'SHARED_PENDING_BODY_SHA_DRIFT'
 exec(compile(_dtc_shared_body_bytes, str(_dtc_shared_body_path), 'exec'), {})
except BaseException as _dtc_shared_outer_error:
 try:
  import pathlib as _dtc_shared_err_p, json as _dtc_shared_err_j, datetime as _dtc_shared_err_d
  _dtc_shared_error_value = dict(status='SHARED_OUTERMOST_PAYLOAD_EXCEPTION_CONTAINED',error=repr(_dtc_shared_outer_error),UTC=_dtc_shared_err_d.datetime.now(_dtc_shared_err_d.timezone.utc).isoformat(),automatic_requeue=False)
  with _dtc_shared_err_p.Path(__ERROR_PATH_LITERAL__).open('x') as _dtc_shared_error_file:
   _dtc_shared_err_j.dump(_dtc_shared_error_value,_dtc_shared_error_file,sort_keys=True,indent=2)
   _dtc_shared_error_file.write('\\n')
 except BaseException:
  pass
'''.replace('__BODY_PATH_LITERAL__',repr(str(body_path))).replace('__BODY_SHA_LITERAL__',repr(body_sha256)).replace('__ERROR_PATH_LITERAL__',repr(str(error_path)))
