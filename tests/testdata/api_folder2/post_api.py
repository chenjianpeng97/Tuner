import requests
import json

url = "https://echo.apifox.com/post"

params = {
  'q1': "v1",
  'q2': "v2"
}

payload = {
  "d": "deserunt",
  "dd": "adipisicing enim deserunt Duis"
}

headers = {
  'User-Agent': "Apifox/1.0.0 (https://apifox.com)",
  'Content-Type': "application/json"
}

response = requests.post(url, params=params, data=json.dumps(payload), headers=headers)
print(response.text)

