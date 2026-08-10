import urllib.request
import json
req = urllib.request.Request(
    'http://localhost:8080/agent/api/v1/chat',
    data=b'{"message": "hi", "conversation_id": null}',
    headers={'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    print(json.dumps(json.loads(resp.read().decode('utf-8')), indent=2))
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")
