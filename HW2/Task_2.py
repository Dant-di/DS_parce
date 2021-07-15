import requests, json
from fake_headers import Headers
headers = Headers(os="lin", browser="firefox", headers=True).generate()

r = requests.get('http://api.weatherstack.com/current?access_key=897c8091a2397387078f05070e7a749c&query=Zurich',
                 headers=headers)
data = r.json()

with open('weather.json', 'w', encoding='utf-8') as out_file:
    json.dump(data, out_file)