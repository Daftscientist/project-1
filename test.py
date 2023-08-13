import requests

result = requests.post("http://127.0.0.1:8000/api/v1/user/login"
, json={"email": "hello@leo-johnston.me", "password": "12345678"})

print(result.text,"/n", result.cookies.get_dict())