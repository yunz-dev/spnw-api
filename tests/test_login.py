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
    requests.post(url, json=data)
    res = requests.post(f"{url}users/login/user={user}/pass={pw}")
    assert res.status_code == 200
    assert res.json() == {"response": "true"}
    data = {"username": user, "password": pw}
    res = requests.post(f"{url}users/delete", json=data)
    assert res.status_code == 200
