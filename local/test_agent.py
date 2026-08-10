import urllib.request
import json
req = urllib.request.Request(
    'http://clothing-agent:8000/api/v1/chat',
    data=b'{"message": "hi"}',
    headers={'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    print(json.dumps(json.loads(resp.read().decode('utf-8')), indent=2))
except Exception as e:
    print(f"Error: {e}")
