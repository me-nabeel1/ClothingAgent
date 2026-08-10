import urllib.request
import json
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/chat',
    data=b'{"message": "I want red trousers", "conversation_id": null}',
    headers={'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    print(json.dumps(json.loads(resp.read().decode('utf-8')), indent=2))
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
