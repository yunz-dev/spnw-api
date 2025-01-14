import requests
from pytest import fixture

url = "http://127.0.0.1:8000/"


def test_normal_get_habit(token: str):
    name = "Hoover house"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    json = res.json()
    habit = json["habit"]
    hid = habit["id"]

    assert res.status_code == 200
    assert json["message"] == "Habit added"
    assert json["habit"]["name"] == name
    assert json["habit"]["type"] == typ

    res = requests.get(f"{url}habit?hid={hid}&habit_type={typ}", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"name": name, "streak": 0, "last_done": None}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_bad_token_get_habit(token: str):
    name = "Laundry"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    json = res.json()
    habit = json["habit"]
    hid = habit["id"]

    assert res.status_code == 200
    assert json["message"] == "Habit added"
    assert json["habit"]["name"] == name
    assert json["habit"]["type"] == typ

    headers = {"spnw-auth-token": "lekw"}
    res = requests.get(f"{url}habit?hid={hid}&habit_type={typ}", headers=headers)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": token}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_bad_type_get_habit(token: str):
    name = "Shower"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    json = res.json()
    habit = json["habit"]
    hid = habit["id"]

    assert res.status_code == 200
    assert json["message"] == "Habit added"
    assert json["habit"]["name"] == name
    assert json["habit"]["type"] == typ

    bad_typ = "chair"
    res = requests.get(f"{url}habit?hid={hid}&habit_type={bad_typ}", headers=headers)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit type does not exist"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_bad_hid_get_habit(token: str):
    name = "Hang clothes"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    json = res.json()
    habit = json["habit"]
    hid = habit["id"]

    assert res.status_code == 200
    assert json["message"] == "Habit added"
    assert json["habit"]["name"] == name
    assert json["habit"]["type"] == typ

    bad_hid = "weee"
    res = requests.get(f"{url}habit?hid={bad_hid}&habit_type={typ}", headers=headers)

    assert res.status_code == 422
    assert res.json() == {"detail": "Invalid id"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_fake_hid_get_habit(token: str):
    name = "Water plants"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    json = res.json()
    habit = json["habit"]
    hid = habit["id"]

    assert res.status_code == 200
    assert json["message"] == "Habit added"
    assert json["habit"]["name"] == name
    assert json["habit"]["type"] == typ

    fake_hid = "0" * 24
    res = requests.get(f"{url}habit?hid={fake_hid}&habit_type={typ}", headers=headers)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit does not exist"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_unowned_get_habit(token: str, token2):
    name = "Grocery shopping"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    json = res.json()
    habit = json["habit"]
    hid = habit["id"]

    assert res.status_code == 200
    assert json["message"] == "Habit added"
    assert json["habit"]["name"] == name
    assert json["habit"]["type"] == typ

    headers = {"spnw-auth-token": token2}
    res = requests.get(f"{url}habit?hid={hid}&habit_type={typ}", headers=headers)

    assert res.status_code == 403
    assert res.json() == {"detail": "Habit not owned by user"}

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": token}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


@fixture
def token() -> str:
    user = "ping"
    email = "pinglee@gmail.com"
    pw = "lee"
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

    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 200
    assert "session_token" in res.json()

    headers = {"spnw-auth-token": res.json()["session_token"]}
    yield headers["spnw-auth-token"]
    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


@fixture
def token2() -> str:
    user = "jim"
    email = "mih@gmail.com"
    pw = "jim"
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

    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 200
    assert "session_token" in res.json()

    headers = {"spnw-auth-token": res.json()["session_token"]}
    yield headers["spnw-auth-token"]
    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}
