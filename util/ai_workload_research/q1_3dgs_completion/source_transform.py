"""Q1 control wrappers around frozen author statements; pure AST, no GPU imports."""
import ast, copy, hashlib
LIVE_KEYS = (
    "is_densify", "counter", "valid_ids", "valid_ids_cpu", "valid_ids_cpu_prev",
    "camtoworlds", "Ks", "pixels", "image_ids", "masks", "height", "width",
    "opacities", "colors0", "colorsN",
)
def _parse(s): return ast.parse(s).body
def transform_train(source, diagnostic=False):
    tree=ast.parse(source)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="Runner")
    fn=copy.deepcopy(next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="train"))
    loop=next(n for n in fn.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=="step")
    old_body=copy.deepcopy(loop.body)
    # Original math and order remain inside the original function/loop frame.
    for n in ast.walk(fn):
        if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=="init_step" for x in n.targets):
            n.value=ast.parse("_q1_ctl.resume_next_step",mode="eval").body
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="DataLoader":
            n.func=ast.Name(id="_q1_make_loader",ctx=ast.Load())
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Attribute) and isinstance(n.func.value.value,ast.Name) and n.func.value.value.id=="tqdm" and n.func.attr=="tqdm":
            pass
    rewritten=[]
    prologue=[]
    for n in fn.body:
        if isinstance(n,ast.Assign) and 995<=n.lineno<=998:
            rewritten.append(ast.If(test=ast.parse("not _q1_ctl.resuming",mode="eval").body,body=[n],orelse=[]))
        elif 1006<=getattr(n,"lineno",0)<=1009:
            prologue.append(n)
            if n.lineno==1009:
                restore=_parse("\n".join(k+" = _q1_ctl.resume_live["+repr(k)+"]" for k in LIVE_KEYS)+"\n_q1_ctl.restore_schedule(schedulers, self)\n_q1_ctl.assert_restored(self, schedulers, locals())\n")
                rewritten.append(ast.If(test=ast.parse("not _q1_ctl.resuming",mode="eval").body,body=prologue,orelse=restore))
        else: rewritten.append(n)
    fn.body=rewritten
    loop.body=_parse("_q1_ctl.before(self, step, locals())")+loop.body+_parse("_q1_ctl.after(self, step, locals())")
    if diagnostic:
        fn=instrument(fn,source)
    fn.name="q1_train"
    ast.fix_missing_locations(fn)
    return fn
def instrument(fn,source):
    class Regions(ast.NodeTransformer):
        def visit_Assign(self,n): return self.wrap(n)
        def visit_Expr(self,n): return self.wrap(n)
        def wrap(self,n):
            text=ast.get_source_segment(source,n) or ""
            # Added control nodes have no author source segment; never diagnose them.
            if "_q1_ctl" in ast.unparse(n): return n
            tag=None
            if "torch.cuda.synchronize()" in text:tag="synchronize"
            elif "subthread.join()" in text:tag="join"
            elif "cpu_optimizer_parallel(" in text:tag="cpu_adam"
            elif "calculate_update_ids(" in text:tag="cpu_id_selection"
            elif "adam_for_next_with_counter(" in text:tag="cpu_parameter_forwarding_adam"
            elif "frustum_culling_gpu(" in text:tag="frustum_launch_host"
            elif ".pin_memory().to(" in text:tag="parameter_H2D_enqueue"
            elif '.to("cpu"' in text:
                tag="ID_D2H_host" if "valid_ids_cpu" in text and "info[" not in text else "metadata_D2H_host"
            elif ".copy_(" in text:
                calls=[c for c in ast.walk(n) if isinstance(c,ast.Call) and isinstance(c.func,ast.Attribute) and c.func.attr=="copy_"]
                def base(x):
                    while isinstance(x,(ast.Subscript,ast.Attribute)):x=x.value
                    return x.id if isinstance(x,ast.Name) else None
                names={base(c.func.value) for c in calls}
                if names & {"colorsN","colors0","opacities"}:tag="parameter_H2D_enqueue"
                elif names & {"opacities_cpu_grad","colors0_cpu_grad","colorsN_cpu_grad"}:tag="gradient_D2H_host"
                else:tag="unclassified_copy_host"
            if tag is None:return n
            tag+="@L"+str(n.lineno)
            before=_parse("_q1_ctl.region_begin("+repr(tag)+")")[0]
            after=_parse("_q1_ctl.region_end("+repr(tag)+")")[0]
            return [ast.copy_location(before,n),n,ast.copy_location(after,n)]
    class Transfers(ast.NodeTransformer):
        def visit_Call(self,n):
            n=self.generic_visit(n)
            if isinstance(n.func,ast.Attribute) and n.func.attr in {"copy_","to"}:
                receiver=n.func.value
                name="_q1_copy" if n.func.attr=="copy_" else "_q1_to"
                n.func=ast.Name(id=name,ctx=ast.Load());n.args=[receiver]+n.args
            return n
    return Transfers().visit(Regions().visit(fn))
def transform_gpu(source):
    cls=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=="Runner")
    fn=copy.deepcopy(next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="gpu_forward_backward"))
    fn=instrument(fn,source);fn.name="q1_gpu_forward_backward"
    ast.fix_missing_locations(fn);return fn
def install(module,source,controller,loader_factory,diagnostic=False):
    module.__dict__.update(_q1_ctl=controller,_q1_make_loader=loader_factory,
                           _q1_copy=controller.transfer.copy_,_q1_to=controller.transfer.to)
    fn=transform_train(source,diagnostic)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(module.__file__)+"[q1-control]", "exec"),module.__dict__)
    module.Runner.train=module.__dict__["q1_train"]
    if diagnostic:
        gpu=transform_gpu(source)
        exec(compile(ast.Module(body=[gpu],type_ignores=[]),str(module.__file__)+"[q1-observer]", "exec"),module.__dict__)
        module.Runner.gpu_forward_backward=module.__dict__["q1_gpu_forward_backward"]
    return {"train_ast_sha256":hashlib.sha256(ast.dump(fn,include_attributes=False).encode()).hexdigest(),
            "control_scope":"Original function and loop frame; same author math/order; loader persistence, exact restore branch, pre/post control callbacks. OFF has no region instrumentation."}
