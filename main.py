from fastapi import FastAPI, Request, Depends,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import Base,SessionLocal,engine,get_db
from sqlalchemy import create_engine, Column, Integer, String,Boolean



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Database model
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200),nullable=False)
    completed = Column(Boolean, default=False, nullable=False)

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
@app.get("/")
def home():
    return RedirectResponse(url="/tasks")
@app.get("/tasks")
def show_task(request: Request, db=Depends(get_db)):
    tasks = db.query(Task).order_by(Task.id.desc()).all()
    return templates.TemplateResponse(
        request=request,name="task.html",context={"tasks":tasks}
    )

@app.post("/tasks")
def add_task(
    title:str=Form(...),db= Depends(get_db)
):
    new_task = Task(title=title)
    db.add(new_task)
    db.commit()
    return RedirectResponse(
        url='/tasks',
        status_code=303
    )
@app.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db=Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is not None:
        task.completed = True
        db.commit()
    return RedirectResponse(
        url='/tasks',
        status_code=303
    )
@app.post("/tasks/{task_id}/delete")
def delete_task(
    task_id : int,
    db = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is not None:
        db.delete(task)
        db.commit()
    return RedirectResponse(
        url='/tasks',
        status_code=303
    )
