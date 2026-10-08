# 🎧 Dj Oxygène237 — Espace Prestations & Live

Application web Streamlit personnelle : profil de l'artiste, galerie de prestations vidéo
(TikTok / YouTube / Facebook) et annonces de lives.

## 📁 Structure du dépôt GitHub

```
dj-oxygene237/
├── app.py                 ← l'application
├── requirements.txt       ← les dépendances
├── README.md              ← ce guide
├── .streamlit/
│   └── config.toml        ← thème (fichier "config.toml" à placer dans le dossier .streamlit)
└── assets/
    └── dj_oxygene237.jpg  ← ta photo de profil (facultatif)
```

> Sur GitHub (téléphone ou ordinateur) : *Add file → Create new file*, puis tape dans le nom
> `.streamlit/config.toml` : le dossier se crée tout seul. Même principe pour `assets/dj_oxygene237.jpg`
> (*Add file → Upload files* après avoir créé le dossier).

## ⚙️ Personnalisation (en haut de `app.py`, PARTIE 1)

- `PHONE_DISPLAY` / `PHONE_INTL` : numéro de contact et WhatsApp
- `TIKTOK_URL` : ton profil TikTok
- `PRESTATIONS_FIXES` / `LIVES_FIXES` : vidéos et lives toujours affichés (jamais perdus)

## 🔐 Mot de passe de gestion (obligatoire pour publier)

Les formulaires d'ajout et les boutons « Supprimer » sont réservés à Dj Oxygène237.

- **Streamlit Cloud** : ton app → *Settings → Secrets* → ajoute :
  ```
  ADMIN_PASSWORD = "ton-mot-de-passe"
  ```
- **En local** : crée `.streamlit/secrets.toml` avec la même ligne.

Ne mets jamais le mot de passe dans le code ou sur GitHub.
Ensuite, ouvre **🔐 Espace gestion** en bas de la page et connecte-toi.

## 💻 Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🚀 Déploiement gratuit (GitHub + Streamlit Community Cloud)

1. Crée un dépôt GitHub (ex. `dj-oxygene237`) et ajoute les fichiers ci-dessus.
2. Va sur [share.streamlit.io](https://share.streamlit.io) et connecte-toi avec GitHub.
3. *Create app* → choisis ton dépôt, la branche `main` et le fichier `app.py` → *Deploy*.
4. Ajoute `ADMIN_PASSWORD` dans *Settings → Secrets* (voir plus haut).

## ⚠️ Données et sauvegarde

Les vidéos et annonces ajoutées via les formulaires sont stockées dans `data/oxygene237.json`.
Sur Streamlit Cloud, ce disque est **temporaire** : elles sont perdues au redémarrage de l'app.

- Télécharge régulièrement la **sauvegarde** dans l'Espace gestion (et restaure-la si besoin).
- Mets tes contenus importants dans `PRESTATIONS_FIXES` / `LIVES_FIXES` : ils sont dans le code.

## 🎬 Liens vidéo acceptés

- **YouTube** : liens `youtube.com/watch?v=…`, `youtu.be/…`, `/shorts/…`
- **TikTok** : lien complet `tiktok.com/@dj.oxygene237/video/…` (les liens courts `vm.tiktok.com` ne s'intègrent pas)
- **Facebook** : lien d'une vidéo publique
- **Fichier direct** : lien finissant par `.mp4`, `.webm`, `.mov`…

Les lives TikTok ne peuvent pas être intégrés dans la page : ils sont annoncés avec un bouton qui ouvre TikTok.
