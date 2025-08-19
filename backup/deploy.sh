#!/bin/bash
# deploy.sh

echo "Début de la mise à jour de l'application..."

# Sauvegarde de la base de données (si nécessaire)
echo "Sauvegarde de la base de données..."
python manage.py dumpdata > backups/backup_$(date +%Y%m%d_%H%M%S).json

# Récupération des dernières modifications
echo "Récupération des dernières modifications..."
git pull origin main

# Mise à jour des dépendances
echo "Mise à jour des dépendances..."
pip install -r requirements.txt

# Application des migrations
echo "Application des migrations..."
python manage.py migrate

# Collecte des fichiers statiques
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Redémarrage du serveur
echo "Redémarrage du serveur..."
pkill -f runserver
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &

echo "Mise à jour terminée avec succès!"
