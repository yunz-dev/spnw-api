import requests
from pytest import fixture

url = "http://127.0.0.1:8000/"


def test_normal_habit_delete(token: str):
    name = "Check emails"
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

    assert res.status_code == 200

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_delete_twice(token: str):
    name = "Watch youtube"
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

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}

    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit does not exist"}


def test_habit_delete_bad_token(token: str):
    name = "dont play league"
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

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": "reeee"}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": token}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_delete_bad_type(token: str):
    name = "check github"
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

    data = {"id": hid, "type": "not_a_type"}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit type does not exist"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_delete_bad_hid(token: str):
    name = "pyanban"
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

    data = {"id": "not an hid", "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 422
    assert res.json() == {"detail": "Invalid id"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_delete_fake_habit(token: str):
    name = "jpdb"
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
    data = {"id": fake_hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit does not exist"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_delete_unowned_habit(token: str, token2: str):
    name = "push to github"
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

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": token2}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 403
    assert res.json() == {"detail": "Habit not owned by user"}

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": token}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


@fixture(autouse=True)
def token() -> str:
    user = "mongey"
    email = "mongey@gmail.com"
    pw = "banana"
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
    user = "greg"
    email = "greg@gmail.com"
    pw = "greg"
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
