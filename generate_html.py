"""
Regenerate docs/index.html with enriched day-by-day paths from enriched_paths.json.
Keeps exact same design, adds day-group headers and all sessions.
"""
import json, html as html_mod

with open("enriched_paths.json", "r", encoding="utf-8") as f:
    data = json.load(f)

profiles = data["profiles"]
total_sessions = sum(p["session_count"] for p in profiles)

# SVG constants
CAL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>'
FOLDER_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>'
LINK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>'

# Profile icons (same as original)
PROFILE_ICONS = {
    "data-engineer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>',
    "data-architect": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
    "cloud-architect": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>',
    "bi-analytics": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "data-science-ai": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83"/></svg>',
    "sales-manager": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    "governance-security": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
}

DAYS_ORDER = ["Lundi 16 mars", "Mardi 17 mars", "Mercredi 18 mars", "Jeudi 19 mars", "Vendredi 20 mars"]

def esc(text):
    return html_mod.escape(text) if text else ""

def build_session_card(s):
    return f'''      <article class="session-card">
        <div class="session-card__meta">
          <span class="session-card__badge session-card__badge--level">{esc(s["level"])}</span>
          <span class="session-card__badge session-card__badge--type">{esc(s["type"])}</span>
          <span class="session-card__date">{CAL_SVG}{esc(s["date"])} · {esc(s["time"])}</span>
        </div>
        <h3 class="session-card__title">{esc(s["title"])}</h3>
        <div class="session-card__track">{FOLDER_SVG}{esc(s["track"])}</div>
        <a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer" class="session-card__link">Voir sur l&#x27;agenda {LINK_SVG}</a>
      </article>'''

def build_profile_section(p):
    pid = p["id"]
    icon = PROFILE_ICONS.get(pid, "")
    focus_tags = "\n        ".join(f'<span class="focus-tag">{esc(f)}</span>' for f in p["focus"])

    # Group sessions by day
    by_day = {}
    for s in p["sessions"]:
        day = s["day"]
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(s)

    sessions_html = ""
    for day in DAYS_ORDER:
        if day not in by_day:
            continue
        sessions_html += f'\n      <div class="day-group">\n        <h3 class="day-group__title">{esc(day)}</h3>\n      </div>\n'
        for s in by_day[day]:
            sessions_html += build_session_card(s) + "\n"

    return f'''<section class="profile-section section" id="{pid}" data-profile="{pid}">
  <div class="container">
    <div class="profile__header">
      <div class="profile__title-row">
        <div class="profile__icon">{icon}</div>
        <div>
          <h2 class="profile__name">{esc(p["name"])}</h2>
          <p class="profile__tagline">{esc(p["tagline"])}</p>
        </div>
      </div>
      <div class="profile__info">
        <div class="profile__info-card">
          <h4>Pourquoi ce parcours</h4>
          <p>{esc(p["why"])}</p>
        </div>
        <div class="profile__info-card">
          <h4>Recommandation</h4>
          <p>{esc(p["recommendation"])}</p>
        </div>
      </div>
      <div class="profile__focus-tags">
        {focus_tags}
      </div>
    </div>
    <div class="sessions-grid">
{sessions_html}    </div>
  </div>
</section>'''

# Build overview cards
def build_overview_card(p):
    pid = p["id"]
    icon = PROFILE_ICONS.get(pid, "")
    return f'''      <a href="#{pid}" class="profile-card" data-goto="{pid}">
        <div class="profile-card__icon">{icon}</div>
        <div class="profile-card__name">{esc(p["name"])}</div>
        <div class="profile-card__tagline">{esc(p["tagline"])}</div>
        <div class="profile-card__count">{p["session_count"]} sessions &rarr;</div>
      </a>'''

overview_cards = "\n".join(build_overview_card(p) for p in profiles)
profile_sections = "\n\n".join(build_profile_section(p) for p in profiles)

# Build full HTML
full_html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Parcours FABCON 2026 par profil — Guide interne</title>
<meta name="description" content="Guide interne : parcours de sessions recommandées pour FABCON 2026 à Atlanta, classés par profil métier.">
<link href="https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@400,500,700,800&f[]=satoshi@300,400,500,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="./styles.css">
</head>
<body>

<!-- ========== HEADER ========== -->
<header class="header" role="banner">
  <div class="container header__inner">
    <a href="#" class="header__logo" aria-label="Accueil">
      <svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <rect x="2" y="2" width="14" height="14" rx="2" fill="currentColor" opacity="0.9"/>
        <rect x="20" y="2" width="14" height="14" rx="2" fill="currentColor" opacity="0.55"/>
        <rect x="2" y="20" width="14" height="14" rx="2" fill="currentColor" opacity="0.55"/>
        <rect x="20" y="20" width="14" height="14" rx="2" fill="var(--color-primary)" opacity="0.85"/>
        <path d="M9 9L27 27" stroke="var(--color-primary)" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M27 9L9 27" stroke="var(--color-primary)" stroke-width="2.5" stroke-linecap="round" opacity="0.4"/>
      </svg>
      <div class="header__logo-text">
        FABCON 2026
        <span>Guide des parcours</span>
      </div>
    </a>
    <nav class="header__nav">
      <div class="header__links">
        <a href="#profiles-overview">Profils</a>
        <a href="#parcours">Parcours</a>
        <a href="#methodologie">Méthodologie</a>
        <a href="https://fabriccon.com/program/agenda" target="_blank" rel="noopener noreferrer">Agenda officiel &#x2197;</a>
      </div>
      <button class="theme-toggle" data-theme-toggle aria-label="Changer le thème">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
      </button>
    </nav>
  </div>
