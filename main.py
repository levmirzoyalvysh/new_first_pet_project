# ИМПОРТЫ С 1-7 СТРОКУ
from contextlib import asynccontextmanager

from fastapi import FastAPI , status
from fastapi import Depends
from pydantic import BaseModel
from uuid import uuid4
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, Mapped
from sqlalchemy import create_engine , select
from sqlalchemy.orm import mapped_column
from starlette.middleware.cors import CORSMiddleware
#ЭТО МОЕ АПИ И НАСТРОЙКИ КОРСА

#
@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
)

# ССЫЛКА НА ПОДКЛЮЧЕНИЕ К БД
DATABASE_URL = "postgresql+psycopg://postgres:admim@127.0.0.1:15432/postgres"
engine = create_engine(DATABASE_URL)
Sessionlocal = sessionmaker[Session](bind=engine)

# ТАСК ОРМ МОДЕЛЬ ТАБЛИЦЫ БАЗЫ ДАННЫХ НА СКЛ АЛХЕМИ
class Base(DeclarativeBase): # БАЗОВЫЙ КЛАСС ОТ КОТОРОГО НАСЛЕДУЮТСЯ ВСЕ МОДЕЛИ
    id: Mapped[str] = mapped_column(primary_key=True,default=lambda: str(uuid4()) )

class TaskORM(Base):
    __tablename__ = "tasks"

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)




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





def get_db() :
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()

def task_orm_to_model(task_orm: TaskORM) -> TaskSchema:
    return TaskSchema(
        id=task_orm.id,
        title=task_orm.title,
        completed=task_orm.completed,
    )


#РУЧКИ ЗАПРОСОВ
@app.get("/")
def hello_world():
    return {"Hello": "World"}

@app.get("/tasks")
def read_tasks(db: Session = Depends(get_db))->list[TaskSchema]:
    tasks_from_db = db.scalars(select(TaskORM)).all()
    return [task_orm_to_model(task) for task in tasks_from_db]

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema ,db: Session = Depends(get_db))-> TaskSchema:
    new_task = TaskORM( title= payload.title, completed=False)
    db.add(new_task)
    db.commit()
    return task_orm_to_model(new_task)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema , db: Session = Depends(get_db)):
    task_for_update = db.get(TaskORM, task_id)
    if payload.title:
        task_for_update.title = payload.title
    if payload.completed:
        task_for_update.completed = payload.completed

    db.commit()
    return task_for_update

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()

