CREATE TABLE IF NOT EXISTS student (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    age INTEGER NOT NULL CHECK (age > 0 AND age < 120),
    course VARCHAR(100) NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_student_name ON student (name);