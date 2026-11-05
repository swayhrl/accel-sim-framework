"""Hash-bound directory-to-config bridge for the unchanged contained builder."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def apply(directory):
 directory=P(directory);binding=json.loads((directory/'MAIN_SOURCE_BINDING.json').read_bytes())
 assert binding['schema']=='CPU_SHARED_MAIN_HASH_BOUND_APPLY_BRIDGE_V1'
 source=P(binding['installer_path']);configuration=P(binding['configuration_path'])
 assert source.is_absolute()and configuration==directory/'CONFIGURATION.json'
 assert sha(source)==binding['installer_sha256']and sha(configuration)==binding['configuration_sha256']
 spec=importlib.util.spec_from_file_location('actual_hash_bound_shared_Main_installer',source)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 return module.apply(configuration)
