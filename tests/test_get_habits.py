import requests
from pytest import fixture

url = "http://127.0.0.1:8000/"


def test_normal_get_habits(token: str):
    habits = [
        ("Wake up", "custom"),
        ("Wash dishes", "custom"),
        ("Run", "custom")
    ]

    hids = []
    headers = {"spnw-auth-token": token}

    for name, typ in habits:
        data = {"type": typ, "name": name}
        res = requests.post(f"{url}habits", headers=headers, json=data)

        json = res.json()
        habit = json["habit"]
        hids.append(habit["id"])

        assert res.status_code == 200
        assert json["message"] == "Habit added"
        assert json["habit"]["name"] == name
        assert json["habit"]["type"] == typ

    res = requests.get(f"{url}habits", headers=headers)

    assert res.status_code == 200
    assert sorted(res.json().get("custom", [])) == sorted(hids)

    for hid, (name, typ) in zip(hids, habits):
        data = {"id": hid, "type": typ}
        res = requests.delete(f"{url}habits", headers=headers, json=data)

        assert res.status_code == 200
        assert res.json() == {"response": "true"}


def test_empty_get_habits(token: str):
    headers = {"spnw-auth-token": token}
    res = requests.get(f"{url}habits", headers=headers)

    assert res.status_code == 200
    assert res.json() == {}


def test_empty_custom_get_habits(token: str):
    name = "Gym"
    typ = "custom"


    headers = {"spnw-auth-token": token}
    data = {"type": typ, "name": name}
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

    res = requests.get(f"{url}habits", headers=headers)

    assert res.status_code == 200
    assert res.json() == {"custom": []}


def test_bad_token_get_habits():
    headers = {"spnw-auth-token": "tingmech"}
    res = requests.get(f"{url}habits", headers=headers)

    assert res.status_code == 401
    assert res.json() == {"detail": "Bad Token"}


@fixture(autouse=True)
def token() -> str:
    user = "bing"
    email = "bing_pigs@gmail.com"
    pw = "pigs"
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
