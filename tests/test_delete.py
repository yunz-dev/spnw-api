import requests

url = "http://127.0.0.1:8000/"


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

    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_delete_no_user():
    user = "key"
    pw = "pspsps"
    data = {
        "username": user,
        "password": pw,
    }
    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Permission Denied"}


def test_delete_wrong_pass():
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

    data = {"username": user, "password": "password"}
    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 403
    assert res.json() == {"detail": "Permission Denied"}

    data = {"username": user, "password": pw}
    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}
