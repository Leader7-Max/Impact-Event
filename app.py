# -*- coding: utf-8 -*-
"""
Impact Event — Application web du collectif DJ & événementiel
Basés à Grenoble • On se déplace partout
DJ Mosi (à l'honneur) • DJ Oxygène • Espace MCs

Lancer en local :  streamlit run app.py
"""

# ============================================================
# PARTIE 1/6 — Imports, configuration et données
# ============================================================
import base64
import html
import json
import threading
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st

st.set_page_config(
    page_title="Impact Event | DJ, MCs & Événementiel à Grenoble",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "community.json"
_LOCK = threading.Lock()


def wa_link(phone: str, text: str = "") -> str:
    """Lien WhatsApp direct (numéro au format international SANS +), message facultatif pré-rempli."""
    return f"https://wa.me/{phone}" + (f"?text={quote(text)}" if text else "")


# ------------------------------------------------------------
# ⚙️ CONFIGURATION À PERSONNALISER
# ------------------------------------------------------------
APP_NAME = "Impact Event"
APP_URL = "https://impact-event.streamlit.app"   # ← l'URL de ton app une fois déployée
CITY = "Grenoble"

CONTACT_EMAIL = "votre-email@exemple.com"        # ← ⚠️ METS ICI VOTRE VRAIE ADRESSE EMAIL
PHONE_MOSI = "33783236211"                       # DJ Mosi    (+33 7 83 23 62 11)
PHONE_OXYGENE = "33773616884"                    # DJ Oxygène (+33 7 73 61 68 84)

SOCIALS = [
    ("WhatsApp DJ Mosi", "💬", "whatsapp",
     wa_link(PHONE_MOSI, "Bonjour DJ Mosi, je vous contacte depuis le site Impact Event.")),
    ("WhatsApp DJ Oxygène", "💬", "whatsapp",
     wa_link(PHONE_OXYGENE, "Bonjour DJ Oxygène, je vous contacte depuis le site Impact Event.")),
    ("Email", "✉️", "email", f"mailto:{CONTACT_EMAIL}"),
    ("TikTok", "🎵", "tiktok", "https://www.tiktok.com/@impactevent"),
    ("YouTube", "▶️", "youtube", "https://www.youtube.com/@impactevent"),
    ("Facebook", "📘", "facebook", "https://www.facebook.com/impactevent"),
]

# ------------------------------------------------------------
# 👥 ÉQUIPE (DJ Mosi est mis à l'honneur : "featured": True)
# ------------------------------------------------------------
TEAM = [
    {
        "id": "mosi",
        "featured": True,
        "initial": "M",
        "name": "DJ Mosi",
        "flag": "🇨🇬",
        "country": "Congo",
        "role": "DJ • Membre partenaire d'Impact Event",
        "phone": PHONE_MOSI,
        "bio": (
            "Passionné de rumba congolaise et de ndombolo, DJ Mosi sait aussi se faire "
            "généraliste pour satisfaire tous les publics, de l'ouverture de bal jusqu'au "
            "dernier titre de la nuit."
        ),
        "specialties": ["Rumba congolaise", "Ndombolo", "Généraliste"],
        "photo": "assets/team/dj_mosi.jpg",
        "links": {
            "💬 WhatsApp": wa_link(PHONE_MOSI, "Bonjour DJ Mosi, je vous contacte depuis le site Impact Event."),
            "🎧 Mix": "https://soundcloud.com/",
            "▶️ YouTube": "https://www.youtube.com/",
            "📘 Facebook": "https://www.facebook.com/",
        },
    },
    {
        "id": "oxygene",
        "initial": "O",
        "name": "DJ Oxygène",
        "flag": "🇨🇲",
        "country": "Cameroun",
        "role": "DJ • Membre partenaire d'Impact Event",
        "phone": PHONE_OXYGENE,
        "bio": (
            "Ambianceur au son chaud et énergique, DJ Oxygène fait vibrer les pistes "
            "avec des sets qui mélangent racines africaines et rythmes du monde. "
            "Mariages, anniversaires, soirées privées : il lit la salle et fait monter la température."
        ),
        "specialties": ["Afrobeat", "Bikutsi", "Zouglou", "Latino"],
        "photo": "assets/team/dj_oxygene.jpg",
        "links": {
            "💬 WhatsApp": wa_link(PHONE_OXYGENE, "Bonjour DJ Oxygène, je vous contacte depuis le site Impact Event."),
            "🎧 Mix": "https://soundcloud.com/",
            "🎵 TikTok": "https://www.tiktok.com/",
            "📘 Facebook": "https://www.facebook.com/",
        },
    },
    {
        "id": "mcs",
        "initial": "🎤",
        "name": "Espace MCs",
        "flag": "🎙️",
        "country": "Partenaires micro",
        "role": "MCs • Animation • Membres partenaires d'Impact Event",
        "phone": PHONE_MOSI,
        "bio": (
            "Nos MCs partenaires donnent la voix à vos événements : présentation des "
            "mariés, animation de la piste, ambiance de cérémonie, jeux et "
            "interaction avec le public. Ils s'adaptent à votre événement et à votre langue."
        ),
        "specialties": ["Animation", "Cérémonies", "Hype man", "Multilingue"],
        "photo": "assets/team/mcs.jpg",
        "links": {
            "💬 WhatsApp": wa_link(PHONE_MOSI, "Bonjour, je souhaite des informations sur les MCs d'Impact Event."),
            "🎵 TikTok": "https://www.tiktok.com/",
        },
    },
]

# ------------------------------------------------------------
# 🔊 CATALOGUE DE MATÉRIEL (prix « sur devis » — modifiable)
# ------------------------------------------------------------
EQUIPMENT = [
    {
        "category": "🔊 Sonorisation",
        "items": [
            {"icon": "🔊", "name": "Bafles / Enceintes professionnelles",
             "desc": "Systèmes son puissants, clairs et adaptés à la taille de votre salle ou de votre extérieur.",
             "tag": "Son"},
        ],
    },
    {
        "category": "💡 Lumières & Effets",
        "items": [
            {"icon": "💡", "name": "Jeux de lumière",
             "desc": "Projecteurs, lyres et effets lumineux synchronisés avec la musique.",
             "tag": "Lumière"},
            {"icon": "🔴", "name": "Lasers (ouverture de bal)",
             "desc": "Faisceaux laser spectaculaires pour une entrée des mariés inoubliable.",
             "tag": "Laser"},
            {"icon": "🌫️", "name": "Machine à fumée lourde",
             "desc": "Brouillard bas qui épouse le sol : effet « nuages » pour la première danse.",
             "tag": "Fumée"},
            {"icon": "✨", "name": "Jet-seines (étincelles froides)",
             "desc": "Fontaines d'étincelles froides, sans danger en intérieur, effet waouh garanti.",
             "tag": "Effet spécial"},
        ],
    },
]

# ------------------------------------------------------------
# 📸 GALERIE (photos / vidéos)
# "src" : chemin local dans le dépôt OU lien https (image ou vidéo/YouTube)
# Si le fichier est absent, un visuel de remplacement s'affiche.
# ------------------------------------------------------------
GALLERY = [
    {"id": "soiree-01", "type": "image", "src": "assets/gallery/soiree_01.jpg",
     "title": "Ouverture de bal — Mariage",
     "caption": "Lasers, fumée lourde et étincelles froides pour l'entrée des mariés."},
    {"id": "soiree-02", "type": "image", "src": "assets/gallery/soiree_02.jpg",
     "title": "Soirée Afrobeat & Rumba",
     "caption": "Les deux univers réunis sur la même piste."},
    {"id": "video-01", "type": "video", "src": "assets/gallery/video_01.mp4",
     "title": "Aftermovie — Soirée VIP",
     "caption": "Revivez l'ambiance en vidéo."},
]

EVENT_TYPES = [
    "Mariage", "Anniversaire", "Soirée privée", "Soirée d'entreprise",
    "Baptême / Cérémonie", "Concert / Showcase", "Autre",
]
SERVICE_OPTIONS = [
    "DJ Mosi", "DJ Oxygène", "MC / Animation",
    "Bafles / Enceintes", "Jeux de lumière", "Laser (ouverture de bal)",
    "Machine à fumée lourde", "Jet-seines (étincelles froides)",
]

PAGES = ["🏠 Accueil", "🎛️ Équipe", "📸 Galerie", "🔊 Matériel", "💬 Livre d'or", "🧾 Devis"]


# ============================================================
# PARTIE 2/6 — Utilitaires, persistance et CSS (thème lumineux)
# ============================================================
esc = html.escape


def H(markup: str) -> None:
    """Affiche du HTML/CSS (nettoie l'indentation et les lignes vides
    pour éviter les blocs de code Markdown)."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines() if line.strip()),
                unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def img_uri(rel_path: str):
    """Convertit une image locale en data-URI (pour l'intégrer dans le HTML). None si absente."""
    path = BASE_DIR / rel_path
    if not path.exists():
        return None
    mimes = {".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp"}
    mime = mimes.get(path.suffix.lower(), "image/jpeg")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


# ---------- Données communautaires (likes, commentaires, livre d'or) ----------
def load_data() -> dict:
    data = {"likes": {}, "comments": {}, "guestbook": []}
    try:
        if DATA_FILE.exists():
            data.update(json.loads(DATA_FILE.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError):
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


def now_str() -> str:
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def add_like(item_id: str) -> None:
    _mutate(lambda d: d["likes"].__setitem__(item_id, d["likes"].get(item_id, 0) + 1))


def add_comment(item_id: str, author: str, text: str) -> None:
    entry = {"name": author[:30], "msg": text[:300], "date": now_str()}
    _mutate(lambda d: d["comments"].setdefault(item_id, []).append(entry))


def add_guest_message(author: str, text: str) -> None:
    entry = {"name": author[:30], "msg": text[:400], "date": now_str()}

    def fn(d):
        d["guestbook"].insert(0, entry)
        d["guestbook"] = d["guestbook"][:200]

    _mutate(fn)


def whatsapp_share_url(title: str) -> str:
    text = f"🎧 Regarde ça : {title} — {APP_NAME}\n{APP_URL}"
    return "https://wa.me/?text=" + quote(text)


def mailto_link(summary: str) -> str:
    """Lien email avec sujet et message déjà rédigés (s'ouvre dans l'appli mail du téléphone)."""
    subject = f"Demande de devis — {APP_NAME}"
    body = summary.replace("*", "") + "\n\nMerci de me répondre par email ou par téléphone."
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}&body={quote(body)}"


def go_to(page: str) -> None:
    """Callback de navigation (utilisable avec on_click)."""
    st.session_state.page = page


# ---------- CSS personnalisé : look Nightclub lumineux ----------
def inject_css() -> None:
    H("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Poppins:wght@300;400;600&display=swap');
    :root{--bg:#2b1d70;--card:#3d3092;--card2:#4b3fa8;--orange:#ff7a2e;--red:#ff3d68;
          --cyan:#27ecff;--blue:#4d8dff;--text:#ffffff;--muted:#d9d4fb;}
    .stApp{background:
        radial-gradient(circle at 10% 0%,rgba(255,122,46,.55),transparent 45%),
        radial-gradient(circle at 95% 10%,rgba(39,236,255,.40),transparent 45%),
        linear-gradient(165deg,#2b1d70 0%,#4b1f7a 55%,#1f3a8f 100%);
        background-attachment:fixed;color:var(--text);font-family:'Poppins',sans-serif;}
    header[data-testid="stHeader"]{background:transparent;}
    #MainMenu,footer{visibility:hidden;}
    .block-container{padding:1rem 1rem 4rem;max-width:760px;}
    h1,h2,h3,label,.stMarkdown p,.stMarkdown li{color:var(--text);}
    a{text-decoration:none;}

    /* ---- Marque / en-tête ---- */
    .brandbar{display:flex;align-items:center;justify-content:center;gap:.6rem;margin:.2rem 0 .8rem;}
    .brand{font-family:'Orbitron',sans-serif;font-weight:800;font-size:1.25rem;letter-spacing:.12em;
           background:linear-gradient(90deg,var(--orange),var(--red),var(--cyan));-webkit-background-clip:text;
           -webkit-text-fill-color:transparent;}
    .pulse{width:10px;height:10px;border-radius:50%;background:var(--red);box-shadow:0 0 12px var(--red);
           animation:pulse 1.4s infinite;}
    @keyframes pulse{0%{transform:scale(.8);opacity:.6}50%{transform:scale(1.25);opacity:1}100%{transform:scale(.8);opacity:.6}}

    /* ---- Navigation en pilules (radio) ---- */
    div[role="radiogroup"]{gap:.4rem;flex-wrap:wrap;justify-content:center;}
    div[role="radiogroup"] label{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);
        border-radius:999px;padding:.3rem .85rem;cursor:pointer;transition:.25s;}
    div[role="radiogroup"] label > div:first-child{display:none;}
    div[role="radiogroup"] label:hover{border-color:var(--cyan);box-shadow:0 0 12px rgba(39,236,255,.45);}
    div[role="radiogroup"] label:has(input:checked){
        background:linear-gradient(90deg,var(--orange),var(--red));border-color:transparent;
        box-shadow:0 0 16px rgba(255,100,60,.6);}

    /* ---- Hero ---- */
    .hero{position:relative;overflow:hidden;border-radius:22px;padding:2.2rem 1.2rem;text-align:center;margin:.6rem 0 1rem;
        background:linear-gradient(120deg,#ff6a1a,#e0245e,#7b2cff,#1f78ff);background-size:300% 300%;
        animation:flow 10s ease infinite;border:1px solid rgba(255,255,255,.35);
        box-shadow:0 10px 40px rgba(255,100,60,.35);}
    @keyframes flow{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
    .hero-badge{display:inline-block;font-size:.68rem;letter-spacing:.18em;color:#fff;
        border:1px solid rgba(255,255,255,.85);background:rgba(0,0,0,.18);border-radius:999px;
        padding:.25rem .8rem;margin-bottom:.8rem;}
    .hero-title{font-family:'Orbitron',sans-serif;font-weight:800;font-size:2.4rem;line-height:1.1;margin:.2rem 0;
        color:#fff;text-shadow:0 3px 14px rgba(0,0,0,.35);}
    .hero-title span{color:var(--cyan);text-shadow:0 3px 14px rgba(0,0,0,.45);}
    .hero-sub{color:#fff;font-weight:400;margin:.6rem 0 0;font-size:.98rem;text-shadow:0 1px 6px rgba(0,0,0,.3);}

    /* ---- Contacts & réseaux ---- */
    .socials{display:grid;grid-template-columns:repeat(2,1fr);gap:.6rem;margin:.4rem 0 1rem;}
    .social-btn{display:flex;align-items:center;justify-content:center;gap:.4rem;padding:.8rem .4rem;border-radius:14px;
        color:#fff!important;font-weight:600;font-size:.88rem;text-align:center;
        border:1px solid rgba(255,255,255,.28);background:rgba(255,255,255,.14);
        transition:transform .2s,box-shadow .2s;}
    .social-btn:hover{transform:translateY(-3px);}
    .social-btn.tiktok:hover{box-shadow:0 0 18px rgba(39,236,255,.8);border-color:var(--cyan);}
    .social-btn.youtube:hover{box-shadow:0 0 18px rgba(255,61,104,.8);border-color:var(--red);}
    .social-btn.facebook:hover{box-shadow:0 0 18px rgba(77,141,255,.8);border-color:var(--blue);}
    .social-btn.whatsapp{background:rgba(37,211,102,.28);border-color:rgba(37,211,102,.8);}
    .social-btn.whatsapp:hover{box-shadow:0 0 18px rgba(37,211,102,.85);}
    .social-btn.email:hover{box-shadow:0 0 18px rgba(255,200,60,.85);border-color:#ffc83c;}

    /* ---- Cartes ---- */
    .card{background:linear-gradient(160deg,var(--card),var(--card2));border:1px solid rgba(255,255,255,.22);
        border-radius:18px;padding:1.1rem;margin:.6rem 0;box-shadow:0 8px 24px rgba(15,8,60,.35);transition:.25s;
        color:#f4f2ff;font-size:.92rem;}
    .card:hover{border-color:rgba(255,160,90,.85);box-shadow:0 0 22px rgba(255,122,46,.4);}
    .banner{border-radius:18px;padding:1.2rem;margin:.6rem 0;color:#fff;border:1px solid rgba(255,255,255,.3);}
    .banner h3{margin:0 0 .25rem;font-family:'Orbitron',sans-serif;font-size:1.05rem;}
    .banner p{margin:0;color:#fff;font-weight:300;font-size:.9rem;}
    .b1{background:linear-gradient(120deg,rgba(255,122,46,.9),rgba(255,61,104,.75));}
    .b2{background:linear-gradient(120deg,rgba(0,190,230,.85),rgba(77,141,255,.85));}
    .b3{background:linear-gradient(120deg,rgba(255,61,104,.85),rgba(110,80,255,.85));}

    .section-title{font-family:'Orbitron',sans-serif;font-size:1.35rem;margin:1rem 0 .2rem;
        background:linear-gradient(90deg,#ffb066,var(--cyan));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .section-sub{color:var(--muted);font-size:.9rem;margin-bottom:.6rem;}
    .divider{height:2px;margin:1.2rem 0;border-radius:2px;
        background:linear-gradient(90deg,transparent,var(--orange),var(--cyan),transparent);
        background-size:200% 100%;animation:slide 4s linear infinite;}
    @keyframes slide{0%{background-position:0% 0}100%{background-position:200% 0}}

    /* ---- DJ Mosi à l'honneur ---- */
    .featured{border:2px solid #ffc83c;background:linear-gradient(160deg,#5a35b0,#8a2f9e);
        box-shadow:0 0 30px rgba(255,200,60,.55);}
    .featured .avatar{width:112px;height:112px;border-color:#ffc83c;box-shadow:0 0 22px rgba(255,200,60,.8);}
    .badge-star{display:inline-block;font-size:.72rem;letter-spacing:.14em;font-weight:600;color:#2b1d70;
        background:linear-gradient(90deg,#ffd24d,#ffa11f);border-radius:999px;padding:.2rem .75rem;margin-bottom:.6rem;}

    /* ---- Équipe ---- */
    .member{display:flex;gap:1rem;align-items:flex-start;}
    .avatar{width:92px;height:92px;border-radius:50%;object-fit:cover;flex:none;border:2px solid var(--orange);
        box-shadow:0 0 18px rgba(255,122,46,.7);}
    .avatar-ph{display:flex;align-items:center;justify-content:center;font-family:'Orbitron',sans-serif;
        font-size:2rem;background:linear-gradient(135deg,var(--orange),var(--red));color:#fff;}
    .member h3{margin:0;font-size:1.15rem;}
    .role{color:var(--cyan);font-size:.8rem;margin:.1rem 0 .5rem;}
    .bio{color:#ece9ff;font-weight:300;font-size:.9rem;margin:.4rem 0;}
    .chip{display:inline-block;margin:.15rem .2rem .15rem 0;padding:.15rem .6rem;border-radius:999px;font-size:.75rem;
        border:1px solid #ffb066;color:#ffe2c8;background:rgba(255,122,46,.22);}
    .link-pill{display:inline-block;margin:.25rem .3rem 0 0;padding:.25rem .75rem;border-radius:999px;font-size:.78rem;
        border:1px solid var(--cyan);color:var(--cyan)!important;transition:.2s;}
    .link-pill:hover{background:rgba(39,236,255,.2);box-shadow:0 0 12px rgba(39,236,255,.6);}

    /* ---- Matériel ---- */
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:.7rem;}
    .gear{background:linear-gradient(160deg,var(--card),var(--card2));border:1px solid rgba(255,255,255,.22);
        border-radius:16px;padding:1rem;transition:.25s;}
    .gear:hover{transform:translateY(-4px);border-color:var(--cyan);box-shadow:0 0 22px rgba(39,236,255,.4);}
    .gear .ic{font-size:2rem;}
    .gear h4{margin:.3rem 0;font-size:1rem;color:#fff;}
    .gear p{margin:0 0 .5rem;color:#ece9ff;font-weight:300;font-size:.86rem;}
    .tag{font-size:.7rem;color:var(--cyan);border:1px solid var(--cyan);border-radius:6px;padding:.05rem .4rem;}
    .price{float:right;font-size:.78rem;color:#ffb066;}

    /* ---- Médias, commentaires, livre d'or ---- */
    .media-title{font-weight:600;font-size:1.05rem;}
    .media-cap{color:var(--muted);font-size:.85rem;}
    .ph{display:flex;align-items:center;justify-content:center;flex-direction:column;height:200px;border-radius:16px;
        margin:.4rem 0;background:linear-gradient(135deg,#5a2a8f,#1f5aa0);border:1px dashed rgba(255,255,255,.45);color:#f4f2ff;}
    .bubble{background:rgba(255,255,255,.14);border-left:3px solid var(--cyan);border-radius:12px;padding:.6rem .8rem;margin:.4rem 0;}
    .bubble .who{color:#ffb066;font-weight:600;font-size:.85rem;}
    .bubble .when{color:var(--muted);font-size:.7rem;margin-left:.4rem;}
    .bubble .txt{color:#fff;font-size:.9rem;margin-top:.15rem;word-wrap:break-word;}

    /* ---- Widgets Streamlit ---- */
    .stButton>button,.stFormSubmitButton>button,a[data-testid="stBaseLinkButton-secondary"],
    a[data-testid="stBaseLinkButton-primary"]{
        background:linear-gradient(90deg,var(--orange),var(--red))!important;color:#fff!important;border:none!important;
        border-radius:12px!important;font-weight:600!important;padding:.55rem 1rem!important;transition:.2s!important;}
    .stButton>button:hover,.stFormSubmitButton>button:hover,a[data-testid="stBaseLinkButton-secondary"]:hover,
    a[data-testid="stBaseLinkButton-primary"]:hover{
        box-shadow:0 0 20px rgba(255,100,60,.8)!important;transform:translateY(-2px);}
    .stButton>button:disabled{opacity:.6;background:rgba(255,255,255,.2)!important;}
    .stTextInput input,.stTextArea textarea,.stDateInput input,.stNumberInput input,
    .stSelectbox div[data-baseweb="select"]>div,.stMultiSelect div[data-baseweb="select"]>div{
        background:rgba(255,255,255,.16)!important;color:#fff!important;border:1px solid rgba(255,255,255,.35)!important;
        border-radius:12px!important;}
    div[data-testid="stExpander"]{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.25);border-radius:14px;}
    div[data-testid="stForm"]{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.25);border-radius:16px;}
    .footer{text-align:center;color:var(--muted);font-size:.78rem;margin-top:2rem;}

    /* ---- Mobile ---- */
    @media (max-width:640px){
        .hero-title{font-size:1.75rem;}
        .block-container{padding:.6rem .6rem 4rem;}
        .avatar{width:72px;height:72px;}
        .featured .avatar{width:88px;height:88px;}
        .member{gap:.7rem;}
        .social-btn{font-size:.8rem;}
    }
    </style>
    """)


# ============================================================
# PARTIE 3/6 — Composants communs, page Accueil, page Équipe
# ============================================================
def divider() -> None:
    H('<div class="divider"></div>')


def section_title(title: str, subtitle: str = "") -> None:
    H(f'<div class="section-title">{esc(title)}</div>')
    if subtitle:
        H(f'<div class="section-sub">{esc(subtitle)}</div>')


def brand_bar() -> None:
    """En-tête : logo SVG s'il existe (assets/logo.svg), sinon marque en texte néon."""
    uri = img_uri("assets/logo.svg")
    if uri:
        H(f'<div class="brandbar"><img src="{uri}" alt="{esc(APP_NAME)}" '
          f'style="width:60%;max-width:260px;"></div>')
    else:
        H(f'<div class="brandbar"><div class="pulse"></div><div class="brand">{esc(APP_NAME.upper())}</div>'
          f'<div class="pulse"></div></div>')


def socials_block() -> None:
    buttons = "".join(
        f'<a class="social-btn {cls}" href="{esc(url)}" target="_blank" rel="noopener">{icon} {name}</a>'
        for name, icon, cls, url in SOCIALS
    )
    H(f'<div class="socials">{buttons}</div>')


def avatar_html(m: dict) -> str:
    uri = img_uri(m["photo"])
    if uri:
        return f'<img class="avatar" src="{uri}" alt="{esc(m["name"])}">'
    return f'<div class="avatar avatar-ph">{esc(m["initial"])}</div>'


def featured_spotlight() -> None:
    """Bloc « À l'honneur » (le membre avec "featured": True dans TEAM)."""
    m = next((x for x in TEAM if x.get("featured")), None)
    if not m:
        return
    chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in m["specialties"])
    H(f"""
    <div class="card featured">
        <div class="badge-star">⭐ À L'HONNEUR</div>
        <div class="member">
            {avatar_html(m)}
            <div>
                <h3>{esc(m["name"])} {m["flag"]}</h3>
                <div class="role">{esc(m["country"])} • {esc(m["role"])}</div>
                <div>{chips}</div>
            </div>
        </div>
        <div class="bio">{esc(m["bio"])}</div>
    </div>
    """)
    c1, c2 = st.columns(2)
    c1.link_button(f"💬 Écrire à {m['name']}",
                   wa_link(m["phone"], f"Bonjour {m['name']}, je vous contacte depuis le site {APP_NAME}."),
                   use_container_width=True)
    c2.button("🎛️ Voir son profil", on_click=go_to, args=("🎛️ Équipe",),
              use_container_width=True, key="spot_profile")


# ---------------------------- ACCUEIL ----------------------------
def page_home() -> None:
    H(f"""
    <div class="hero">
        <div class="hero-badge">📍 {esc(CITY.upper())} • ON SE DÉPLACE PARTOUT</div>
        <div class="hero-title">IMPACT<br><span>EVENT</span></div>
        <p class="hero-sub">Le collectif événementiel qui crée l'impact sur vos soirées.<br>
        DJ Mosi • DJ Oxygène • MCs • Sono • Lumières • Effets spéciaux</p>
    </div>
    """)

    featured_spotlight()

    divider()
    section_title("Contactez-nous", "WhatsApp direct, email ou réseaux : un clic suffit")
    socials_block()

    st.button("🧾 Demander un devis gratuit", on_click=go_to, args=("🧾 Devis",),
              use_container_width=True, key="home_cta")

    divider()
    section_title("Qui sommes-nous ?")
    H(f"""
    <div class="card">
        <b>Impact Event</b> est un collectif d'artistes et de prestataires événementiels
        basé à <b>{esc(CITY)}</b>. <b>DJ Mosi 🇨🇬</b>, <b>DJ Oxygène 🇨🇲</b> et nos
        <b>MCs partenaires 🎤</b> travaillent ensemble pour vous offrir une soirée complète :
        musique, animation, sonorisation et effets lumineux.
    </div>
    <div class="card">
        📍 <b>Basés à {esc(CITY)}</b>, nous nous déplaçons <b>partout</b> pour votre événement.
        Dites-nous où et quand, on s'occupe du reste.
    </div>
    """)

    divider()
    section_title("À la une", "Ce que nous faisons pour vous")
    H("""
    <div class="banner b1"><h3>💍 Mariages & Ouvertures de bal</h3>
    <p>Lasers, fumée lourde et étincelles froides pour une entrée mémorable.</p></div>
    <div class="banner b2"><h3>🎂 Anniversaires & Soirées privées</h3>
    <p>Des playlists sur mesure, de la rumba à l'Afrobeat, pour toutes les générations.</p></div>
    <div class="banner b3"><h3>🎤 DJ + MC + Matériel clé en main</h3>
    <p>Un seul collectif pour la musique, l'animation, le son et la lumière.</p></div>
    """)

    divider()
    section_title("Nos univers musicaux")
    chips = "".join(
        f'<span class="chip">{esc(s)}</span>'
        for m in TEAM for s in m["specialties"]
    )
    H(f'<div class="card">{chips}</div>')

    c1, c2 = st.columns(2)
    c1.button("🎛️ Voir l'équipe", on_click=go_to, args=("🎛️ Équipe",),
              use_container_width=True, key="home_team")
    c2.button("📸 Voir la galerie", on_click=go_to, args=("📸 Galerie",),
              use_container_width=True, key="home_gallery")


# ----------------------------- ÉQUIPE ----------------------------
def page_team() -> None:
    section_title("L'équipe", f"Les membres partenaires d'Impact Event • Basés à {CITY}")

    for m in TEAM:
        featured = m.get("featured", False)
        badge = '<div class="badge-star">⭐ À L\'HONNEUR</div>' if featured else ""
        css_class = "card featured" if featured else "card"
        chips = "".join(f'<span class="chip">{esc(s)}</span>' for s in m["specialties"])
        links = "".join(
            f'<a class="link-pill" href="{esc(url)}" target="_blank" rel="noopener">{esc(label)}</a>'
            for label, url in m["links"].items()
        )
        H(f"""
        <div class="{css_class}">{badge}<div class="member">
            {avatar_html(m)}
            <div>
                <h3>{esc(m["name"])} {m["flag"]}</h3>
                <div class="role">{esc(m["country"])} • {esc(m["role"])}</div>
                <div>{chips}</div>
            </div>
        </div>
        <div class="bio">{esc(m["bio"])}</div>
        <div>{links}</div></div>
        """)

    st.button("🧾 Réserver notre équipe", on_click=go_to, args=("🧾 Devis",),
              use_container_width=True, key="team_cta")


# ============================================================
# PARTIE 4/6 — Galerie multimédia (likes, commentaires, partage)
# ============================================================
def render_media(item: dict) -> None:
    """Affiche une photo/vidéo (fichier local ou lien). Visuel de remplacement si absent."""
    src, kind = item["src"], item["type"]
    if src.startswith("http"):
        if kind == "video":
            st.video(src)
        else:
            st.image(src, use_container_width=True)
        return
    path = BASE_DIR / src
    if path.exists():
        if kind == "video":
            st.video(str(path))
        else:
            st.image(str(path), use_container_width=True)
    else:
        icon = "🎬" if kind == "video" else "📷"
        H(f'<div class="ph"><div style="font-size:2.4rem">{icon}</div>'
          f'<div>Ajoutez <b>{esc(src)}</b> dans le dépôt</div></div>')


def render_bubbles(entries: list, limit: int = 8) -> None:
    for e in reversed(entries[-limit:]):
        H(f'<div class="bubble"><span class="who">{esc(e["name"])}</span>'
          f'<span class="when">{esc(e["date"])}</span>'
          f'<div class="txt">{esc(e["msg"])}</div></div>')


def page_gallery() -> None:
    section_title("Prestations & Galerie", "Nos soirées en photos et en vidéos — likez, commentez, partagez !")
    data = load_data()
    liked = st.session_state.setdefault("liked", set())

    for item in GALLERY:
        iid = item["id"]
        likes = data["likes"].get(iid, 0)
        comments = data["comments"].get(iid, [])

        H(f'<div class="card"><div class="media-title">{esc(item["title"])}</div>'
          f'<div class="media-cap">{esc(item["caption"])}</div></div>')
        render_media(item)

        c1, c2 = st.columns(2)
        with c1:
            already = iid in liked
            label = f"❤️ Aimé • {likes}" if already else f"🤍 J'aime • {likes}"
            if st.button(label, key=f"like_{iid}", disabled=already, use_container_width=True):
                add_like(iid)
                liked.add(iid)
                st.rerun()
        with c2:
            st.link_button("🟢 Partager sur WhatsApp", whatsapp_share_url(item["title"]),
                           use_container_width=True)

        with st.expander(f"💬 Commentaires ({len(comments)})"):
            render_bubbles(comments)
            with st.form(f"cform_{iid}", clear_on_submit=True):
                name = st.text_input("Votre prénom", max_chars=30, key=f"cn_{iid}")
                text = st.text_area("Votre commentaire", max_chars=300, height=80, key=f"ct_{iid}")
                if st.form_submit_button("Publier"):
                    if name.strip() and text.strip():
                        add_comment(iid, name.strip(), text.strip())
                        st.rerun()
                    else:
                        st.warning("Merci de renseigner votre prénom et votre commentaire.")
        divider()


# ============================================================
# PARTIE 5/6 — Location de matériel & Livre d'or communautaire
# ============================================================
def page_equipment() -> None:
    section_title("Location de Matériel & Effets Spéciaux",
                  "Un catalogue pro, livré et installé pour votre événement")

    for group in EQUIPMENT:
        H(f'<div class="media-title" style="margin-top:.8rem">{esc(group["category"])}</div>')
        cards = "".join(
            f'<div class="gear"><div class="ic">{it["icon"]}</div>'
            f'<h4>{esc(it["name"])}</h4><p>{esc(it["desc"])}</p>'
            f'<span class="tag">{esc(it["tag"])}</span><span class="price">Sur devis</span></div>'
            for it in group["items"]
        )
        H(f'<div class="grid">{cards}</div>')

    divider()
    H(f'<div class="card">🚚 <b>Livraison, installation et technicien</b> possibles partout '
      f'(basés à {esc(CITY)}). Dites-nous votre lieu et votre date : nous vous répondons rapidement.</div>')
    st.button("🧾 Demander un devis pour ce matériel", on_click=go_to, args=("🧾 Devis",),
              use_container_width=True, key="equip_cta")


def page_guestbook() -> None:
    section_title("Livre d'or & Chat", "Laissez un message, partagez votre projet ou votre ressenti")
    data = load_data()

    with st.form("guestbook_form", clear_on_submit=True):
        name = st.text_input("Votre prénom / pseudo", max_chars=30)
        msg = st.text_area("Votre message", max_chars=400, height=110,
                           placeholder="Merci pour la soirée ! / J'organise un mariage en décembre…")
        if st.form_submit_button("📨 Publier mon message"):
            if name.strip() and msg.strip():
                add_guest_message(name.strip(), msg.strip())
                st.rerun()
            else:
                st.warning("Merci de renseigner votre prénom et votre message.")

    divider()
    messages = data["guestbook"]
    if not messages:
        H('<div class="card">Soyez le premier à laisser un message ! 🎉</div>')
    for e in messages[:50]:
        H(f'<div class="bubble"><span class="who">{esc(e["name"])}</span>'
          f'<span class="when">{esc(e["date"])}</span>'
          f'<div class="txt">{esc(e["msg"])}</div></div>')


# ============================================================
# PARTIE 6/6 — Devis gratuit (WhatsApp + email), pied de page, lancement
# ============================================================
def build_quote_summary(f: dict) -> str:
    services = ", ".join(f["services"]) if f["services"] else "À définir ensemble"
    lines = [
        f"🎧 *DEMANDE DE DEVIS — {APP_NAME}*",
        f"👤 Nom : {f['name']}",
        f"📞 Téléphone : {f['phone']}",
        f"🎉 Événement : {f['event']}",
        f"📅 Date : {f['date'].strftime('%d/%m/%Y')}",
        f"📍 Lieu : {f['place'] or 'À préciser'}",
        f"👥 Invités (approx.) : {f['guests']}",
        f"🔊 Souhaité : {services}",
    ]
    if f.get("email"):
        lines.insert(3, f"✉️ Email : {f['email']}")
    if f["details"]:
        lines.append(f"📝 Détails : {f['details']}")
    return "\n".join(lines)


def page_quote() -> None:
    section_title("Devis Gratuit",
                  f"Basés à {CITY}, nous nous déplaçons partout. Remplissez le formulaire, "
                  "puis envoyez-le par WhatsApp ou par email.")

    with st.form("quote_form"):
        name = st.text_input("Votre nom *", max_chars=60)
        phone = st.text_input("Téléphone / WhatsApp *", max_chars=20, placeholder="+33 6 12 34 56 78")
        email = st.text_input("Votre email (facultatif)", max_chars=80, placeholder="vous@exemple.com")
        event = st.selectbox("Type d'événement *", EVENT_TYPES)
        c1, c2 = st.columns(2)
        ev_date = c1.date_input("Date *", min_value=date.today(), value=date.today())
        guests = c2.number_input("Invités (approx.)", min_value=1, max_value=5000, value=100, step=10)
        place = st.text_input("Lieu / Ville", max_chars=80)
        services = st.multiselect("Prestations & matériel souhaités", SERVICE_OPTIONS)
        details = st.text_area("Précisions (ambiance, horaires, styles musicaux…)", max_chars=400, height=90)
        submitted = st.form_submit_button("✨ Générer mon résumé de devis")

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
        H('<div class="media-title">✅ Votre résumé est prêt : envoyez-le comme vous préférez</div>')
        st.code(summary, language=None)
        st.link_button("🟢 Envoyer sur WhatsApp à DJ Mosi",
                       wa_link(PHONE_MOSI, summary), use_container_width=True)
        st.link_button("🟢 Envoyer sur WhatsApp à DJ Oxygène",
                       wa_link(PHONE_OXYGENE, summary), use_container_width=True)
        st.link_button("✉️ Envoyer par email", mailto_link(summary), use_container_width=True)
        st.caption(f"WhatsApp et email s'ouvrent avec le message déjà rédigé : il ne reste qu'à envoyer. "
                   f"Vous pouvez aussi copier le résumé et l'envoyer à {CONTACT_EMAIL}.")


def footer() -> None:
    divider()
    H(f'<div class="footer">© {date.today().year} {esc(APP_NAME)} • Collectif DJ & événementiel<br>'
      f'📍 Basés à {esc(CITY)} • Déplacements partout<br>'
      f'DJ Mosi 🇨🇬 • DJ Oxygène 🇨🇲 • MCs partenaires 🎤<br>'
      f'Fait avec ❤️ pour mettre le feu à vos soirées</div>')


PAGE_FUNCS = {
    "🏠 Accueil": page_home,
    "🎛️ Équipe": page_team,
    "📸 Galerie": page_gallery,
    "🔊 Matériel": page_equipment,
    "💬 Livre d'or": page_guestbook,
    "🧾 Devis": page_quote,
}


def main() -> None:
    inject_css()
    brand_bar()
    st.session_state.setdefault("page", PAGES[0])
    st.radio("Navigation", PAGES, horizontal=True, key="page", label_visibility="collapsed")
    PAGE_FUNCS[st.session_state.page]()
    footer()


main()
