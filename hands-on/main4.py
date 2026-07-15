import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Final demo uses the same Postgres connection pattern as earlier files.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/classdemo",
)

engine = create_engine(DATABASE_URL, echo=True)


# SQLModel can act like both a Pydantic model and a database model.
class StudentBase(SQLModel):
    name: str = Field(index=True, min_length=2, max_length=50)
    course: str = Field(min_length=2, max_length=100)
    age: int = Field(gt=0, lt=120)


class Student(StudentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: int


def get_session():
    # FastAPI injects this session into any endpoint that asks for SessionDep.
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_student_or_404(student_id: int, session: Session) -> Student:
    student = session.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} does not exist")
    return student


app = FastAPI(title="FastAPI Demo 4: Simple Postgres GET and POST")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Student API is connected to Postgres and supports creating and viewing students."
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
    limit: int = Query(default=5, ge=1, le=50),
    name: str | None = Query(default=None, min_length=1),
) -> list[Student]:
    # Start with a query for all students.
    statement = select(Student)

    if name:
        # Apply a filter only when the client provides a name query parameter.
        statement = statement.where(Student.name.ilike(f"%{name}%"))

    items = session.exec(statement.offset(offset).limit(limit)).all()
    return items


@app.get("/students/{student_id}", response_model=StudentRead)
async def get_student(student_id: int, session: SessionDep) -> Student:
    return get_student_or_404(student_id, session)