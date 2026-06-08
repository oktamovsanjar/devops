"""DevOps Bootcamp engine — SQLite ma'lumotlar bazasi (stdlib, dependency yo'q)."""
import hashlib
import json
import os
import sqlite3

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
DEVOPS_HOME = os.environ.get("DEVOPS_HOME", os.path.dirname(ENGINE_DIR))
DB_PATH = os.path.join(ENGINE_DIR, "bootcamp.db")

# topic -> kategoriya (track) xaritasi
CATEGORY = {
    "linux": "devops", "bash": "devops", "shell": "devops", "git": "devops",
    "docker": "devops", "kubernetes": "devops", "k8s": "devops", "cicd": "devops",
    "terraform": "devops", "ansible": "devops", "aws": "devops", "networking": "devops",
    "monitoring": "devops", "nginx": "devops",
    "python": "python",
    "english": "english",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT NOT NULL,
  category TEXT NOT NULL,
  difficulty INTEGER NOT NULL DEFAULT 1,
  qtype TEXT NOT NULL DEFAULT 'quiz',
  question TEXT NOT NULL,
  options TEXT NOT NULL,
  correct INTEGER NOT NULL,
  explanation TEXT,
  source TEXT DEFAULT 'seed',
  hash TEXT UNIQUE,
  created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS srs (
  question_id INTEGER PRIMARY KEY REFERENCES questions(id) ON DELETE CASCADE,
  ease REAL DEFAULT 2.5,
  interval INTEGER DEFAULT 0,
  reps INTEGER DEFAULT 0,
  lapses INTEGER DEFAULT 0,
  due TEXT,
  last_review TEXT
);
CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
  ts TEXT DEFAULT (datetime('now')),
  correct INTEGER,
  chosen INTEGER
);
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);
CREATE TABLE IF NOT EXISTS day_progress (
  day INTEGER PRIMARY KEY,
  status TEXT DEFAULT 'pending',   -- pending | active | done
  started_at TEXT,
  completed_at TEXT,
  deadline TEXT,
  xp INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS task_progress (
  day INTEGER,
  task_id TEXT,
  done_at TEXT DEFAULT (datetime('now')),
  PRIMARY KEY (day, task_id)
);
CREATE TABLE IF NOT EXISTS quiz_plan (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  pos INTEGER,
  question_id INTEGER,
  consumed INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS sent_polls (
  poll_id TEXT PRIMARY KEY,
  question_id INTEGER,
  correct_pos INTEGER,
  ts TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS exam_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam TEXT,
  ts TEXT DEFAULT (datetime('now')),
  score INTEGER,
  max INTEGER,
  passed INTEGER
);
CREATE TABLE IF NOT EXISTS checkpoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic TEXT,
  ts TEXT DEFAULT (datetime('now')),
  score INTEGER,
  total INTEGER,
  pct INTEGER,
  passed INTEGER
);
CREATE INDEX IF NOT EXISTS idx_plan_date ON quiz_plan(date, consumed);
CREATE INDEX IF NOT EXISTS idx_q_topic ON questions(topic);
CREATE INDEX IF NOT EXISTS idx_srs_due ON srs(due);
"""


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def init():
    con = connect()
    con.executescript(SCHEMA)
    cols = [r[1] for r in con.execute("PRAGMA table_info(questions)")]
    if "day" not in cols:                          # migratsiya: savol qaysi KUN darsiga tegishli
        con.execute("ALTER TABLE questions ADD COLUMN day INTEGER")
    con.commit()
    con.close()


def q_hash(question):
    return hashlib.sha256(question.strip().lower().encode()).hexdigest()[:16]


def add_question(con, topic, question, options, correct, explanation="",
                 difficulty=1, source="seed", category=None, day=None):
    """Bitta savol qo'shadi. Dublikat bo'lsa (hash) o'tkazib yuboradi. id yoki None qaytaradi."""
    category = category or CATEGORY.get(topic, "devops")
    h = q_hash(question)
    try:
        cur = con.execute(
            "INSERT INTO questions(topic,category,difficulty,qtype,question,options,correct,explanation,source,hash,day)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (topic, category, int(difficulty), "quiz", question,
             json.dumps(options, ensure_ascii=False), int(correct),
             explanation, source, h, day),
        )
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None  # dublikat


def import_seed_dir(con, path):
    """Papkadagi har bir <topic>.json (flat array) ni import qiladi."""
    added = skipped = 0
    if not os.path.isdir(path):
        return 0, 0
    for fn in sorted(os.listdir(path)):
        if not fn.endswith(".json"):
            continue
        topic = fn[:-5]
        with open(os.path.join(path, fn), encoding="utf-8") as f:
            try:
                items = json.load(f)
            except json.JSONDecodeError:
                continue
        for it in items:
            rid = add_question(
                con, topic, it["q"], it["options"], it["correct"],
                it.get("explanation", ""), it.get("difficulty", 1), source="seed",
            )
            if rid:
                added += 1
            else:
                skipped += 1
    con.commit()
    return added, skipped


def counts(con):
    rows = con.execute(
        "SELECT category, COUNT(*) n FROM questions GROUP BY category"
    ).fetchall()
    total = con.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    return total, {r["category"]: r["n"] for r in rows}


# ---- holat (state) / kun progressi ----

def get_meta(con, key, default=None):
    r = con.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default


def set_meta(con, key, value):
    con.execute(
        "INSERT INTO meta(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, str(value)),
    )
    con.commit()


def ensure_state(con):
    """Birinchi marta: start_date va current_day ni o'rnatadi."""
    import datetime
    if get_meta(con, "start_date") is None:
        set_meta(con, "start_date", datetime.date.today().isoformat())
    if get_meta(con, "current_day") is None:
        set_meta(con, "current_day", "1")


def get_day(con, day):
    return con.execute("SELECT * FROM day_progress WHERE day=?", (day,)).fetchone()


def upsert_day(con, day, **fields):
    if get_day(con, day) is None:
        con.execute("INSERT INTO day_progress(day) VALUES(?)", (day,))
    if fields:
        cols = ", ".join(f"{k}=?" for k in fields)
        con.execute(f"UPDATE day_progress SET {cols} WHERE day=?",
                    (*fields.values(), day))
    con.commit()
    return get_day(con, day)


def done_task_ids(con, day):
    return {r["task_id"] for r in
            con.execute("SELECT task_id FROM task_progress WHERE day=?", (day,))}


def mark_task(con, day, task_id):
    con.execute(
        "INSERT OR IGNORE INTO task_progress(day, task_id) VALUES(?,?)",
        (day, task_id),
    )
    con.commit()
