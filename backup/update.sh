#!/bin/bash
# update.sh

APP_NAME="school_app"
INSTALL_DIR="/opt/$APP_NAME"
USER="school_user"

echo "Mise à jour de $APP_NAME..."

# Sauvegarde
timestamp=$(date +%Y%m%d_%H%M%S)
sudo -u $USER python $INSTALL_DIR/manage.py dumpdata > /tmp/backup_$timestamp.json

# Arrêt du service
sudo systemctl stop school_app

# Mise à jour des fichiers
sudo cp -r app/* $INSTALL_DIR/
sudo chown -R $USER:$USER $INSTALL_DIR

# Mise à jour des dépendances
cd $INSTALL_DIR
sudo -u $USER pip install -r requirements.txt

# Application des migrations
sudo -u $USER python $INSTALL_DIR/manage.py migrate

# Collecte des fichiers statiques
sudo -u $USER python $INSTALL_DIR/manage.py collectstatic --noinput

# Redémarrage du service
sudo systemctl start school_app

echo "Mise à jour terminée!"
