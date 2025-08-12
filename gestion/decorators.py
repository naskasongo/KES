from django.core.exceptions import PermissionDenied

def role_required(*roles):
    """ Vérifie si l'utilisateur a le bon rôle pour accéder à la vue. """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied  # Retourne une erreur 403
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
