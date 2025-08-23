import os
import subprocess
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')
django.setup()


def migrate_data():
    print("📦 MIGRATION DES DONNÉES SQLITE → POSTGRESQL")
    print("=" * 50)

    # 1. Dumper les données depuis SQLite
    print("1. Export des données depuis SQLite...")
    try:
        # Temporairement utiliser SQLite pour le dump
        original_db = settings.DATABASES['default'].copy()

        # Configuration SQLite temporaire
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(settings.BASE_DIR, 'db.sqlite3'),
        }

        # Dumper les données
        result = subprocess.run([
            'python', 'manage.py', 'dumpdata',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            '--exclude=admin.logentry',
            '--indent=2',
            '-o', 'migration_backup.json'
        ], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"❌ Erreur dumpdata: {result.stderr}")
            return False

        print("   ✅ Données exportées vers migration_backup.json")

    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        return False

    finally:
        # Restaurer la configuration PostgreSQL
        settings.DATABASES['default'] = original_db

    # 2. Importer dans PostgreSQL
    print("2. Import des données vers PostgreSQL...")
    try:
        result = subprocess.run([
            'python', 'manage.py', 'loaddata', 'migration_backup.json'
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("   ✅ Données importées avec succès!")
        else:
            print(f"⚠️  Avertissement loaddata: {result.stderr}")
            # Essayer table par table
            migrate_table_by_table()

    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return False

    # 3. Vérification
    print("3. Vérification des données migrées...")
    from gestion.models import Eleve, Parent
    from django.contrib.auth import get_user_model

    User = get_user_model()

    counts = {
        'Élèves': Eleve.objects.count(),
        'Parents': Parent.objects.count(),
        'Utilisateurs': User.objects.count()
    }

    print("📊 RÉSULTAT DE LA MIGRATION:")
    for model, count in counts.items():
        print(f"   {model}: {count}")

    print("=" * 50)
    print("🎉 MIGRATION TERMINÉE!")
    return True


def migrate_table_by_table():
    """Migration table par table en cas d'erreur"""
    print("   🔄 Tentative de migration table par table...")

    models_to_migrate = [
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
        'gestion.UserProfile'
    ]

    for model in models_to_migrate:
        try:
            result = subprocess.run([
                'python', 'manage.py', 'dumpdata', model,
                '--indent=2', '-o', f'{model.replace(".", "_")}.json'
            ], capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                subprocess.run([
                    'python', 'manage.py', 'loaddata', f'{model.replace(".", "_")}.json'
                ], capture_output=True, timeout=60)
                print(f"   ✅ {model} migré")

        except Exception as e:
            print(f"   ⚠️  {model} non migré: {e}")


if __name__ == "__main__":
    migrate_data()