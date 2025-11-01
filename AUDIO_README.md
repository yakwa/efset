# 🎧 Guide pour ajouter des fichiers audio

## Emplacement des fichiers audio
Placez vos fichiers audio dans le dossier : `static/audio/`

## Fichiers requis
Selon `data/questions.json`, vous devez créer ces fichiers :
- audio1.mp3
- audio2.mp3
- audio3.mp3
- audio4.mp3
- audio5.mp3
- audio6.mp3
- audio7.mp3
- audio8.mp3
- audio9.mp3
- audio10.mp3

## Format recommandé
- **Format** : MP3 (recommandé pour la compatibilité)
- **Qualité** : 128 kbps ou plus
- **Durée** : 10-30 secondes par audio
- **Taille** : Moins de 1 MB par fichier

## Comment créer des fichiers audio

### Option 1 : Enregistrement vocal
1. Utilisez l'enregistreur vocal de Windows ou votre smartphone
2. Lisez le texte correspondant à chaque question
3. Exportez en format MP3
4. Renommez le fichier (ex: audio1.mp3)
5. Placez-le dans `static/audio/`

### Option 2 : Text-to-Speech (TTS)
Utilisez des services en ligne gratuits :
- **Google Text-to-Speech** : https://cloud.google.com/text-to-speech
- **Natural Readers** : https://www.naturalreaders.com
- **TTSMaker** : https://ttsmaker.com

### Option 3 : IA vocale
- **ElevenLabs** : https://elevenlabs.io (voix très naturelles)
- **Play.ht** : https://play.ht
- **Murf.ai** : https://murf.ai

## Exemples de textes pour les audios

**audio1.mp3** : "I am reading a book in the library. It's very quiet here."

**audio2.mp3** : "Welcome to the city library. Please keep your voice down."

**audio3.mp3** : "I'm so happy today! The weather is beautiful and I'm going to the park."

**audio4.mp3** : "I brought my book with me. I love reading in the afternoon."

**audio5.mp3** : "Excuse me, can you tell me how to get to the train station?"

**audio6.mp3** : "Let's meet on Friday evening at 7 PM."

**audio7.mp3** : "I'm going to play tennis this afternoon. Do you want to join me?"

**audio8.mp3** : "Attention passengers, the train to Paris is delayed by 30 minutes."

**audio9.mp3** : "The meeting is scheduled for 2 PM in the conference room."

**audio10.mp3** : "The museum is open from 10 AM to 6 PM every day."

## Vérification
Une fois les fichiers ajoutés, redémarrez le serveur Flask et testez la section Listening.

## Note
En attendant d'avoir les vrais fichiers audio, le système affiche un placeholder élégant avec un bouton de simulation.
