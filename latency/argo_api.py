from pprint import pprint

import requests
import yaml
import json

#configuration = argo_workflows.Configuration(host="https://localhost:2746")
#configuration.verify_ssl = False
base_url = "https://localhost:2746/api/v1/workflows/argo-wf"

resp = requests.get('https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml')
manifest = yaml.safe_load(resp.text)
print(manifest)

resp2 = requests.post(url=base_url, headers={"content-type": "application/json"}, json=manifest, verify=False)
print(resp2.text)

resp3 = requests.get(url=base_url, verify=False)
#pprint(resp2.json())
result = resp3.json()
for item in result["items"]:
    pprint(item["metadata"]["name"])
