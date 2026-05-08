from requests import post

img = input()
url = 'http://localhost:8000/convert'

with open(img, 'rb') as file:
    files = {'file': file}
    response = post(url, files=files)

if response.status_code == 200:
    result = response.json()

if result: print(result)