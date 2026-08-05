from requests import post

img = input()
url = "http://localhost:8000/"

with open(img, "rb") as file:
    files = {"file": file}
    response = post(url, files=files)

if code := response.status_code == 200:
    result = response.json()
else:
    result = f"{code} | {response.text}"

if result:
    print(result)
