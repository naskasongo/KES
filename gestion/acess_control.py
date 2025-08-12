# gestion/access_control.py
from django.core.exceptions import PermissionDenied
from .models import Section, Classe


def check_section_access(user, section_name):
    """Vérifie si l'utilisateur a accès à la section donnée"""
    section_name = section_name.lower()

    if user.is_superuser or user.role == 'admin':
        return True

    if user.role == 'directeur' and section_name in ['maternelle', 'primaire']:
        return True

    if user.role == 'prefet' and section_name in ['secondaire', 'humanités']:
        return True

    if user.role == 'prefet_itm' and section_name == 'itm':
        return True

    return False


def get_accessible_sections(user):
    """Retourne les sections accessibles par l'utilisateur"""
    if user.is_superuser or user.role == 'admin':
        return Section.objects.all()

    section_names = []
    if user.role == 'directeur':
        section_names = ['Maternelle', 'Primaire']
    elif user.role == 'prefet':
        section_names = ['Secondaire', 'Humanités']
    elif user.role == 'prefet_itm':
        section_names = ['ITM']

    return Section.objects.filter(nom__in=section_names)


def section_required(view_func):
    """Décorateur pour vérifier l'accès à une section"""

    def wrapper(request, *args, **kwargs):
        section_id = kwargs.get('section_id')
        if section_id:
            section = Section.objects.get(id=section_id)
            if not check_section_access(request.user, section.nom):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def classe_required(view_func):
    """Décorateur pour vérifier l'accès à une classe"""

    def wrapper(request, *args, **kwargs):
        classe_id = kwargs.get('classe_id')
        if classe_id:
            classe = Classe.objects.get(id=classe_id)
            if not check_section_access(request.user, classe.section.nom):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper



def check_section_access(user, section_name):
    """Vérifie si l'utilisateur a accès à la section donnée"""
    if user.is_superuser or user.role == 'admin':
        return True

    # Directeur: accès à Maternelle et Primaire
    if user.role == 'directeur' and section_name.lower() in ['maternelle', 'primaire']:
        return True

    # Préfet: accès à Secondaire et Humanités
    if user.role == 'prefet' and section_name.lower() in ['secondaire', 'humanités']:
        return True

    # Préfet ITM: accès à ITM
    if user.role == 'prefet_itm' and section_name.lower() == 'itm':
        return True

    return False


def section_required(view_func):
    """Décorateur pour vérifier l'accès à une section"""

    def wrapper(request, *args, **kwargs):
        section_id = kwargs.get('section_id')
        if section_id:
            section = get_object_or_404(Section, id=section_id)
            if not check_section_access(request.user, section.nom):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def classe_required(view_func):
    """Décorateur pour vérifier l'accès à une classe"""

    def wrapper(request, *args, **kwargs):
        classe_id = kwargs.get('classe_id')
        if classe_id:
            classe = get_object_or_404(Classe, id=classe_id)
            if not check_section_access(request.user, classe.section.nom):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper