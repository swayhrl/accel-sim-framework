#!/usr/bin/env python3
import json,sys

def subset(expected,observed,path=''):
 if isinstance(expected,dict):
  for k,v in expected.items():subset(v,observed[k],path+'.'+k)
 else:
  assert expected==observed,(path,expected,observed)
if __name__=='__main__':
 try:
  subset(json.load(open(sys.argv[1])),json.load(open(sys.argv[2])))
 except (AssertionError,KeyError,ValueError) as e:
  print(str(e));sys.exit(1)
 sys.exit(0)
