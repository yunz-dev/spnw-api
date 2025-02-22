import datetime as dt
import secrets
from os import getenv
from typing import Annotated

import bcrypt
import pytz
from bson.objectid import ObjectId
from fastapi import Cookie, FastAPI, Form, Header, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class TokenCookie(BaseModel):
    session_token: str


app = FastAPI()
client = MongoClient(getenv("MONGO_URI"), server_api=ServerApi("1"))
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

try:
    client.admin.command("ping")
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.get("/", response_class=HTMLResponse)
# def read_root(request: Request, cookies: Annotated[TokenCookie, Cookie()] = None):
def read_root(request: Request):
    cookie_token = request.cookies.get("session_token", None)
    if cookie_token is None:
        return RedirectResponse(url="/login", status_code=302)
    if get_user_from_session(cookie_token) is None:
        return RedirectResponse(url="/login", status_code=302)
    else:
        return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def api_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def api_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


#
#
# USER ENDPOINTS ---------------------------------------------------------------


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


#
# Helper Functions for Auth -------------------------------------------------
sessions = {}


def create_session(uid: str) -> str:
    token = secrets.token_hex(32)
    sessions[token] = uid
    return token


def get_user_from_session(token: str) -> str | None:
    return sessions.get(token, None)


def remove_from_session(token: str):
    sessions.pop(token, None)


def get_uid_from_user(username: str) -> str | None:
    users = client["users"]["users"]
    user = users.find_one({"username": username})
    if user:
        return user["_id"]
    else:
        return None


class UserDelete(BaseModel):
    username: str


def check_login(details: UserLogin) -> (bool, int):
    users = client["users"]["users"]
    user = users.find_one({"username": details.username})

    if user is None:
        return (False, 404)

    if verify_pass(details.password, user["password"]):
        return (True, 200)
    return (False, 403)


def hash_pass(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def verify_pass(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


# Helper Functions for Auth -------------------------------------------------
#


@app.delete("/api/users")
def delete_user(spnw_auth_token: Annotated[str | None, Header()]):
    token = spnw_auth_token
    uid = sessions.get(token, None)
    if uid:
        users = client["users"]["users"]
        filter = {"_id": uid}
        users.delete_one(filter)
        remove_from_session(token)
        return {"response": "true"}
    else:
        raise HTTPException(status_code=401, detail="Bad Token")


#  TODO: Add more security layers, e.g make password certain length


@app.post("/api/users/register")
async def register_user(user: UserRegistration):
    users = client["users"]["users"]

    # check if unique user
    registered_email = users.find_one({"email": user.email})
    if registered_email:
        raise HTTPException(status_code=409, detail="Email Already Exists")

    registered_username = users.find_one({"username": user.username})
    if registered_username:
        raise HTTPException(status_code=409, detail="Username Already Exists")

    # Saves user to database
    # TODO: Hash + Salt Password
    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hash_pass(user.password),
    }

    result = users.insert_one(new_user)
    print(
        "new user created in collections users: id:"
        f"{result.inserted_id}\n user: {new_user}"
    )

    # Returns 200
    return {
        "message": "Registration successful",
        "user": {"username": user.username, "email": user.email},
    }


# TODO: parse variables via header


@app.post("/api/users/login")
def login(user: UserLogin):
    valid, code = check_login(user)
    if valid:
        return {"session_token": create_session(get_uid_from_user(user.username))}
    else:
        raise HTTPException(status_code=code, detail="Permission Denied")


@app.post("/api/users/logout")
def logout(request: Request):
    cookie_token = request.cookies.get("session_token", None)
    if cookie_token is None:
        return RedirectResponse(url="/login", status_code=302)
    uid = sessions.get(cookie_token, None)
    if uid:
        sessions.pop(cookie_token)
        return {"response": "true"}
    else:
        raise HTTPException(status_code=401, detail="Bad Token")


# USER ENDPOINTS ---------------------------------------------------------------
#
#

#
#
# HABIT ENDPOINTS --------------------------------------------------------------


class HabitAdd(BaseModel):
    type: str
    name: str


class HabitUpdate(BaseModel):
    id: str
    type: str
    name: str | None = None
    done: bool | None = None


class HabitDelete(BaseModel):
    id: str
    type: str


#
# Helper Functions for habits -------------------------------------------------


def check_uid(uid: ObjectId):
    """check uid exists"""
    if not uid:
        raise HTTPException(status_code=401, detail="Bad Token")


def check_user(user: dict):
    """check user exists"""
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")


def check_habit_type(habit_type: str):
    """check habit type exists"""
    if habit_type != "custom":
        raise HTTPException(status_code=404, detail="Habit type does not exist")


def check_id(id: str):
    """check id is a valid mongo db object id"""
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=422, detail="Invalid id")


