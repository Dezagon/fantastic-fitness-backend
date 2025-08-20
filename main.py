from fastapi import Depends, FastAPI, status, HTTPException
from sqlmodel import Session, select
from database import get_db

from models import Member, Trainer, Class, Attendance
from schemas import CreateMemberRequest, CreateTrainerRequest, CreateClassRequest, UpdateMemberRequest, UpdateTrainerRequest, UpdateClassRequest

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# GET
@app.get("/members")
async def get_members(db: Session = Depends(get_db)) -> list[Member]:
    return db.exec(select(Member)).all()

@app.get("/trainers")
async def get_trainers(db: Session = Depends(get_db)) -> list[Trainer]:
    return db.exec(select(Trainer)).all()

@app.get("/classes")
async def get_classes(db: Session = Depends(get_db)) -> list[Class]:
    return db.exec(select(Class)).all()

# CREATE

@app.post("/members", status_code=status.HTTP_201_CREATED)
async def create_member(create_member_request: CreateMemberRequest, db: Session = Depends(get_db)) -> int:
    member: Member = Member(create_member_request.model_dump())
    db.add(member)
    db.commit()
    db.refresh(member)
    return member.id

@app.post("/trainers", status_code=status.HTTP_201_CREATED)
async def create_trainer(create_trainer_request: CreateTrainerRequest, db: Session = Depends(get_db)) -> int:
    trainer: Trainer = Trainer(**create_trainer_request.model_dump())
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer.id

@app.post("/classes", status_code=status.HTTP_201_CREATED)
async def create_class(create_class_request: CreateClassRequest, db: Session = Depends(get_db)) -> int:
    course: Class = Class(**create_class_request.model_dump())
    db.add(course)
    db.refresh()
    db.commit(course)
    return course.id

# PATCH