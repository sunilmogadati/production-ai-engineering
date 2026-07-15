# API design self-study pack: assignment tickets

Self-paced assignment tickets covering API design progression (formerly the
live Session 3 — restructured 2026-07-06 when the calendar jumped to AI/ML).
Follows the ticket template in `COHORT_COLLABORATION_MODEL.md` (section 4) and the
Session 3+ pack (section 5). Assign one ticket per student; each is a small PR.
Review the merged PRs in a 15-minute block of any later session.

Focus: model separation, broader API surface, pagination/filtering, CRUD.
Reference files: `main2.py`, `main3.py`, `main4.py`.

Instructor note: keep earlier demos runnable. New work should be additive and
should not change the behavior of `main1.py`.

---

## Ticket 3.1: Add a PATCH endpoint

- **Objective:** Allow partial update of a student.
- **File(s) to edit:** `main3.py`
- **Acceptance criteria:**
  - `PATCH /students/{id}` updates only the fields present in the request body.
  - Missing student returns `404`.
  - Existing GET/POST behavior is unchanged.
- **API request example:**
  ```bash
  curl -X PATCH http://127.0.0.1:8000/students/1 \
    -H "Content-Type: application/json" \
    -d '{"course":"Advanced Databases"}'
  ```
- **Expected output:** `200` with the updated student; only `course` changed.
- **Reviewer checklist:**
  - [ ] Partial update leaves untouched fields intact.
  - [ ] `404` path verified.
  - [ ] No change to unrelated endpoints.

---

## Ticket 3.2: Add a DELETE endpoint

- **Objective:** Remove a student by id.
- **File(s) to edit:** `main3.py`
- **Acceptance criteria:**
  - `DELETE /students/{id}` deletes the row and returns a clear result.
  - Missing student returns `404`.
- **API request example:**
  ```bash
  curl -X DELETE http://127.0.0.1:8000/students/1
  ```
- **Expected output:** `200` (or `204`) on success; a following GET of the same id returns `404`.
- **Reviewer checklist:**
  - [ ] Row is actually removed from Postgres.
  - [ ] `404` path verified.
  - [ ] Status code is consistent and documented.

---

## Ticket 3.3: Add pagination and a name filter

- **Objective:** Support `limit`, `offset`, and `name` query parameters on the list endpoint.
- **File(s) to edit:** `main4.py`
- **Acceptance criteria:**
  - `GET /students?limit=&offset=` returns a bounded page of results.
  - `GET /students?name=` filters by name (case-insensitive is a plus).
  - Sensible defaults when no query parameters are given.
- **API request example:**
  ```bash
  curl "http://127.0.0.1:8000/students?limit=2&offset=0"
  curl "http://127.0.0.1:8000/students?name=Rahul"
  ```
- **Expected output:** A filtered/paginated list matching the query.
- **Reviewer checklist:**
  - [ ] Defaults are reasonable and bounded.
  - [ ] Filter and pagination compose correctly.
  - [ ] Invalid `limit`/`offset` values are rejected or clamped.

---

## Ticket 3.4: Separate create and read models

- **Objective:** Demonstrate why request and response models can differ.
- **File(s) to edit:** `main2.py`
- **Acceptance criteria:**
  - A `StudentCreate` input model (no client-supplied `id`).
  - A `StudentRead` response model (includes `id`).
  - `POST` accepts `StudentCreate`; responses use `StudentRead`.
- **API request example:**
  ```bash
  curl -X POST http://127.0.0.1:8000/students \
    -H "Content-Type: application/json" \
    -d '{"name":"Meera","age":22,"course":"APIs"}'
  ```
- **Expected output:** `201` with a `StudentRead` payload including the generated `id`.
- **Reviewer checklist:**
  - [ ] Client cannot set `id` on create.
  - [ ] Response schema is the read model.
  - [ ] Docs (`/docs`) show the two distinct schemas.

---

## Ticket 3.5: Docs update

- **Objective:** Keep learner docs in sync with the new endpoints.
- **File(s) to edit:** `README.md` (and this file if scope changes)
- **Acceptance criteria:**
  - One sample request/response added for each new endpoint above that ships.
  - Commands use the project venv form.
- **Expected output:** README shows working, copy-pasteable examples.
- **Reviewer checklist:**
  - [ ] Examples were actually run.
  - [ ] No broken doc links (`python3 scripts/validate_repo.py`).
