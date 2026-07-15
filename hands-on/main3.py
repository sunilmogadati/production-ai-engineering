import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Same database setup as main2, reused for the CRUD demo.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/classdemo",
)

engine = create_engine(DATABASE_URL, echo=True)


# Base model with the shared student fields.
class StudentBase(SQLModel):
    name: str = Field(index=True)
    course: str
    age: int = Field(gt=0, lt=120)


class Student(StudentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int


# All fields are optional because PATCH updates only the fields provided.
class StudentUpdate(SQLModel):
    name: str | None = None
    course: str | None = None
    age: int | None = Field(default=None, gt=0, lt=120)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_student_or_404(student_id: int, session: Session) -> Student:
    # Put repeated lookup logic in one place.
    student = session.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} was not found")
    return student


app = FastAPI(title="FastAPI Demo 3: Full CRUD with SQLModel")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Demo full CRUD with Postgres, SQLModel, and FastAPI dependency injection."
    }


@app.post("/students", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, session: SessionDep) -> Student:
    db_student = Student.model_validate(student)
    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


@app.get("/students", response_model=list[StudentRead])
async def list_students(
    session: SessionDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
) -> list[Student]:
    # offset/limit is a simple form of pagination.
    students = session.exec(select(Student).offset(offset).limit(limit)).all()
    return students


@app.get("/students/{student_id}", response_model=StudentRead)
async def get_student(student_id: int, session: SessionDep) -> Student:
    return get_student_or_404(student_id, session)


@app.patch("/students/{student_id}", response_model=StudentRead)
async def update_student(student_id: int, student_update: StudentUpdate, session: SessionDep) -> Student:
    db_student = get_student_or_404(student_id, session)
    # exclude_unset=True keeps only the fields the client actually sent.
    update_data = student_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # Update the database object field by field.
        setattr(db_student, key, value)

    session.add(db_student)
    session.commit()
    session.refresh(db_student)
    return db_student


@app.delete("/students/{student_id}")
async def delete_student(student_id: int, session: SessionDep) -> dict[str, str]:
    db_student = get_student_or_404(student_id, session)
    # delete() marks the row for deletion, and commit() makes it permanent.
    session.delete(db_student)
    session.commit()
    return {"message": f"Student {student_id} deleted"}