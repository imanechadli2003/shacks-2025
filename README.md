# Sneak Snap

Une application autonome (Executable) en Python pour l'enregistrement et la surveillance des interactions PC.

## 📌 À Propos du Projet

Sneak Snap est une application développée en Python et distribuée sous forme d'exécutable autonome. L'objectif est de fournir un outil prêt à l'emploi, ne nécessitant aucune installation de dépendances Python, pour enregistrer et gérer diverses interactions sur un ordinateur de manière discrète et efficace.

Ce projet permet de capturer des informations sur l'activité d'un PC, que ce soit pour l'analyse de productivité, la surveillance ou l'archivage.

## ✨ Fonctionnalités Principales

- **Exécutable Autonome** : Lancement simple et direct de l'application sans nécessiter d'installation Python ni de ligne de commande.
- **Enregistrement des Frappes (Keystrokes)** : Capture et sauvegarde toutes les frappes clavier dans un journal sécurisé.
- **Capture des Entrées Souris** : Enregistre les clics de souris ainsi que les coordonnées de ses mouvements pour un suivi complet de l'activité.
- **Suivi des Applications** : Garde un historique des applications ouvertes et du temps passé sur la fenêtre active.
- **Captures d'Écran Automatisées** : Prenez des captures d'écran à intervalles réguliers.
- **Gestion des Données** : Sauvegardez automatiquement les journaux et les 'snaps' localement dans des répertoires organisés avec des noms de fichiers personnalisables.

## 🛠️ Stack Technique

- **Langage Principal** : Python 3.10+
- **Empaquetage** : PyInstaller
- **Bibliothèques Clés** : pynput, keyboard, Pillow, psutil, PyAutoGUI, requests

## 🚀 Démarrage Rapide (Utilisation de l'Exécutable)

Cette méthode ne nécessite aucune connaissance de Python.

1. **Télécharger l'Exécutable**  
Rendez-vous sur la page des "Releases" du dépôt GitHub et téléchargez la dernière version de l'exécutable compressé (par exemple, un fichier `.zip`).

2. **Lancer l'Application**  
Décompressez le fichier téléchargé et exécutez directement le fichier binaire :

- Windows : `SneakSnap.exe`
- macOS/Linux : `./SneakSnap` (après avoir donné les permissions d'exécution)

L'application commencera le monitoring ou affichera une interface selon sa configuration.

## 💻 Démarrage Rapide (Installation Locale pour le Développement)

Si vous souhaitez modifier le code source :

1. **Prérequis**  
- Python (version 3.10 ou plus récente)  
- pip (le gestionnaire de paquets Python)  
- Git

2. **Cloner le Dépôt**  
```bash
git clone https://github.com/LoukaG/shacks-2025.git
cd shacks-2025
