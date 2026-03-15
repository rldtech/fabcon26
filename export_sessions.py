"""
Export all sessions as a JS data file for the search/filter feature.
"""
import json

with open("fabcon_agenda_complete.json", "r", encoding="utf-8") as f:
    data = json.load(f)

sessions = []
for s in data["sessions"]:
    if not s.get("title"):
        continue
    # Build tags from track + level + type
    tracks = [t.strip() for t in s["track"].split(",")]
    tags = list(set(tracks))

    sessions.append({
        "t": s["title"],
        "d": s["date"],
        "s": s["start_time"],
        "e": s["end_time"],
        "tr": s["track"],
        "ty": s.get("session_type", "Session"),
        "l": s.get("level", "").split(" - ")[0].strip() if s.get("level") else "",
        "sp": s.get("speakers", []),
        "desc": s.get("description", ""),
        "u": s.get("url", ""),
        "tags": tags,
    })

js_content = "/* Auto-generated session data for search */\nwindow.FABCON_SESSIONS = " + json.dumps(sessions, ensure_ascii=False, indent=None) + ";\n"

with open("docs/sessions.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"✅ Exported {len(sessions)} sessions to docs/sessions.js ({len(js_content)//1024}KB)")
