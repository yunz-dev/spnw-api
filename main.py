from fastapi import FastAPI, HTTPException
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
