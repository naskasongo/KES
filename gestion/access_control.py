from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Section, Classe


# 确保这些权限函数已正确实现
def get_accessible_sections(user):
    if user.is_superuser or getattr(user, 'role', None) == 'admin':
        return Section.objects.all()

    role_sections = {
        'directeur': ['Maternelle', 'Primaire'],
        'prefet': ['Secondaire', 'Humanités'],
        'prefet_itm': ['ITM'],
        'directeur_financier': ['Maternelle', 'Primaire'],
        'prefet_financier': ['Secondaire', 'Humanités'],
        'ITM_financier': ['ITM']
    }.get(getattr(user, 'role', ''), [])

    return Section.objects.filter(nom__in=role_sections)

def check_section_access(user, section_name):
    # 修复：添加类型检查和空值处理
    if user.is_superuser or getattr(user, 'role', None) == 'admin':
        return True
        
    allowed_sections = {
        'directeur': ['Maternelle', 'Primaire'],
        'prefet': ['Secondaire', 'Humanités'],
        'prefet_itm': ['ITM'],
        'directeur_financier': ['Maternelle', 'Primaire'],
        'prefet_financier': ['Secondaire', 'Humanités'],
        'ITM_financier': ['ITM']
    }.get(getattr(user, 'role', ''), [])
    
    return str(section_name) in [str(s) for s in allowed_sections]

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

        # Pour les paiements et autres modèles avec relation indirecte vers section
        if section_field == 'classe__section__nom':
            classe_condition = Q(classe__isnull=True)
            return queryset.filter(condition | classe_condition)

        return queryset.filter(condition)
    except Exception as e:
        print(f"Erreur dans filter_by_user_role: {str(e)}")
        return queryset.none()


class SectionRequiredMixin:
    """Mixin pour les vues basées sur les classes nécessitant un accès à une section"""

    def dispatch(self, request, *args, **kwargs):
        section_id = self.kwargs.get('section_id') or request.POST.get('section_id')
        if section_id:
            section = get_object_or_404(Section, id=section_id)
            if not check_section_access(request.user, section.nom):
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


def section_required(view_func):
    """Décorateur pour vérifier l'accès à une section"""

    def _wrapped_view(request, *args, **kwargs):
        section_id = kwargs.get('section_id')
        if section_id:
            section = get_object_or_404(Section, id=section_id)
            if not check_section_access(request.user, section.nom):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def classe_required(view_func):
    """Décorateur pour vérifier l'accès à une classe"""

    def _wrapped_view(request, *args, **kwargs):
        classe_id = kwargs.get('classe_id')
        if classe_id:
            classe = get_object_or_404(Classe, id=classe_id)
            if not check_section_access(request.user, classe.section.nom):
                raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def role_required(allowed_roles):
    """Décorateur générique pour vérifier les rôles"""

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not (
                    request.user.is_superuser or request.user.role == 'admin') and request.user.role not in allowed_roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# Décorateurs spécifiques par rôle
directeur_required = role_required(['directeur', 'directeur_financier'])
prefet_required = role_required(['prefet', 'prefet_financier'])
itm_required = role_required(['prefet_itm', 'ITM_financier'])
financier_required = role_required(['directeur_financier', 'prefet_financier', 'ITM_financier'])

def finance_required(view_func):
    """Décorateur pour vérifier les droits financiers"""
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.role in ['directeur_financier', 'prefet_financier', 'ITM_financier']):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def prefets_required(view_func):
    """Décorateur pour vérifier les droits financiers"""
    def _wrapped_view(request, *args, **kwargs):
        if not (
                request.user.role in ['directeur', 'prefet', 'prefet_itm']):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """Décorateur pour vérifier les droits financiers"""
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view
