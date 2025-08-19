# local_settings.py
RUNSERVER_DEFAULT_ADDR = '0.0.0.0'
RUNSERVER_DEFAULT_PORT = '8380'
# config/local_settings.py
# Configuration spécifique à l'environnement local

# Adresse IP statique du serveur
SERVER_IP = '192.168.66.95'

# Configuration HTTPS pour le développement local
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Configuration du port (si différent de 8000)
SERVER_PORT = 8300

# Configuration de la base de données pour le développement
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}
