# middleware.py

import threading
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.contrib.auth.models import User

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


class SingleSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get the current session key
            current_session_key = request.session.session_key
            
            # Get the session key stored in the user's profile or a custom model
            try:
                user_profile = request.user.userprofile
                stored_session_key = getattr(user_profile, 'session_key', None)
                
                # If there's a stored session key and it's different from current one
                if stored_session_key and stored_session_key != current_session_key:
                    # Check if the stored session still exists
                    try:
                        stored_session = Session.objects.get(session_key=stored_session_key)
                        # Check if the session has expired
                        if stored_session.expire_date > timezone.now():
                            # Log out the current session
                            logout(request)
                            messages.error(request, "Vous avez été déconnecté car vous vous êtes connecté depuis un autre appareil.")
                            return redirect('login')
                    except Session.DoesNotExist:
                        # Stored session doesn't exist, so we can continue
                        pass
                
                # Update the session key in user profile
                if current_session_key:
                    user_profile.session_key = current_session_key
                    user_profile.save(update_fields=['session_key'])
                    
            except AttributeError:
                # User doesn't have a userprofile, create one
                from .models import UserProfile
                user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                if current_session_key:
                    user_profile.session_key = current_session_key
                    user_profile.save(update_fields=['session_key'])
        
        response = self.get_response(request)
        return response
