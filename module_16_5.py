from fastapi import FastAPI, Request, HTTPException, Path
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from typing import Annotated, List
app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": True}, debug=True)
# Настраиваем Jinja2 для загрузки шаблонов из папки templates
templates = Jinja2Templates(directory="templates")
class User(BaseModel):
    id: int
    username: str
    age: int
users: List[User] = []
@app.get("/", response_class=HTMLResponse)
def welcome(request: Request):
    return templates.TemplateResponse("users.html", {"request": request, "users": users})
@app.get("/user/{user_id}", response_class=HTMLResponse)
def get_user(request: Request, user_id: int = Path(..., ge=1, le=100, description="Enter User ID")):
    for user in users:
        if user.id == user_id:
            return templates.TemplateResponse("users.html", {"request": request, "user": user})
    raise HTTPException(status_code=404, detail="User not found")
@app.get("/user/{username}/{age}", response_model=str)
def get_user_info(
    username: Annotated[str, Path(min_length=5, max_length=20, pattern="^[A-Za-z0-9_-]+$", description="Enter username")],
    age: Annotated[int, Path(ge=18, le=120, description="Enter age")],
):
    return f"Информация о пользователе. Имя: {username}, Возраст: {age}"
@app.get("/users", response_model=List[User])
def get_users():
    return users
@app.post("/user/{username}/{age}", response_model=User)
def create_user(username: str, age: int):
    new_user_id = max((user.id for user in users), default=0) + 1
    new_user = User(id=new_user_id, username=username, age=age)
    users.append(new_user)
    return new_user
@app.put("/user/{user_id}/{username}/{age}", response_model=User)
def update_user(user_id: int, username: str, age: int):
    for user in users:
        if user.id == user_id:
            user.username = username
            user.age = age
            return user
    raise HTTPException(status_code=404, detail="User was not found")
@app.delete("/user/{user_id}", response_model=dict)
def delete_user(user_id: int):
    for i, user in enumerate(users):
        if user.id == user_id:
            delete_user = users.pop(i)
            return {"detail": f"User ID :{delete_user} deleted!"}
    raise HTTPException(status_code=404, detail="User not found")