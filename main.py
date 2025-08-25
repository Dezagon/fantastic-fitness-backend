from fastapi import Depends, FastAPI, status, HTTPException, APIRouter
from sqlmodel import Session, select, Field
from sqlalchemy import func
from database import get_db

from models import Member, Trainer, Class, Attendance
from schemas import GetMemberResponse, GetTrainerResponse, GetClassResponse, AttendancePerClassResponse, ClassResponse, CreateMemberRequest, CreateTrainerRequest, CreateClassRequest, UpdateMemberRequest, UpdateTrainerRequest, UpdateClassRequest

app = FastAPI()
router = APIRouter()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# GET
@router.get("/members", tags=["members"])
async def get_members(db: Session = Depends(get_db)) -> list[GetMemberResponse]:
    return [GetMemberResponse(id=member.id, name=member.name, active=member.active, classes=[ClassResponse(name=course.name, trainer_id=course.trainer_id, date=course.date, duration=course.duration) for course in member.classes]) for member in db.exec(select(Member)).all()]

@router.get("/trainers", tags=["trainers"])
async def get_trainers(db: Session = Depends(get_db)) -> list[GetTrainerResponse]:
    return [GetTrainerResponse(id=trainer.id, name=trainer.name, specialty=trainer.specialty, classes=[GetClassResponse(id=course.id, name=course.name, trainer_id=course.trainer_id, trainer=course.trainer.name, date=course.date, members=[member.name for member in course.members], duration=course.duration) for course in trainer.classes]) for trainer in db.exec(select(Trainer)).all()]

@router.get("/classes", tags=["classes"])
async def get_classes(db: Session = Depends(get_db)) -> list[GetClassResponse]:
    return [GetClassResponse(id=course.id, name=course.name, trainer_id=course.trainer_id, trainer=course.trainer.name, date=course.date, duration=course.duration, members=[member.name for member in course.members]) for course in db.exec(select(Class)).all()]

# GET: BY ID
@router.get("/members/{member_id}", tags=["members"], status_code=status.HTTP_200_OK)
async def get_member_by_id(member_id, db: Session = Depends(get_db)) -> GetMemberResponse:
    member: Member | None = db.get(Member, member_id)
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    return GetMemberResponse(id=member.id, name=member.name, active=member.active, classes=[ClassResponse(name=course.name, trainer_id=course.trainer_id, date=course.date, duration=course.duration) for course in member.classes])

@router.get("/trainers/{trainer_id}", tags=["trainers"], status_code=status.HTTP_200_OK)
async def get_trainer_by_id(trainer_id, db: Session = Depends(get_db)) -> GetTrainerResponse:
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {trainer_id} not found")
    return GetTrainerResponse(id=trainer.id, name=trainer.name, specialty=trainer.specialty, classes=[ClassResponse(name=course.name, trainer_id=course.trainer_id, date=course.date, duration=course.duration) for course in trainer.classes])

@router.get("/classes/{class_id}", tags=["classes"], status_code=status.HTTP_200_OK)
async def get_class_by_id(class_id: int, db: Session = Depends(get_db)) -> ClassResponse:
    course: Class | None = db.get(Class, class_id)
    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    return GetClassResponse(id=course.id, name=course.name, trainer_id=course.trainer_id, trainer=course.trainer.name, date=course.date, members=[member.name for member in course.members], duration=course.duration)

# GET REPORTS
# Attendance per class (count per class_id)
@router.get("/attendance/courses", tags=["attendance"], status_code=status.HTTP_200_OK)
async def get_attendance_per_class(db: Session = Depends(get_db)):
    final_results: list[str] = []
    results = db.exec(select(Attendance.member_id, func.count(Attendance.class_id).label("attendance_per_class")).group_by(Attendance.member_id)).all()
    for member_id, attendance_per_class in results:
        final_results.append(f"Member ID: {member_id}, Classes attended: {attendance_per_class}")
    return final_results

#Attendance per trainer (how many members attend their classes)
@router.get("/attendance/attendance_per_trainer", tags=["attendance"], status_code=status.HTTP_200_OK)
async def get_attendance_per_trainer(db: Session = Depends(get_db)):
    final_results: list[str] = []
    results = db.exec(select(Trainer.id, func.count(Trainer.classes).label("members_attended")).group_by(Trainer.id))
    for trainer_id, members_attended in results:
        final_results.append(f"Trainer ID: {trainer_id}, Total members attended: {members_attended}")
    return final_results


# #Most popular day of the week for classes (group by date)
# @router.get("/attendance/day_of_week", tags=["attendance"], status_code=status.HTTP_200_OK)
# async def get_attendance_by_day_of_week(db: Session = Depends(get_db)):
#     final_results: list[str] = []
#     results = db.exec(select(Class.id, func.count(Class.members).label()))

# # Active members
# @router.get("/attendance/active_members", tags=["attendance"], status_code=status.HTTP_200_OK)

