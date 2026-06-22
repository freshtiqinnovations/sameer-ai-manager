import json
def analyze(limit=20):
 return {"total":0,"by_category":{},"latest":[]}
if name == "main":
 print(json.dumps(analyze(), indent=2))
