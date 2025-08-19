# update_checker.py
import os
import subprocess
import requests
from datetime import datetime


def check_for_updates():
    """Vérifie les mises à jour depuis le dépôt Git"""
    try:
        # Récupérer les dernières modifications
        result = subprocess.run(['git', 'fetch'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Erreur lors de la récupération des mises à jour")
            return False

        # Vérifier s'il y a des mises à jour
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            return True
        return False
    except Exception as e:
        print(f"Erreur lors de la vérification des mises à jour: {e}")
        return False


def apply_updates():
    """Applique les mises à jour disponibles"""
    try:
        print("Application des mises à jour...")

        # Sauvegarde de la base de données
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.system(f"python manage.py dumpdata > backups/backup_{timestamp}.json")

        # Mise à jour du code
        result = subprocess.run(['git', 'pull', 'origin', 'main'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Erreur lors de la mise à jour du code")
            return False

        # Mise à jour des dépendances
        os.system("pip install -r requirements.txt")

        # Application des migrations
        os.system("python manage.py migrate")

        # Collecte des fichiers statiques
        os.system("python manage.py collectstatic --noinput")

        print("Mises à jour appliquées avec succès!")
        return True
    except Exception as e:
        print(f"Erreur lors de l'application des mises à jour: {e}")
        return False


if __name__ == "__main__":
    if check_for_updates():
        apply_updates()
    else:
        print("Aucune mise à jour disponible")