# CREATE
@router.post("/members", tags=["members"], status_code=status.HTTP_201_CREATED)
async def create_member(create_member_request: CreateMemberRequest, db: Session = Depends(get_db)) -> int:
    member: Member = Member(**create_member_request.model_dump())
    member.id = len(db.exec(select(Member)).all()) + 1
    db.add(member)
    db.commit()
    db.refresh(member)
    return member.id

@router.post("/trainers", tags=["trainers"], status_code=status.HTTP_201_CREATED)
async def create_trainer(create_trainer_request: CreateTrainerRequest, db: Session = Depends(get_db)) -> int:
    trainer: Trainer = Trainer(**create_trainer_request.model_dump())
    trainer.id = len(db.exec(select(Trainer)).all()) + 1
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer.id

@router.post("/classes", tags=["classes"], status_code=status.HTTP_201_CREATED)
async def create_class(create_class_request: CreateClassRequest, db: Session = Depends(get_db)) -> int:
    course: Class = Class(**create_class_request.model_dump())
    course.id = len(db.exec(select(Class)).all()) + 1
    trainer: Trainer | None = db.get(Trainer, create_class_request.trainer_id)
    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {create_class_request.trainer_id} not found")
    course.trainer_id = trainer.id
    course.trainer = trainer
    trainer.classes.append(course)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course.id

# POST: CHECK MEMBER INTO CLASS
@router.post("/attendance/{class_id}/{member_id}", tags=["attendance"], status_code=status.HTTP_201_CREATED)
async def check_member_into_class(class_id: int, member_id: int, db: Session = Depends(get_db)) -> int:
    course: Class | None = db.get(Class, class_id)
    member: Member | None = db.get(Member, member_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    
    if member in course.members:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Member with ID of {member.id} already in class")

    course.members.append(member)
    member.classes.append(course)
    db.commit()
    db.refresh(member)
    db.refresh(course)
    raise HTTPException(status_code=status.HTTP_201_CREATED, detail=f"Member with ID of {member.id} successfully checked into class with ID of {course.id}")

# PATCH
@router.patch("/members/{member_id}", tags=["members"], status_code=status.HTTP_204_NO_CONTENT)
async def update_member(member_id: int, update_member_request: UpdateMemberRequest, db: Session = Depends(get_db)):
    member: Member | None = db.get(Member, member_id)
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    
    for k, v in update_member_request.model_dump(exclude_unset=True).items():
        setattr(member, k, v)

    db.commit()

@router.patch("/trainers/{trainer_id}", tags=["trainers"], status_code=status.HTTP_204_NO_CONTENT)
async def update_trainer(trainer_id: int, update_trainer_request: UpdateTrainerRequest, db: Session = Depends(get_db)):
    trainer: Trainer | None = db.get(Trainer, trainer_id)
    
    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {trainer_id} not found")
    
    for k, v in update_trainer_request.model_dump(exclude_unset=True).items():
        setattr(trainer, k, v)

    db.commit()

@router.patch("/classes/{class_id}", tags=["classes"], status_code=status.HTTP_204_NO_CONTENT)
async def update_class(class_id: int, update_class_request: UpdateClassRequest, db: Session = Depends(get_db)):
    course: Class | None = db.get(Class, class_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")

    if update_class_request.trainer_id != None:
        trainer: Trainer | None = db.get(Trainer, update_class_request.trainer_id)
        if trainer == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {update_class_request.trainer_id} not found")
        course.trainer = trainer

    for k, v in update_class_request.model_dump(exclude_unset=True).items():
        setattr(course, k, v)

    db.commit()

# DELETE
@router.delete("/members/{member_id}", tags=["members"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(member_id, db: Session = Depends(get_db)):
    member: Member | None = db.get(Member, member_id)

    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    db.delete(member)
    db.commit()

@router.delete("/trainers/{trainer_id}", tags=["trainers"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_trainer(trainer_id, db: Session = Depends(get_db)):
    trainer: Trainer | None = db.get(Trainer, trainer_id)

    if trainer == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trainer with ID of {trainer_id} not found")
    db.delete(trainer)
    db.commit()

@router.delete("/classes/{class_id}", tags=["classes"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(class_id: int, db: Session = Depends(get_db)):
    course: Class | None = db.get(Class, class_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    db.delete(course)
    db.commit()

# DELETE: Member from Class
@router.delete("/classes/{class_id}/{member_id}", tags=["classes"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_member_from_class(class_id: int, member_id: int, db: Session = Depends(get_db)):
    course: Class | None = db.get(Class, class_id)
    member: Member | None = db.get(Member, member_id)

    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    if member not in course.members:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not in class")

    course.members.remove(member)
    db.commit()

    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)


# DELETE: Class from Member classes list
@router.delete("/members/{member_id}/{class_id}", tags=["members"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_class_from_member(member_id: int, class_id: int, db: Session = Depends(get_db)):
    member: Member | None = db.get(Member, member_id)
    course: Class | None = db.get(Class, class_id)

    if member == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID of {member_id} not found")
    if course == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not found")
    if course not in member.classes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Class with ID of {class_id} not in member's classes list")

    member.classes.remove(course)
    db.commit()
    

app.include_router(router)