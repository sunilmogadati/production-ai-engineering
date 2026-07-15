# FastAPI with Postgres

This project shows a simple FastAPI app step by step.

For AI/tool/agent handoff and continuity, start with `DOCUMENTATION_INDEX.md`, `AGENT_CONTEXT.json`, and `AGENT_HANDOFF.md`.

For the full progression plan (hello-world-first across FastAPI, SQLModel, ML/AI, and frontend), see `LEARNING_STRATEGY.md`.

For the reusable cohort-level teaching roadmap (what we completed, progressive modules, theory topics, and next build steps), see `COHORT_TEACHING_PLAYBOOK.md`.

For the repeatable session calendar (what to run each class, expected outcomes, and checklist), see `COHORT_SESSION_PLAN.md`.

For repository publishing/versioning strategy of progressive lessons, see `GITHUB_STRATEGY.md`.

For cohort collaboration and assignment workflow (IKEA effect), see `COHORT_COLLABORATION_MODEL.md`.

For AI-personalized learner path design, see `AI_PERSONALIZED_PATH_STRATEGY.md`.

The main idea is:

- start a web API
- connect it to Postgres
- read data from a table
- add new data to the table
- show a normal API error like `404 Not Found`

## What you will learn

By the end of the class, you should understand:

- what FastAPI does
- how a URL calls a Python function
- how Python classes can describe API data
- how FastAPI reads and returns JSON
- how FastAPI connects to a database
- how to get data and post data

## Which file we will use

For the main classroom demo, use `main1.py`.

Why this file?

- it is simple
- it uses one `Student` class
- it connects to Postgres
- it has `GET` and `POST`
- it shows a normal `404` error

## Before you start

You need:

- Python
- Docker Desktop running
- this project folder

## Step 1: install Python packages

Run this command:

```bash
python3 -m pip install -r requirements.txt
```

This installs the tools used by the project:

- `fastapi`: the API framework
- `uvicorn`: the web server
- `sqlmodel`: the library used for database tables and models
- `psycopg`: the PostgreSQL driver

## Step 2: start Postgres

Run this command:

```bash
docker compose up -d
```

This starts PostgreSQL in Docker.

Database details:

- host: `localhost`
- port: `5432`
- database: `classdemo`
- username: `postgres`
- password: `postgres`

## Step 3: table used in this project

This project uses one table called `student`.

It has these columns:

- `id`
- `name`
- `age`
- `course`

The table is created by the SQL file in `sql/init/001_create_students.sql`.

The FastAPI code uses the table. It does not create the table.

## Step 4: optional manual row in Postgres

If you want data to already exist before testing `GET`, add one row manually:

```sql
INSERT INTO student (name, age, course)
VALUES ('John', 21, 'FastAPI Basics');
```

## Step 5: run the FastAPI app

Use this command:

```bash
./venv/bin/python -m uvicorn main1:app --reload
```

Use this exact command for this project.

Why?

- it uses the project virtual environment
- it avoids Python package mismatch problems

## Step 6: open the app

Open these in your browser:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

`/docs` is the built-in FastAPI test page.

## Step 7: try the API

### Get all students

```bash
curl http://127.0.0.1:8000/students
```

### Get one student

```bash
curl http://127.0.0.1:8000/students/1
```

### Add a new student

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul","age":24,"course":"Databases"}'
```

### Get a student that does not exist

```bash
curl http://127.0.0.1:8000/students/999
```

This should return a `404` error.

## What to notice in class

When you run the app:

- FastAPI listens for web requests
- `GET /students` reads rows from Postgres
- `POST /students` adds a new row to Postgres
- `GET /students/999` shows how an API returns an error

## Simple concepts

## What is FastAPI?

FastAPI is a Python tool used to build web APIs.

An API lets one system send or receive data from another system.

## What is a route?

A route connects a URL to a Python function.

Example:

```python
@app.get("/students")
async def list_students():
    return []
