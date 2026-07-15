import os
from typing import Annotated

from fastapi import Depends, FastAPI, status
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Read the database URL from the environment, or use the classroom default.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/classdemo",
)

# The engine knows how to talk to Postgres.
engine = create_engine(DATABASE_URL, echo=True)


# Shared fields used by multiple models.
class StudentBase(SQLModel):
    name: str = Field(index=True)
    course: str
    age: int = Field(gt=0, lt=120)


# table=True tells SQLModel to create a real database table for this model.
class Student(StudentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


# Used for incoming create requests.
class StudentCreate(StudentBase):
    pass


# Used for outgoing responses.
class StudentRead(StudentBase):
    id: int


def get_session():
    # This dependency gives each request its own database session.
    with Session(engine) as session:
        yield session


# A reusable type alias so endpoint signatures stay short and readable.
SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI(title="FastAPI Demo 2: SQLModel Create and Read")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Run Docker Postgres, then use POST /students and GET /students to demo SQLModel with session dependency injection."
    }


@app.post("/students", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
async def create_student(student: StudentCreate, session: SessionDep) -> Student:
    # Convert the request model into a database model.
    db_student = Student.model_validate(student)
    session.add(db_student)
    session.commit()
    # refresh() loads generated values such as the new ID from the database.
    session.refresh(db_student)
    return db_student


@app.get("/students", response_model=list[StudentRead])
async def list_students(session: SessionDep) -> list[Student]:
    # select(Student) means: fetch rows from the Student table.
    students = session.exec(select(Student).order_by(Student.id)).all()
    return students