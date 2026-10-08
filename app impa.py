# -*- coding: utf-8 -*-
"""
Dj Oxygène237 — Espace Prestations & Live
Application Streamlit personnelle : profil et biographie, galerie de prestations vidéo
(TikTok / YouTube / Facebook), annonces de lives, liste du matériel et demande de devis gratuit.

Lancer en local :  streamlit run app.py
"""

# ============================================================
# PARTIE 1/5 — Imports et configuration (à personnaliser ici)
# ============================================================
import base64
import hmac
import html
import io
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
CONTACT_EMAIL = ""                               # ← mets ton adresse email ici (active l'envoi des devis par email)
PHOTO_PATH = "assets/dj_oxygene237.jpg"          # photo permanente (dans le dépôt GitHub), facultatif
LIVE_DURATION_H = 3                              # un live est « en direct » pendant 3 h après son début

STYLES_PRESENTATION = [
    "Afrobeat", "Bikutsi", "Makossa", "Ndombolo", "Coupé-décalé",
    "Shatta", "Dancehall", "Hip-hop", "Salsa", "Latino",
]
STYLES_MUSICAUX = STYLES_PRESENTATION + ["Mix généraliste", "Animation MC / Live", "Autre"]

PLATFORMS = ["TikTok", "YouTube", "Facebook", "Instagram", "Autre"]
PLATFORM_ICONS = {"TikTok": "🎵", "YouTube": "▶️", "Facebook": "📘", "Instagram": "📸", "Autre": "🔗"}

# ------------------------------------------------------------
# 📖 BIOGRAPHIE (**mot** = en gras)
# ------------------------------------------------------------
BIO_PARAGRAPHS = [
    "Derrière les platines et derrière le micro, il y a **Dj Oxygène237**, un artiste aux multiples "
    "facettes, à la fois **DJ polyvalent et MC**. Véritable showman, il s'impose comme une valeur sûre "
    "pour enflammer tous les types de scènes et de publics.",
    "Porté par une culture musicale vaste et un sens inné de la fête, Dj Oxygène237 casse les frontières "
    "des genres. Qu'il s'agisse de faire vibrer les pistes aux sons enivrants de l'**Afrobeat**, du "
    "**Bikutsi**, du **Makossa**, du **Ndombolo** ou du **Coupé-décalé**, ou de dynamiser les foules avec "
    "des rythmes urbains et caribéens comme le **Shatta**, le **Dancehall**, le **Hip-hop**, la **Salsa** "
    "et le **Latino**, il adapte instantanément son set à l'énergie de la salle.",
    "Mais son talent ne s'arrête pas au mix : en tant que **Master of Ceremonies (MC)**, il maîtrise l'art "
    "de captiver le public, de porter l'ambiance à son paroxysme et de transformer chaque événement "
    "(soirées en club, mariages, anniversaires ou concerts) en une expérience mémorable.",
    "Toujours connecté à sa communauté à travers ses réseaux et ses sessions live régulières (notamment "
    "sur TikTok), Dj Oxygène237 insuffle une énergie unique à chaque prestation, prouvant que la musique "
    "est avant tout un partage universel.",
]

