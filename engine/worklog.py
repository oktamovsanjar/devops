"""Activity log'dan bugungi ish vaqtini hisoblaydi (log time tracking)."""
import os
from datetime import datetime

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
DEVOPS_HOME = os.environ.get("DEVOPS_HOME", os.path.dirname(ENGINE_DIR))
LOG_DIR = os.path.join(DEVOPS_HOME, "logs", "activity")
IDLE_GAP_MIN = 10   # 10 daqiqadan katta tanaffus "ish" sanalmaydi


def _parse(date):
    path = os.path.join(LOG_DIR, f"commands-{date}.log")
    times = []
    if not os.path.exists(path):
        return times
    with open(path) as f:
        for line in f:
            parts = line.split("|", 3)
            if len(parts) != 4:
                continue
            try:
                times.append(datetime.strptime(parts[0].strip(), "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue
    return times


def _active_minutes(times):
    total = 0.0
    for a, b in zip(times, times[1:]):
        gap = (b - a).total_seconds() / 60.0
        if gap <= IDLE_GAP_MIN:
            total += gap
    return total


def today_activity(date=None):
    date = date or datetime.now().strftime("%Y-%m-%d")
    times = _parse(date)
    if not times:
        return {"minutes": 0, "commands": 0, "first": None, "last": None}
    return {
        "minutes": int(_active_minutes(times)),
        "commands": len(times),
        "first": times[0].strftime("%H:%M"),
        "last": times[-1].strftime("%H:%M"),
    }
