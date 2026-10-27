"""Explicit private-instance splice UNDER the already installed CPU wrapper.
No import-time mutation. No source/code objects, specs or actual models change.
"""
import threading
from frame_read_guard import FrameReadGuard

CPU_MARKER = 'DTC_L2_MLP_ZERO_START_CPU_REBIND_V1'
MARKER = 'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1'


def original_cell(wrapper):
    names = wrapper.__code__.co_freevars
    assert names.count('original') == 1, 'CPU original closure shape changed'
    return wrapper.__closure__[names.index('original')]


def install_in_owner(main, aging, res, owner_assert, sleeper=None):
    assert threading.current_thread() is threading.main_thread()
    owner_assert()
    with aging.lock:
        assert not hasattr(main, MARKER), 'Guard already coupled'
        cpu = getattr(main, CPU_MARKER)
        assert cpu['res'] is res and res.choose_dispatch is cpu['wrapper']
        cell = original_cell(cpu['wrapper'])
        old = aging.wrapper
        assert cell.cell_contents is old and cpu['original'] is old
        assert aging.installed is res, 'Expected already installed E owner'
        gate = FrameReadGuard(aging, **({'sleeper':sleeper} if sleeper else {}))
        state = dict(gate=gate, aging=aging, res=res, cpu=cpu, cell=cell,
                     old_aging_wrapper=old, cpu_wrapper=cpu['wrapper'])
        try:
            cell.cell_contents = gate.wrapper
            cpu['original'] = gate.wrapper
            aging.wrapper = gate.wrapper
            setattr(main, MARKER, state)
        except BaseException:
            cell.cell_contents = old
            cpu['original'] = old
            aging.wrapper = old
            if hasattr(main, MARKER):delattr(main, MARKER)
            raise
        assert res.choose_dispatch is cpu['wrapper']
        return dict(status='COUPLED_INSIDE_EXISTING_CPU_WRAPPER',
                    path='CPU -> frame guard -> unchanged E.choose -> B',
                    cpu_outer_preserved=True, code_objects_changed=False,
                    models_started=0, signals_sent=0)


def restore_in_owner(main, owner_assert):
    assert threading.current_thread() is threading.main_thread()
    owner_assert()
    state = getattr(main, MARKER)
    aging=state['aging'];res=state['res'];cpu=state['cpu'];gate=state['gate']
    with aging.lock:
        assert aging.wrapper is gate.wrapper and state['cell'].cell_contents is gate.wrapper
        assert cpu['original'] is gate.wrapper
        if hasattr(main, CPU_MARKER):
            assert getattr(main, CPU_MARKER) is cpu and res.choose_dispatch is cpu['wrapper']
        else:
            # CPU.restore legitimately exposes guard as its saved original.
            assert res.choose_dispatch is gate.wrapper, 'Restore newer outer wrapper first'
            res.choose_dispatch = state['old_aging_wrapper']
        state['cell'].cell_contents = state['old_aging_wrapper']
        cpu['original'] = state['old_aging_wrapper']
        aging.wrapper = state['old_aging_wrapper']
        delattr(main, MARKER)
        return dict(status='PRIVATE_GUARD_SPLICE_RESTORED', models_untouched=True,
                    bindings_not_rolled_back=True)
