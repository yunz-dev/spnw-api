from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from os import getenv

app = FastAPI()
client = MongoClient(getenv("MONGO_URI"), server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)


def check_login(username: str, password: str) -> (bool, int):
    users = client["users"]["users"]
    user = users.find_one({"username": username})

    if user is None:
        return (False, 404)

    if user["password"] == password:
        return (True, 200)
    return (False, 403)


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


def hash_pass(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def verify_pass(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


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


@app.post("/users/login/user={user}/pass={pw}")
def login(user: str, pw: str):
    valid, code = check_login(user, pw)
    if valid:
        return {"response": "true"}
    else:
        raise HTTPException(status_code=code, detail="Permission Denied")


# USER ENDPONTS ---------------------------------------------------------------
#
#


#
#
# HABIT ENDPONTS --------------------------------------------------------------
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
# HABIT ENDPONTS --------------------------------------------------------------
#
#
