import sqlite3, random
from faker import Faker

fake = Faker()

specialties = [
    "cardiology","neurology","gastroenterology","dermatology",
    "orthopedics","pediatrics","endocrinology","urology",
    "psychiatry","oncology"
]
skills = {
    "cardiology":       ["echocardiogram","stress test","angioplasty"],
    "neurology":        ["EEG","EMG","lumbar puncture"],
    "gastroenterology": ["upper endoscopy","colonoscopy","liver biopsy"],
    "dermatology":      ["skin biopsy","mole removal","laser therapy"],
    "orthopedics":      ["joint replacement","arthroscopy","fracture fixation"],
    "pediatrics":       ["well-child exam","immunizations","developmental screening"],
    "endocrinology":    ["insulin therapy","thyroid panels","bone density scan"],
    "urology":          ["cystoscopy","urinalysis","prostate biopsy"],
    "psychiatry":       ["psychiatric eval","medication management","CBT"],
    "oncology":         ["chemotherapy","radiation planning","tumor biopsy"]
}

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

def random_hour_blocks(blocks_per_doc=3, min_hour=8, max_hour=17, block_length=2):
    """
    Returns a list of (day_of_week, start_hour, end_hour) tuples.
    - selects `blocks_per_doc` random days
    - each block is `block_length` hours long
    - hours run between min_hour and max_hour-block_length
    """
    chosen_days = random.sample(days, k=blocks_per_doc)
    slots = []
    for day in chosen_days:
        start = random.randint(min_hour, max_hour - block_length)
        end = start + block_length
        slots.append((day, start, end))
    return slots

# 1) Connect & ensure your new schema is applied
conn = sqlite3.connect("doctors.db")
c = conn.cursor()
c.executescript("""
CREATE TABLE IF NOT EXISTS doctors (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  name      TEXT    NOT NULL,
  specialty TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS skills (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL REFERENCES doctors(id),
  skill     TEXT    NOT NULL
);
CREATE TABLE IF NOT EXISTS schedule (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id    INTEGER NOT NULL REFERENCES doctors(id),
  day_of_week  TEXT    NOT NULL,
  start_hour   INTEGER NOT NULL,
  end_hour     INTEGER NOT NULL
);
""")

# 2) Insert 100 doctors + skills + new schedule
for _ in range(500):
    name = fake.name()
    spec  = random.choice(specialties)
    c.execute("INSERT INTO doctors (name,specialty) VALUES (?,?)", (name, spec))
    doc_id = c.lastrowid

    # skills
    for sk in skills[spec]:
        c.execute("INSERT INTO skills (doctor_id,skill) VALUES (?,?)", (doc_id, sk))

    # schedule blocks
    for day, start, end in random_hour_blocks():
        c.execute(
            "INSERT INTO schedule (doctor_id,day_of_week,start_hour,end_hour) VALUES (?,?,?,?)",
            (doc_id, day, start, end)
        )

conn.commit()
conn.close()
print("✔ doctors.db populated with day-of-week + hour-block schedules")