```

This means:

- someone calls `/students`
- FastAPI runs the function
- the function returns JSON

## What is a class in this project?

In this project, a class helps describe data.

Example:

```python
class Employee(BaseModel):
    id: int
    name: str
    department: str
```

This says what an `Employee` should look like.

## What is Pydantic?

Pydantic checks data.

It helps make sure values are in the correct format.

For example, it can check:

- is `age` a number?
- is `name` present?
- does the data match the expected structure?

## What is `BaseModel`?

`BaseModel` is used when you want to describe API data.

Use it for:

- request data
- response data
- validation

It does not create a database table.

## What is SQLModel?

SQLModel helps connect Python classes to database tables.

It is useful because one class can describe:

- Python data
- API data
- database columns

## What makes a class a database table class?

A class becomes a database table class when it looks like this:

```python
class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int
    course: str
```

Why this is a table class:

- it inherits from `SQLModel`
- it uses `table=True`
- the fields become table columns

## What is a session?

A session is the object used to talk to the database.

You use it to:

- read rows
- add rows
- update rows
- delete rows

## What is `HTTPException`?

`HTTPException` is how FastAPI returns an API error.

Example:

```python
raise HTTPException(status_code=404, detail="Student not found")
```

This tells the client:

- the request failed
- the status code is `404`
- the reason is `Student not found`

## About `StudentCreate` and `StudentRead`

Some files in this project use classes named `StudentCreate` and `StudentRead`.

Simple meaning:

- `StudentCreate` is for data sent into the API
- `StudentRead` is for data sent back from the API

Do you need them?

- for a simple beginner class: no
- for cleaner real-world design: yes, sometimes

That is why `main1.py` is the best place to start. It is simpler.

## Best class order

If you want to keep the class simple, use this order:

1. `main0.py` for the smallest FastAPI example
2. `main.py` for `HTTPException` and a simple class
3. `main1.py` for Postgres with `GET` and `POST`
4. `main3.py` only if you want to show full CRUD

## From rules to ML (Sessions 3-4)

The AI/ML demos run on a synthetic call-center dataset. No Docker needed.

One-time setup:

```bash
./venv/bin/python -m pip install -r requirements-ml.txt
```

Start with the hello worlds (~20 lines each, in-file data, follow Meera):

```bash
./venv/bin/python hello_rules.py       # a rule gets Meera wrong
./venv/bin/python hello_logistic.py    # the model gets Meera right
./venv/bin/python hello_save_load.py   # the model is a FILE (train once, use anywhere)
./venv/bin/python hello_linear.py      # the model discovers a formula
./venv/bin/python hello_tree.py        # the machine writes the elifs
```

Then the same story at dataset scale (2,000 synthetic leads):

```bash
./venv/bin/python ml01_generate_synthetic_data.py   # make the data
./venv/bin/python ai01_rules_baseline.py            # rules vs reality (~58%)
./venv/bin/python ml02_logistic_regression.py       # ML learns the pattern (~75%)
./venv/bin/python ml09_train_and_save.py            # train time: save the model
./venv/bin/python ml10_load_and_predict.py          # predict time: no retraining
./venv/bin/python ml06_linear_regression.py         # predict order value
./venv/bin/python ml03_decision_tree.py             # readable learned rules
./venv/bin/python ml04_random_forest.py             # many trees vote
./venv/bin/python ml05_xgboost.py                   # boosting benchmark
```

See `SESSION_03.md` and `SESSION_04.md` for the full classroom flow.

## Quick command list

### Install packages

```bash
python3 -m pip install -r requirements.txt
```

### Start Postgres

```bash
docker compose up -d
```

### Run the beginner database app

```bash
./venv/bin/python -m uvicorn main1:app --reload
```

### Open docs

```text
http://127.0.0.1:8000/docs
```

### Get all students

```bash
curl http://127.0.0.1:8000/students
```

### Get one student

```bash
curl http://127.0.0.1:8000/students/1
```

### Add a student

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul","age":24,"course":"Databases"}'
```

### Show a `404`

```bash
curl http://127.0.0.1:8000/students/999
```