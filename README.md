# Audio Cutter Java

Application Java simple pour découper un fichier audio en plusieurs morceaux de durée fixe avec FFmpeg.

## Fonctionnement
- Tu donnes le chemin du fichier audio
- Tu choisis une durée : 10, 15, 30 secondes ou autre
- L'application découpe automatiquement
- Les fichiers sont nommés :
  - nom_001
  - nom_002
  - nom_003

## Important
FFmpeg doit être installé sur l'appareil ou le PC.

## Lancer
Compiler :
javac AudioCutter.java

Exécuter :
java AudioCutter
