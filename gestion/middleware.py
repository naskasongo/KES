# middleware.py

import threading
from django.shortcuts import redirect

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        return self.get_response(request)

class TemporaryPasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'is_password_temporary'):
            if request.user.is_password_temporary and not request.path.startswith('/password/'):
                return redirect('password_change')
        return self.get_response(request)


# middleware/annee_scolaire_middleware.py
from gestion.models import AnneeScolaire

class AnneeScolaireMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if 'annee_scolaire_id' not in request.session:
                annee = AnneeScolaire.obtenir_annee_courante()
                request.session['annee_scolaire_id'] = annee.id
        response = self.get_response(request)
        return response
