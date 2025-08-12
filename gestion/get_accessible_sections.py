from gestion.models import Section


def get_accessible_sections(user):
    """
    Retourne les sections auxquelles l'utilisateur a accès.
    """
    if user.is_superuser:
        # Un superutilisateur a accès à toutes les sections
        return Section.objects.all()
    else:
        # Récupérer les sections associées aux rôles ou permissions de l'utilisateur
        return Section.objects.filter(user_permissions=user)