def check_habit(typ: str, habit: dict, owner: dict):
    """check habit exists and is owned by owner"""
    if not habit:
        raise HTTPException(status_code=404, detail="Habit does not exist")

    if (
        typ not in owner.get("habits", {})
        or str(habit["_id"]) not in owner["habits"][typ]
    ):
        raise HTTPException(status_code=403, detail="Habit not owned by user")


def check_habit_done(date: dt.datetime) -> bool:
    """checks if a given date is on the same day as today"""
    aest = pytz.timezone("Australia/Sydney")
    if not date:
        return False
    today = dt.datetime.now(aest)
    # make date timezone aware
    date = date.replace(tzinfo=dt.timezone.utc)
    date = date.astimezone(aest)
    return today.date() == date.date()


def streak_update(habit: dict, habit_type: str) -> None:
    """resets streak if its broken"""
    aest = pytz.timezone("Australia/Sydney")
    if "last_done" not in habit:
        return
    date = habit["last_done"]
    yesterday = dt.datetime.now(aest) - dt.timedelta(days=1)
    # make date timezone aware
    date = date.replace(tzinfo=dt.timezone.utc)
    date = date.astimezone(aest)

    if date.date() < yesterday.date() and habit["streak"] != 0:
        client["habits"][habit_type].update_one(
            {"_id": habit["_id"]},
            {
                "$set": {
                    "streak": 0,
                },
            },
        )
        habit["streak"] = 0


# Helper Functions for habits -------------------------------------------------
#


@app.get("/api/habit")
def get_habit(
    spnw_auth_token: Annotated[str | None, Header()], hid: str, habit_type: str
):
    """gets specific habit for given user"""
    user_id = get_user_from_session(spnw_auth_token)
    check_uid(user_id)

    users = client["users"]["users"]
    user = users.find_one({"_id": user_id})

    check_user(user)
    check_habit_type(habit_type)
    check_id(hid)

    habits = client["habits"][habit_type]
    habit = habits.find_one({"_id": ObjectId(hid)})
    check_habit(habit_type, habit, user)

    streak_update(habit, habit_type)

    return {
        "name": habit["name"],
        "streak": habit["streak"],
        "last_done": habit.get("last_done", None),
    }


@app.get("/api/habits")
def get_habits(spnw_auth_token: Annotated[str | None, Header()]):
    """gets all habits for given user"""
    user_id = get_user_from_session(spnw_auth_token)
    check_uid(user_id)

    users = client["users"]["users"]
    user = users.find_one({"_id": user_id})
    check_user(user)

    return user.get("habits", {})


@app.put("/api/habits")
def update_habit(
    spnw_auth_token: Annotated[str | None, Header()],
    habit_info: HabitUpdate,
    response: Response,
):
    """updates a habit"""
    user_id = get_user_from_session(spnw_auth_token)
    check_uid(user_id)

    users = client["users"]["users"]
    user = users.find_one({"_id": user_id})

    check_user(user)
    check_habit_type(habit_info.type)
    check_id(habit_info.id)

    habits = client["habits"][habit_info.type]
    habit = habits.find_one({"_id": ObjectId(habit_info.id)})
    check_habit(habit_info.type, habit, user)

    if habit_info.done:
        streak_update(habit, habit_info.type)

        if check_habit_done(habit.get("last_done", None)):
            raise HTTPException(
                status_code=429, detail="Habit can only be done once a day"
            )

        habits.update_one(
            {"_id": ObjectId(habit_info.id)},
            {"$currentDate": {"last_done": True}, "$inc": {"streak": 1}},
        )

    if habit_info.name:
        habits.update_one(
            {"_id": ObjectId(habit_info.id)}, {"$set": {"name": habit_info.name}}
        )

    # Query new changes
    habit = habits.find_one({"_id": ObjectId(habit_info.id)})

    response.headers["HX-Trigger"] = habit_info.id
    return {
        "message": "Habit updated",
        "habit": {"name": habit["name"], "streak": habit["streak"]},
    }


