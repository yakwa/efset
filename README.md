# EF SET - Démo (Flask)

## Installation
1. Créez un environnement virtuel et activez-le
```
python -m venv .venv
.\.venv\Scripts\activate
```
2. Installez les dépendances
```
pip install -r requirements.txt
```

## Lancement
```
set FLASK_SECRET_KEY=change-me
python app.py
```
Ouvrez http://localhost:5000

## Données
- Les questions sont dans `data/questions.json`.
- 10 Reading + 10 Listening.
- Pour Listening, placez vos fichiers audio dans `static/audio/` et mettez à jour les noms `audioX.mp3`.

## Certificat PDF
- Généré via ReportLab avec QR code (page `/verify/<code>`)
- Le registre de vérification est en mémoire (disparaît au redémarrage). Pour la prod, utilisez une base de données.

## Limitations
- Les fichiers audio d'exemple ne sont pas fournis. Ajoutez vos mp3.
- Le QR code pointe vers l'URL de vérification locale.