</header>

<!-- ========== HERO ========== -->
<section class="hero" id="hero">
  <div class="container hero__content">
    <div class="hero__badge">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
      16–20 mars 2026 · Atlanta
    </div>
    <h1 class="hero__title">Parcours FABCON 2026 par profil</h1>
    <p class="hero__subtitle">Guide interne pour choisir ses sessions selon son métier. Parcours complets jour par jour, sans chevauchement, à partir de l&#x27;agenda officiel.</p>
    <div class="hero__meta">
      <div class="hero__meta-item">
        {CAL_SVG}
        5 jours
      </div>
      <div class="hero__meta-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        7 profils métier
      </div>
      <div class="hero__meta-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        {total_sessions} sessions sélectionnées
      </div>
    </div>
  </div>
</section>

<!-- ========== STATS ========== -->
<section class="stats section" id="stats">
  <div class="container">
    <div class="stats__grid">
      <div class="stat-card">
        <div class="stat-card__number">275</div>
        <div class="stat-card__label">Sessions au total</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__number">24</div>
        <div class="stat-card__label">Tracks</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__number">4</div>
        <div class="stat-card__label">Niveaux</div>
      </div>
      <div class="stat-card">
        <div class="stat-card__number">5</div>
        <div class="stat-card__label">Jours de conférence</div>
      </div>
    </div>
  </div>
</section>

<!-- ========== PROFILES OVERVIEW ========== -->
<section class="profiles-overview section" id="profiles-overview">
  <div class="container">
    <div class="section-header" style="text-align:center; margin-bottom: var(--space-10);">
      <div class="section-header__label">7 parcours recommandés</div>
      <h2 class="section-header__title">Trouvez votre profil</h2>
      <p class="section-header__desc" style="margin-inline:auto;">Cliquez sur un profil pour voir le planning jour par jour, sans chevauchement de sessions.</p>
    </div>
    <div class="profiles-overview__grid">
{overview_cards}
    </div>
  </div>
</section>

<!-- ========== PROFILE FILTER NAV ========== -->
<nav class="profile-nav" id="parcours" aria-label="Filtrer par profil">
  <div class="container profile-nav__inner">
    <button class="chip chip--active" data-profile="all">Tous les profils</button>
    <button class="chip" data-profile="data-engineer">Data Engineer</button>
    <button class="chip" data-profile="data-architect">Data Architect</button>
    <button class="chip" data-profile="cloud-architect">Cloud Architect</button>
    <button class="chip" data-profile="bi-analytics">BI / Analytics</button>
    <button class="chip" data-profile="data-science-ai">Data Science / AI</button>
    <button class="chip" data-profile="sales-manager">Sales / Manager</button>
    <button class="chip" data-profile="governance-security">Governance / Security</button>
  </div>
</nav>

<!-- ========== PROFILE SECTIONS ========== -->
{profile_sections}

<!-- ========== METHODOLOGY ========== -->
<section class="methodology section" id="methodologie">
  <div class="container">
    <div class="section-header">
      <div class="section-header__label">À propos</div>
      <h2 class="section-header__title">Méthodologie &amp; sources</h2>
    </div>
    <div class="methodology__content">
      <p>Les parcours ci-dessus sont construits automatiquement à partir de l&#x27;agenda officiel FABCON 2026 (275 sessions). Chaque profil propose un planning complet jour par jour, du lundi au vendredi, sans chevauchement entre les sessions.</p>
      <p>Les sessions sont sélectionnées par un scoring basé sur la correspondance des tracks, le niveau de la session, le type (keynote, workshop, corenote), et les mots-clés présents dans la description.</p>
      <p>Les niveaux vont de 100 (Business Level) à 400 (Deep Technical). Ce guide est fourni à titre indicatif. Consultez l&#x27;agenda officiel pour les horaires à jour.</p>
      <div class="methodology__links">
        <a href="https://fabriccon.com/program/agenda" target="_blank" rel="noopener noreferrer" class="methodology__link">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
          Agenda officiel
        </a>
        <a href="https://fabriccon.com/" target="_blank" rel="noopener noreferrer" class="methodology__link methodology__link--secondary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
          Site FABCON
        </a>
      </div>
    </div>
  </div>
</section>

<!-- ========== FOOTER ========== -->
<footer class="footer" role="contentinfo">
  <div class="container footer__inner">
    <div class="footer__text">Guide interne — Parcours FABCON 2026 par profil</div>
    <div class="footer__links">
      <a href="https://fabriccon.com/program/agenda" target="_blank" rel="noopener noreferrer">Agenda officiel</a>
      <a href="https://fabriccon.com/" target="_blank" rel="noopener noreferrer">fabriccon.com</a>
    </div>
  </div>
</footer>

<!-- Back to top -->
<button class="back-to-top" aria-label="Retour en haut">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 15l-6-6-6 6"/></svg>
</button>

<script src="./script.js"></script>
</body>
</html>'''

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"✅ Regenerated docs/index.html with {total_sessions} sessions across {len(profiles)} profiles")
