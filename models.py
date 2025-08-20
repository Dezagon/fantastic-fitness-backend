from sqlmodel import Field, Relationship, SQLModel

# Attendance linking table
class Attendance(SQLModel, table=True):
    class_id: int | None = Field(foreign_key="class.id", primary_key=True)
    member_id: int | None = Field(foreign_key="member.id", primary_key=True)

# Member
class Member(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str
    classes: list["Class"] = Relationship(back_populates="members", link_model=Attendance)
    active: bool

# Trainer
class Trainer(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str
    specialty: str
    classes: list["Class"] = Relationship(back_populates="trainer")

# Class
class Class(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str
    trainer_id: int = Field(foreign_key="trainer.id")
    trainer: Trainer = Relationship(back_populates="classes")
    members: list[Member] = Relationship(back_populates="classes", link_model=Attendance)
    date: str
    duration: int


