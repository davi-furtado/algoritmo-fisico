from os import listdir
from requests import post
from json import dump

url = "http://localhost:8000/"

results = []
for path in ["../pics/" + p for p in listdir("pics")]:
    with open(path, "rb") as entry:
        files = {"file": entry}
        response = post(url, files=files)

    if response.status_code != 200:
        data = {"error": response.text}
    else:
        data = response.json()
    if not data:
        continue

    results.append({"path": path} | data)

with open("results.json", "w") as file:
    dump(results, file, indent=2)
