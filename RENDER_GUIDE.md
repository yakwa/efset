# 🚀 Guide de Déploiement Rapide sur Render

## ✅ Code déjà sur GitHub
Votre code est maintenant sur: https://github.com/yakwa/efset

## 📋 Étapes pour déployer sur Render

### 1. Créer un compte Render
- Allez sur https://render.com
- Cliquez sur "Get Started" ou "Sign Up"
- Connectez-vous avec votre compte GitHub

### 2. Créer un nouveau Web Service
1. Une fois connecté, cliquez sur **"New +"** en haut à droite
2. Sélectionnez **"Web Service"**

### 3. Connecter votre dépôt
1. Render va vous demander d'autoriser l'accès à GitHub
2. Cherchez et sélectionnez le dépôt **"yakwa/efset"**
3. Cliquez sur **"Connect"**

### 4. Configurer le service
Remplissez les champs suivants:

- **Name**: `conseilux-english-training` (ou le nom de votre choix)
- **Region**: Choisissez la région la plus proche (ex: Frankfurt pour l'Europe)
- **Branch**: `main`
- **Root Directory**: Laissez vide
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

### 5. Choisir le plan
- **Instance Type**: Sélectionnez **"Free"** pour commencer
  - ⚠️ Note: Le plan gratuit met l'app en veille après 15 min d'inactivité
  - Pour un service 24/7, choisissez un plan payant

### 6. Variables d'environnement (optionnel)
Render va automatiquement générer `FLASK_SECRET_KEY` grâce au fichier `render.yaml`

### 7. Déployer
1. Cliquez sur **"Create Web Service"**
2. Render va commencer à construire et déployer votre application
3. Attendez 2-5 minutes pour le premier déploiement

### 8. Accéder à votre application
Une fois le déploiement terminé, votre application sera accessible à:
```
https://conseilux-english-training.onrender.com
```
(ou le nom que vous avez choisi)

## 🔄 Mises à jour automatiques
Chaque fois que vous poussez du code sur GitHub (branch main), Render redéploiera automatiquement votre application!

## 📞 Informations de contact mises à jour
✅ Email: contact@conseiluxtraining.com
✅ Siège: 50, rue du pont tinel, Le Havre, France
✅ Téléphones: France, Bénin, Côte d'Ivoire, Togo, Niger

## 🎯 Fonctionnalités déployées
- ✅ Site en plein écran
- ✅ Navigation dans le footer
- ✅ Logo Conseilux mis à jour
- ✅ Listening en audio uniquement (pas de texte)
- ✅ Certificat disponible uniquement pour score >= 18/20
- ✅ Lien LinkedIn de Daven BANKA dans le footer

## 🆘 Besoin d'aide?
Contact: contact@conseiluxtraining.com
