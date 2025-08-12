# Correction des erreurs de mapping et ajout du contrôle d'accès aux formulaires
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from .models import Section, Classe

def check_section_access(user, section_name):
    """
    Vérifie si l'utilisateur a le droit d'accéder à une section
    Returns: True si l'accès est autorisé, False sinon
    """
    if user.is_superuser or user.role == 'admin':
        return True
    
    # Mapping des rôles aux sections autorisées (corrigé)
    ROLE_SECTIONS = {
        'admin': ['Maternelle', 'Primaire', 'Secondaire', 'Humanités', 'ITM'],
        'directeur': ['Maternelle', 'Primaire'],
        'directeur_financier': ['Maternelle', 'Primaire'],
        'prefet': ['Secondaire', 'Humanités'],
        'prefet_financier': ['Secondaire', 'Humanités'],
        'prefet_itm': ['ITM'],
        'ITM_financier': ['ITM'],
        'enseignant': ['Maternelle', 'Primaire', 'Secondaire', 'Humanités', 'ITM'],
        'parent': ['Maternelle', 'Primaire', 'Secondaire', 'Humanités', 'ITM'],
    }
    
    if user.role in ROLE_SECTIONS:
        if section_name in ROLE_SECTIONS[user.role]:
            return True
        # Ajout du message d'avertissement
        messages.warning(user, f"Accès refusé: Vous n'avez pas le droit d'accéder à la section {section_name}")
        return False
    
    return False

def get_accessible_sections(user):
    """Retourne les sections accessibles par l'utilisateur"""
    if user.is_superuser or user.role == 'admin':
        return Section.objects.all()

    section_names = []
    if user.role in ['directeur', 'directeur_financier']:
        section_names = ['Maternelle', 'Primaire']
    elif user.role in ['prefet', 'prefet_financier']:
        section_names = ['Secondaire', 'Humanités']
    elif user.role in ['prefet_itm', 'ITM_financier']:
        section_names = ['ITM']

    return Section.objects.filter(nom__in=section_names)

def filter_by_user_role(queryset, user, section_field='section__nom'):
    """
    Filtre un queryset selon les permissions de l'utilisateur
    Args:
        queryset: Le queryset à filtrer
        user: L'utilisateur connecté
        section_field: Le champ utilisé pour le filtrage (ex: 'section__nom', 'classe__section__nom')
    Returns:
        QuerySet: QuerySet filtré selon les sections accessibles
    """
    if user.is_superuser or user.role == 'admin':
        return queryset
        
    try:
        from django.db.models import Q
        
        accessible_sections = get_accessible_sections(user)
        if not accessible_sections.exists():
            return queryset.none()
            
        # Créer la condition de filtrage dynamiquement selon le champ spécifié
        condition = Q(**{f"{section_field}__in": accessible_sections.values_list('nom', flat=True)})
        
        return queryset.filter(condition)
    except Exception as e:
        print(f"Erreur dans filter_by_user_role: {str(e)}")
        return queryset.none()
