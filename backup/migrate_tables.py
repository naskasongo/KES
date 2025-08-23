import os
import subprocess
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')
django.setup()


def migrate_tables_individually():
    """Migrer chaque table individuellement avec encodage correct"""

    tables = [
        'gestion.Parent',
        'gestion.AnneeScolaire',
        'gestion.Section',
        'gestion.Option',
        'gestion.Classe',
        'gestion.CustomUser',
        'gestion.Eleve',
        'gestion.Frais',
        'gestion.Paiement',
        'gestion.Depense',
        'gestion.Inscription',
        'gestion.HistoriqueAction',
        'gestion.Notification',
        'gestion.UserProfile',
        'auth.Group',
        'auth.Permission'
    ]

    print("📦 MIGRATION TABLE PAR TABLE")
    print("=" * 50)

    # Configuration temporaire SQLite
    original_db = settings.DATABASES['default'].copy()
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
    }

    try:
        for table in tables:
            print(f"🔄 Migration de {table}...")

            # Dumper depuis SQLite
            result = subprocess.run([
                'python', 'manage.py', 'dumpdata', table,
                '--indent=2', '-o', f'{table.replace(".", "_")}.json'
            ], capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"   ⚠️  Erreur dump: {result.stderr}")
                continue

            print(f"   ✅ Exporté: {table}")

    finally:
        # Restaurer PostgreSQL
        settings.DATABASES['default'] = original_db

    # Maintenant importer dans PostgreSQL
    for table in tables:
        json_file = f'{table.replace(".", "_")}.json'
        if os.path.exists(json_file):
            try:
                result = subprocess.run([
                    'python', 'manage.py', 'loaddata', json_file
                ], capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    print(f"   ✅ Importé: {table}")
                else:
                    print(f"   ❌ Erreur import {table}: {result.stderr}")

            except Exception as e:
                print(f"   ⚠️  Exception {table}: {e}")

    # Vérification finale
    from gestion.models import Eleve, Parent
    from django.contrib.auth import get_user_model

    User = get_user_model()
    print("=" * 50)
    print("📊 RÉSULTAT FINAL:")
    print(f"   Élèves: {Eleve.objects.count()}")
    print(f"   Parents: {Parent.objects.count()}")
    print(f"   Utilisateurs: {User.objects.count()}")


if __name__ == "__main__":
    migrate_tables_individually()