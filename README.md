# Wantashi - Système de Gestion Scolaire

Wantashi est une application de gestion scolaire complète développée avec Django. Cette application permet de gérer les élèves, les paiements, les classes et générer des rapports.

## Fonctionnalités principales

- Gestion des utilisateurs et des rôles
- Enregistrement et suivi des élèves
- Gestion des paiements et des frais scolaires
- Suivi des classes et des sections
- Génération de rapports et de statistiques
- Interface administrateur pour la gestion du système

## Technologies utilisées

- **Backend** : Python, Django
- **Frontend** : HTML, CSS (Bootstrap, Argon Dashboard), JavaScript
- **Base de données** : SQLite (développement), extensible vers PostgreSQL ou MySQL
- **Déploiement** : Waitress (serveur WSGI)

## Installation

### Prérequis

- Python 3.13.6 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. Cloner le dépôt :
   git clone <url_du_dépôt> 
   cd wantashi
2. Créer un environnement virtuel :
    bash python -m venv venv 
    source venv/bin/activate # Sur Windows: venv\Scripts\activate
3. Installer les dépendances :
    bash pip install -r requirements.txt
4. Appliquer les migrations :
   python manage.py migrate

5. Créer un superutilisateur :
   python manage.py createsuperuser

6. Lancer le serveur de développement :
    python manage.py runserver
    pip install waitress python manage.py collectstatic waitress-serve --host=0.0.0.0 --port=8000 waitress_wsgi:application

## Configuration

Avant de lancer l'application, configurez les paramètres dans `wantashi/settings.py` :
- Base de données
- Clé secrète (SECRET_KEY)
- Paramètres de messagerie (EMAIL_*)
- Paramètres spécifiques à l'environnement

## Contributeurs

- Jonas Kasongo - Ingénieur en Télécommunications et Réseaux

## Contact

- Email : jonaskasongo7@gmail.com
- Téléphone : +243970338991

## Licence

Ce projet est sous licence Proprietaire - voir le fichier [LICENSE.md](LICENSE.md) pour plus de détails.

# SECURITY WARNING: keep the secret key used in production secret!
# Note: En production, utilisez une variable d'environnement
# SECRET_KEY = os.environ.get('SECRET_KEY', 'votre-clé-secrète-ici')
SECRET_KEY = 'django-insecure-hv-efhi9*wfnoe=(rh6x$1hrq46#+lpvltf$4*wz$@!gr@h!pf'

# SECURITY WARNING: don't run with debug turned on in production!
# Note: En production, désactivez le DEBUG
# DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
DEBUG = True

# Note: En production, spécifiez les hôtes autorisés
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

Django>=5.1
waitress>=2.1.0

# Ajouter tous les fichiers au suivi Git
git add .

# Vérifier l'état du dépôt
git status

# Faire le commit initial
git commit -m "Initial commit: Projet Wantashi - Système de gestion scolaire complet

- Application Django complète avec gestion des élèves, paiements et classes
- Interface utilisateur avec Argon Dashboard
- Configuration de déploiement avec Waitress
- Documentation complète dans README.md
- Fichiers de configuration et dépendances inclus"

# Vérifier l'historique des commits
git log --oneline

   