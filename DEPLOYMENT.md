# Déploiement sur Render

## Étapes pour déployer Conseilux English Training sur Render

### 1. Préparer le dépôt GitHub

```bash
# Initialiser git (si pas déjà fait)
git init

# Ajouter tous les fichiers
git add .

# Commit
git commit -m "Mise à jour des informations de contact et préparation pour Render"

# Ajouter le remote GitHub (remplacer par votre URL)
git remote add origin https://github.com/VOTRE-USERNAME/conseilux-efset.git

# Pousser sur GitHub
git push -u origin main
```

### 2. Déployer sur Render

1. Allez sur [render.com](https://render.com) et connectez-vous
2. Cliquez sur "New +" puis "Web Service"
3. Connectez votre dépôt GitHub
4. Sélectionnez le dépôt `conseilux-efset`
5. Configurez le service :
   - **Name**: conseilux-english-training
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (ou payant selon vos besoins)

6. Cliquez sur "Create Web Service"

### 3. Variables d'environnement (optionnel)

Dans les paramètres de votre service Render, vous pouvez ajouter :
- `FLASK_SECRET_KEY`: Une clé secrète pour Flask (générée automatiquement par render.yaml)

### 4. Accéder à votre application

Une fois déployée, votre application sera accessible à :
`https://conseilux-english-training.onrender.com`

## Fichiers de configuration

- `render.yaml`: Configuration automatique pour Render
- `requirements.txt`: Dépendances Python (inclut gunicorn)
- `app.py`: Application Flask configurée pour la production

## Notes importantes

- Le déploiement gratuit sur Render peut prendre quelques minutes au premier lancement
- L'application se met en veille après 15 minutes d'inactivité (plan gratuit)
- Pour un service 24/7, considérez un plan payant

## Support

Pour toute question : contact@conseiluxtraining.com
