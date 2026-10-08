# -*- coding: utf-8 -*-
"""
Dj Oxygène237 — Espace Prestations & Live
Application Streamlit personnelle : profil, galerie de prestations vidéo
(TikTok / YouTube / Facebook) et annonces de lives.

Lancer en local :  streamlit run app.py
"""

# ============================================================
# PARTIE 1/5 — Imports et configuration (à personnaliser ici)
# ============================================================
import base64
import hmac
import html
import json
import os
import re
import threading
import uuid
from datetime import date, datetime, time as dtime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

import streamlit as st
import streamlit.components.v1 as components

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Europe/Paris")
except Exception:  # fuseau indisponible : on utilise l'heure du serveur
    TZ = None

st.set_page_config(
    page_title="Dj Oxygène237 - Espace Prestations & Live",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# ⚙️ PROFIL & CONTACT
# ------------------------------------------------------------
ARTIST_NAME = "Dj Oxygène237"
SUBTITLE = "Espace Prestations & Live"
PHONE_DISPLAY = "+33 7 73 61 68 84"
PHONE_INTL = "33773616884"                       # format international, sans + ni espaces
TIKTOK_URL = "https://www.tiktok.com/@dj.oxygene237"
PHOTO_PATH = "assets/dj_oxygene237.jpg"          # facultatif : ta photo de profil
LIVE_DURATION_H = 3                              # un live est « en direct » pendant 3 h après son début

STYLES_PRESENTATION = [
    "Makossa", "Ndombolo", "Bikutsi", "Coupé-décalé",
    "Afrobeat", "Hip-hop", "Shatta", "Dancehall",
]
STYLES_MUSICAUX = STYLES_PRESENTATION + ["Mix généraliste", "Animation MC / Live", "Autre"]

PLATFORMS = ["TikTok", "YouTube", "Facebook", "Instagram", "Autre"]
PLATFORM_ICONS = {"TikTok": "🎵", "YouTube": "▶️", "Facebook": "📘", "Instagram": "📸", "Autre": "🔗"}

# ------------------------------------------------------------
# 📌 CONTENUS FIXES (toujours affichés, même si le serveur redémarre)
# Ajoute tes vidéos ou lives importants ici : ils ne seront jamais perdus.
# ------------------------------------------------------------
PRESTATIONS_FIXES = [
    # {"title": "Mix Makossa", "style": "Makossa", "description": "Extrait de soirée",
    #  "url": "https://www.tiktok.com/@dj.oxygene237/video/1234567890123456789"},
]
LIVES_FIXES = [
    # {"title": "Live Ndombolo", "platform": "TikTok", "start": "2026-11-01T20:00",
    #  "url": "https://www.tiktok.com/@dj.oxygene237/live", "description": "Rendez-vous sur TikTok !"},
]


# ============================================================
# PARTIE 2/5 — Données, liens vidéo, dates, accès gestion
# ============================================================
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "oxygene237.json"
_LOCK = threading.Lock()
esc = html.escape

PRESTATION_FIELDS = ("title", "style", "description", "url", "added")
ANNONCE_FIELDS = ("title", "platform", "start", "url", "description")

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
PLATFORM_NAMES = {"tiktok": "TikTok", "youtube": "YouTube", "facebook": "Facebook",
                  "instagram": "Instagram", "direct": "la vidéo", "autre": "le lien"}


def H(markup: str) -> None:
    """Affiche du HTML/CSS (aplatit le texte pour éviter les blocs de code Markdown)."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()),
                unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def img_uri(rel_path: str):
    """Convertit une image locale en data-URI. Renvoie None si le fichier n'existe pas."""
    path = BASE_DIR / rel_path
    if not path.exists():
        return None
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def wa_link(text: str = "") -> str:
    return f"https://wa.me/{PHONE_INTL}" + (f"?text={quote(text)}" if text else "")


# ---------- Stockage (fichier JSON) ----------
def load_data() -> dict:
    data = {"prestations": [], "annonces": []}
    try:
        if DATA_FILE.exists():
            raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            for key in data:
                if isinstance(raw.get(key), list):
                    data[key] = [x for x in raw[key] if isinstance(x, dict)]
    except (json.JSONDecodeError, OSError, AttributeError):
        pass
    return data


def save_data(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DATA_FILE)


def _mutate(fn) -> None:
    with _LOCK:
        data = load_data()
        fn(data)
        save_data(data)


def now_local() -> datetime:
    return datetime.now(TZ) if TZ else datetime.now()


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def add_prestation(title: str, style: str, description: str, url: str) -> None:
    entry = {"id": new_id(), "title": title[:80], "style": style, "description": description[:400],
             "url": url, "added": now_local().strftime("%d/%m/%Y")}
    _mutate(lambda d: d["prestations"].append(entry))


def add_annonce(title: str, platform: str, start_iso: str, url: str, description: str) -> None:
    entry = {"id": new_id(), "title": title[:80], "platform": platform, "start": start_iso,
             "url": url, "description": description[:400]}
    _mutate(lambda d: d["annonces"].append(entry))


def delete_item(kind: str, item_id: str) -> None:
    _mutate(lambda d: d.__setitem__(kind, [x for x in d[kind] if x.get("id") != item_id]))


def restore_backup(raw: dict) -> None:
    """Restaure une sauvegarde JSON (nettoie chaque entrée avant de l'enregistrer)."""
    def clean(items, fields):
        out = []
        for it in (items if isinstance(items, list) else [])[:500]:
            if not isinstance(it, dict):
                continue
            row = {k: str(it.get(k, ""))[:500] for k in fields}
            if "url" in row:
                row["url"] = clean_url(row["url"])
            row["id"] = re.sub(r"[^\w-]", "", str(it.get("id", "")))[:20] or new_id()
            out.append(row)
        return out

    new = {"prestations": clean(raw.get("prestations"), PRESTATION_FIELDS),
           "annonces": clean(raw.get("annonces"), ANNONCE_FIELDS)}
    with _LOCK:
        save_data(new)


def all_prestations(data: dict) -> list:
    fixed = [dict(p, id=f"fixe-{i}", fixed=True) for i, p in enumerate(PRESTATIONS_FIXES)]
    return list(reversed(data["prestations"])) + fixed      # les plus récentes d'abord


# ---------- Liens vidéo ----------
def clean_url(url: str) -> str:
    """Renvoie une URL http(s) valide, sinon une chaîne vide."""
    url = (url or "").strip()
    if not url or " " in url:
        return ""
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    p = urlparse(url)
    if p.scheme not in ("http", "https") or "." not in p.netloc:
        return ""
    return url


def detect_platform(url: str) -> str:
    p = urlparse(url)
    host = p.netloc.lower()
    if "tiktok.com" in host:
        return "tiktok"
    if "youtube.com" in host or "youtu.be" in host:
        return "youtube"
    if "facebook.com" in host or "fb.watch" in host or "fb.com" in host:
        return "facebook"
    if "instagram.com" in host:
        return "instagram"
    if p.path.lower().endswith((".mp4", ".webm", ".mov", ".m4v", ".ogg")):
        return "direct"
    return "autre"


def youtube_id(url: str) -> str:
    p = urlparse(url)
    if "youtu.be" in p.netloc.lower():
        vid = p.path.strip("/").split("/")[0]
    else:
        qs = parse_qs(p.query)
        if "v" in qs:
            vid = qs["v"][0]
        else:
            m = re.match(r"^/(?:shorts|embed|live|v)/([^/?#]+)", p.path)
            vid = m.group(1) if m else ""
    return vid if re.fullmatch(r"[\w-]{6,20}", vid or "") else ""


def tiktok_id(url: str) -> str:
    m = re.search(r"/video/(\d{8,25})", url)
    return m.group(1) if m else ""


# ---------- Dates ----------
def parse_start(value: str):
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if TZ and dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt


def fr_date(dt: datetime) -> str:
    return f"{JOURS[dt.weekday()].capitalize()} {dt.day} {MOIS[dt.month - 1]} {dt.year} à {dt:%H:%M}"


def countdown_text(delta: timedelta) -> str:
    secs = max(int(delta.total_seconds()), 0)
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return f"dans {days} j {hours} h"
    if hours:
        return f"dans {hours} h {minutes:02d} min"
    return f"dans {max(minutes, 1)} min"


def live_status(start: datetime, now: datetime) -> str:
    if now < start:
        return "upcoming"
    if now <= start + timedelta(hours=LIVE_DURATION_H):
        return "live"
    return "past"


# ---------- Accès gestion (réservé à Dj Oxygène237) ----------
def get_admin_password() -> str:
    try:
        pwd = st.secrets.get("ADMIN_PASSWORD", "")
    except Exception:
        pwd = ""
    return str(pwd or os.environ.get("ADMIN_PASSWORD", ""))


def is_admin() -> bool:
    return bool(st.session_state.get("is_admin"))


def flash(message: str) -> None:
    st.session_state["flash"] = message


# ============================================================
# PARTIE 3/5 — Style (CSS) et en-tête / profil
# ============================================================
def inject_css() -> None:
    H("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@300;400;600&display=swap');
    :root{--orange:#ff7a2e;--red:#ff3d68;--cyan:#27ecff;--card:#3d3092;--card2:#4b3fa8;--muted:#d9d4fb;}
    .stApp{background:
        radial-gradient(circle at 10% 0%,rgba(255,122,46,.55),transparent 45%),
        radial-gradient(circle at 95% 10%,rgba(39,236,255,.40),transparent 45%),
        linear-gradient(165deg,#2b1d70 0%,#4b1f7a 55%,#1f3a8f 100%);
        background-attachment:fixed;color:#fff;font-family:'Poppins',sans-serif;}
    header[data-testid="stHeader"]{background:transparent;}
    #MainMenu,footer{visibility:hidden;}
    .block-container{padding:1rem 1rem 4rem;max-width:760px;}
    h1,h2,h3,label,.stMarkdown p,.stMarkdown li{color:#fff;}
    a{text-decoration:none;}

    /* ---- En-tête ---- */
    .hero{border-radius:22px;padding:1.6rem 1rem;text-align:center;margin:.4rem 0 1rem;
        background:linear-gradient(120deg,#ff6a1a,#e0245e,#7b2cff,#1f78ff);background-size:300% 300%;
        animation:flow 10s ease infinite;border:1px solid rgba(255,255,255,.35);
        box-shadow:0 10px 40px rgba(255,100,60,.35);}
    @keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
    .avatar{width:104px;height:104px;border-radius:50%;object-fit:cover;border:3px solid #ffc83c;
        box-shadow:0 0 22px rgba(255,200,60,.8);margin-bottom:.6rem;}
    .avatar-ph{display:inline-flex;align-items:center;justify-content:center;font-size:2.6rem;
        background:linear-gradient(135deg,var(--orange),var(--red));}
    .hero-badge{display:inline-block;font-size:.68rem;letter-spacing:.18em;border:1px solid rgba(255,255,255,.85);
        background:rgba(0,0,0,.18);border-radius:999px;padding:.25rem .8rem;margin-bottom:.6rem;}
    .hero-title{font-family:'Orbitron',sans-serif;font-weight:800;font-size:1.7rem;line-height:1.2;
        text-shadow:0 3px 14px rgba(0,0,0,.35);margin:.2rem 0;}
    .hero-title span{display:block;font-size:1.05rem;color:var(--cyan);font-weight:600;margin-top:.3rem;}
    .contact{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin:.6rem 0 .8rem;}
    .contact a{display:flex;align-items:center;justify-content:center;gap:.3rem;padding:.75rem .3rem;border-radius:14px;
        color:#fff!important;font-weight:600;font-size:.85rem;border:1px solid rgba(255,255,255,.3);
        background:rgba(255,255,255,.16);transition:transform .2s,box-shadow .2s;}
    .contact a:hover{transform:translateY(-3px);box-shadow:0 0 18px rgba(255,255,255,.5);}
    .contact a.wa{background:rgba(37,211,102,.4);border-color:rgba(37,211,102,.9);}
    .phone{font-size:.95rem;margin-top:.2rem;}

    /* ---- Cartes & titres ---- */
    .card{background:linear-gradient(160deg,var(--card),var(--card2));border:1px solid rgba(255,255,255,.22);
        border-radius:18px;padding:1.1rem;margin:.6rem 0;box-shadow:0 8px 24px rgba(15,8,60,.35);color:#f4f2ff;font-size:.92rem;}
    .card-title{font-weight:600;font-size:1.08rem;margin-bottom:.4rem;}
    .bio{color:#ece9ff;font-weight:300;font-size:.9rem;margin-top:.5rem;}
    .section-title{font-family:'Orbitron',sans-serif;font-size:1.25rem;margin:.6rem 0 .2rem;
        background:linear-gradient(90deg,#ffb066,var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .section-sub{color:var(--muted);font-size:.88rem;margin-bottom:.6rem;}
    .divider{height:2px;margin:1.1rem 0;border-radius:2px;
        background:linear-gradient(90deg,transparent,var(--orange),var(--cyan),transparent);}
    .chip{display:inline-block;margin:.15rem .25rem .15rem 0;padding:.15rem .6rem;border-radius:999px;font-size:.75rem;
        border:1px solid #ffb066;color:#ffe2c8;background:rgba(255,122,46,.22);}
    .chip-cyan{border-color:var(--cyan);color:#c8fbff;background:rgba(39,236,255,.15);}
    .ph{display:flex;align-items:center;justify-content:center;text-align:center;padding:1rem;height:120px;border-radius:16px;
        margin:.4rem 0;background:linear-gradient(135deg,#5a2a8f,#1f5aa0);border:1px dashed rgba(255,255,255,.45);}

    /* ---- Lives ---- */
    .live-card{border-radius:18px;padding:1.1rem;margin:.6rem 0;border:1px solid rgba(255,255,255,.25);
        background:linear-gradient(160deg,#3d3092,#4b3fa8);}
    .live-card.is-live{border:2px solid #ff3d68;background:linear-gradient(160deg,#7a1a4a,#b02a5c);
        box-shadow:0 0 28px rgba(255,61,104,.7);}
    .live-card.is-next{border:2px solid #ffc83c;box-shadow:0 0 22px rgba(255,200,60,.45);}
    .live-card.is-past{opacity:.7;}
    .live-date{font-size:.9rem;color:#ffe2c8;margin:.3rem 0;}
    .badge{display:inline-block;font-size:.72rem;font-weight:600;letter-spacing:.06em;border-radius:999px;
        padding:.2rem .7rem;margin-bottom:.4rem;}
    .badge-live{background:#ff3d68;animation:pulse 1.2s infinite;}
    .badge-soon{background:linear-gradient(90deg,#ffd24d,#ffa11f);color:#2b1d70;}
    .badge-past{background:rgba(255,255,255,.25);}
    @keyframes pulse{0%{box-shadow:0 0 0 0 rgba(255,61,104,.8)}70%{box-shadow:0 0 0 12px rgba(255,61,104,0)}100%{box-shadow:0 0 0 0 rgba(255,61,104,0)}}

    /* ---- Widgets Streamlit ---- */
    .stButton>button,.stFormSubmitButton>button,a[data-testid="stBaseLinkButton-secondary"],
    a[data-testid="stBaseLinkButton-primary"],.stDownloadButton>button{
        width:100%;display:flex;justify-content:center;
        background:linear-gradient(90deg,var(--orange),var(--red))!important;color:#fff!important;border:none!important;
        border-radius:12px!important;font-weight:600!important;padding:.55rem 1rem!important;transition:.2s!important;}
    .stButton>button:hover,.stFormSubmitButton>button:hover,a[data-testid="stBaseLinkButton-secondary"]:hover,
    a[data-testid="stBaseLinkButton-primary"]:hover,.stDownloadButton>button:hover{
        box-shadow:0 0 20px rgba(255,100,60,.8)!important;transform:translateY(-2px);}
    .stTextInput input,.stTextArea textarea,.stDateInput input,.stTimeInput input,
    .stSelectbox div[data-baseweb="select"]>div{
        background:rgba(255,255,255,.16)!important;color:#fff!important;border:1px solid rgba(255,255,255,.35)!important;
        border-radius:12px!important;}
    div[data-testid="stExpander"]{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:14px;}
    div[data-testid="stForm"]{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.25);border-radius:16px;}
    .stTabs [data-baseweb="tab-list"]{gap:.4rem;}
    .stTabs [data-baseweb="tab"]{color:#fff;font-weight:600;background:rgba(255,255,255,.12);border-radius:12px 12px 0 0;padding:.5rem .9rem;}
    .footer{text-align:center;color:var(--muted);font-size:.78rem;margin-top:2rem;}

    @media (max-width:640px){
        .hero-title{font-size:1.35rem;}
        .block-container{padding:.6rem .6rem 4rem;}
        .contact a{font-size:.78rem;}
    }
    </style>
    """)


def divider() -> None:
    H('<div class="divider"></div>')


def section_title(title: str, subtitle: str = "") -> None:
    H(f'<div class="section-title">{esc(title)}</div>')
    if subtitle:
        H(f'<div class="section-sub">{esc(subtitle)}</div>')


def render_header() -> None:
    """Titre, présentation, styles musicaux et boutons de contact."""
    uri = img_uri(PHOTO_PATH)
    avatar = (f'<img class="avatar" src="{uri}" alt="{esc(ARTIST_NAME)}">' if uri
              else '<div class="avatar avatar-ph">🎧</div>')
    chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in STYLES_PRESENTATION)
    msg = f"Bonjour {ARTIST_NAME}, je vous contacte depuis votre site pour une prestation."
    H(f"""
    <div class="hero">
        {avatar}
        <div class="hero-badge">DJ POLYVALENT • MC • LIVE</div>
        <h1 class="hero-title">{esc(ARTIST_NAME)} <span>- {esc(SUBTITLE)}</span></h1>
    </div>
    <div class="card">
        <div class="card-title">🎧 DJ polyvalent &amp; MC</div>
        <div>{chips}<span class="chip">et bien plus encore</span></div>
        <div class="bio">Je mets l'ambiance sur vos événements et sur mes lives : mix, animation au micro
        et énergie sur la piste. Contactez-moi directement pour votre prestation.</div>
    </div>
    <div class="contact">
        <a class="wa" href="{esc(wa_link(msg))}" target="_blank" rel="noopener">💬 WhatsApp</a>
        <a href="tel:+{PHONE_INTL}">📞 Appeler</a>
        <a href="{esc(TIKTOK_URL)}" target="_blank" rel="noopener">🎵 TikTok</a>
    </div>
    <div class="phone" style="text-align:center">📱 Contact direct &amp; WhatsApp : <b>{esc(PHONE_DISPLAY)}</b></div>
    """)


# ============================================================
# PARTIE 4/5 — Galerie de Prestations Vidéo
# ============================================================
def render_video(url: str) -> None:
    """Affiche la vidéo : YouTube / TikTok / Facebook en intégration, fichier direct avec st.video."""
    kind = detect_platform(url)
    if kind == "youtube" and youtube_id(url):
        components.html(
            f'<iframe src="https://www.youtube.com/embed/{youtube_id(url)}" width="100%" height="300" '
            'style="border:0;border-radius:14px" allowfullscreen '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">'
            '</iframe>', height=310)
        return
    if kind == "tiktok" and tiktok_id(url):
        components.html(
            '<div style="display:flex;justify-content:center">'
            f'<iframe src="https://www.tiktok.com/embed/v2/{tiktok_id(url)}" width="325" height="740" '
            'style="border:0;border-radius:14px;max-width:100%" allowfullscreen allow="encrypted-media;">'
            '</iframe></div>', height=750)
        return
    if kind == "facebook":
        components.html(
            f'<iframe src="https://www.facebook.com/plugins/video.php?href={quote(url, safe="")}'
            '&amp;show_text=false&amp;width=560" width="100%" height="320" '
            'style="border:0;overflow:hidden;border-radius:14px" scrolling="no" allowfullscreen="true" '
            'allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>',
            height=330)
        return
    if kind == "direct":
        st.video(url)
        return
    H('<div class="ph">Aperçu indisponible pour ce lien : utilisez le bouton ci-dessous '
      '(pour TikTok, collez le lien complet de la vidéo, avec /video/…).</div>')


def render_prestation(p: dict, admin: bool) -> None:
    url = p.get("url", "")
    name = PLATFORM_NAMES.get(detect_platform(url), "le lien")
    desc = f'<div class="bio">{esc(p["description"])}</div>' if p.get("description") else ""
    added = f' • {esc(p["added"])}' if p.get("added") else ""
    H(f'<div class="card"><div class="card-title">{esc(p.get("title") or "Sans titre")}</div>'
      f'<span class="chip">{esc(p.get("style", ""))}</span>'
      f'<span class="chip chip-cyan">{esc(name.capitalize())}{added}</span>{desc}</div>')
    render_video(url)
    st.link_button(f"🔗 Ouvrir sur {name}", url)
    if admin and not p.get("fixed"):
        if st.button("🗑️ Supprimer cette prestation", key=f"del_p_{p['id']}"):
            delete_item("prestations", p["id"])
            flash("Prestation supprimée.")
            st.rerun()
    divider()


def prestation_form() -> None:
    """Formulaire d'ajout : titre, style musical, description, lien de la vidéo."""
    n = st.session_state.form_n
    with st.form(f"form_prestation_{n}"):
        title = st.text_input("Titre de la prestation *", max_chars=80, key=f"p_title_{n}")
        style = st.selectbox("Style musical *", STYLES_MUSICAUX, key=f"p_style_{n}")
        description = st.text_area("Description", max_chars=400, height=90, key=f"p_desc_{n}")
        url = st.text_input("Lien de la vidéo * (TikTok, YouTube, Facebook ou fichier .mp4)", key=f"p_url_{n}",
                            placeholder="https://www.tiktok.com/@dj.oxygene237/video/…")
        submitted = st.form_submit_button("➕ Publier la prestation")
    if submitted:
        link = clean_url(url)
        if not title.strip():
            st.error("Merci d'indiquer un titre.")
        elif not link:
            st.error("Le lien de la vidéo est invalide (il doit commencer par https://).")
        else:
            add_prestation(title.strip(), style, description.strip(), link)
            st.session_state.form_n += 1
            flash("✅ Prestation publiée !")
            st.rerun()


def section_gallery(data: dict) -> None:
    section_title("Galerie de Prestations Vidéo", "Mes mix et mes animations live en vidéo")
    admin = is_admin()
    if admin:
        with st.expander("➕ Ajouter une nouvelle prestation"):
            prestation_form()

    items = all_prestations(data)
    styles = sorted({p.get("style", "") for p in items if p.get("style")})
    if len(styles) > 1:
        choice = st.selectbox("Filtrer par style", ["Tous"] + styles, key="filtre_style")
        if choice != "Tous":
            items = [p for p in items if p.get("style") == choice]

    if not items:
        H('<div class="card">Aucune vidéo pour le moment : les prochaines prestations arrivent bientôt 🎬</div>')
    for p in items:
        render_prestation(p, admin)
    if not admin:
        st.caption("🔒 Les publications sont réservées à Dj Oxygène237 (Espace gestion en bas de page).")


# ============================================================
# PARTIE 5/5 — Annonces & Lives, espace gestion, lancement
# ============================================================
def render_live(a: dict, start: datetime, status: str, now: datetime, admin: bool, is_next: bool = False) -> None:
    platform = a.get("platform", "Autre")
    icon = PLATFORM_ICONS.get(platform, "🔗")
    url = a.get("url", "") or (TIKTOK_URL if platform == "TikTok" else "")
    css = {"live": "is-live", "upcoming": "is-next" if is_next else "", "past": "is-past"}[status]
    badge = {
        "live": '<span class="badge badge-live">🔴 EN DIRECT MAINTENANT</span>',
        "upcoming": f'<span class="badge badge-soon">⏳ {esc(countdown_text(start - now))}</span>',
        "past": '<span class="badge badge-past">✔ Terminé</span>',
    }[status]
    desc = f'<div class="bio">{esc(a["description"])}</div>' if a.get("description") else ""
    H(f'<div class="live-card {css}">{badge}'
      f'<div class="card-title">{esc(a.get("title") or "Live")}</div>'
      f'<span class="chip chip-cyan">{icon} {esc(platform)}</span>'
      f'<div class="live-date">📅 {esc(fr_date(start))}</div>{desc}</div>')
    if url and status != "past":
        st.link_button("🔴 Rejoindre le live" if status == "live" else f"🔔 Ouvrir sur {platform}", url)
    if admin and not a.get("fixed"):
        if st.button("🗑️ Supprimer cette annonce", key=f"del_a_{a['id']}"):
            delete_item("annonces", a["id"])
            flash("Annonce supprimée.")
            st.rerun()


def live_form() -> None:
    """Formulaire d'ajout d'une annonce de live."""
    n = st.session_state.form_n
    with st.form(f"form_live_{n}"):
        title = st.text_input("Titre du live *", max_chars=80, key=f"l_title_{n}",
                              placeholder="Live Ndombolo & Coupé-décalé")
        platform = st.selectbox("Plateforme *", PLATFORMS, key=f"l_plat_{n}")
        c1, c2 = st.columns(2)
        day = c1.date_input("Date *", value=now_local().date(), key=f"l_date_{n}")
        hour = c2.time_input("Heure (Paris) *", value=dtime(20, 0), key=f"l_time_{n}")
        url = st.text_input("Lien du live (facultatif)", key=f"l_url_{n}",
                            placeholder="Si vide et TikTok : lien de ton profil")
        description = st.text_area("Message pour la communauté", max_chars=400, height=80, key=f"l_desc_{n}")
        submitted = st.form_submit_button("📢 Publier l'annonce")
    if submitted:
        link = clean_url(url) if url.strip() else ""
        if not title.strip():
            st.error("Merci d'indiquer un titre.")
        elif url.strip() and not link:
            st.error("Le lien est invalide (il doit commencer par https://).")
        else:
            start_iso = datetime.combine(day, hour).strftime("%Y-%m-%dT%H:%M")
            add_annonce(title.strip(), platform, start_iso, link, description.strip())
            st.session_state.form_n += 1
            flash("✅ Annonce publiée !")
            st.rerun()


def section_lives(data: dict) -> None:
    section_title("Annonces & Lives", "Mes prochains lives et alertes de diffusion en direct")
    admin = is_admin()
    if admin:
        with st.expander("➕ Ajouter une annonce de live"):
            live_form()

    now = now_local()
    lives = []
    fixed = [dict(a, id=f"fixe-{i}", fixed=True) for i, a in enumerate(LIVES_FIXES)]
    for a in list(data["annonces"]) + fixed:
        start = parse_start(a.get("start", ""))
        if start:
            lives.append((start, a, live_status(start, now)))

    now_live = [x for x in lives if x[2] == "live"]
    upcoming = sorted([x for x in lives if x[2] == "upcoming"], key=lambda x: x[0])
    past = sorted([x for x in lives if x[2] == "past"], key=lambda x: x[0], reverse=True)

    for start, a, status in now_live:
        render_live(a, start, status, now, admin)
    for i, (start, a, status) in enumerate(upcoming):
        render_live(a, start, status, now, admin, is_next=(i == 0 and not now_live))
    if not now_live and not upcoming:
        H('<div class="card">📭 Aucun live annoncé pour le moment. Suis-moi sur TikTok pour ne rien rater !</div>')

    st.link_button("🎵 Me suivre sur TikTok", TIKTOK_URL)
    if past:
        with st.expander(f"🕘 Lives passés ({len(past)})"):
            for start, a, status in past[:10]:
                render_live(a, start, status, now, admin)


def admin_panel(data: dict) -> None:
    """Connexion par mot de passe + sauvegarde / restauration des données."""
    with st.expander("🔐 Espace gestion (réservé à Dj Oxygène237)", expanded=is_admin()):
        if is_admin():
            st.success("Connecté : tu peux publier et supprimer des contenus.")
            if st.button("Se déconnecter", key="logout"):
                st.session_state.is_admin = False
                st.rerun()
            st.markdown("**Sauvegarde** : le disque de Streamlit Cloud est temporaire, "
                        "télécharge régulièrement une sauvegarde.")
            st.download_button("💾 Télécharger la sauvegarde (JSON)",
                               data=json.dumps(data, ensure_ascii=False, indent=2),
                               file_name="sauvegarde_oxygene237.json", mime="application/json")
            up = st.file_uploader("Restaurer une sauvegarde (.json)", type=["json"],
                                  key=f"restore_{st.session_state.form_n}")
            if up is not None and st.button("♻️ Restaurer cette sauvegarde", key="restore_btn"):
                try:
                    restore_backup(json.loads(up.getvalue().decode("utf-8")))
                except (ValueError, AttributeError):
                    st.error("Fichier de sauvegarde invalide.")
                else:
                    st.session_state.form_n += 1
                    flash("✅ Sauvegarde restaurée.")
                    st.rerun()
            return

        password = get_admin_password()
        if not password:
            st.info("Pour activer la gestion, ajoute un mot de passe : sur Streamlit Cloud, ouvre "
                    "⚙️ Settings → Secrets et écris  ADMIN_PASSWORD = \"ton-mot-de-passe\".  "
                    "En local, crée le fichier .streamlit/secrets.toml avec la même ligne.")
            return
        if st.session_state.get("fails", 0) >= 5:
            st.error("Trop de tentatives. Recharge la page pour réessayer.")
            return
        with st.form("login_form"):
            typed = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
        if submitted:
            if hmac.compare_digest(typed.encode("utf-8"), password.encode("utf-8")):
                st.session_state.is_admin = True
                st.session_state.fails = 0
                st.rerun()
            else:
                st.session_state.fails = st.session_state.get("fails", 0) + 1
                st.error("Mot de passe incorrect.")


def footer() -> None:
    divider()
    H(f'<div class="footer">© {date.today().year} {esc(ARTIST_NAME)} • {esc(SUBTITLE)}<br>'
      f'📱 {esc(PHONE_DISPLAY)} • <a href="{esc(TIKTOK_URL)}" target="_blank" rel="noopener" '
      f'style="color:#27ecff">TikTok @dj.oxygene237</a></div>')


def main() -> None:
    st.session_state.setdefault("is_admin", False)
    st.session_state.setdefault("form_n", 0)
    inject_css()
    render_header()
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message)

    data = load_data()
    tab_gallery, tab_lives = st.tabs(["🎬 Galerie de Prestations", "📢 Annonces & Lives"])
    with tab_gallery:
        section_gallery(data)
    with tab_lives:
        section_lives(data)

    admin_panel(data)
    footer()


main()
