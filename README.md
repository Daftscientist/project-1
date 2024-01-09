# Project 1

[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](https://github.com/Daftscientist/my-pterodactyl/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/Daftscientist/my-pterodactyl.svg?branch=master)](https://travis-ci.org/Daftscientist/my-pterodactyl)
[![Coverage Status](https://coveralls.io/repos/github/Daftscientist/my-pterodactyl/badge.svg?branch=master)](https://coveralls.io/github/Daftscientist/my-pterodactyl?branch=master)

A project to replace pterodactyl and be a showcase of my Python and React skills.

- This project does not follow Open Authorization specification. Read the documentation.

## TODO
| Done? | Idea |
| --- | --- |
| ❌ | Rewrite the whole codebase to use global app context for all common functions. |
| ❌ | Write a cache system - option to use SQLite|Redis. (start with sqlite) |
| 🖊️ | Implement the use of the new session system. |
| ✔️ | Rewrite the session system to not rely on python dictionaries. |
| ✔️ | Move the authentication routes to /auth/... |
| ✔️ | Decorator for authenticated routes. |
| 🖊️ | View and edit user data via API. |
| ❌ | Add create server routes. |
| ❌ | Replace `sanic_dantic` with my own solution. |
| ❌ | Add email verification with code/link for signup. |
| ❌ | Add option to login with email code/link. |
| ❌ | Add 2FA and Oauth2 |
| ❌ | Create the entire plugin system from scratch. |

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Responses](#responses)
- [Exceptions](#exceptions-in-production)
- [Plugin System](#plugins)
- [Contributing](#contributing)
- [License](#license)

## Features

### Made with compatibility in mind 
- Built with SQLAlchemy, allowing for connections to `SQLite`, `Postgresql`, `MySQL`, `Oracle`, `MS-SQL`, `Firebird`, `Sybase`.
### Plugin system
- Ingegrated, out-the-box [plugin support](#plugins).
### Contributor focused
- Built with documentation, comments and moduled. This allows for easy contribution.

## Installation

Download the files:
```shell
git clone https://github.com/Daftscientist/my-pterodactyl
```
Unzip the downloaded files:
```shell
Ubuntu: unzip my-pterodactyl-main.zip -d my-pterodactyl-main
Windows: zip file. tar -xf my-pterodactyl-main.zip
```
Make sure your in the backend folder:
```shell
cd backend
```
Check if python is installed:
```shell
python –version
OR
python3 -version
```
Make sure PIP package manager is installed:
```shell
python -m pip --version
OR
python3 -m pip --version
```
Install required dependencies:
```shell
pip install -r requirements.txt
OR
pip3 install -r requirements.txt
```
Run the backend API:
```shell
sanic main
```
Use `ctrl+c` to stop the backend running.

### Development tips

Creating virtual environments:
```shell
python -m venv
OR
python3 -m venv
```
Entering the virtual environment:
```shell
Unix or MacOS - bash shell: source /venv/bin/activate
Unix or MacOS - csh shell: source /venv/bin/activate.csh
Unix or MacOS - fish shell: source /venv/bin/activate.fish
Windows - Command Prompt: venv\Scripts\activate.bat
Windows - PowerShell: venv\Scripts\Activate.ps1
```
Running the backend API with live reloading:
```shell
sanic main --reload
```
Running the backend API in debug mode:
```shell
sanic main --debug
```
You can combine `sanic main --dev` for development.

## Usage

Creating a user:
```python
import requests

API_URL = "http://localhost:8080/api/v1"

response = requests.post(API_URL + "/user/create", json={
  "username": "example_username",
  "email": "user@example.com",
  "password": "password1",
  "repeated_password": "password1"
})
print(response.json())
```
Logging in:
```python
import requests

API_URL = "http://localhost:8080/api/v1"

response = requests.post(API_URL + "/user/login", json={
  "email": "user@example.com",
  "password": "password1"
})
print(response.json())
print(response.cookies.get_dict().session)
```

Logging out (cookies from login must be included in the request):
```python
import requests

API_URL = "http://localhost:8080/api/v1"

response = requests.post(API_URL + "/user/logout", cookies={'session': 'jwt-encoded-string'})
print(response.json())
```

## Responses
Example error:
```json
{
  "error": "Page not found",
  "status": 404,
  "path": "/api/v1/user/nothing",
  "request_id": "request-id",
  "timestamp": "May 10, 2023, 12:00:00 AM"
 }
```

## Exceptions in production
When stumbling across an exception during a production installation of this project, this rarity will be written to the log file. This file, located in `backend/localstorage/exceptions.log`, will provide the error ID (provided to the user in the UI), message, HTTP code and timestamp.
#### An excerpt from a real file:
```log
ID: 9ac65dcb-fbe3-4ce0-af0e-5136c70fe2f1 - Message: 'Invalid response type <coroutine object Success at 0x0000024A20732960> (need HTTPResponse)' - Code: 500 - Timestamp: 2023-05-23 20:38:26.521845
```
Once this information is gathered, check through all open and already solved GitHub issues before reporting it to the development team.

## Contributing
We welcome contributions from the community! To contribute to this project, please follow the guidelines below:

Fork the repository and create your branch.
Set up the development environment.
Make your changes and test thoroughly.
Submit a pull request, clearly describing the changes you've made.
Please make sure to follow our code of conduct and be respectful to all contributors.

## License
This project is licensed under the Apache License 2.0.
