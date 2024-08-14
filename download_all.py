import requests
import json

resp = requests.get("http://141.72.13.23:3000/api/search").json()

dashs = {d["uri"].split("/")[1]: d["uid"] for d in resp}

for name in dashs:
    print("Downloading "+name)
    with open(f"prometheus/{name}.json", "w") as out:
        resp = requests.get("http://141.72.13.23:3000/api/dashboards/uid/"+dashs[name]).json();
        json.dump(resp, out, indent=4)
