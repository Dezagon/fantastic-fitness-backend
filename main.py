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

# GET: BY ID
@app.get("/members/{member_id}", status_code=status.HTTP_200_OK)
async def get_member_by_id(member_id, db: Session = Depends(get_db)) -> Member:
    member: Member | None = db.get(Member, member_id)
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    return member

@app.get("/trainers/{trainer_id}", status_code=status.HTTP_200_OK)
async def get_trainer_by_id(trainer_id, db: Session = Depends(get_db)) -> Trainer:
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {trainer_id} not found")
    return trainer

@app.get("/classes/{class_id}", status_code=status.HTTP_200_OK)
async def get_class_by_id(class_id: int, db: Session = Depends(get_db)) -> Class:
    course: Class | None = db.get(Class, class_id)
    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    return course

# CREATE
@app.post("/members", status_code=status.HTTP_201_CREATED)
async def create_member(create_member_request: CreateMemberRequest, db: Session = Depends(get_db)) -> int:
    member: Member = Member(create_member_request.model_dump(), id=len(db.exec(select(Member)).all()) + 1)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member.id

@app.post("/trainers", status_code=status.HTTP_201_CREATED)
async def create_trainer(create_trainer_request: CreateTrainerRequest, db: Session = Depends(get_db)) -> int:
    trainer: Trainer = Trainer(**create_trainer_request.model_dump(), id=len(db.exec(select(Member)).all()) + 1)
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer.id

@app.post("/classes", status_code=status.HTTP_201_CREATED)
async def create_class(create_class_request: CreateClassRequest, db: Session = Depends(get_db)) -> int:
    course: Class = Class(**create_class_request.model_dump(), id=len(db.exec(select(Member)).all()) + 1)
    db.add(course)
    db.refresh()
    db.commit(course)
    return course.id

# POST: CHECK MEMBER INTO CLASS
@app.post("/attendance/{class_id}/{member_id}", status_code=status.HTTP_201_CREATED)
async def check_member_into_class(class_id: int, member_id: int, db: Session = Depends(get_db)) -> int:
    course: Class | None = db.get(Class, class_id)
    member: Member | None = db.get(Member, member_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")

    course.members.append(member)
    return member.id

# PATCH
@app.patch("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_member(member_id: int, update_member_request: UpdateMemberRequest, db: Session = Depends(get_db)):
    member: Member | None = db.get(Member, member_id)
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    
    for k, v in update_member_request.model_dump(exclude_unset=True).items():
        setattr(member, k, v)

    db.commit()

@app.patch("/trainers/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_trainer(trainer_id: int, update_trainer_request: UpdateTrainerRequest, db: Session = Depends(get_db)):
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    
    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {trainer_id} not found")
    
    for k, v in update_trainer_request.model_dump(exclude_unset=True).items():
        setattr(trainer, k, v)

    db.commit()

@app.patch("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_class(class_id: int, update_class_request: UpdateClassRequest, db: Session = Depends(get_db)):
    course: Class | None = db.get(Class, class_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")

    for k, v in update_class_request.model_dump(exclude_unset=True).items():
        setattr(course, k, v)

    db.commit()

# DELETE
@app.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(member_id, db: Session = Depends(get_db)):
    member: Member | None = db.get(Member, member_id)

    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    db.delete(member)
    db.commit()

@app.delete("/trainers/{trainer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trainer(trainer_id, db: Session = Depends(get_db)):
    trainer: Trainer | None = db.get(Trainer, trainer_id)

    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {trainer_id} not found")
    db.delete(trainer)
    db.commit()

@app.delete("/classes/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(class_id: int, db: Session = Depends(get_db)):
    course: Class | None = db.get(Class, class_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    db.delete(course)
    db.commit()