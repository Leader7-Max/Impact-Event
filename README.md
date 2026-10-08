# 🎧 Dj Oxygène237 — Espace Prestations & Live

Application web Streamlit personnelle : profil et biographie, galerie de prestations vidéo
(TikTok / YouTube / Facebook), annonces de lives, liste du matériel et demande de devis gratuit.

## 📁 Structure du dépôt GitHub

```
dj-oxygene237/
├── app.py                 ← l'application
├── requirements.txt       ← les dépendances
├── README.md              ← ce guide
├── .streamlit/
│   └── config.toml        ← thème (le fichier "config.toml" va dans le dossier .streamlit)
└── assets/
    └── dj_oxygene237.jpg  ← photo de profil permanente (facultatif)
```

> Sur GitHub (téléphone ou ordinateur) : *Add file → Create new file*, puis tape dans le nom
> `.streamlit/config.toml` : le dossier se crée tout seul, puis colle le contenu du fichier.
> Le fichier `config.toml` donne son thème sombre à l'application : ne l'oublie pas.

## ⚙️ Personnalisation (en haut de `app.py`, PARTIE 1)

- `CONTACT_EMAIL` : **ton adresse email** (le bouton « Envoyer par email » du devis n'apparaît que si elle est renseignée)
- `PHONE_DISPLAY` / `PHONE_INTL` : numéro de contact et WhatsApp
- `TIKTOK_URL` : ton profil TikTok
- `BIO_PARAGRAPHS` : ta biographie (`**mot**` = en gras)
- `EQUIPMENT` : liste du matériel (quantité, désignation, caractéristique) et `VEHICLE_TEXT`
- `PRESTATIONS_FIXES` / `LIVES_FIXES` : vidéos et lives toujours affichés (jamais perdus)

## 📸 Photo de profil

Deux façons :
1. **Depuis l'application** : Espace gestion (bas de page) → *Photo de profil* → choisir une image → *Enregistrer*.
   La photo est recadrée en carré automatiquement.
2. **Photo permanente** : ajoute `assets/dj_oxygene237.jpg` dans le dépôt GitHub.
   Elle est utilisée quand aucune photo n'a été envoyée depuis l'application.

> Sur Streamlit Cloud, une photo envoyée depuis l'application disparaît au redémarrage :
> elle est incluse dans la **sauvegarde** téléchargeable (restaurable), ou mets-la dans `assets/`.

## 🔐 Mot de passe de gestion (obligatoire pour publier)

Les formulaires d'ajout, la photo et les boutons « Supprimer » sont réservés à Dj Oxygène237.

- **Streamlit Cloud** : ton app → *Settings → Secrets* → ajoute :
  ```
  ADMIN_PASSWORD = "ton-mot-de-passe"
  ```
- **En local** : crée `.streamlit/secrets.toml` avec la même ligne.

Ne mets jamais le mot de passe dans le code ou sur GitHub.
Ensuite, ouvre **🔐 Espace gestion** en bas de la page et connecte-toi.

## 🧾 Devis gratuit

Le visiteur remplit le formulaire (nom, téléphone, événement, date, lieu, prestations souhaitées…)
et obtient un résumé prêt à envoyer sur **WhatsApp** (+33 7 73 61 68 84) ou **par email**.

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
