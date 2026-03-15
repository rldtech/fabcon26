"""
Build enriched day-by-day non-overlapping paths for each FABCON persona.
Reads fabcon_agenda_complete.json + fabcon_site_content.json, outputs enriched_paths.json.
"""
import json, re
from collections import defaultdict

with open("fabcon_agenda_complete.json", "r", encoding="utf-8") as f:
    agenda = json.load(f)

with open("fabcon_site_content.json", "r", encoding="utf-8") as f:
    site = json.load(f)

sessions = [s for s in agenda["sessions"] if s.get("title")]

# ── helpers ──────────────────────────────────────────────────────────
DATE_LABELS = {
    "2026-03-16": "16 mars",
    "2026-03-17": "17 mars",
    "2026-03-18": "18 mars",
    "2026-03-19": "19 mars",
    "2026-03-20": "20 mars",
}

DAY_NAMES = {
    "2026-03-16": "Lundi 16 mars",
    "2026-03-17": "Mardi 17 mars",
    "2026-03-18": "Mercredi 18 mars",
    "2026-03-19": "Jeudi 19 mars",
    "2026-03-20": "Vendredi 20 mars",
}

def parse_time(t):
    """Convert '09:00 AM' -> minutes since midnight."""
    m = re.match(r"(\d+):(\d+)\s*(AM|PM)", t.strip(), re.I)
    if not m:
        return 0
    h, mn, ap = int(m.group(1)), int(m.group(2)), m.group(3).upper()
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return h * 60 + mn

def overlaps(s1, s2):
    """Check if two sessions overlap in time (same day)."""
    if s1["date"] != s2["date"]:
        return False
    start1, end1 = parse_time(s1["start_time"]), parse_time(s1["end_time"])
    start2, end2 = parse_time(s2["start_time"]), parse_time(s2["end_time"])
    return start1 < end2 and start2 < end1

def session_tracks(s):
    return [t.strip() for t in s["track"].split(",")]

def score_session(s, profile):
    """Score a session for a given profile. Higher = better fit."""
    tracks = session_tracks(s)
    focus = profile["focus"]
    sc = 0

    # Track match
    for t in tracks:
        if t in focus:
            sc += 10
        # Partial match
        for f in focus:
            if f.lower() in t.lower() or t.lower() in f.lower():
                sc += 3

    # Session type bonuses
    stype = s.get("session_type", "")
    if stype in ("KEYNOTE", "CORENOTE"):
        sc += 8  # keynotes are always valuable
    if stype == "Customer Story" and profile["id"] in ("sales-manager", "bi-analytics"):
        sc += 5
    if stype == "AMA":
        sc += 2

    # Level preference per profile
    level = s.get("level", "")
    if profile["id"] == "sales-manager":
        if "100" in level:
            sc += 4
        elif "200" in level:
            sc += 3
        elif "300" in level:
            sc += 0
    elif profile["id"] in ("data-engineer", "cloud-architect", "data-architect", "governance-security"):
        if "300" in level:
            sc += 4
        elif "400" in level:
            sc += 5
        elif "200" in level:
            sc += 2
    elif profile["id"] in ("data-science-ai", "bi-analytics"):
        if "300" in level:
            sc += 3
        elif "200" in level:
            sc += 3
        elif "400" in level:
            sc += 4

    # Keyword bonuses from description
    desc = (s.get("description", "") + " " + s.get("title", "")).lower()
    keyword_maps = {
        "data-engineer": ["pipeline", "spark", "lakehouse", "medallion", "ingestion", "etl", "delta", "parquet", "streaming", "notebook", "orchestrat"],
        "data-architect": ["architecture", "model", "warehouse", "migration", "govern", "pattern", "schema", "medallion", "onelake", "enterprise"],
        "cloud-architect": ["security", "govern", "ci/cd", "devops", "compliance", "network", "private link", "well-architected", "monitor", "deploy"],
        "bi-analytics": ["power bi", "semantic", "report", "dashboard", "copilot", "visual", "dax", "analytics", "adoption", "insight"],
        "data-science-ai": ["agent", "ml", "machine learning", "notebook", "model", "ai", "copilot", "foundry", "iq", "embedding", "rag", "predict"],
        "sales-manager": ["business", "roi", "adoption", "customer", "value", "story", "roadmap", "vision", "demo", "copilot", "insight"],
        "governance-security": ["security", "purview", "govern", "compliance", "access", "label", "catalog", "protect", "audit", "dlp", "encrypt"],
    }
    kws = keyword_maps.get(profile["id"], [])
    for kw in kws:
        if kw in desc:
            sc += 2

    return sc

