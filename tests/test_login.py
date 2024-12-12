import requests

url = "http://127.0.0.1:8000/"


def test_normal_login():
    user = "yunz"
    email = "yunz@gmail.com"
    pw = "znuy"
    data = {
        "username": user,
        "email": email,
        "password": pw,
    }
    res = requests.post(f"{url}users/register", json=data)
    assert res.status_code == 200
    data = {"username": user, "password": pw}
    res = requests.post(f"{url}users/login", json=data)
    assert res.status_code == 200
    assert res.json() == {"response": "true"}
    res = requests.delete(f"{url}users", json=data)
    assert res.status_code == 200