# ------------------------------------------------------------
# 🔊 MATÉRIEL : (quantité, désignation, caractéristique)
# ------------------------------------------------------------
EQUIPMENT = [
    ("🔊 Sonorisation", [
        ("×2", "Caissons de basses QSC 18\"", "3600 W"),
        ("×2", "Caissons de basses ALTO 18\"", "2000 W"),
        ("×4", "Satellites HK 12\"", "1200 W"),
        ("×4", "Satellites db Technologies Chromo 12\"", "1200 W"),
        ("×12", "Satellites db Technologies 15\"", "800 W"),
    ]),
    ("🎚️ Régie & micros", [
        ("×1", "Table de mixage YAMAHA 8 pistes", ""),
        ("×2", "Micros pro", ""),
    ]),
    ("💡 Lumières", [
        ("×1", "Laser 1000 W (pour l'ouverture de bal)", "1000 W"),
        ("×2", "Lyres Beam Wash", "150 W"),
        ("×2", "Lyres Beam", "280 W"),
        ("×4", "Lyres Wash avec zoom", ""),
        ("×4", "Pars LED", ""),
        ("×1", "Ordinateur pour piloter les lumières", ""),
    ]),
    ("✨ Effets spéciaux", [
        ("×1", "Machine à fumée lourde", ""),
        ("×1", "Machine à fumée", ""),
        ("×1", "Machine à brouillard", ""),
        ("×1", "Machine à neige", ""),
        ("×2", "Fumigènes à étincelles froides", ""),
        ("×4", "Fumigènes à étincelles chaudes", ""),
    ]),
    ("📺 Écran & animation", [
        ("12 m²", "Écran LED", ""),
        ("×1", "Appareil photomaton", ""),
    ]),
]
VEHICLE_TEXT = ("Un véhicule de déplacement est disponible pour transporter le matériel "
                "jusqu'à votre événement.")

# ------------------------------------------------------------
# 🧾 DEVIS GRATUIT
# ------------------------------------------------------------
EVENT_TYPES = [
    "Mariage", "Anniversaire", "Soirée privée", "Soirée d'entreprise",
    "Baptême / Cérémonie", "Concert / Showcase", "Soirée en club", "Autre",
]
SERVICE_OPTIONS = [
    "DJ", "MC / Animation", "Sonorisation", "Jeux de lumière (lyres, pars LED)",
    "Laser (ouverture de bal)", "Machines à fumée / neige / brouillard",
    "Étincelles froides / chaudes", "Écran LED", "Photomaton", "Transport du matériel",
]

PAGES = ["🎬 Galerie", "📢 Lives", "🔊 Matériel", "🧾 Devis gratuit"]

# ------------------------------------------------------------
# 📌 CONTENUS FIXES (toujours affichés, même si le serveur redémarre)
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
# PARTIE 2/5 — Données, photo de profil, liens vidéo, dates, accès gestion
# ============================================================
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "oxygene237.json"
PHOTO_UPLOAD = BASE_DIR / "data" / "profil.jpg"      # photo envoyée depuis l'Espace gestion
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


def rich(text: str) -> str:
    """Échappe le texte puis transforme **mot** en gras."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(text))


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


# ---------- Photo de profil ----------
def profile_photo_uri():
    """Photo envoyée depuis l'Espace gestion en priorité, sinon la photo du dépôt (assets/)."""
    try:
        if PHOTO_UPLOAD.exists():
            return "data:image/jpeg;base64," + base64.b64encode(PHOTO_UPLOAD.read_bytes()).decode()
    except OSError:
        pass
    return img_uri(PHOTO_PATH)


def save_profile_photo(raw: bytes) -> bool:
    """Vérifie, recadre en carré (480 px) et enregistre la photo. Renvoie False si l'image est invalide."""
    if not raw or len(raw) > 8 * 1024 * 1024:
        return False
    try:
        from PIL import Image, ImageOps
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img).convert("RGB")
        img = ImageOps.fit(img, (480, 480))
        PHOTO_UPLOAD.parent.mkdir(parents=True, exist_ok=True)
        img.save(PHOTO_UPLOAD, "JPEG", quality=88)
        return True
    except Exception:
        return False


def delete_profile_photo() -> None:
    try:
        PHOTO_UPLOAD.unlink()
    except OSError:
        pass


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


def build_backup(data: dict) -> dict:
    """Données + photo de profil (encodée) pour la sauvegarde téléchargeable."""
    out = dict(data)
    try:
        if PHOTO_UPLOAD.exists():
            out["profil_photo"] = base64.b64encode(PHOTO_UPLOAD.read_bytes()).decode()
    except OSError:
        pass
    return out


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
    photo = raw.get("profil_photo")
    if isinstance(photo, str) and photo:
        try:
            save_profile_photo(base64.b64decode(photo, validate=True))
        except ValueError:
            pass


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


def go_to(page: str) -> None:
    """Callback de navigation (boutons « Demander un devis »)."""
    st.session_state.page = page


