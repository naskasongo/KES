#!/usr/bin/env python
"""
Robust data migration from SQLite to PostgreSQL - Final fixed version
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')
django.setup()

from django.db import transaction
import sqlite3


def migrate_data():
    print("Starting robust data migration from SQLite to PostgreSQL...")

    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('wantashi/db.sqlite3')
    sqlite_cursor = sqlite_conn.cursor()

    try:
        # Migrate in the correct order to handle foreign key dependencies
        migrate_sections(sqlite_cursor)
        migrate_options(sqlite_cursor)
        migrate_classes(sqlite_cursor)
        migrate_parents(sqlite_cursor)
        migrate_annee_scolaires(sqlite_cursor)
        migrate_users(sqlite_cursor)
        migrate_eleves(sqlite_cursor)
        migrate_frais(sqlite_cursor)
        migrate_paiements(sqlite_cursor)
        migrate_inscriptions(sqlite_cursor)
        migrate_depenses(sqlite_cursor)

        print("Data migration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        sqlite_conn.close()


def migrate_sections(sqlite_cursor):
    """Migrate sections"""
    try:
        sqlite_cursor.execute("SELECT id, nom FROM gestion_section")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No sections to migrate")
            return

        from gestion.models import Section
        count = 0
        for row in rows:
            id, nom = row
            # Map section names to types
            if 'Maternelle' in nom:
                type_section = 'maternelle'
            elif 'Primaire' in nom:
                type_section = 'primaire'
            elif 'Secondaire' in nom or 'Humanit' in nom:
                type_section = 'secondaire'
            elif 'ITM' in nom:
                type_section = 'itm'
            else:
                type_section = 'itm'  # default

            Section.objects.get_or_create(
                id=id,
                defaults={
                    'nom': nom,
                    'type_section': type_section
                }
            )
            count += 1

        print(f"Migrated {count} sections")

    except Exception as e:
        print(f"Error migrating sections: {e}")


def migrate_options(sqlite_cursor):
    """Migrate options"""
    try:
        sqlite_cursor.execute("SELECT id, nom, section_id FROM gestion_option")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No options to migrate")
            return

        from gestion.models import Option
        count = 0
        for row in rows:
            id, nom, section_id = row

            Option.objects.get_or_create(
                id=id,
                defaults={
                    'nom': nom,
                    'section_id': section_id
                }
            )
            count += 1

        print(f"Migrated {count} options")

    except Exception as e:
        print(f"Error migrating options: {e}")


def migrate_classes(sqlite_cursor):
    """Migrate classes"""
    try:
        sqlite_cursor.execute("SELECT id, nom, option_id, section_id FROM gestion_classe")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No classes to migrate")
            return

        from gestion.models import Classe
        count = 0
        for row in rows:
            id, nom, option_id, section_id = row

            Classe.objects.get_or_create(
                id=id,
                defaults={
                    'nom': nom,
                    'option_id': option_id if option_id else None,
                    'section_id': section_id
                }
            )
            count += 1

        print(f"Migrated {count} classes")

    except Exception as e:
        print(f"Error migrating classes: {e}")


def migrate_parents(sqlite_cursor):
    """Migrate parents"""
    try:
        sqlite_cursor.execute("SELECT id, nom, telephone, email, adresse, profession, relation FROM gestion_parent")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No parents to migrate")
            return

        from gestion.models import Parent
        count = 0
        for row in rows:
            id, nom, telephone, email, adresse, profession, relation = row

            Parent.objects.get_or_create(
                id=id,
                defaults={
                    'nom': nom,
                    'telephone': telephone,
                    'email': email if email else None,
                    'adresse': adresse if adresse else None,
                    'profession': profession if profession else None,
                    'relation': relation
                }
            )
            count += 1

        print(f"Migrated {count} parents")

    except Exception as e:
        print(f"Error migrating parents: {e}")


def migrate_annee_scolaires(sqlite_cursor):
    """Migrate annee scolaires"""
    try:
        sqlite_cursor.execute("SELECT id, annee FROM gestion_anneescolaire")
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No annee scolaires to migrate")
            return

        from gestion.models import AnneeScolaire
        count = 0
        for row in rows:
            id, annee = row
            # Handle case where annee might be None
            if annee is None:
                # Check if "2024-2025" already exists to avoid duplicates
                if not AnneeScolaire.objects.filter(annee="2024-2025").exists():
                    annee = "2024-2025"  # Default value
                else:
                    # If it exists, skip this record
                    continue

            # Check if this annee already exists
            if not AnneeScolaire.objects.filter(annee=annee).exists():
                AnneeScolaire.objects.get_or_create(
                    id=id,
                    defaults={
                        'annee': annee
                    }
                )
                count += 1

        print(f"Migrated {count} annee scolaires")

    except Exception as e:
        print(f"Error migrating annee scolaires: {e}")


def migrate_users(sqlite_cursor):
    """Migrate users"""
    try:
        sqlite_cursor.execute("""
                              SELECT id,
                                     password,
                                     last_login,
                                     is_superuser,
                                     username,
                                     first_name,
                                     last_name,
                                     email,
                                     is_staff,
                                     is_active,
                                     date_joined,
                                     role
                              FROM gestion_customuser
                              """)
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No users to migrate")
            return

        from gestion.models import CustomUser
        count = 0
        for row in rows:
            (id, password, last_login, is_superuser, username, first_name,
             last_name, email, is_staff, is_active, date_joined, role) = row

            CustomUser.objects.get_or_create(
                id=id,
                defaults={
                    'password': password,
                    'last_login': last_login,
                    'is_superuser': is_superuser,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'is_staff': is_staff,
                    'is_active': is_active,
                    'date_joined': date_joined,
                    'role': role
                }
            )
            count += 1

        print(f"Migrated {count} users")

    except Exception as e:
        print(f"Error migrating users: {e}")


def migrate_eleves(sqlite_cursor):
    """Migrate eleves"""
    try:
        sqlite_cursor.execute("""
                              SELECT id,
                                     nom,
                                     post_nom,
                                     prenom,
                                     sexe,
                                     date_naissance,
                                     lieu_naissance,
                                     matricule,
                                     annee_scolaire,
                                     classe_id,
                                     option_id,
                                     section_id,
                                     parent_id
                              FROM gestion_eleve
                              """)
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No eleves to migrate")
            return

        from gestion.models import Eleve
        count = 0
        for row in rows:
            (id, nom, post_nom, prenom, sexe, date_naissance, lieu_naissance,
             matricule, annee_scolaire, classe_id, option_id, section_id, parent_id) = row

            # Handle missing values
            if prenom is None:
                prenom = ''
            if sexe is None:
                sexe = 'M'
            if date_naissance is None:
                date_naissance = '2000-01-01'
            if lieu_naissance is None:
                lieu_naissance = ''

            # Find the annee_scolaire_id
            from gestion.models import AnneeScolaire
            try:
                annee_obj = AnneeScolaire.objects.get(annee=annee_scolaire)
                annee_scolaire_id = annee_obj.id
            except AnneeScolaire.DoesNotExist:
                # Create a default one if not exists
                if annee_scolaire is None:
                    annee_scolaire = "2024-2025"
                # Check if it already exists to avoid duplicates
                if not AnneeScolaire.objects.filter(annee=annee_scolaire).exists():
                    annee_obj = AnneeScolaire.objects.create(annee=annee_scolaire)
                else:
                    annee_obj = AnneeScolaire.objects.get(annee=annee_scolaire)
                annee_scolaire_id = annee_obj.id
            except AnneeScolaire.MultipleObjectsReturned:
                # If multiple objects found, use the first one
                annee_obj = AnneeScolaire.objects.filter(annee=annee_scolaire).first()
                annee_scolaire_id = annee_obj.id

            Eleve.objects.get_or_create(
                id=id,
                defaults={
                    'nom': nom,
                    'post_nom': post_nom,
                    'prenom': prenom,
                    'sexe': sexe,
                    'date_naissance': date_naissance,
                    'lieu_naissance': lieu_naissance,
                    'matricule': matricule,
                    'annee_scolaire_id': annee_scolaire_id,
                    'classe_id': classe_id,
                    'option_id': option_id if option_id else None,
                    'section_id': section_id,
                    'parent_id': parent_id if parent_id else None
                }
            )
            count += 1

        print(f"Migrated {count} eleves")

    except Exception as e:
        print(f"Error migrating eleves: {e}")


def migrate_frais(sqlite_cursor):
    """Migrate frais"""
    try:
        sqlite_cursor.execute("""
                              SELECT id, nom, montant, type_frais, mois, tranche, annee_scolaire_id
                              FROM gestion_frais
                              """)
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No frais to migrate")
            return

        from gestion.models import Frais
        count = 0
        for row in rows:
            id, nom, montant, type_frais, mois, tranche, annee_scolaire_id = row

            Frais.objects.get_or_create(
                id=id,
                defaults={
                    'nom': nom,
                    'montant': montant,
                    'type_frais': type_frais,
                    'mois': mois if mois else None,  # Changed to None instead of empty string
                    'tranche': tranche if tranche else None,  # Changed to None instead of empty string
                    'annee_scolaire_id': annee_scolaire_id
                }
            )
            count += 1

        print(f"Migrated {count} frais")

    except Exception as e:
        print(f"Error migrating frais: {e}")


def migrate_paiements(sqlite_cursor):
    """Migrate paiements"""
    try:
        # Check which columns exist in the paiement table
        sqlite_cursor.execute("PRAGMA table_info(gestion_paiement)")
        columns = [column[1] for column in sqlite_cursor.fetchall()]

        # Build query based on available columns
        base_columns = ["id", "mois", "tranche", "montant_paye", "solde_restant",
                        "date_paiement", "recu_numero", "eleve_id", "frais_id"]

        # Check if annee_scolaire_id exists
        if "annee_scolaire_id" in columns:
            select_columns = base_columns + ["annee_scolaire_id"]
            query = f"SELECT {', '.join(select_columns)} FROM gestion_paiement"
        else:
            # If annee_scolaire_id doesn't exist, don't select it
            select_columns = base_columns
            query = f"SELECT {', '.join(select_columns)} FROM gestion_paiement"

        sqlite_cursor.execute(query)
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No paiements to migrate")
            return

        from gestion.models import Paiement
        count = 0
        for row in rows:
            row_dict = dict(zip(select_columns, row))

            defaults = {
                'mois': row_dict.get('mois') if row_dict.get('mois') else None,  # Changed to None
                'tranche': row_dict.get('tranche') if row_dict.get('tranche') else None,  # Changed to None
                'montant_paye': row_dict.get('montant_paye'),
                'solde_restant': row_dict.get('solde_restant'),
                'date_paiement': row_dict.get('date_paiement'),
                'recu_numero': row_dict.get('recu_numero'),
                'eleve_id': row_dict.get('eleve_id'),
                'frais_id': row_dict.get('frais_id')
            }

            # Add annee_scolaire_id only if it exists in the row
            if 'annee_scolaire_id' in row_dict and row_dict['annee_scolaire_id'] is not None:
                defaults['annee_scolaire_id'] = row_dict['annee_scolaire_id']

            Paiement.objects.get_or_create(
                id=row_dict['id'],
                defaults=defaults
            )
            count += 1

        print(f"Migrated {count} paiements")

    except Exception as e:
        print(f"Error migrating paiements: {e}")


def migrate_inscriptions(sqlite_cursor):
    """Migrate inscriptions"""
    try:
        # Check which columns exist in the inscription table
        sqlite_cursor.execute("PRAGMA table_info(gestion_inscription)")
        columns = [column[1] for column in sqlite_cursor.fetchall()]

        # Build query based on available columns
        base_columns = ["id", "date_inscription", "eleve_id"]

        # Check if est_reinscription exists
        if "est_reinscription" in columns:
            select_columns = base_columns + ["est_reinscription"]
            # Check if annee_scolaire_id exists
            if "annee_scolaire_id" in columns:
                select_columns.append("annee_scolaire_id")
            # Check if classe_id exists
            if "classe_id" in columns:
                select_columns.append("classe_id")
            query = f"SELECT {', '.join(select_columns)} FROM gestion_inscription"
        else:
            # Check if annee_scolaire_id exists
            additional_columns = []
            if "annee_scolaire_id" in columns:
                additional_columns.append("annee_scolaire_id")
            # Check if classe_id exists
            if "classe_id" in columns:
                additional_columns.append("classe_id")
            select_columns = base_columns + additional_columns
            query = f"SELECT {', '.join(select_columns)} FROM gestion_inscription"

        sqlite_cursor.execute(query)
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No inscriptions to migrate")
            return

        from gestion.models import Inscription
        count = 0
        for row in rows:
            row_dict = dict(zip(select_columns, row))

            defaults = {
                'date_inscription': row_dict.get('date_inscription'),
                'eleve_id': row_dict.get('eleve_id')
            }

            # Add est_reinscription only if it exists in the row
            if 'est_reinscription' in row_dict:
                defaults['est_reinscription'] = bool(row_dict['est_reinscription'])

            # Add annee_scolaire_id only if it exists in the row
            if 'annee_scolaire_id' in row_dict and row_dict['annee_scolaire_id'] is not None:
                defaults['annee_scolaire_id'] = row_dict['annee_scolaire_id']

            # Add classe_id only if it exists in the row
            if 'classe_id' in row_dict and row_dict['classe_id'] is not None:
                defaults['classe_id'] = row_dict['classe_id']

            Inscription.objects.get_or_create(
                id=row_dict['id'],
                defaults=defaults
            )
            count += 1

        print(f"Migrated {count} inscriptions")

    except Exception as e:
        print(f"Error migrating inscriptions: {e}")


def migrate_depenses(sqlite_cursor):
    """Migrate depenses"""
    try:
        sqlite_cursor.execute("""
                              SELECT id, motif, montant, date_depense, annee_scolaire_id, section_id
                              FROM gestion_depense
                              """)
        rows = sqlite_cursor.fetchall()

        if not rows:
            print("No depenses to migrate")
            return

        from gestion.models import Depense
        count = 0
        for row in rows:
            id, motif, montant, date_depense, annee_scolaire_id, section_id = row

            Depense.objects.get_or_create(
                id=id,
                defaults={
                    'motif': motif,
                    'montant': montant,
                    'date_depense': date_depense,
                    'annee_scolaire_id': annee_scolaire_id if annee_scolaire_id else None,
                    'section_id': section_id if section_id else None
                }
            )
            count += 1

        print(f"Migrated {count} depenses")

    except Exception as e:
        print(f"Error migrating depenses: {e}")


if __name__ == '__main__':
    migrate_data()
