import requests

url = "http://127.0.0.1:8000/api/"


def test_login_normal():
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
    assert res.json() == {
        "message": "Registration successful",
        "user": {
            "username": user,
            "email": email,
        },
    }

    data = {"username": user, "password": pw}
    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 200
    assert "session_token" in res.json()

    headers = {"spnw-auth-token": res.json()["session_token"]}
    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_login_no_user():
    user = "mon"
    pw = "eeek"
    data = {
        "username": user,
        "password": pw,
    }
    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Permission Denied"}


def test_login_wrong_pass():
    user = "park"
    email = "hinga@proton.me"
    pw = "<3"
    data = {
        "username": user,
        "email": email,
        "password": pw,
    }
    res = requests.post(f"{url}users/register", json=data)

    assert res.status_code == 200
    assert res.json() == {
        "message": "Registration successful",
        "user": {
            "username": user,
            "email": email,
        },
    }

    data = {"username": user, "password": "wrong password"}
    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 403
    assert res.json() == {"detail": "Permission Denied"}

    data = {"username": user, "password": pw}
    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 200
    assert "session_token" in res.json()

    headers = {"spnw-auth-token": res.json()["session_token"]}
    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}
