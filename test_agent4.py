import urllib.request
import json
# First turn
req1 = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/chat',
    data=b'{"message": "I want red trousers", "conversation_id": null}',
    headers={'Content-Type': 'application/json'}
)
resp1 = urllib.request.urlopen(req1)
data1 = json.loads(resp1.read().decode('utf-8'))
cid = data1['conversation_id']

# Second turn
req2 = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/chat',
    data=json.dumps({"message": "size 34", "conversation_id": cid}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
resp2 = urllib.request.urlopen(req2)
print(json.dumps(json.loads(resp2.read().decode('utf-8')), indent=2))
