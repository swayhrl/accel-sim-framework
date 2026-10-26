"""CPU-only fixed-identity preparation; no model or CUDA initialization."""
import pathlib,os,json,csv,io,hashlib,time,sys,importlib.metadata,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1';P=OUT/'.private'
MODEL=pathlib.Path('/data/c16/stagea_runtime_qualification_v1/assets/qwen2.5-3b-instruct/aa8e72537993ba99e69dfaafa59ed015b17504d1')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def canonical(ids):return json.dumps(ids,separators=(',',':')).encode()
def main():
 started=time.time();checks=[];manifest=json.loads((P/'sources/asset_receipt').read_text());asset=[]
 for f in manifest['files']:
  path=MODEL/f['path'];assert path.stat().st_size==f['size_bytes'],f['path'];h=hashlib.sha256()
  with path.open('rb') as stream:
   for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
  assert h.hexdigest()==f['sha256'],f['path'];asset.append({**f,'actual_sha256':h.hexdigest(),'status':'PASS_FULL_STREAMING_SHA256'})
 model_license=(MODEL/'LICENSE').read_text();assert 'FOR NON-COMMERCIAL PURPOSES ONLY' in model_license and 'research or evaluation purposes only' in model_license
 card_url='https://huggingface.co/datasets/Salesforce/wikitext/raw/b08601e04326c79dfdd32d625aee71d232d685c3/README.md'
 card=(P/'sources/wikitext_license_disclosure.json').read_bytes()
 assert len(card)<100000 and all(x in card for x in [b'cc-by-sa-3.0',b'gfdl',b'CC BY-SA 4.0'])
 assert json.loads(card)['source_url']==card_url
 license_receipt={'model':{'name':'Qwen RESEARCH LICENSE AGREEMENT','sha256':sha(model_license.encode()),'basis':'Existing local model; non-commercial AI-ARCH research/evaluation expressly within research grant; no redistribution of materials or model outputs'},'input':{'source':card_url,'captured_disclosure_sha256':sha(card),'capture_method':'Pinned raw README inspected with web tool; hash covers selected-field disclosure JSON, not original README bytes','metadata_licenses':['cc-by-sa-3.0','gfdl'],'prose_license':'CC BY-SA 4.0','version_conflict_disclosed':True,'local_use_basis':'Local research use of previously frozen natural text allowed under attribution/share-alike licenses; no text/token IDs/generated text redistributed; retain Salesforce/Wikipedia attribution and immutable source hashes','attribution':'WikiText, Stephen Merity, Caiming Xiong, James Bradbury, Richard Socher (2016), Salesforce; derived from Wikipedia. Dataset rows API is not commit-addressed; frozen bytes remain authority.'}}
 import torch,transformers,tokenizers,jinja2
 assert not torch.cuda.is_initialized();assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 tok=transformers.AutoTokenizer.from_pretrained(str(MODEL),local_files_only=True,use_fast=True,trust_remote_code=False)
 receipts=list(csv.DictReader(io.StringIO((P/'sources/token_receipts').read_text()),delimiter='\t'))
 template_sha=sha(tok.chat_template.encode());assert template_sha=='cd8e9439f0570856fd70470bf8889ebd8b5d1107207f67a5efb46e342330527f'
 inputs=[];private_inputs={}
 def encode(text):
  result=tok.apply_chat_template([{'role':'user','content':text}],tokenize=True,add_generation_prompt=True)
  result=result['input_ids'] if hasattr(result,'keys') else result
  assert isinstance(result,list) and all(type(x) is int for x in result),'Unexpected tokenizer ID shape'
  return result
 for suffix in ['00','01']:
  source='TRAIN_A_DISCOVERY_'+suffix;old=next(r for r in receipts if r['model_key']=='QWEN_BF16' and r['source_text_id']==source)
  text_raw=(P/'sources'/('text_'+suffix)).read_bytes();assert sha(text_raw)==old['source_utf8_sha256'];text=text_raw.decode()
  ids_raw=(P/'sources'/('ids512_'+suffix)).read_bytes();ids=json.loads(ids_raw)
  assert sha(ids_raw)==old['token_id_file_sha256'] and sha(canonical(ids))==old['token_ids_sha256'] and len(ids)==512
  # Check historical selected prefix semantics without replacing its frozen IDs.
  prefix=text_raw[:int(old['prefix_utf8_byte_count'])].decode();assert encode(prefix)==ids
  row={'source':source,'prompt_tokens':512,'source_sha256':sha(text_raw),'source_bytes':len(text_raw),'prefix_utf8_bytes':int(old['prefix_utf8_byte_count']),'token_ids_sha256':sha(canonical(ids)),'token_file_sha256':sha(ids_raw),'tokenizer_sha256':old['tokenizer_json_sha256'],'chat_template_sha256':template_sha,'status':'PASS_HISTORICAL_IDS_UNCHANGED'}
  inputs.append(row);private_inputs[source+'_512']=ids
  full=encode(text);lo=0;hi=len(text)
  while lo<hi:
   mid=(lo+hi+1)//2
   if len(encode(text[:mid]))<=2048:lo=mid
   else:hi=mid-1
  chosen=encode(text[:lo]);longest=lo
  assert lo==len(text) or len(encode(text[:lo+1]))>2048,'historical adjacent monotonicity guard failed'
  # Same token-count plateau: explicit shortest-byte tie break in new Goal.
  while lo>0 and len(encode(text[:lo-1]))==len(chosen):lo-=1
  chosen=encode(text[:lo]);status='PASS_EXACT_2048' if len(chosen)==2048 else 'SOURCE_TARGET_LENGTH_NOT_REACHED'
  row={**row,'prompt_tokens':len(chosen),'target_tokens':2048,'full_templated_tokens':len(full),'prefix_utf8_bytes':len(text[:lo].encode()),'longest_bisection_prefix_characters':longest,'selected_prefix_characters':lo,'selection_rule':'Historical full-chat-template prefix bisection and adjacent guard; same-count plateau shortest-byte tie break; no padding/repetition/substitution','token_ids_sha256':sha(canonical(chosen)),'token_file_sha256':sha(canonical(chosen)+b'\n'),'status':status}
  inputs.append(row)
  if status=='PASS_EXACT_2048':private_inputs[source+'_2048']=chosen
 save(P/'inputs.json',private_inputs)
 old_contract=json.loads((P/'sources/old_contract').read_text());reference=old_contract['accepted_outputs']['MP02_A'];ref=pathlib.Path(reference['path']);ref_receipt={**reference,'available':ref.is_file()}
 if ref.is_file():
  raw=ref.read_bytes();assert sha(raw)==reference['sha256'];value=json.loads(raw);assert value['status']=='PASS' and value['mode']=='A';(P/'reference.json').write_bytes(raw);ref_receipt['status']='PASS_PINNED_HISTORICAL_REFERENCE'
 else:ref_receipt['status']='HISTORICAL_OUTPUT_NOT_REVERIFIED'
 site=pathlib.Path('/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/lib/python3.12/site-packages');source_hashes={k:sha((site/'vllm'/rel).read_bytes()) for k,rel in [('compilation.py','config/compilation.py'),('qwen2.py','model_executor/models/qwen2.py')]};assert source_hashes==old_contract['vllm_installed_source_sha256']
 cache_interfaces={}
 for rel,needles in [('vllm/envs.py',['VLLM_CACHE_ROOT']),('vllm/compilation/decorators.py',['envs.VLLM_CACHE_ROOT','torch_aot_compile']),('vllm/compilation/backends.py',['self.compilation_config.cache_dir','local_cache_dir']),('torch/_inductor/runtime/cache_dir_utils.py',['TORCHINDUCTOR_CACHE_DIR'])]:
  path=site/rel;raw=path.read_bytes() if path.is_file() else b'';cache_interfaces[rel]={'sha256':sha(raw),'exists':path.is_file(),'markers':{n:n.encode() in raw for n in needles}}
 assert cache_interfaces['vllm/compilation/decorators.py']['markers']['envs.VLLM_CACHE_ROOT']
 versions={n:importlib.metadata.version(n) for n in ['vllm','torch','transformers','tokenizers','jinja2','nvidia-ml-py']};assert versions['vllm']=='0.30.0'
 save(OUT/'INPUT_RECEIPT.json',{'status':'PASS','license':license_receipt,'inputs':inputs,'tokenizer_versions':versions,'template_sha256':template_sha,'private_ID_payloads_not_committed':True,'no_CUDA_initialized':not torch.cuda.is_initialized(),'reference':ref_receipt})
 save(OUT/'SOURCE_AND_RUNTIME.json',{'status':'G0_PASS','model_revision':manifest['revision'],'model_path':str(MODEL),'asset_files':asset,'asset_hash_scope':'FULL_STREAMING_SHA256_ALL12FILES','versions':versions,'vllm_source_commit_historical':old_contract['vllm_source_commit'],'vllm_installed_source_sha256':source_hashes,'cache_isolation_interfaces':cache_interfaces,'new_compilation_identity':'NEW_MODE_A_COMPILATION_IDENTITY','old_caches_read_or_modified':False,'no_CUDA_initialized':not torch.cuda.is_initialized(),'cpu_prep_seconds':time.time()-started,'source_anchors':json.loads((P/'sources.json').read_text())})
 print(json.dumps({'G0':'PASS','versions':versions,'inputs':[{k:r[k] for k in ['source','prompt_tokens','prefix_utf8_bytes','status']} for r in inputs],'reference':ref_receipt['status'],'CPU_seconds':time.time()-started}),flush=True)
if __name__=='__main__':main()
