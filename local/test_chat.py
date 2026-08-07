import urllib.request
import json

data = json.dumps({'message': 'I want gym outfits in large size.'}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/api/v1/chat', data=data, headers={'Content-Type': 'application/json'})

try:
    response = urllib.request.urlopen(req)
    print(response.read().decode())
except Exception as e:
    print(f"Error {e.code}")
    print(e.read().decode())
