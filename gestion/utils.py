# utils.py
import os
import csv
from datetime import datetime

DATA_DIR = "data"

def get_csv_path(eleve):
    """
    Fonction utilitaire réutilisable pour récupérer les élèves d'une classe filtrés par année scolaire.
    
    Args:
        request: L'objet HttpRequest
        classe_id: ID de la classe pour filtrer les élèves
    
    Returns:
        JsonResponse avec les données des élèves et de l'année scolaire ou une erreur
    """
    try:
        # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

        if not annee_id:
            # Utiliser l'année courante si aucune année n'est sélectionnée
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
        else:
            # Vérifier que l'année existe
            try:
                annee = AnneeScolaire.objects.get(id=annee_id)
            except AnneeScolaire.DoesNotExist:
                annee = AnneeScolaire.obtenir_annee_courante()
                annee_id = annee.id

        # Vérifier les permissions de la classe
        classe = Classe.objects.get(id=classe_id)
        if not check_section_access(request.user, classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Appliquer le filtrage selon les permissions et l'année scolaire
        eleves = Eleve.objects.filter(classe_id=classe_id, annee_scolaire_id=annee_id)

        if not (request.user.is_superuser or request.user.role == 'admin'):
            eleves = filter_by_user_role(eleves, request.user, 'classe__section__nom')

        eleves_list = list(eleves.values("id", "nom", "post_nom", "matricule"))

        return JsonResponse({
            'eleves': eleves_list,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Classe.DoesNotExist:
        return JsonResponse({'error': 'Classe introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur : {str(e)}'}, status=500)


# D:\Projects\school\gestion\utils.py

from django.http import JsonResponse
from .models import AnneeScolaire, Classe



def get_eleves_by_classe_and_year(request, classe_id):
    """
    Fonction utilitaire réutilisable pour récupérer les élèves d'une classe filtrés par année scolaire.

    Args:
        request: L'objet HttpRequest
        classe_id: ID de la classe pour filtrer les élèves

    Returns:
        JsonResponse avec les données des élèves et de l'année scolaire ou une erreur
    """
    try:
        # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

        if not annee_id:
            # Utiliser l'année courante si aucune année n'est sélectionnée
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
        else:
            # Vérifier que l'année existe
            try:
                annee = AnneeScolaire.objects.get(id=annee_id)
            except AnneeScolaire.DoesNotExist:
                annee = AnneeScolaire.obtenir_annee_courante()
                annee_id = annee.id

        # Vérifier les permissions de la classe
        classe = Classe.objects.get(id=classe_id)
        if not check_section_access(request.user, classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Appliquer le filtrage selon les permissions et l'année scolaire
        eleves = Eleve.objects.filter(classe_id=classe_id, annee_scolaire_id=annee_id)

        if not (request.user.is_superuser or request.user.role == 'admin'):
            eleves = filter_by_user_role(eleves, request.user, 'classe__section__nom')

        eleves_list = list(eleves.values("id", "nom", "post_nom", "matricule"))

        return JsonResponse({
            'eleves': eleves_list,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Classe.DoesNotExist:
        return JsonResponse({'error': 'Classe introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur : {str(e)}'}, status=500)

from gestion.models import AnneeScolaire

# utils/annee_scolaire.py
from gestion.models import AnneeScolaire

def recuperer_annee_active(request):
    annee_id = request.GET.get('annee_scolaire')
    try:
        if annee_id:
            selected_annee = AnneeScolaire.objects.get(id=annee_id)
        else:
            selected_annee = AnneeScolaire.obtenir_annee_courante()
    except AnneeScolaire.DoesNotExist:
        selected_annee = AnneeScolaire.obtenir_annee_courante()

    request.session['annee_scolaire_id'] = selected_annee.id
    return selected_annee
