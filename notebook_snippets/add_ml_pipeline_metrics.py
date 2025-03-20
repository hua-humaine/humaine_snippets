
#this is an example snippet for adding a relevant json for pipeline metrics exposure to the Kubeflow environment
import json
metrics = {}
metrics['metrics'] = []
metrics['metrics'].append({'name':'myname', 'numberValue':5})
print(metrics)
with open('/tmp/mlpipeline-metrics.json', 'w') as f1:
    json.dump(metrics, f1)
