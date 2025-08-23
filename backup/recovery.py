import os
import csv
import django
from django.conf import settings
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')
django.setup()


def import_from_csv():
    print("📤 IMPORT DEPUIS CSV")
    print("=" * 50)

    # Mapping des tables et modèles
    import_mapping = {
        'parents.csv': {
            'model': 'gestion.Parent',
            'fields': {
                'id': 'id',
                'nom': 'nom',
                'telephone': 'telephone',
                'email': 'email',
                'adresse': 'adresse',
                'profession': 'profession',
                'relation': 'relation'
            }
        },
        'eleves.csv': {
            'model': 'gestion.Eleve',
            'fields': {
                'id': 'id',
                'nom': 'nom',
                'post_nom': 'post_nom',
                'prenom': 'prenom',
                'matricule': 'matricule',
                'sexe': 'sexe',
                'date_naissance': 'date_naissance',
                'lieu_naissance': 'lieu_naissance',
                'section_id': 'section_id',
                'classe_id': 'classe_id',
                'annee_scolaire_id': 'annee_scolaire_id',
                'option_id': 'option_id',
                'parent_id': 'parent_id'
            }
        },
        'frais.csv': {
            'model': 'gestion.Frais',
            'fields': {
                'id': 'id',
                'nom': 'nom',
                'montant': 'montant',
                'type_frais': 'type_frais',
                'mois': 'mois',
                'section_id': 'section_id',
                'option_id': 'option_id',
                'tranche': 'tranche',
                'annee_scolaire_id': 'annee_scolaire_id'
            }
        }
    }

    imported_counts = {}

    for csv_file, config in import_mapping.items():
        if not os.path.exists(csv_file):
            print(f"⚠️  Fichier {csv_file} introuvable")
            continue

        print(f"🔄 Import de {csv_file}...")

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')
                model = django.apps.apps.get_model(config['model'])
                count = 0

                with transaction.atomic():
                    for row in reader:
                        # Préparer les données
                        data = {}
                        for csv_field, model_field in config['fields'].items():
                            if csv_field in row and row[csv_field]:
                                data[model_field] = row[csv_field]

                        # Créer l'objet
                        try:
                            obj, created = model.objects.get_or_create(
                                id=data.get('id'),
                                defaults=data
                            )
                            if created:
                                count += 1
                        except Exception as e:
                            print(f"   ⚠️  Erreur ligne {reader.line_num}: {e}")
                            continue

                imported_counts[csv_file] = count
                print(f"   ✅ {count} enregistrements importés")

        except Exception as e:
            print(f"❌ Erreur avec {csv_file}: {e}")

    # Résumé
    print("=" * 50)
    print("📊 RÉSUMÉ DE L'IMPORT:")
    for file, count in imported_counts.items():
        print(f"   {file}: {count} enregistrements")

    return True


if __name__ == "__main__":
    import_from_csv()