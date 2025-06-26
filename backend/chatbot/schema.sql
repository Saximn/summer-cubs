CREATE TABLE doctors (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  name      TEXT    NOT NULL,
  specialty TEXT    NOT NULL
);
CREATE TABLE skills (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL REFERENCES doctors(id),
  skill     TEXT    NOT NULL
);
CREATE TABLE schedule (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id    INTEGER NOT NULL REFERENCES doctors(id),
  day_of_week  TEXT    NOT NULL,
  start_hour   INTEGER NOT NULL,
  end_hour     INTEGER NOT NULL
);