@app.post("/api/habits")
def add_habits(
    spnw_auth_token: Annotated[str | None, Header()],
    habit_info: HabitAdd,
    Accept: Annotated[str | None, Header()] = None,
):
    """adds a habit"""
    user_id = get_user_from_session(spnw_auth_token)
    check_uid(user_id)

    users = client["users"]["users"]
    user = users.find_one({"_id": user_id})

    check_user(user)
    check_habit_type(habit_info.type)

    # Adds habit to database
    new_habit = {"name": habit_info.name, "streak": 0}

    habits = client["habits"][habit_info.type]
    result = habits.insert_one(new_habit)

    # Add habit id to user habits field
    users.update_one(
        {"_id": user["_id"]},
        {
            "$push": {
                f"habits.{habit_info.type}": str(result.inserted_id),
            },
        },
    )

    if Accept == "text/html":
        habit_temp = templates.get_template("habit.html")
        html = habit_temp.render(
            {
                "title": habit_info.name,
                "streak": 0,
                "done": False,
                "id": str(result.inserted_id),
                "type": habit_info.type,
            }
        )
        return HTMLResponse(content=html, status_code=200)
    # Returns 200
    return {
        "message": "Habit added",
        "habit": {
            "id": str(result.inserted_id),
            "name": habit_info.name,
            "type": habit_info.type,
        },
    }


@app.delete("/api/habits")
def delete_habit(
    spnw_auth_token: Annotated[str | None, Header()], habit_info: HabitDelete
):
    user_id = get_user_from_session(spnw_auth_token)
    check_uid(user_id)

    users = client["users"]["users"]
    user = users.find_one({"_id": user_id})

    check_user(user)
    check_habit_type(habit_info.type)
    check_id(habit_info.id)

    habits = client["habits"][habit_info.type]
    habit = habits.find_one({"_id": ObjectId(habit_info.id)})

    check_habit(habit_info.type, habit, user)

    habits.delete_one({"_id": habit["_id"]})

    users.update_one(
        {"_id": user_id},
        {
            "$pull": {
                f"habits.{habit_info.type}": str(habit["_id"]),
            },
        },
    )

    return {"response": "true"}


# HABIT ENDPOINTS --------------------------------------------------------------
#
#


#
#
# FE ENDPOINTS -----------------------------------------------------------------


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, cookies: Annotated[TokenCookie, Cookie()]):
    cookie_token = request.cookies.get("session_token", None)
    user_id = get_user_from_session(cookies.session_token)
    if cookie_token is None:
        return RedirectResponse(url="/login", status_code=302)
    if user_id is None:
        return RedirectResponse(url="/login", status_code=302)

    user = client["users"]["users"].find_one({"_id": user_id})
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    user_habits = user.get("habits", {})
    habits = []
    for typ, ids in user_habits.items():
        habit_objs = client["habits"][typ].find(
            {"_id": {"$in": [ObjectId(id) for id in ids]}}
        )
        for habit in habit_objs:
            streak_update(habit, typ)
            habits.append(
                {
                    "title": habit["name"],
                    "streak": habit["streak"],
                    "done": check_habit_done(habit.get("last_done")),
                    "id": habit["_id"],
                    "type": typ,
                }
            )
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "habits": habits}
    )


@app.get("/fe/habit", response_class=HTMLResponse)
def one_habit(cookies: Annotated[TokenCookie, Cookie()], hid: str, type: str):
    user_id = get_user_from_session(cookies.session_token)
    check_uid(user_id)

    users = client["users"]["users"]
    user = users.find_one({"_id": user_id})

    check_user(user)
    check_habit_type(type)
    check_id(hid)

    habits = client["habits"][type]
    habit = habits.find_one({"_id": ObjectId(hid)})
    check_habit(type, habit, user)
    streak_update(habit, type)

    habit_temp = templates.get_template("habit.html")
    return habit_temp.render(
        {
            "title": habit["name"],
            "streak": habit["streak"],
            "done": check_habit_done(habit.get("last_done")),
            "id": hid,
            "type": type,
        }
    )


# FE ENDPOINTS -----------------------------------------------------------------
#
#
