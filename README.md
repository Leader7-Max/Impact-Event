# 🎧 Impact Event

Application web mobile-friendly (Streamlit) du collectif **Impact Event**, basé à **Grenoble**
(déplacements partout) : **DJ Mosi 🇨🇬 (à l'honneur) • DJ Oxygène 🇨🇲 • Espace MCs 🎤**.
Accueil, équipe, galerie (likes / commentaires / partage WhatsApp), location de matériel,
livre d'or et devis gratuit à envoyer par **WhatsApp ou par email**.

## 📁 Structure du projet

```
impact-event/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/config.toml
├── assets/
│   ├── logo.svg   → logo Impact Event
│   ├── team/      → dj_mosi.jpg, dj_oxygene.jpg, mcs.jpg  (photos carrées, ~600x600 px)
│   └── gallery/   → soiree_01.jpg, soiree_02.jpg, video_01.mp4
└── data/          → créé automatiquement (likes, commentaires, livre d'or)
```

Si une photo, une vidéo ou le logo est absent, l'application affiche un visuel de remplacement.

## ⚙️ Personnalisation (en haut de `app.py`)

- `CONTACT_EMAIL` : **ton adresse email** (à remplacer, c'est elle qui reçoit les devis par email)
- `PHONE_MOSI` / `PHONE_OXYGENE` : numéros WhatsApp (format international sans `+`)
- `CITY` : ville de base (Grenoble)
- `SOCIALS` : liens TikTok / YouTube / Facebook
- `TEAM`, `EQUIPMENT`, `GALLERY` : textes, photos, matériel, médias
- Mettre un autre membre à l'honneur : déplace `"featured": True` dans `TEAM`

## 💻 Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🚀 Déploiement gratuit (GitHub + Streamlit Community Cloud)

1. Crée un compte sur [github.com](https://github.com) puis un **nouveau dépôt** (ex. `impact-event`).
2. Envoie tous les fichiers du projet (*Add file → Upload files*).
3. Va sur [share.streamlit.io](https://share.streamlit.io) et connecte-toi avec GitHub.
4. Clique sur **Create app** → choisis ton dépôt, la branche `main` et le fichier `app.py`.
5. Clique sur **Deploy**.
6. Copie l'URL obtenue dans `APP_URL` (dans `app.py`).

## ⚠️ Persistance des données

Sur Streamlit Community Cloud, le disque est **temporaire** : les likes, commentaires
et messages du livre d'or sont **effacés** à chaque redémarrage de l'application.
Pour une sauvegarde durable, branche Supabase, Firebase ou Google Sheets en remplaçant
`load_data()` / `save_data()` dans `app.py`.
