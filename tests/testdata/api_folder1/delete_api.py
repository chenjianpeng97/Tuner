import requests

url = "https://echo.apifox.com/delete"

params = {
  'q1': "v1"
}

payload = {
  'b1': 'v1',
  'b2': 'v2'
}

headers = {
  'User-Agent': "Apifox/1.0.0 (https://apifox.com)",
}

response = requests.delete(url, params=params, data=payload, headers=headers)

print(response.text)