# ============================================================
# PARTIE 3/5 — Style sobre (CSS) et en-tête / profil
# ============================================================
def inject_css() -> None:
    H("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Montserrat:wght@600;700;800&display=swap');
    :root{--bg:#12151c;--card:#1b2029;--line:rgba(255,255,255,.10);--accent:#ff8a3d;
          --text:#f2f4f8;--muted:#a6afbf;}
    html,body,.stApp,.stMarkdown,p,li,label,input,textarea,button,[data-baseweb="tab"],
    [data-baseweb="select"] div{font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;}
    .stApp{background:var(--bg);color:var(--text);}
    header[data-testid="stHeader"]{background:transparent;}
    #MainMenu,footer{visibility:hidden;}
    .block-container{padding:1rem 1rem 4rem;max-width:720px;}
    h1,h2,h3,label,.stMarkdown p,.stMarkdown li{color:var(--text);}
    a{text-decoration:none;}

    /* ---- En-tête ---- */
    .hero{text-align:center;padding:1.4rem 1rem 1.2rem;margin:.2rem 0 .8rem;border-radius:20px;
        background:var(--card);border:1px solid var(--line);}
    .avatar{width:112px;height:112px;border-radius:50%;object-fit:cover;border:2px solid var(--accent);
        margin-bottom:.7rem;}
    .avatar-ph{display:inline-flex;align-items:center;justify-content:center;font-size:2.6rem;
        background:#242a36;}
    .hero-title{font-family:'Montserrat','Inter',sans-serif;font-weight:800;font-size:1.65rem;line-height:1.25;
        margin:.1rem 0 .2rem;color:var(--text);}
    .hero-title span{display:block;font-size:.82rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;
        color:var(--accent);margin-top:.35rem;}
    .contact{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin:.9rem 0 .5rem;}
    .contact a{display:flex;align-items:center;justify-content:center;padding:.7rem .3rem;border-radius:12px;
        color:var(--text)!important;font-weight:600;font-size:.86rem;border:1px solid var(--line);
        background:#242a36;transition:border-color .2s,background .2s;}
    .contact a:hover{border-color:var(--accent);}
    .contact a.main{background:var(--accent);border-color:var(--accent);color:#12151c!important;}
    .phone{font-size:.88rem;color:var(--muted);}

    /* ---- Cartes & titres ---- */
    .card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:1rem 1.1rem;
        margin:.6rem 0;color:var(--text);font-size:.92rem;}
    .card-title{font-family:'Montserrat','Inter',sans-serif;font-weight:700;font-size:1.02rem;margin-bottom:.45rem;}
    .bio{color:#d3d9e4;font-size:.9rem;line-height:1.55;margin-top:.5rem;}
    .section-title{font-family:'Montserrat','Inter',sans-serif;font-weight:700;font-size:1.3rem;margin:.8rem 0 .15rem;
        color:var(--text);}
    .section-sub{color:var(--muted);font-size:.88rem;margin-bottom:.6rem;}
    .divider{height:1px;margin:1.1rem 0;background:var(--line);}
    .chip{display:inline-block;margin:.15rem .25rem .15rem 0;padding:.14rem .65rem;border-radius:999px;font-size:.75rem;
        border:1px solid var(--line);color:#d3d9e4;background:#242a36;}
    .chip-accent{border-color:var(--accent);color:var(--accent);background:transparent;}
    .ph{display:flex;align-items:center;justify-content:center;text-align:center;padding:1rem;height:110px;border-radius:14px;
        margin:.4rem 0;background:#242a36;border:1px dashed var(--line);color:var(--muted);}

    /* ---- Matériel ---- */
    .gear-row{display:flex;align-items:baseline;gap:.7rem;padding:.5rem 0;border-bottom:1px solid var(--line);}
    .gear-row:last-child{border-bottom:none;}
    .qty{min-width:3.1rem;font-weight:700;color:var(--accent);}
    .gear-name{flex:1;}
    .gear-spec{color:var(--muted);font-size:.85rem;white-space:nowrap;}

    /* ---- Lives ---- */
    .live-card{border-radius:16px;padding:1rem 1.1rem;margin:.6rem 0;border:1px solid var(--line);background:var(--card);}
    .live-card.is-live{border:2px solid #e5484d;}
    .live-card.is-next{border:1px solid var(--accent);}
    .live-card.is-past{opacity:.65;}
    .live-date{font-size:.9rem;color:var(--muted);margin:.3rem 0;}
    .badge{display:inline-block;font-size:.72rem;font-weight:600;letter-spacing:.05em;border-radius:999px;
        padding:.18rem .7rem;margin-bottom:.4rem;}
    .badge-live{background:#e5484d;color:#fff;animation:pulse 1.4s infinite;}
    .badge-soon{border:1px solid var(--accent);color:var(--accent);}
    .badge-past{background:#242a36;color:var(--muted);}
    @keyframes pulse{0%{opacity:1}50%{opacity:.6}100%{opacity:1}}

    /* ---- Navigation (pilules) ---- */
    div[role="radiogroup"]{gap:.4rem;flex-wrap:wrap;justify-content:center;}
    div[role="radiogroup"] label{background:var(--card);border:1px solid var(--line);border-radius:999px;
        padding:.3rem .9rem;cursor:pointer;transition:border-color .2s;}
    div[role="radiogroup"] label > div:first-child{display:none;}
    div[role="radiogroup"] label:hover{border-color:var(--accent);}
    div[role="radiogroup"] label:has(input:checked){background:var(--accent);border-color:var(--accent);}
    div[role="radiogroup"] label:has(input:checked) p{color:#12151c;font-weight:600;}

    /* ---- Widgets Streamlit ---- */
    .stButton>button,.stFormSubmitButton>button,a[data-testid="stBaseLinkButton-secondary"],
    a[data-testid="stBaseLinkButton-primary"],[data-testid="stLinkButton"] a,.stDownloadButton>button{
        width:100%;display:flex;justify-content:center;
        background:var(--accent)!important;color:#12151c!important;border:none!important;
        border-radius:12px!important;font-weight:600!important;padding:.55rem 1rem!important;transition:filter .2s!important;}
    .stButton>button:hover,.stFormSubmitButton>button:hover,a[data-testid="stBaseLinkButton-secondary"]:hover,
    a[data-testid="stBaseLinkButton-primary"]:hover,[data-testid="stLinkButton"] a:hover,.stDownloadButton>button:hover{
        filter:brightness(1.1);}
    .stButton>button p,.stFormSubmitButton>button p,[data-testid="stLinkButton"] a p,.stDownloadButton>button p{color:#12151c!important;}
    .stTextInput input,.stTextArea textarea,.stDateInput input,.stTimeInput input,.stNumberInput input,
    .stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{
        background:#242a36!important;color:var(--text)!important;border:1px solid var(--line)!important;border-radius:10px!important;}
    div[data-testid="stExpander"]{background:var(--card);border:1px solid var(--line);border-radius:14px;}
    div[data-testid="stForm"]{background:var(--card);border:1px solid var(--line);border-radius:16px;}
    .footer{text-align:center;color:var(--muted);font-size:.78rem;margin-top:2rem;}

    @media (max-width:640px){
        .hero-title{font-size:1.35rem;}
        .block-container{padding:.6rem .6rem 4rem;}
        .contact a{font-size:.8rem;}
        .gear-row{flex-wrap:wrap;gap:.3rem .7rem;}
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
    """Photo, titre, styles musicaux, biographie et boutons de contact."""
    uri = profile_photo_uri()
    avatar = (f'<img class="avatar" src="{uri}" alt="{esc(ARTIST_NAME)}">' if uri
              else '<div class="avatar avatar-ph">🎧</div>')
    chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in STYLES_PRESENTATION)
    msg = f"Bonjour {ARTIST_NAME}, je vous contacte depuis votre site pour une prestation."
    H(f"""
    <div class="hero">
        {avatar}
        <h1 class="hero-title">{esc(ARTIST_NAME)} <span>- {esc(SUBTITLE)}</span></h1>
        <div class="bio">DJ polyvalent &amp; MC</div>
        <div style="margin-top:.5rem">{chips}</div>
        <div class="contact">
            <a class="main" href="{esc(wa_link(msg))}" target="_blank" rel="noopener">💬 WhatsApp</a>
            <a href="tel:+{PHONE_INTL}">📞 Appeler</a>
            <a href="{esc(TIKTOK_URL)}" target="_blank" rel="noopener">🎵 TikTok</a>
        </div>
        <div class="phone">Contact direct &amp; WhatsApp : <b>{esc(PHONE_DISPLAY)}</b></div>
    </div>
    """)
    with st.expander("📖 Biographie"):
        H("".join(f'<div class="bio">{rich(p)}</div>' for p in BIO_PARAGRAPHS))
    st.button("🧾 Demander un devis gratuit", on_click=go_to, args=("🧾 Devis gratuit",), key="cta_header")


# ============================================================
# PARTIE 4/5 — Galerie vidéo, matériel, devis gratuit
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
      f'<span class="chip chip-accent">{esc(p.get("style", ""))}</span>'
      f'<span class="chip">{esc(name.capitalize())}{added}</span>{desc}</div>')
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


def page_gallery(data: dict) -> None:
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


def page_equipment(data: dict) -> None:
    section_title("Matériel & Effets Spéciaux", "Sonorisation, lumières et effets pour tous vos événements")
    for title, items in EQUIPMENT:
        rows = "".join(
            f'<div class="gear-row"><span class="qty">{esc(qty)}</span>'
            f'<span class="gear-name">{esc(name)}</span><span class="gear-spec">{esc(spec)}</span></div>'
            for qty, name, spec in items
        )
        H(f'<div class="card"><div class="card-title">{esc(title)}</div>{rows}</div>')
    H(f'<div class="card"><div class="card-title">🚐 Véhicule de déplacement</div>'
      f'<div class="bio" style="margin-top:0">{esc(VEHICLE_TEXT)}</div></div>')
    st.button("🧾 Demander un devis gratuit", on_click=go_to, args=("🧾 Devis gratuit",), key="cta_equipment")


def build_quote_summary(f: dict) -> str:
    services = ", ".join(f["services"]) if f["services"] else "À définir ensemble"
    lines = [
        f"🎧 *DEMANDE DE DEVIS GRATUIT — {ARTIST_NAME}*",
        f"👤 Nom : {f['name']}",
        f"📞 Téléphone : {f['phone']}",
    ]
    if f.get("email"):
        lines.append(f"✉️ Email : {f['email']}")
    lines += [
        f"🎉 Événement : {f['event']}",
        f"📅 Date : {f['date'].strftime('%d/%m/%Y')}",
        f"📍 Lieu : {f['place'] or 'À préciser'}",
        f"👥 Invités (approx.) : {f['guests']}",
        f"🔊 Souhaité : {services}",
    ]
    if f["details"]:
        lines.append(f"📝 Détails : {f['details']}")
    return "\n".join(lines)


def mailto_link(summary: str) -> str:
    subject = f"Demande de devis gratuit — {ARTIST_NAME}"
    body = summary.replace("*", "") + "\n\nMerci de me répondre par email ou par téléphone."
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}&body={quote(body)}"


def page_quote(data: dict) -> None:
    section_title("Demande de devis gratuit",
                  "Remplissez le formulaire : votre demande est prête à envoyer sur WhatsApp"
                  + (" ou par email." if CONTACT_EMAIL else "."))
    with st.form("quote_form"):
        name = st.text_input("Votre nom *", max_chars=60)
        phone = st.text_input("Téléphone / WhatsApp *", max_chars=20, placeholder="+33 6 12 34 56 78")
        email = st.text_input("Votre email (facultatif)", max_chars=80, placeholder="vous@exemple.com")
        event = st.selectbox("Type d'événement *", EVENT_TYPES)
        c1, c2 = st.columns(2)
        ev_date = c1.date_input("Date *", min_value=now_local().date(), value=now_local().date())
        guests = c2.number_input("Invités (approx.)", min_value=1, max_value=5000, value=100, step=10)
        place = st.text_input("Lieu / Ville", max_chars=80)
        services = st.multiselect("Prestations & matériel souhaités", SERVICE_OPTIONS)
        details = st.text_area("Précisions (ambiance, horaires, styles musicaux…)", max_chars=400, height=90)
        submitted = st.form_submit_button("✨ Générer ma demande de devis")

    if submitted:
        digits = "".join(ch for ch in phone if ch.isdigit())
        if not name.strip() or len(digits) < 8:
            st.error("Merci d'indiquer votre nom et un numéro de téléphone valide.")
        elif email.strip() and "@" not in email:
            st.error("L'adresse email semble incorrecte.")
        else:
            st.session_state.quote = build_quote_summary({
                "name": name.strip(), "phone": phone.strip(), "email": email.strip(),
                "event": event, "date": ev_date, "place": place.strip(),
                "guests": int(guests), "services": services, "details": details.strip(),
            })

    summary = st.session_state.get("quote")
    if summary:
        divider()
        H('<div class="card-title">✅ Votre demande est prête : envoyez-la</div>')
        st.code(summary, language=None)
        st.link_button("💬 Envoyer sur WhatsApp", wa_link(summary))
        if CONTACT_EMAIL:
            st.link_button("✉️ Envoyer par email", mailto_link(summary))
        st.caption("Le bouton ouvre l'application avec le message déjà rédigé : il ne reste qu'à l'envoyer.")


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
      f'<span class="chip chip-accent">{icon} {esc(platform)}</span>'
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


def page_lives(data: dict) -> None:
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
    """Connexion par mot de passe, photo de profil, sauvegarde / restauration."""
    with st.expander("🔐 Espace gestion (réservé à Dj Oxygène237)", expanded=is_admin()):
        if is_admin():
            st.success("Connecté : tu peux publier et supprimer des contenus.")
            if st.button("Se déconnecter", key="logout"):
                st.session_state.is_admin = False
                st.rerun()

            st.markdown("**📸 Photo de profil**")
            if PHOTO_UPLOAD.exists():
                st.image(str(PHOTO_UPLOAD), width=120)
            photo = st.file_uploader("Choisir une photo (JPG, PNG ou WEBP)", type=["jpg", "jpeg", "png", "webp"],
                                     key=f"photo_{st.session_state.form_n}")
            if photo is not None and st.button("💾 Enregistrer cette photo", key="photo_btn"):
                if save_profile_photo(photo.getvalue()):
                    st.session_state.form_n += 1
                    flash("✅ Photo de profil enregistrée.")
                    st.rerun()
                else:
                    st.error("Image invalide ou trop lourde (8 Mo maximum).")
            if PHOTO_UPLOAD.exists() and st.button("🗑️ Retirer la photo", key="photo_del"):
                delete_profile_photo()
                flash("Photo retirée.")
                st.rerun()

            st.markdown("**💾 Sauvegarde** : le disque de Streamlit Cloud est temporaire, "
                        "télécharge régulièrement une sauvegarde (elle contient aussi ta photo).")
            st.download_button("Télécharger la sauvegarde (JSON)",
                               data=json.dumps(build_backup(data), ensure_ascii=False, indent=2),
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
      f'style="color:#ff8a3d">TikTok @dj.oxygene237</a></div>')


PAGE_FUNCS = {
    "🎬 Galerie": page_gallery,
    "📢 Lives": page_lives,
    "🔊 Matériel": page_equipment,
    "🧾 Devis gratuit": page_quote,
}


def main() -> None:
    st.session_state.setdefault("is_admin", False)
    st.session_state.setdefault("form_n", 0)
    st.session_state.setdefault("page", PAGES[0])
    inject_css()
    render_header()
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message)

    st.radio("Navigation", PAGES, horizontal=True, key="page", label_visibility="collapsed")
    data = load_data()
    PAGE_FUNCS[st.session_state.page](data)

    admin_panel(data)
    footer()


main()
