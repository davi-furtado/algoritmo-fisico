from requests import post

img = input()
url = 'http://SEU_IP_AQUI:8000/'

with open(img, 'rb') as file:
    files = {'file': file}
    response = post(url, files=files)

if response.status_code == 200:
    result = response.json()

if result: print(result)