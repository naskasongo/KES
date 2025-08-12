from gestion.models import Frais, Section, AnneeScolaire

# Dictionnaire FRAIS_MAPPING
FRAIS_MAPPING = {
    'FIP': {'type_frais': 'Mensuel', 'section': None},
    'ETAT': {'type_frais': 'Trimestriel', 'section': None},
    'connexe': {'type_frais': 'Trimestriel', 'section': None},
    'frais connexe': {'type_frais': 'Annuel', 'section': None},
    'inscription': {'type_frais': 'Annuel', 'section': None},
    'bulletin': {'type_frais': 'Annuel', 'section': None},
    'sonas': {'type_frais': 'Annuel', 'section': None},
    'Quotite DPS': {'type_frais': 'Trimestriel', 'section': 'ITM'},
    'Stage': {'type_frais': 'Trimestriel', 'section': 'ITM'},
    "jury fin d'annee": {'type_frais': 'Annuel', 'section': 'ITM'},
    'Minerval': {'type_frais': 'Annuel', 'section': 'ITM'},
    'macaron': {'type_frais': 'Annuel', 'section': 'ITM'},
    'Planification familiale': {'type_frais': 'Annuel', 'section': 'ITM'},
    'fiche de renseignement': {'type_frais': 'Annuel', 'section': 'ITM'},
    'carnet de renseignement': {'type_frais': 'Annuel', 'section': 'ITM'},
    "carnet d'apprenant": {'type_frais': 'Annuel', 'section': 'ITM'},
}


def ajouter_frais(frais_mapping, current_annee_scolaire_label):
    # Récupérer l'année scolaire en cours
    annee_scolaire, created = AnneeScolaire.objects.get_or_create(annee=current_annee_scolaire_label)

    for nom, details in frais_mapping.items():
        # Récupérer ou définir la section
        section = None
        if details['section']:
            section = Section.objects.filter(nom=details['section']).first()
            if not section:
                print(f"La section '{details['section']}' n'existe pas dans la base de données. Ignorée.")
                continue

        # Créer le frais
        frais, created = Frais.objects.get_or_create(
            nom=nom,
            type_frais=details['type_frais'],
            section=section,
            annee_scolaire=annee_scolaire
        )

        if created:
            print(f"Frais '{nom}' ajouté avec succès.")
        else:
            print(f"Frais '{nom}' existe déjà.")


# Exemple d'utilisation
# Assurez-vous de fournir le label correct pour l'année scolaire actuelle
current_annee_scolaire_label = AnneeScolaire.get_current_year()
ajouter_frais(FRAIS_MAPPING, current_annee_scolaire_label)
