from pydantic import BaseModel
from models import Member, Trainer, Class 

# CREATE
class CreateMemberRequest(BaseModel):
    name: str
    classes: list[Class]
    active: bool

class CreateTrainerRequest(BaseModel):
    name: str
    specialty: str
    classes: list[Class]

class CreateClassRequest(BaseModel):
    name: str
    trainer_id: int
    trainer: Trainer
    members: list[Member] 
    date: str
    duration: int

# UPDATE
class UpdateMemberRequest(BaseModel):
    name: str | None = None
    classes: str | None = None
    active: bool | None = None

class UpdateTrainerRequest(BaseModel):
    name: str | None = None
    specialty: str | None = None
    classes: list[Class] | None = None

class UpdateClassRequest(BaseModel):
    name: str | None = None
    trainer_id: int | None = None
    trainer: Trainer | None = None
    members: list[Member] | None = None
    date: str | None = None
    duration: int | None = None

    


