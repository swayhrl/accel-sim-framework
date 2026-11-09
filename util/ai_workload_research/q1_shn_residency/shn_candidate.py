"""Opt-in shN state owner for the frozen Q1 late pipeline.

No CUDA is initialized by importing this module. All tensors are FP32. The
counter and U remain the original CPUAdam's CPU metadata; only shN state,
gradient and next-camera parameter production move to the chosen device.
"""
import ast
import copy
import hashlib
import math
import struct


def f32(x):
    return struct.unpack("f", struct.pack("f", float(x)))[0]


def coefficients(step, lr, beta1, beta2, eps):
    """Mirror the C++ correction table, including its FP32 stored entries."""
    assert step >= 17, "late-window CPUAdam correction requires step>=17"
    b1, b2, lr, eps = map(f32, (beta1, beta2, lr, eps))
    bc1 = f32(1 - math.pow(b1, step))
    bc2 = f32(1 - math.pow(b2, step))
    step_size = f32(lr / bc1)
    sqrt_bc2 = f32(math.sqrt(bc2))
    scale = f32(b1 / math.sqrt(b2))
    correction = [0.0] * 16
    p1 = [0.0] * 16
    p2 = [0.0] * 16
    p1[0], p1[1] = b1, f32(b1*b1)
    p2[0], p2[1] = b2, f32(b2*b2)
    correction[1] = f32((lr*b1) / (math.sqrt(b2/(1-math.pow(b2,step-1))) * (1-math.pow(b1,step-1))))
    for i in range(2, 16):
        term = f32((lr*b1) / (math.sqrt(b2/(1-math.pow(b2,step-i))) * (1-math.pow(b1,step-i))))
        correction[i] = f32(f32(scale*correction[i-1]) + term)
        p1[i] = f32(b1*p1[i-1])
        p2[i] = f32(b2*p2[i-1])
    return correction, p1, p2, step_size, sqrt_bc2, eps


class ShNResident:
    def __init__(self, weight, grad, exp_avg, exp_avg_sq, chunk_rows=32768):
        import torch
        assert all(x.dtype == torch.float32 and x.device == weight.device for x in (weight, grad, exp_avg, exp_avg_sq))
        assert all(x.shape == weight.shape for x in (grad, exp_avg, exp_avg_sq))
        self.weight, self.grad, self.m, self.v = weight, grad, exp_avg, exp_avg_sq
        self.chunk_rows = chunk_rows

    def _rows(self, cpu_ids, cpu_counter, step, lr, b1, b2, eps, mutate):
        import torch
        assert cpu_ids.device.type == cpu_counter.device.type == "cpu"
        assert cpu_counter.dtype == torch.int8
        assert cpu_ids.dtype in (torch.int32, torch.int64)
        assert self.chunk_rows > 0
        effective_step = int(step) if mutate else int(step) + 1
        correction, p1, p2, step_size, sqrt_bc2, eps = coefficients(effective_step, lr, b1, b2, eps)
        tables = [torch.tensor(x, dtype=torch.float32, device=self.weight.device) for x in (correction, p1, p2)]
        outputs = []
        with torch.no_grad():
            for begin in range(0, cpu_ids.numel(), self.chunk_rows):
                part = cpu_ids[begin:begin+self.chunk_rows].long()
                age_cpu = cpu_counter.index_select(0, part)
                assert bool(((age_cpu >= 0) & (age_cpu <= 15)).all()), "counter outside frozen correction table"
                idx = part.to(self.weight.device)
                age = age_cpu.long().to(self.weight.device)
                shape = (-1,) + (1,) * (self.weight.ndim-1)
                c, b1p, b2p = (tab.index_select(0, age).reshape(shape) for tab in tables)
                w = self.weight.index_select(0, idx)
                g = self.grad.index_select(0, idx)
                m0 = self.m.index_select(0, idx)
                v0 = self.v.index_select(0, idx)
                m = b1p*m0 + (1-f32(b1))*g
                v = b2p*v0 + (1-f32(b2))*g*g
                restored = w - (c*m0)/(torch.sqrt(v0)+eps)
                result = restored - step_size*m/(torch.sqrt(v)/sqrt_bc2+eps)
                if mutate:
                    assert part.unique().numel() == part.numel(), "update U must be unique"
                    self.weight.index_copy_(0, idx, result)
                    self.m.index_copy_(0, idx, m)
                    self.v.index_copy_(0, idx, v)
                else:
                    outputs.append(result)
        if mutate:
            return None
        return torch.cat(outputs, dim=0) if outputs else self.weight.new_empty((0,)+tuple(self.weight.shape[1:]))

    def update(self, update_ids_cpu, counter_cpu, step, lr, b1, b2, eps):
        return self._rows(update_ids_cpu, counter_cpu, step, lr, b1, b2, eps, True)

    def forward(self, visible_ids_cpu, counter_cpu, step, lr, b1, b2, eps):
        return self._rows(visible_ids_cpu, counter_cpu, step, lr, b1, b2, eps, False)


