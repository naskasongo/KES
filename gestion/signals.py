# signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db import ProgrammingError

User = get_user_model()

def get_request_user():
    """Récupère l'utilisateur connecté avec plus de robustesse"""
    try:
        from .middleware import get_current_user
        user = get_current_user()
        if user and not user.is_anonymous:
            return user
    except Exception:
        pass
    return None

# Liste des modèles à ignorer pour éviter la récursion
MODELELES_A_IGNORER = {
    'Session', 'ContentType', 'Permission', 'Group',
    'User', 'LogEntry', 'HistoriqueAction', 'Notification'
}

def safe_log_action(**kwargs):
    """
    Safely log an action, handling cases where the HistoriqueAction table
    might not exist yet (e.g., during initial migrations)
    """
    try:
        from .models import HistoriqueAction
        return HistoriqueAction.objects.create(**kwargs)
    except ProgrammingError:
        # Table doesn't exist yet, skip logging
        pass
    except Exception:
        # Other error, skip logging
        pass

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if sender.__name__ in MODELELES_A_IGNORER:
        return

    from .models import HistoriqueAction

    user = get_request_user()
    username = "Système"

    if user:
        username = user.get_full_name() or user.username
    elif hasattr(instance, 'utilisateur'):
        try:
            user = instance.utilisateur
            username = user.get_full_name() or user.username
        except (AttributeError, ObjectDoesNotExist):
            pass

    safe_log_action(
        utilisateur=user,
        username=username,
        modele=sender.__name__,
        objet_id=instance.id if hasattr(instance, 'id') else None,
        action=HistoriqueAction.ACTION_CREATION if created else HistoriqueAction.ACTION_MODIFICATION,
        details=f"{'Création' if created else 'Modification'} de {instance}"
    )

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender.__name__ in MODELELES_A_IGNORER:
        return

    try:
        utilisateur = get_request_user()
    except Exception:
        utilisateur = None

    username = utilisateur.get_full_name() if utilisateur else None

    safe_log_action(
        utilisateur=utilisateur,
        username=username,
        modele=sender.__name__,
        objet_id=instance.id if hasattr(instance, 'id') and instance.id is not None else None,
        action=HistoriqueAction.ACTION_SUPPRESSION,
        details=f"Supprimé : {instance}"
    )
