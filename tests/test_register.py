import requests

url = "http://127.0.0.1:8000/"


def test_normal_register():
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
    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_same_name_register():
    user = "jim"
    email = "jim@hotmail.com"
    pw = "batman"
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

    data = {
        "username": user,
        "email": "other@gmail.com",
        "password": "otherpw",
    }
    res = requests.post(f"{url}users/register", json=data)

    assert res.status_code == 409
    assert res.json() == {"detail": "Username Already Exists"}

    data = {"username": user, "password": pw}
    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_email_name_register():
    user = "jim"
    email = "jim@hotmail.com"
    pw = "batman"
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

    data = {
        "username": "joe",
        "email": email,
        "password": "superman",
    }
    res = requests.post(f"{url}users/register", json=data)

    assert res.status_code == 409
    assert res.json() == {"detail": "Email Already Exists"}

    data = {"username": user, "password": pw}
    res = requests.delete(f"{url}users", json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}
