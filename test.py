import requests

result = requests.post("http://127.0.0.1:8000/api/v1/user/create", data={
    "username": "leo",
    "password": "kdfffd"
})

print(result.text)