#!/usr/bin/env python3
"""
devops sim — buzilgan tizimni TUZATISH mashqi (troubleshooting/diagnostika).

Har bir stsenariy (sims/<id>/sim.json) real buzuq muhit yaratadi (setup) —
o'quvchi alomatni ko'radi, log o'qiydi, sababni topadi va ROSTAN tuzatadi.
`check` (shell, exit 0 = tuzalgan) yechimni tasdiqlaydi. Hint — XP evaziga.

Mavzu-qamrov kunliklar bilan bir xil qoida: faqat O'RGANILGAN mavzular
(profile.learned_topics) va min_day <= joriy kun bo'lgan simlar ochiq.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import db  # noqa: E402
import profile  # noqa: E402

SIMS_DIR = os.path.join(db.DEVOPS_HOME, "sims")
LAB_ROOT = os.path.join(SIMS_DIR, ".lab")
HINT_COST = 5          # har hint -5 XP
MIN_XP = 10


def _script(sim, key):
    """setup/check/cleanup — satr yoki satrlar ro'yxati bo'lishi mumkin."""
    v = sim.get(key)
    if isinstance(v, list):
        return "\n".join(v)
    return v or ""


def load_all():
    sims = []
    if not os.path.isdir(SIMS_DIR):
        return sims
    for name in sorted(os.listdir(SIMS_DIR)):
        f = os.path.join(SIMS_DIR, name, "sim.json")
        if os.path.isfile(f):
            try:
                s = json.load(open(f, encoding="utf-8"))
                s["id"] = s.get("id", name)
                sims.append(s)
            except Exception:
                continue
    sims.sort(key=lambda s: (s.get("min_day", 1), s.get("difficulty", 1), s["id"]))
    return sims


def get(sim_id):
    return next((s for s in load_all() if s["id"] == sim_id), None)


def lab_dir(sim_id):
    return os.path.join(LAB_ROOT, sim_id)


def run_shell(sim, key, timeout=60):
    """Stsenariy skriptini lab papkada ($SIM) bajaradi. returncode qaytaradi."""
    script = _script(sim, key)
    if not script:
        return 0
    lab = lab_dir(sim["id"])
    os.makedirs(lab, exist_ok=True)
    env = {**os.environ, "SIM": lab}
    try:
        return subprocess.run(["bash", "-c", script], env=env,
                              capture_output=True, timeout=timeout).returncode
    except Exception:
        return 1


def states(con):
    return {r["sim_id"]: r for r in con.execute("SELECT * FROM sim_progress")}


def available(con):
    """O'rganilgan mavzu + kun yetgan simlar."""
    day = int(db.get_meta(con, "current_day", "1"))
    learned = set(profile.learned_topics(con))
    return [s for s in load_all()
            if s.get("min_day", 1) <= day and s.get("topic") in learned]


def pick_next(con):
    """Tavsiya: avval yangi (oson->qiyin), keyin taşlab ketilganlar (retry)."""
    st = states(con)
    av = available(con)
    new = [s for s in av if s["id"] not in st]
    if new:
        return new[0]
    retry = [s for s in av if st[s["id"]]["status"] == "given_up"]
    return retry[0] if retry else None


def active(con):
    sid = db.get_meta(con, "sim_active", "")
    if not sid:
        return None
    s = get(sid)
    if not s:
        db.set_meta(con, "sim_active", "")
    return s


def start(con, sim):
    """Lab'ni tozalab, buzuq muhitni quradi. True = tayyor."""
    run_shell(sim, "cleanup", timeout=120)              # eski izlarni tozala
    lab = lab_dir(sim["id"])
    subprocess.run(["rm", "-rf", lab], capture_output=True)
    os.makedirs(lab, exist_ok=True)
    rc = run_shell(sim, "setup", timeout=300)
    if rc != 0:
        return False
    db.set_meta(con, "sim_active", sim["id"])
    con.execute("INSERT INTO sim_progress(sim_id,status,hints_used) VALUES(?, 'active', 0) "
                "ON CONFLICT(sim_id) DO UPDATE SET status='active', hints_used=0",
                (sim["id"],))
    con.commit()
    return True


def run_check(sim):
    return run_shell(sim, "check", timeout=90) == 0


def solve(con, sim):
    """Yechildi: XP hisobla, yoz, muhitni tozala. earned XP qaytaradi."""
    r = con.execute("SELECT hints_used FROM sim_progress WHERE sim_id=?",
                    (sim["id"],)).fetchone()
    hints = r["hints_used"] if r else 0
    earned = max(MIN_XP, int(sim.get("xp", 25)) - HINT_COST * hints)
    con.execute("UPDATE sim_progress SET status='solved', xp=?, "
                "solved_at=datetime('now') WHERE sim_id=?", (earned, sim["id"]))
    con.commit()
    db.set_meta(con, "sim_active", "")
    run_shell(sim, "cleanup", timeout=120)
    return earned


def use_hint(con, sim):
    """Navbatdagi hintni qaytaradi (None = hint qolmadi)."""
    r = con.execute("SELECT hints_used FROM sim_progress WHERE sim_id=?",
                    (sim["id"],)).fetchone()
    used = r["hints_used"] if r else 0
    hints = sim.get("hints", [])
    if used >= len(hints):
        return None, used
    con.execute("UPDATE sim_progress SET hints_used=? WHERE sim_id=?",
                (used + 1, sim["id"]))
    con.commit()
    return hints[used], used + 1


def giveup(con, sim):
    con.execute("UPDATE sim_progress SET status='given_up' WHERE sim_id=?", (sim["id"],))
    con.commit()
    db.set_meta(con, "sim_active", "")
    run_shell(sim, "cleanup", timeout=120)


def new_count(con):
    """Dashboard uchun: nechta yangi sim kutyapti."""
    st = states(con)
    return sum(1 for s in available(con) if s["id"] not in st)


def totals(con):
    r = con.execute("SELECT COUNT(*) n, COALESCE(SUM(xp),0) xp FROM sim_progress "
                    "WHERE status='solved'").fetchone()
    return r["n"], r["xp"]
