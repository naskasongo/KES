import csv
import json
from datetime import datetime
import os

# Définir le chemin correct vers le fichier CSV
csv_file_path = os.path.join('backup', 'csv', 'gestion_paiement.csv')
json_file_path = 'paiements.json'

data = []
try:
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            # Skip the '#' column and handle empty values
            data.append({
                "model": "gestion.paiement",
                "pk": int(row['id']) if row['id'] and row['id'].strip() else i+1,
                "fields": {
                    "mois": row['mois'] if row['mois'] and row['mois'].strip() and row['mois'] != '""' else None,
                    "tranche": row['tranche'] if row['tranche'] and row['tranche'].strip() and row['tranche'] != '""' else None,
                    "montant_paye": float(row['montant_paye']) if row['montant_paye'] and row['montant_paye'].strip() and row['montant_paye'] != '""' else 0.0,
                    "solde_restant": float(row['solde_restant']) if row['solde_restant'] and row['solde_restant'].strip() and row['solde_restant'] != '""' else 0.0,
                    "date_paiement": row['date_paiement'] if row['date_paiement'] and row['date_paiement'].strip() and row['date_paiement'] != '""' else None,
                    "recu_numero": row['recu_numero'] if row['recu_numero'] and row['recu_numero'].strip() and row['recu_numero'] != '""' else "",
                    "eleve_id": int(row['eleve_id']) if row['eleve_id'] and row['eleve_id'].strip() and row['eleve_id'] != '""' else None,
                    "frais_id": int(row['frais_id']) if row['frais_id'] and row['frais_id'].strip() and row['frais_id'] != '""' else None,
                    "annee_scolaire_id": int(row['annee_scolaire_id']) if row['annee_scolaire_id'] and row['annee_scolaire_id'].strip() and row['annee_scolaire_id'] != '""' else None
                }
            })

    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=2)

    print(f"Conversion completed! Generated {json_file_path} with {len(data)} records.")

except FileNotFoundError:
    print(f"Error: Could not find the CSV file at {csv_file_path}")
    print("Please check if the file exists and the path is correct.")
except Exception as e:
    print(f"Error during conversion: {e}")
