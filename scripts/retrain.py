import os
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api")

print(f"Triggering model retrain on {BASE_URL}/retrain...")
try:
    r = requests.post(f"{BASE_URL}/retrain", json={})
    print(f"Status Code: {r.status_code}")
    print("Response:", r.json())
except Exception as e:
    print(f"Error connecting to backend: {e}")
