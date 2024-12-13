from typing import Annotated
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, EmailStr
import bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from os import getenv
import secrets


app = FastAPI()
client = MongoClient(getenv("MONGO_URI"), server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


#
#
# USER ENDPONTS ---------------------------------------------------------------

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
    return sessions.get(token)


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
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def verify_pass(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


# Helper Functions for Auth -------------------------------------------------
#


@app.delete("/users")
def delete_user(spnw_auth_token: Annotated[str | None, Header()]):
    token = spnw_auth_token
    uid = sessions.get(token, None)
    if uid:
        users = client["users"]["users"]
        filter = {"_id": uid}
        users.delete_one(filter)
        return {"response": "true"}
    else:
        raise HTTPException(status_code=401, detail="Bad Token")


#  TODO: Add more security layers, e.g make password certain length


@app.post("/users/register")
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
    print(f"new user created in collections users: id: {
          result.inserted_id}\n user: {new_user}")

    # Returns 200
    return {"message": "Registration successful", "user":
            {"username": user.username, "email": user.email}}

# TODO: parse variables via header


@app.post("/users/login")
def login(user: UserLogin):
    valid, code = check_login(user)
    if valid:
        return {"session_token": create_session(get_uid_from_user(user.username))}
    else:
        raise HTTPException(status_code=code, detail="Permission Denied")


@app.post("/users/logout")
def logout(spnw_auth_token: Annotated[str | None, Header()]):
    token = spnw_auth_token
    uid = sessions.get(token, None)
    if uid:
        sessions.pop(token)
        return {"response": "true"}
    else:
        raise HTTPException(status_code=401, detail="Bad Token")


# USER ENDPONTS ---------------------------------------------------------------
#
#


#
#
# HABIT ENDPONTS --------------------------------------------------------------

class HabitAdd(BaseModel):
    habit_type: str
    habit_name: str


@app.get("/habits/token={token}/habit={habit}")
def get_habit():
    '''gets specific habit for given user'''
    return {"response": "yay"}


@app.get("/habits/token={token}/")
def get_habits():
    '''gets all habits for given user'''
    return {"response": "yay"}


@app.put("/habits/token={token}/hid={hid}")
def update_habits():
    '''updates habit'''
    return {"response": "yay"}


@app.post("/habits")
def add_habits(spnw_auth_token: Annotated[str | None, Header()], habit: HabitAdd):
    '''adds a habit'''
    users = client["users"]["users"]
    user_id = get_user_from_session(spnw_auth_token)

    # check if user exists
    user = users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    if habit.habit_type != "custom":
        raise HTTPException(status_code=404, detail="Habit type does not exist")

    # Adds habit to database
    new_habit = {
        "name": habit.habit_name,
        "streak": 0
    }

    habits = client["habits"][habit.habit_type]
    result = habits.insert_one(new_habit)

    # Add habit id to user habits field
    users.update_one({"_id": user["_id"]}, {
        "$push": {
            f"habits.{habit.habit_type}": str(result.inserted_id),
        },
    })

    # Returns 200
    return {
        "message": "Habit added",
        "habit": {
            "name": habit.habit_name,
            "type": habit.habit_type,
        },
    }
# HABIT ENDPONTS --------------------------------------------------------------
#
#
