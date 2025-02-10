import requests
from pytest import fixture

url = "http://127.0.0.1:8000/api/"


def test_normal_habit_add(token: str):
    name = "Drink water"
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


def test_habit_add_bad_token(token: str):
    name = "jpdb"
    typ = "custom"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": "bogus_token"}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}


def test_habit_add_bad_type(token: str):
    name = "duolingo"
    typ = "non_existent_type"

    data = {"type": typ, "name": name}
    headers = {"spnw-auth-token": token}
    res = requests.post(f"{url}habits", headers=headers, json=data)

    assert res.status_code == 404
    assert res.json() == {"detail": "Habit type does not exist"}


@fixture(autouse=True)
def token() -> str:
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

    res = requests.post(f"{url}users/login", json=data)

    assert res.status_code == 200
    assert "session_token" in res.json()

    headers = {"spnw-auth-token": res.json()["session_token"]}
    yield headers["spnw-auth-token"]
    res = requests.delete(f"{url}users", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"response": "true"}
