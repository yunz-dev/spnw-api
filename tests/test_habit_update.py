import requests
from pytest import fixture

url = "http://127.0.0.1:8000/api/"


def test_normal_habit_update_name(token: str):
    name = "Eat breakfast"
    typ = "custom"
    new_name = "Eat eggs"

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

    data = {"id": hid, "type": typ, "name": new_name}
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {
        "message": "Habit updated",
        "habit": {
            "name": new_name,
            "streak": 0,
        },
    }

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_normal_habit_update_done(token: str):
    name = "PJSK Challenge Show"
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

    data = {"id": hid, "type": typ, "done": True}
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {
        "message": "Habit updated",
        "habit": {
            "name": name,
            "streak": 1,
        },
    }

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_normal_habit_update_both(token: str):
    name = "duolingo"
    typ = "custom"
    new_name = "Fight Mafia"

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

    data = {"id": hid, "type": typ, "name": new_name, "done": True}
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {
        "message": "Habit updated",
        "habit": {
            "name": new_name,
            "streak": 1,
        },
    }

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_normal_habit_update_none(token: str):
    name = "scream"
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
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {
        "message": "Habit updated",
        "habit": {
            "name": name,
            "streak": 0,
        },
    }

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_normal_habit_update_done_twice(token: str):
    name = "Nap"
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

    data = {"id": hid, "type": typ, "done": True}
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {
        "message": "Habit updated",
        "habit": {
            "name": name,
            "streak": 1,
        },
    }

    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 429
    assert res.json() == {"detail": "Habit can only be done once a day"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_update_bad_token(token: str):
    name = "Anki"
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

    headers = {"spnw-auth-token": "reeee"}
    data = {"id": hid, "type": typ, "done": True}
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}

    data = {"id": hid, "type": typ}
    headers = {"spnw-auth-token": token}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_update_bad_type(token: str):
    name = "Paxism"
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
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit type does not exist"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_update_bad_hid(token: str):
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
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 422
    assert res.json() == {"detail": "Invalid id"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_update_fake_habit(token: str):
    name = "open spnw"
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
    res = requests.put(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit does not exist"}

    data = {"id": hid, "type": typ}
    res = requests.delete(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}


def test_habit_update_unowned_habit(token: str, token2: str):
    name = "open spnw"
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
    res = requests.put(f"{url}habits", headers=headers, json=data)

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
