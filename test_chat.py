import urllib.request
import json
req = urllib.request.Request(
    'http://localhost:8080/agent/api/v1/chat',
    data=b'{"message": "I want clothes for a special occasion"}',
    headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req)
print(json.dumps(json.loads(resp.read().decode('utf-8')), indent=2))
