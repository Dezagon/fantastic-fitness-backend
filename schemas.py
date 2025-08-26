from pydantic import BaseModel
# from models import Member, Trainer, Class 

# GET
# GET MEMBER RESPONSE
class GetMemberResponse(BaseModel):
    id: int
    name: str
    classes: list["ClassResponse"]
    active: bool

# GET TRAINER RESPONSE
class GetTrainerResponse(BaseModel):
    id: int
    name: str
    specialty: str
    classes: list["GetClassResponse"]

# GET CLASS RESPONSE
class GetClassResponse(BaseModel):
    id: int
    name: str
    trainer_id: int
    trainer: str
    date: str
    members: list[str]
    duration: int

# SIMPLE CLASS RESPONSE
class ClassResponse(BaseModel):
    name: str
    trainer_id: int
    date: str
    duration: int

# GET ATTENDANCE PER CLASS
class AttendancePerClassResponse(BaseModel):
    class_id: int 
    attendance_total: int

# GET ATTENDANCE PER TRAINER
class AttendancePerTrainerResponse(BaseModel):
    trainer_id: int
    attendance_total: int | None = 0



# CREATE
class CreateMemberRequest(BaseModel):
    name: str
    active: bool

class CreateTrainerRequest(BaseModel):
    name: str
    specialty: str

class CreateClassRequest(BaseModel):
    name: str
    trainer_id: int
    date: str
    duration: int

# UPDATE
class UpdateMemberRequest(BaseModel):
    name: str | None = None
    active: bool | None = None

class UpdateTrainerRequest(BaseModel):
    name: str | None = None
    specialty: str | None = None

class UpdateClassRequest(BaseModel):
    name: str | None = None
    trainer_id: int | None = None
    date: str | None = None
    duration: int | None = None

    


