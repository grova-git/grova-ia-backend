import requests

url = "http://localhost:8001/api/products/bulk"
headers = {"Authorization": "Bearer TEST_TOKEN"}
files = {"file": open("C:/Users/ezequ/Desktop/productos_farmacia.csv", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.status_code)
print(response.json())
