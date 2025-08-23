import os
import json
import django
from django.conf import settings
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')
django.setup()


def controlled_migration():
    print("🎯 MIGRATION CONTRÔLÉE MANUELLE")
    print("=" * 60)

    # 1. Vérifier la connexion PostgreSQL
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables")
            table_count = cursor.fetchone()[0]
        print(f"✅ PostgreSQL connecté ({table_count} tables)")
    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        return False

    # 2. Importer les données table par table avec gestion d'erreurs
    tables_to_import = [
        'gestion_parent', 'gestion_anneescolaire', 'gestion_section',
        'gestion_option', 'gestion_classe', 'gestion_customuser',
        'gestion_eleve', 'gestion_frais', 'gestion_paiement',
        'gestion_depense', 'gestion_inscription', 'gestion_notification',
        'gestion_userprofile', 'auth_group'
    ]

    imported_count = 0
    for table_file in tables_to_import:
        json_file = f"{table_file}.json"

        if os.path.exists(json_file):
            print(f"🔄 Import de {json_file}...")

            try:
                # Lire et nettoyer le JSON
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Nettoyer les caractères problématiques
                cleaned_content = content.encode('utf-8', 'ignore').decode('utf-8')

                # Réécrire le fichier nettoyé
                with open(f"cleaned_{json_file}", 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)

                # Importer
                result = os.system(f'python manage.py loaddata cleaned_{json_file}')

                if result == 0:
                    print(f"   ✅ {json_file} importé")
                    imported_count += 1
                else:
                    print(f"   ⚠️  {json_file} erreur à l'import")

            except Exception as e:
                print(f"   ❌ {json_file} erreur: {e}")

    # 3. Créer les données manquantes si nécessaire
    if imported_count == 0:
        print("📝 Création des données de base manuellement...")
        create_base_data()

    # 4. Vérification finale
    verify_data()

    print("=" * 60)
    print(f"🎉 Migration terminée: {imported_count} tables importées")
    return True


def create_base_data():
    """Créer les données de base manuellement"""
    from gestion.models import Section, AnneeScolaire, CustomUser

    # Créer les sections de base
    sections = ['Maternelle', 'Primaire', 'Secondaire', 'ITM', 'Humanités']
    for section in sections:
        Section.objects.get_or_create(nom=section)
        print(f"   ✅ Section créée: {section}")

    # Créer l'année scolaire actuelle
    annee = AnneeScolaire.obtenir_annee_courante()
    print(f"   ✅ Année scolaire: {annee}")

    # Créer un superutilisateur si aucun n'existe
    if not CustomUser.objects.exists():
        user = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        print("   ✅ Superutilisateur créé: admin/admin123")


def verify_data():
    """Vérifier les données migrées"""
    from gestion.models import Eleve, Parent, Section
    from django.contrib.auth import get_user_model

    User = get_user_model()

    print("📊 VÉRIFICATION DES DONNÉES:")
    print(f"   Sections: {Section.objects.count()}")
    print(f"   Élèves: {Eleve.objects.count()}")
    print(f"   Parents: {Parent.objects.count()}")
    print(f"   Utilisateurs: {User.objects.count()}")

    # Afficher quelques données
    if Section.objects.exists():
        print(f"   Exemple section: {Section.objects.first().nom}")


if __name__ == "__main__":
    controlled_migration()