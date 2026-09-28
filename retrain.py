import requests

BASE_URL = "http://127.0.0.1:8000/api"

print("Triggering Retrain (this will regenerate the dataset and reload the model)...")
r = requests.post(f"{BASE_URL}/retrain", json={})
print(r.status_code, r.json())
