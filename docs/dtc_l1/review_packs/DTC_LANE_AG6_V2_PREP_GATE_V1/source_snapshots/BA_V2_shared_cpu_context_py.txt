"""PREPARED_NOT_TESTED. Bind peer views to one actual direct-Popen CPU manager.

CPU-only glue; no process creation/signals/locks. The exact manager source,
entrypoint, executable, argv and requests are published by the CPU qualifier.
No peer is discovered or adopted by basename, directory or arbitrary PPID.
"""
import hashlib
import json
import os
from pathlib import Path
import time

from shared_authority import require, verified_peer_view

HERE = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

class CPUContext:
    def __init__(self, request, identity_reader, process_reader):
        require(request['purpose'] == 'CPU_FIXTURE', 'CPU_CONTEXT_NOT_SIMULATION_AUTHORITY')
        self.request = request
        self.identity = identity_reader
        self.process = process_reader
        self.path = Path(request['shared_cpu_registry'])
        self.manager = identity_reader(os.getppid())
        self.manager_role = request['shared_manager_role']
        require(self.manager['pid'] == os.getppid(), 'DIRECT_CPU_MANAGER_REQUIRED')
        self.read_registry()

    def read_registry(self):
        data = json.loads(self.path.read_text())
        role = self.manager_role
        manager = self.process(self.manager['pid'])
        require(manager is not None, 'CPU_MANAGER_ABSENT')
        require(manager['start_ticks'] == self.manager['start_ticks'], 'CPU_MANAGER_PID_REUSED')
        require(manager['argv'] in role['argvs'] and manager['cwd'] == role['cwd'], 'CPU_MANAGER_ARGV_OR_CWD_CHANGED')
        require(manager['exe'] == role['executable'] and sha(manager['exe']) == role['executable_sha256'], 'CPU_MANAGER_ELF_CHANGED')
        for path, digest in role['source_sha256'].items():
            require(sha(path) == digest, 'CPU_MANAGER_SOURCE_CHANGED:' + path)
        require(data['manager']['pid'] == self.manager['pid'] and data['manager']['start_ticks'] == self.manager['start_ticks'], 'CPU_REGISTRY_PUBLISHER_CHANGED')
        require(data['purpose'] == 'EXACT_TWO_CPU_ROOTS_NOT_SIMULATION', 'CPU_REGISTRY_PURPOSE_CHANGED')
        require(len(data['guards']) <= 2, 'CPU_GUARD_CEILING_TWO')
        for row in data['guards']:
            # The exact source-bound sole manager writes only these records from
            # its own Popen returns; request bytes must still match each launch.
            require(sha(row['request_path']) == row['request_sha256'], 'CPU_PEER_REQUEST_CHANGED')
            peer = json.loads(Path(row['request_path']).read_text())
            require(peer['purpose'] == 'CPU_FIXTURE' and
                    peer['prepared_source_sha256'] == self.request['prepared_source_sha256'] and
                    peer['manifests_sha256'] == self.request['manifests_sha256'] and
                    peer['shared_cpu_registry'] == str(self.path) and
                    peer['shared_manager_role'] == self.manager_role,
                    'CPU_PEER_NOT_SAME_REGISTERED_QUALIFIER')
        return data

    def peers(self):
        data = self.read_registry()
        result = []
        for row in data['guards']:
            if row['pid'] == os.getpid():
                require(row['start_ticks'] == self.identity(os.getpid())['start_ticks'], 'SELF_GUARD_PID_REUSED')
                continue
            current = self.process(row['pid'])
            if current is None or current['state'] == 'Z':
                # A terminal peer conveys no authority. The coordinator's
                # existing engine terminal/owned-instance exit checks remain.
                continue
            result.append(verified_peer_view(
                row, row['active_path'], row['request_sha256'], row['argv'],
                self.manager_role['executable_sha256'],
                {str(HERE / name): digest for name, digest in self.request['prepared_source_sha256'].items()},
                self.process, self.identity, time.monotonic_ns()))
        return result

    def controller_roles(self):
        data = self.read_registry()
        roles = [self.manager_role]
        for row in data['guards']:
            roles.append({'name': 'EXACT_OWN_CPU_GUARD', 'cwd': self.manager_role['cwd'],
                          'executable': self.manager_role['executable'],
                          'executable_sha256': self.manager_role['executable_sha256'],
                          'argvs': [row['argv']],
                          'source_sha256': {str(HERE / p): h for p, h in self.request['prepared_source_sha256'].items()}})
        return roles