# ── Build paths ──────────────────────────────────────────────────────

# The keynote on Wednesday is shared across all profiles
keynote = None
for s in sessions:
    if s.get("session_type") == "KEYNOTE" and s["date"] == "2026-03-18":
        keynote = s
        break

profiles = site["profiles"]

# Sort all sessions by date then start_time
sessions.sort(key=lambda s: (s["date"], parse_time(s["start_time"])))

# Group sessions by date
by_date = defaultdict(list)
for s in sessions:
    by_date[s["date"]].append(s)

ALL_DAYS = ["2026-03-16", "2026-03-17", "2026-03-18", "2026-03-19", "2026-03-20"]

def build_path(scored, exclude=None):
    """Build a non-overlapping schedule from scored sessions.
    `exclude` is an optional set of session titles to skip."""
    exclude = exclude or set()
    selected_by_day = defaultdict(list)

    # Mon/Tue: full-day workshops — pick the best one per day
    for day in ["2026-03-16", "2026-03-17"]:
        day_sessions = [(sc, s) for sc, s in scored if s["date"] == day and s["title"] not in exclude]
        day_sessions.sort(key=lambda x: -x[0])
        if day_sessions:
            selected_by_day[day].append(day_sessions[0][1])

    # Wed/Thu/Fri: multi-slot days — greedy non-overlapping schedule
    for day in ["2026-03-18", "2026-03-19", "2026-03-20"]:
        day_sessions = [(sc, s) for sc, s in scored if s["date"] == day and sc > 0 and s["title"] not in exclude]
        day_sessions.sort(key=lambda x: (-x[0], parse_time(x[1]["start_time"])))

        chosen = []
        # Always include keynote on Wednesday
        if day == "2026-03-18" and keynote:
            chosen.append(keynote)

        for sc, s in day_sessions:
            if s in chosen:
                continue
            conflict = False
            for c in chosen:
                if overlaps(s, c):
                    conflict = True
                    break
            if not conflict:
                chosen.append(s)

        chosen.sort(key=lambda s: parse_time(s["start_time"]))
        selected_by_day[day] = chosen

    # Build output list
    path_sessions = []
    for day in ALL_DAYS:
        for s in selected_by_day.get(day, []):
            path_sessions.append({
                "title": s["title"],
                "date": DATE_LABELS[s["date"]],
                "day": DAY_NAMES[s["date"]],
                "time": f"{s['start_time'].lstrip('0').replace(' ', '')}–{s['end_time'].lstrip('0').replace(' ', '')}",
                "track": s["track"],
                "level": s.get("level", "").split(" - ")[0] if s.get("level") else "",
                "type": s.get("session_type", "Session"),
                "url": s.get("url", ""),
                "speakers": s.get("speakers", []),
                "description": s.get("description", "")[:200] + ("..." if len(s.get("description", "")) > 200 else ""),
            })
    return path_sessions


enriched_profiles = []

for profile in profiles:
    pid = profile["id"]

    # Score all sessions for this profile
    scored = [(score_session(s, profile), s) for s in sessions]
    scored.sort(key=lambda x: -x[0])

    # Main path
    main_sessions = build_path(scored)

    # Alternate path — exclude main path sessions
    main_titles = {s["title"] for s in main_sessions}
    alt_sessions = build_path(scored, exclude=main_titles)

    enriched_profile = {
        "id": profile["id"],
        "name": profile["name"],
        "tagline": profile["tagline"],
        "focus": profile["focus"],
        "why": profile["why"],
        "recommendation": profile["recommendation"],
        "sessions": main_sessions,
        "session_count": len(main_sessions),
        "alt_sessions": alt_sessions,
        "alt_session_count": len(alt_sessions),
    }
    enriched_profiles.append(enriched_profile)

    # Summary
    print(f"\n{profile['name']} ({pid}): {len(main_sessions)} main + {len(alt_sessions)} alt sessions")
    print("  Main path:")
    for s in main_sessions:
        print(f"    {s['day']} {s['time']:>14s}  {s['type']:>12s}  {s['title'][:70]}")
    print("  Alternate path:")
    for s in alt_sessions:
        print(f"    {s['day']} {s['time']:>14s}  {s['type']:>12s}  {s['title'][:70]}")

# Write output
output = {
    "meta": site["meta"],
    "stats": site["stats"],
    "profiles": enriched_profiles,
    "source_note": site["source_note"],
}

with open("enriched_paths.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ Written enriched_paths.json with {len(enriched_profiles)} profiles")
