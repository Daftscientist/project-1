import requests

result = requests.post("http://127.0.0.1:8000/api/v1/user/login"
, json={"email": "hello@leo-johnston.me", "password": "12345678"})

print(result.json())

cookie = result.cookies.get_dict()
print(cookie)
cookie = cookie["session"]

result = requests.post("http://127.0.0.1:8000/api/v1/user/logout", cookies={"session": cookie})
print(result.json())
print(result.cookies.get_dict())
