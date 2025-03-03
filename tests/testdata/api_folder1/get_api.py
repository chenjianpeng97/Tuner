import requests

url = "https://echo.apifox.com/get"

params = {
  'q1': "v1",
  'q2': "v2"
}

headers = {
  'User-Agent': "Apifox/1.0.0 (https://apifox.com)"
}

response = requests.get(url, params=params, headers=headers)

print(response.text)