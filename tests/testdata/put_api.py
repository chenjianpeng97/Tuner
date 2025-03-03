import requests

url = "https://echo.apifox.com/put"

params = {
  'q1': "v1"
}

payload = "test value"

headers = {
  'User-Agent': "Apifox/1.0.0 (https://apifox.com)",
  'Content-Type': "text/plain"
}

response = requests.put(url, params=params, data=payload, headers=headers)

print(response.text)