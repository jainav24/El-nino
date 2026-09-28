import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

with open('sample_request.json', 'r') as f:
    sample_request = json.load(f)

with open('sample_whatif.json', 'r') as f:
    sample_whatif = json.load(f)

print("1. GET /health")
r = requests.get(f"{BASE_URL}/health")
print(r.status_code, r.json())
print()

print("2. GET /model-info")
r = requests.get(f"{BASE_URL}/model-info")
print(r.status_code, r.json())
print()

print("3. POST /predict")
r = requests.post(f"{BASE_URL}/predict", json=sample_request)
print(r.status_code, "Success" if r.status_code == 200 else r.text)
print()

print("4. POST /what-if")
r = requests.post(f"{BASE_URL}/what-if", json=sample_whatif)
print(r.status_code, "Success" if r.status_code == 200 else r.text)
print()

print("5. GET /statistics")
r = requests.get(f"{BASE_URL}/statistics")
print(r.status_code, r.json())
print()

print("6. GET /history")
r = requests.get(f"{BASE_URL}/history")
print(r.status_code, f"Total records: {r.json().get('total')}")
print()
