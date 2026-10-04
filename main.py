# ИМПОРТЫ С 1-7 СТРОКУ
from fastapi import FastAPI , status
from pydantic import BaseModel
from uuid import uuid4
from starlette.middleware.cors import CORSMiddleware
#ЭТО МОЕ АПИ И НАСТРОЙКИ КОРСА
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

#КЛАССЫ Это Pydantic-модель — класс,
# который описывает структуру данных
# и автоматически проверяет их при
# получении/отправке через FastAPI
class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool

class TaskCreateSchema(BaseModel):
    title: str

class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None
#ПРОСТО СПИСОК ЗАДАЧ
tasks: list[TaskSchema] = []


#РУЧКИ ЗАПРОСОВ
@app.get("/")
def hello_world():
    return {"Hello": "World"}

@app.get("/tasks")
def read_tasks()->list[TaskSchema]:
    return tasks

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema)-> TaskSchema:
    new_task = TaskSchema(id=str(uuid4()), title= payload.title, completed=False)
    tasks.append(new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema):
    for task in tasks:
        if task.id == task_id:
            if payload.title:
                task.title = payload.title
            if task.completed is not None:
                task.completed = payload.completed
            return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)

