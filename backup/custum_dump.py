import os
import sys
import django
import json
from django.core import serializers
from django.apps import apps
from django.conf import settings

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wantashi.settings')

# Ajoutez le chemin de votre projet au Python path
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Initialisez Django
django.setup()


def custom_dump_data():
    excluded_models = [
        'contenttypes.ContentType',
        'auth.Permission',
        'admin.LogEntry',
        'sessions.Session'
    ]

    all_data = []

    print("Starting data dump...")

    for app_config in apps.get_app_configs():
        app_label = app_config.label
        print(f"Processing app: {app_label}")

        for model in app_config.get_models():
            model_name = f"{app_label}.{model._meta.model_name}"

            if model_name in excluded_models:
                print(f"Skipping {model_name}")
                continue

            try:
                print(f"  Dumping {model_name}...")
                queryset = model.objects.all()
                count = queryset.count()

                if count > 0:
                    data = serializers.serialize('json', queryset)
                    model_data = json.loads(data)
                    all_data.extend(model_data)
                    print(f"    Dumped {count} records")
                else:
                    print(f"    No records found for {model_name}")

            except Exception as e:
                print(f"    Error processing {model_name}: {str(e)}")
                continue

    # Sauvegarder les données
    with open('custom_dump.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"Dump completed successfully! Saved {len(all_data)} records to custom_dump.json")


if __name__ == "__main__":
    custom_dump_data()