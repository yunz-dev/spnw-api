from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# TODO: parse variables via header
@app.post("/users/login/user={user}/pass={pw}")
def login(user: str, pw: str):
    if user == "yunz" and pw == "<3":
        return {"response": "true"}
    else:
        raise HTTPException(status_code=403, detail="Permission Denied")
