class ExactModuleStreamer:
 """Orchestrates existing runtime modules; deliberately contains no Qwen math."""
 def __init__(self,model,materializer=None): self.model=model;self.materializer=materializer
 def execute_layer(self,layer,hidden_states,**kwargs):
  return layer(hidden_states,**kwargs)
 def run_layers(self,hidden_states,layers,states):
  outputs=[]
  for i,layer in enumerate(layers):
   result=self.execute_layer(layer,hidden_states,**states.get(i,{}))
   hidden_states=result[0] if isinstance(result,tuple) else result
   outputs.append(hidden_states)
  return hidden_states,outputs