def install(module, source, controller, loader_factory, diagnostic=False, enabled=False):
    """Keep the old OFF transform verbatim; replace only three shN statements for ON."""
    from source_transform import install as original_install, transform_train
    if not enabled:
        return original_install(module, source, controller, loader_factory, diagnostic)
    # Install original hooks and then replace the transformed train function.
    info = original_install(module, source, controller, loader_factory, diagnostic)
    fn = transform_train(source, diagnostic=False)
    class Patch(ast.NodeTransformer):
        def visit_Assign(self, node):
            if node.lineno > 1100 and node.lineno < 1200 and any(isinstance(t, ast.Name) and t.id == "colorsN_cpu_grad" for t in node.targets):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "empty_like":
                    return ast.copy_location(ast.Pass(), node)
            return self.generic_visit(node)
        def visit_Expr(self, node):
            if 1100 < node.lineno < 1200 and "colorsN_cpu_grad.copy_" in ast.unparse(node):
                return ast.copy_location(ast.parse("colorsN_cpu_grad = colorsN_grad.detach()").body[0], node)
            return self.generic_visit(node)
        def visit_If(self, node):
            if node.lineno > 1200 and "count < 180000" in ast.unparse(node.test):
                return ast.copy_location(ast.parse("colorsN = _q1_shn.forward(valid_ids_cpu, counter, s, lr, b1, b2, eps)").body[0], node)
            return self.generic_visit(node)
        def visit_Call(self, node):
            node = self.generic_visit(node)
            if isinstance(node.func, ast.Name) and node.func.id == "cpu_optimizer_parallel":
                node.func.id = "_q1_shn_cpu_optimizer_parallel"
            return node
    fn = Patch().visit(fn)
    ast.fix_missing_locations(fn)
    module.__dict__["_q1_shn"] = controller.shn
    module.__dict__["_q1_shn_cpu_optimizer_parallel"] = controller.cpu_optimizer_parallel
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(module.__file__)+"[shn-resident]", "exec"), module.__dict__)
    module.Runner.train = module.__dict__["q1_train"]
    info["candidate_train_ast_sha256"] = hashlib.sha256(ast.dump(fn, include_attributes=False).encode()).hexdigest()
    info["candidate_scope"] = "opt-in shN owner/update/next-camera production only"
    return info


def attach_controller(ctl):
    """Attach migration after the original byte-exact restore check."""
    import torch
    from cpu_adam import adam_deferred_update, update_counter
    original = ctl.assert_restored
    def restored(runner, schedulers, loc):
        original(runner, schedulers, loc)
        if not ctl.job.get("shn_resident", False):
            return
        old = runner.splats["shN"]
        opt = runner.optimizers_cpu["shN"]
        state = opt.state.pop(old)
        new = torch.nn.Parameter(old.detach().to("cuda:0"), requires_grad=old.requires_grad)
        new.grad = old.grad.detach().to("cuda:0")
        state["exp_avg"] = state["exp_avg"].to("cuda:0")
        state["exp_avg_sq"] = state["exp_avg_sq"].to("cuda:0")
        opt.state[new] = state
        opt.param_groups[0]["params"] = [new]
        runner.splats["shN"] = new
        ctl.shn = ShNResident(new.data, new.grad, state["exp_avg"], state["exp_avg_sq"])
        # The AST function resolves this proxy at call time after migration.
        ctl.shn_proxy.target = ctl.shn
    ctl.assert_restored = restored
    def cpu_optimizer_parallel(valid, update_ids, counter, w1,w2,w3,g1,g2,g3,m1,m2,m3,v1,v2,v3,lr1,lr2,lr3,step,b1,b2,eps):
        with torch.no_grad():
            adam_deferred_update(w1,g1,m1,v1,update_ids,counter,step,lr1,b1,b2,eps)
            adam_deferred_update(w2,g2,m2,v2,update_ids,counter,step,lr2,b1,b2,eps)
            ctl.shn.update(update_ids,counter,step,lr3,b1,b2,eps)
            update_counter(counter,update_ids)
            g1[valid] = 0;g2[valid] = 0;g3[valid] = 0
        return 1
    ctl.cpu_optimizer_parallel = cpu_optimizer_parallel
    class Proxy:
        target = None
        def forward(self,*a):
            assert self.target is not None, "shN migration incomplete"
            return self.target.forward(*a)
    ctl.shn_proxy = Proxy()
    ctl.shn = ctl.shn_proxy
