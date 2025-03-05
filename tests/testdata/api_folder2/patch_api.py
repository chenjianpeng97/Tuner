import requests

url = "https://echo.apifox.com/patch"

params = {
  'q1': "v1"
}

headers = {
  'User-Agent': "Apifox/1.0.0 (https://apifox.com)",
  'Content-Type': "application/json"
}

response = requests.patch(url, params=params, headers=headers)
print(response.json())