import requests, json
from fake_headers import Headers

headers = Headers(os="win", browser="chrome", headers=True).generate()

r = requests.get('https://api.github.com/users/Dant-di/repos?type=owner', headers=headers)
data = r.json()

with open('Dant-di_repo.json', 'w', encoding='utf-8') as out_file:
    json.dump(data, out_file)

