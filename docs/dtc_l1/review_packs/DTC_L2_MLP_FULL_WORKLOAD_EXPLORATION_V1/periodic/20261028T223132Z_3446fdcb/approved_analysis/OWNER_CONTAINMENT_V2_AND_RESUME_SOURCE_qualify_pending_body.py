import pathlib,hashlib,json,importlib.util,tempfile
P=pathlib.Path;D=P(__file__).parent
sp=importlib.util.spec_from_file_location('pending_body',D/'pending_callback_body.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
for mode in ['wrong_source_sha','apply_raises_baseexception','logging_already_exists','success']:
    root=P(tempfile.mkdtemp(prefix='PRIVATE_PENDING_BODY_',dir=D));p=root/'fixture.py'
    p.write_text('def apply(directory):\n    '+('return None'if mode=='success'else'raise KeyboardInterrupt("PRIVATE_CPU_APPLY_EXCEPTION")')+'\n')
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    if mode=='wrong_source_sha':h='0'*64
    if mode=='logging_already_exists':(root/'CALLBACK_ERROR.json').write_text('existing immutable error\n')
    body=m.build_body(p,h,root);exec(compile(body,'private_pending_body','exec'),{})
    if mode=='success':assert not(root/'CALLBACK_ERROR.json').exists()
    elif mode=='logging_already_exists':assert(root/'CALLBACK_ERROR.json').read_text()=='existing immutable error\n'
    else:assert json.loads((root/'CALLBACK_ERROR.json').read_bytes())['original_owner_exception_contained']is True
    checks.append(mode+' returns normally without a C callback error claim')
result=dict(schema='MAIN_PENDING_BODY_CPU_V2',status='PASS',count=len(checks),checks=checks,builder_sha256=hashlib.sha256((D/'pending_callback_body.py').read_bytes()).hexdigest(),qualification_scope='Python body returns normally for success/preflight/apply/log errors; not a new actual C/API or model qualification.',model_starts=0,owner_mutations=0)
with (D/'PENDING_BODY_CPU_QUALIFICATION.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
