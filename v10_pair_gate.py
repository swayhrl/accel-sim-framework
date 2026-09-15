import json
def gate(x):
 for k in ('token_sha','decode_token','layer','role','shape','raw','awq'):
  if k not in x:return False,'MISSING_'+k
 if x['token_sha']!='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9':return False,'TOKEN_MISMATCH'
 if x['decode_token']!=23578:return False,'DECODE_TOKEN_MISMATCH'
 if x['layer']!=0 or x['role']!='mlp.down_proj' or x['shape']!=[1,1,18944]:return False,'SEMANTIC_MISMATCH'
 for side in ('raw','awq'):
  y=x[side]
  if not all(y.get(k) for k in ('replay_equivalence','signature_equivalence','coverage','ack')):return False,'INVALID_'+side.upper()
 if x.get('ncu_units_compatible') is not True:return False,'NCU_DESCRIPTOR_INCOMPATIBLE'
 return True,'MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON'
if __name__=='__main__':
 x={'token_sha':'0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9','decode_token':23578,'layer':0,'role':'mlp.down_proj','shape':[1,1,18944],'raw':{'replay_equivalence':True,'signature_equivalence':True,'coverage':True,'ack':True},'awq':{'replay_equivalence':True,'signature_equivalence':True,'coverage':True,'ack':True},'ncu_units_compatible':True};print(json.dumps({'result':gate(x),'negative_missing':gate({}),'negative_token':gate(dict(x,token_sha='x'))}))
