import os
import sys
import json
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")

with open(os.path.join(SAMPLES_DIR, "sample_request.json"), "r") as f:
    sample_request = json.load(f)

with open(os.path.join(SAMPLES_DIR, "sample_whatif.json"), "r") as f:
    sample_whatif = json.load(f)

print(f"Testing API at: {BASE_URL}")
print("-" * 50)

print("1. GET /health")
try:
    r = requests.get(f"{BASE_URL}/health")
    print(r.status_code, r.json())
except Exception as e:
    print(f"Failed: {e}")
print()

print("2. GET /model-info")
try:
    r = requests.get(f"{BASE_URL}/model-info")
    print(r.status_code, r.json())
except Exception as e:
    print(f"Failed: {e}")
print()

print("3. POST /predict")
try:
    r = requests.post(f"{BASE_URL}/predict", json=sample_request)
    print(r.status_code, "Success" if r.status_code == 200 else r.text)
except Exception as e:
    print(f"Failed: {e}")
print()

print("4. POST /what-if")
try:
    r = requests.post(f"{BASE_URL}/what-if", json=sample_whatif)
    print(r.status_code, "Success" if r.status_code == 200 else r.text)
except Exception as e:
    print(f"Failed: {e}")
print()

print("5. GET /advisory/enso-status")
try:
    r = requests.get(f"{BASE_URL}/advisory/enso-status")
    print(r.status_code, r.json() if r.status_code == 200 else r.text)
except Exception as e:
    print(f"Failed: {e}")
print()
