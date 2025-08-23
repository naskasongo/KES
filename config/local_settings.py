# local_settings.py
# Configuration spécifique à l'environnement local

# Adresse IP statique du serveur
SERVER_IP = '192.168.54.95'

# Configuration HTTPS pour le développement local
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Configuration du port
SERVER_PORT = 8300

# Configuration de la base de données PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'schooldb',
        'USER': 'postgres',  # Vérifiez que c'est bien 'postgres' et non 'podgre'
        'PASSWORD': 'Nas08@kas05',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}