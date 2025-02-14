import requests

url = "http://127.0.0.1:8000/api/"


def test_delete_normal():
    user = "monkey"
    email = "monkey@gmail.com"
    pw = "keymon"
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


def test_delete_no_user():
    headers = {"spnw-auth-token": "eeee"}
    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}


def test_delete_twice():
    user = "joey"
    email = "michal@gmail.com"
    pw = "lekw"
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

    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}
