import requests

url = 'http://localhost:5000/refresh_dashboard'

response = requests.post(url)
print(response.text)
print(response.json())