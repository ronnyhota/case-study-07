import requests

url = "http://127.0.0.1:5000/upload"
file_path = "lanternfly.png"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "image/png")}
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response text:", response.text)
