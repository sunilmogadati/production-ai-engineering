import os
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Read the database URL from the environment, or use the classroom default.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/classdemo",
)


# The engine manages the connection to Postgres.
engine = create_engine(DATABASE_URL, echo=True)


# This class is both the API model and the database table.
class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=50)
    age: int = Field(gt=0, lt=120)
    course: str = Field(min_length=2, max_length=100)


def get_session():
    # FastAPI injects this database session into the endpoint.
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_student_or_404(student_id: int, session: Session) -> Student:
    student = session.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return student


# Create the FastAPI application object.
app = FastAPI(title="FastAPI Demo 1: Postgres GET and POST")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Student API is ready. You can create a student and fetch students from Postgres."
    }


@app.post("/students", response_model=Student, status_code=status.HTTP_201_CREATED)
async def create_student(student: Student, session: SessionDep) -> Student:
    # Do not allow clients to send their own ID when creating a new row.
    if student.id is not None:
        raise HTTPException(status_code=400, detail="Do not send id when creating a student")

    session.add(student)
    session.commit()
    session.refresh(student)
    return student


@app.get("/students", response_model=list[Student])
async def list_students(session: SessionDep) -> list[Student]:
    students = session.exec(select(Student).order_by(Student.id)).all()
    return students


@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int, session: SessionDep) -> Student:
    return get_student_or_404(student_id, session)