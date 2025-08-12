from django.contrib.auth.forms import UserChangeForm
from django.db.models import Sum, Count, Q, Avg, F
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .decorators import role_required
from django.db.models import Max
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models.functions import TruncMonth
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
import csv
from django.http import HttpResponse
from django.db import transaction
from decimal import Decimal, InvalidOperation

from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserChangeForm
from .models import Parent, AnneeScolaire, MoisPaiement, Classe, Option, Section, Paiement, Depense, Eleve, Frais, \
    Inscription, TRANCHE_CHOICES
from .forms import DepenseForm, SuiviFinancierForm, FraisForm, PaiementForm, FiltragePaiementForm, EleveForm
import re
from datetime import date
import json
from django.core.serializers.json import DjangoJSONEncoder

import gestion.access_control as access_control
from .access_control import check_section_access, role_required
from .models import Section

import random
import string
from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm


def generate_simple_password():
    """Génère un mot de passe simple facile à utiliser"""
    # 4 lettres majuscules + 2 chiffres
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=2))
    return f"{letters}{numbers}"


@login_required
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Générer un mot de passe simple si aucun mot de passe n'est fourni
            if not user.password:
                simple_password = generate_simple_password()
                user.set_password(simple_password)
                user.is_password_temporary = True  # Champ à créer dans le modèle

            user.save()
            login(request, user)

            # Rediriger vers une page d'information sur le mot de passe temporaire
            return redirect('password_change')  # ou une page spécifique expliquant qu'il faut changer le mot de passe
    else:
        form = CustomUserCreationForm()

    return render(request, 'gestion/register.html', {'form': form})


from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy


# views.py


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'gestion/password_change_form.html'
    success_url = reverse_lazy('dashboard')  # Redirection après changement réussi

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour changer votre mot de passe.")
            return redirect('login')

        if not hasattr(request.user, 'is_password_temporary'):
            messages.error(request, "Erreur : Statut du mot de passe inconnu.")
            return redirect('dashboard')

        if not request.user.is_password_temporary:
            messages.info(request, "Vous n'avez pas de mot de passe temporaire.")
            return redirect('dashboard')

        messages.warning(request, "Vous utilisez un mot de passe temporaire. Veuillez en choisir un nouveau.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        old_password = self.request.user.password
        new_password = form.cleaned_data.get("new_password1")

        if old_password == new_password:
            form.add_error("new_password1", "Le nouveau mot de passe doit être différent de l'ancien.")
            return self.form_invalid(form)

        self.request.user.is_password_temporary = False
        self.request.user.save()

        messages.success(self.request, "Votre mot de passe a été mis à jour avec succès !")
        return super().form_valid(form)


# views.py
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from .models import CustomUser


class AdminPasswordChangeView(PasswordChangeView):
    template_name = 'gestion/password_change_form.html'
    success_url = reverse_lazy('utilisateurs')  # Redirection vers la liste des utilisateurs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour effectuer cette action.")
            return redirect('login')

        if not (request.user.is_superuser or request.user.role == 'admin'):
            messages.error(request, "Accès refusé : vous n'avez pas les droits nécessaires.")
            return redirect('utilisateurs')

        self.user = get_object_or_404(CustomUser, id=kwargs['user_id'])

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user  # Utilisateur dont on change le mot de passe
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, f"Le mot de passe de {self.user.username} a été modifié avec succès.")
        return super().form_valid(form)


# Vue pour la connexion
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Vous êtes connecté.")
            return redirect('dashboard')  # Modifiez 'dashboard' avec votre URL réelle
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'gestion/login.html', {'form': form})


# Vue pour la déconnexion

"""Vue supprimer utlisateur"""

# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model


@login_required
def supprimer_utilisateur(request, user_id):
    User = get_user_model()
    utilisateur = get_object_or_404(User, id=user_id)

    if request.user.id == utilisateur.id:
        # Empêcher l'utilisateur de se supprimer lui-même
        return redirect('utilisateurs')

    utilisateur.delete()
    return redirect('utilisateurs')


@login_required
def detail_utilisateur(request, user_id):
    """
    Vue pour afficher les détails d'un utilisateur.
    """
    utilisateur = get_object_or_404(CustomUser, id=user_id)

    return render(request, 'gestion/detail_utilisateur.html', {
        'utilisateur': utilisateur,
    })


@login_required
def modifier_utilisateur(request, user_id):
    """
    Vue pour modifier les informations d'un utilisateur.
    """
    utilisateur = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Utilisateur mis à jour avec succès.")
            return redirect('detail_utilisateur', user_id=utilisateur.id)
        else:
            messages.error(request, "❌ Erreur lors de la mise à jour. Vérifiez les champs.")
    else:
        form = CustomUserChangeForm(instance=utilisateur)

    return render(request, 'gestion/modifier_utilisateur.html', {
        'form': form,
        'utilisateur': utilisateur,
    })


@login_required  # Assure que seul un utilisateur connecté peut accéder à cette vue
def profil_utilisateur(request):
    utilisateur = request.user  # Récupère l'utilisateur connecté
    context = {
        'utilisateur': utilisateur,
    }
    return render(request, 'gestion/profil_utilisateur.html', context)


def user_logout(request):
    logout(request)
    return redirect('login')


from gestion.models import CustomUser  # Importez votre modèle utilisateur personnalisé

from django.core.paginator import Paginator


@role_required('admin')
@login_required
def liste_utilisateurs(request):
    query = request.GET.get('q')
    utilisateurs = CustomUser.objects.all().order_by('-date_joined')

    if query:
        utilisateurs = utilisateurs.filter(username__icontains=query)

    paginator = Paginator(utilisateurs, 10)  # 10 utilisateurs par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gestion/utilisateurs.html', {
        'utilisateurs': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj
    })


# les roles des utilisateurs
@login_required
def home(request):
    return render(request, 'gestion/login.html')


# views eleves

@login_required
def valider_documents(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)  # Récupère l'élève correspondant
    return render(request, 'valider_documents.html', {'eleve': eleve})  # Retourne un gabarit


# modiifer eleve
@login_required
def modifier_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)
    if request.method == 'POST':
        form = EleveForm(request.POST, instance=eleve)
        if form.is_valid():
            form.save()
            return redirect('liste_eleves')
    else:
        form = EleveForm(instance=eleve)
    return render(request, 'gestion/modifier_eleve.html', {'form': form, 'eleve': eleve})


@login_required
def supprimer_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)

    if request.method == 'POST':
        # Récupérer le mot de passe soumis
        mot_de_passe = request.POST.get('password')

        # Authentifier l'utilisateur avec son mot de passe
        utilisateur = authenticate(request, username=request.user.username, password=mot_de_passe)

        if utilisateur is not None:
            # Si l'utilisateur est authentifié, supprimer l'élève
            eleve.delete()
            messages.success(request, "✅ Élève supprimé avec succès.")
            return redirect('liste_eleves')
        else:
            # Si le mot de passe est incorrect, afficher un message d'erreur
            messages.error(request, "❌ Mot de passe incorrect. Suppression annulée.")

    return render(request, 'gestion/supprimer_eleve.html', {'eleve': eleve})


# Liste des élèves avec filtrage par section, option et classe
from django.shortcuts import render


# Dans views.py


@login_required
def liste_eleves(request):
    # Récupérer les paramètres de filtre
    section_id = request.GET.get('section')
    option_id = request.GET.get('option')
    classe_id = request.GET.get('classe')
    annee_scolaire_id = request.GET.get('annee_scolaire')
    sexe = request.GET.get('sexe')
    matricule = request.GET.get('matricule')

    # Filtrage de base selon les permissions
    eleves = filter_by_user_role(Eleve.objects.all(), request.user, 'classe__section__nom')
    
    # Application des filtres supplémentaires avec vérification des permissions
    if section_id:
        section = get_object_or_404(Section, id=section_id)
        if not check_section_access(request.user, section.nom):
            raise PermissionDenied
        eleves = eleves.filter(classe__section_id=section_id)

    if option_id:
        eleves = filter_by_user_role(eleves, request.user, 'classe__option__section__nom')
        eleves = eleves.filter(classe__option_id=option_id)
    if classe_id:
        eleves = eleves.filter(classe_id=classe_id)
    if annee_scolaire_id:
        eleves = eleves.filter(annee_scolaire_id=annee_scolaire_id)
    if sexe:
        eleves = eleves.filter(sexe=sexe)
    if matricule:
        eleves = eleves.filter(matricule__icontains=matricule)

    # Calcul des statistiques
    total_eleves = eleves.count()
    garcons = eleves.filter(sexe='M').count()
    filles = eleves.filter(sexe='F').count()

    # Préparation des données pour le template
    context = {
        'eleves': eleves,
        'sections': Section.objects.all(),
        'options': Option.objects.all(),
        'classes': Classe.objects.all(),
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'stats': {
            'total': total_eleves,
            'garcons': garcons,
            'filles': filles
        }
    }

    return render(request, 'gestion/liste_eleves.html', context)


@login_required
def ajouter_eleve(request):
    if request.method == 'POST':
        form = EleveForm(request.POST)
        if form.is_valid():
            eleve = form.save(commit=False)

            # Assignation année scolaire
            annee_courante = AnneeScolaire.obtenir_annee_courante()
            eleve.annee_scolaire = annee_courante

            # Vérification doublon
            if Eleve.objects.filter(
                    nom=eleve.nom,
                    post_nom=eleve.post_nom,
                    prenom=eleve.prenom,
                    date_naissance=eleve.date_naissance
            ).exists():
                messages.error(request, "Un élève avec ces informations existe déjà")
                return render(request, 'gestion/ajouter_eleve.html', {'form': form})

            # Génération matricule
            annee_courte = annee_courante.annee[2:4]
            initiales = f"{eleve.nom[0]}{eleve.post_nom[0]}".upper()
            dernier_num = Eleve.objects.filter(
                matricule__startswith=f"{annee_courte}{initiales}"
            ).count()
            eleve.matricule = f"{annee_courte}{initiales}{(dernier_num + 1):03d}"

            # Sauvegarde et création inscription
            eleve.save()
            Inscription.objects.create(
                eleve=eleve,
                annee_scolaire=annee_courante,
                classe=eleve.classe,
                est_reinscription=False
            )

            messages.success(request, "Nouvel élève inscrit avec succès")
            return redirect('ajouter_paiement')

    else:
        form = EleveForm()

    return render(request, 'gestion/ajouter_eleve.html', {'form': form})


# views.py
def trouver_classes_suivantes(classe_actuelle):
    """
    Détermine les classes possibles pour la réinscription.
    """
    try:
        nom_classe = classe_actuelle.nom.strip().lower()
        section_nom = classe_actuelle.section.nom.strip().lower()

        if section_nom == "maternelle" and "3" in nom_classe:
            # Passer au Primaire - 1ère année A ou B
            return Classe.objects.filter(section__nom="Primaire", nom__in=["1ère A", "1ère B"])

        elif section_nom == "primaire" and "6" in nom_classe:
            # Passer au Secondaire - 7ème A ou B
            return Classe.objects.filter(section__nom="Secondaire", nom__in=["7ème A", "7ème B"])

        elif section_nom == "secondaire" and ("8" in nom_classe or "b" in nom_classe):
            # Choix entre Humanités (3ème) ou ITM (1ère)
            humanite_classe = Classe.objects.filter(section__nom="Humanités", nom="3ème")
            itm_classe = Classe.objects.filter(section__nom="ITM", nom="1ère")
            return humanite_classe.union(itm_classe)

        else:
            # Réinscription normale : reste dans la même section/option mais monte en niveau
            if classe_actuelle.option:
                return Classe.objects.filter(
                    option=classe_actuelle.option,
                    section=classe_actuelle.section,
                    nom__gt=classe_actuelle.nom
                ).order_by('nom')
            else:
                return Classe.objects.filter(
                    section=classe_actuelle.section,
                    nom__gt=classe_actuelle.nom
                ).order_by('nom')

    except Exception as e:
        print("Erreur dans la détermination des classes suivantes:", e)
        return []


@login_required
def reinscription(request):
    eleve = None
    classes_suivantes = []
    options = []
    sections = Section.objects.all()
    paiements_precedents = []
    frais_a_payer = 0
    total_paye = 0
    reste_a_payer = 0
    nouvelle_section_possible = False
    nouvelles_sections = []

    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        try:
            eleve = Eleve.objects.get(matricule=matricule)
            annee_courante = AnneeScolaire.obtenir_annee_courante()

            if Inscription.objects.filter(eleve=eleve, annee_scolaire=annee_courante).exists():
                messages.warning(request, "Cet élève est déjà inscrit pour l'année courante.")
                return redirect('reinscription')

            classe_actuelle = eleve.classe
            if not classe_actuelle:
                raise ValueError("Classe non définie pour cet élève.")

            # Déterminer les classes possibles
            classes_suivantes = trouver_classes_suivantes(classe_actuelle)

            if not classes_suivantes.exists():
                messages.info(request, "Aucune classe disponible pour la réinscription.")

            # Gestion des informations du parent
            options = Option.objects.filter(section=classe_actuelle.section) if classe_actuelle.section else []

            # Récupérer les paiements précédents
            annee_precedente = AnneeScolaire.obtenir_annee_precedente()
            paiements_precedents = Paiement.objects.filter(
                eleve=eleve,
                date_paiement__range=(annee_precedente.debut, annee_precedente.fin)
            ).order_by('-date_paiement')

            total_paye = sum(p.montant_paye for p in paiements_precedents)

            # Calcul des frais pour la première classe proposée
            if classes_suivantes.exists():
                premiere_classe = classes_suivantes.first()
                frais_de_classe = Frais.objects.filter(classes=premiere_classe)
                frais_a_payer = sum(f.montant for f in frais_de_classe)

            reste_a_payer = max(0, frais_a_payer - total_paye)

        except Eleve.DoesNotExist:
            messages.error(request, "Aucun élève trouvé avec ce matricule.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la recherche : {str(e)}")

    return render(request, 'gestion/reinscription.html', {
        'eleve': eleve,
        'sections': sections,
        'options': options,
        'classes_suivantes': classes_suivantes,
        'paiements_precedents': paiements_precedents,
        'frais_a_payer': frais_a_payer,
        'total_paye': total_paye,
        'reste_a_payer': reste_a_payer
    })


@login_required
def supprimer_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)
    if request.method == 'POST':
        eleve.delete()
        return redirect('liste_eleves')
    return render(request, 'gestion/supprimer_eleve.html', {'eleve': eleve})


@login_required
def detail_eleve(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)

    # Récupération des frais
    frais_mensuels = Frais.objects.filter(section=eleve.section, type_frais="Mensuel")
    frais_trimestriels = Frais.objects.filter(section=eleve.section, type_frais="Trimestriel").order_by("tranche")
    frais_annuels = Frais.objects.filter(section=eleve.section, type_frais="Annuel")

    # Récupérer tous les paiements faits par cet élève
    paiements = Paiement.objects.filter(eleve=eleve).order_by('-date_paiement')

    # Calcul des totaux
    total_paye = sum(p.montant_paye for p in paiements)

    # Filtrer les paiements par type
    paiements_mensuels = paiements.filter(frais__type_frais="Mensuel")
    paiements_trimestriels = paiements.filter(frais__type_frais="Trimestriel")
    paiements_annuels = paiements.filter(frais__type_frais="Annuel")

    # Compter les paiements par type
    paiements_mensuels_count = paiements_mensuels.count()
    paiements_trimestriels_count = paiements_trimestriels.count()
    paiements_annuels_count = paiements_annuels.count()

    # Dernier paiement (peut être None si aucun paiement)
    dernier_paiement = paiements.first()

    # Ajouter une liste des mois
    months = ["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin"]
    col_missing_mensuel = max(0, 10 - len(frais_mensuels))  # Exemple si tu veux 10 colonnes max
    col_missing_trimestriel = range(3 - len(frais_trimestriels))  # 3 = Nombre de tranches

    context = {
        'eleve': eleve,
        'frais_mensuels': frais_mensuels,
        'frais_trimestriels': frais_trimestriels,
        'frais_annuels': frais_annuels,
        'months': months,
        'col_missing_mensuel': range(col_missing_mensuel),
        'col_missing_trimestriel': col_missing_trimestriel,
        'paiements': paiements,
        'total_paye': total_paye,
        'paiements_mensuels': paiements_mensuels,
        'paiements_trimestriels': paiements_trimestriels,
        'paiements_annuels': paiements_annuels,
        'paiements_mensuels_count': paiements_mensuels_count,
        'paiements_trimestriels_count': paiements_trimestriels_count,
        'paiements_annuels_count': paiements_annuels_count,
        'dernier_paiement': dernier_paiement,
    }
    return render(request, 'details_eleve.html', context)


@login_required
def eleves_par_classe(request, classe_id):
    classe = get_object_or_404(Classe, id=classe_id)
    eleves = Eleve.objects.filter(classe=classe)
    return render(request, 'gestion/liste_eleves.html', {'eleves': eleves, 'classe': classe})


@login_required
def eleves_par_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    eleves = Eleve.objects.filter(section=section)
    return render(request, 'gestion/liste_eleves.html', {'eleves': eleves, 'section': section})


# modeles details eleves
@login_required
def liste_inscriptions(request):
    """ Affiche tous les élèves inscrits avec un filtre optionnel par année scolaire """
    # Récupérer l'année depuis les paramètres GET
    annee = request.GET.get('annee', None)

    # Assurez-vous que l'année spécifiée existe dans la base de données
    if annee:
        try:
            # Vérifiez si l'année existe dans AnneeScolaire
            annee_obj = AnneeScolaire.objects.get(annee=annee)
            # Filtrer les élèves par année scolaire
            eleves = Eleve.objects.filter(annee_scolaire=annee_obj)
        except AnneeScolaire.DoesNotExist:
            # Si l'année scolaire n'existe pas, retourner une liste vide
            eleves = Eleve.objects.none()
    else:
        # Si aucun filtre n'est appliqué, récupérer tous les élèves
        eleves = Eleve.objects.all()

    # Récupérer toutes les années scolaires disponibles pour les filtres
    annees = AnneeScolaire.objects.all()

    return render(request, 'gestion/liste_inscriptions.html', {
        'eleves': eleves,
        'annees': annees,
        'annee_actuelle': annee,  # Utilisé pour afficher la sélection active dans la vue
    })


# frais

# views.py

@login_required
def liste_frais(request):
    """ Afficher tous les frais scolaires avec filtres """
    frais = Frais.objects.all()

    # Récupérer les paramètres de filtre
    section_id = request.GET.get('section')
    classe_id = request.GET.get('classe')

    # Appliquer les filtres de manière sécurisée
    if section_id and section_id.isdigit():
        frais = frais.filter(section_id=int(section_id))

    if classe_id and classe_id.isdigit():
        frais = frais.filter(classes__id=int(classe_id))

    # Préparer les données pour les filtres
    sections = Section.objects.all()
    options = Option.objects.all().values_list('id', 'nom')  # toutes les options.
    classes = Classe.objects.all().values_list('id', 'nom')  # Toutes les classes

    # Calculer les statistiques
    total_frais = sum(f.montant for f in frais)

    # Nombre de frais par section (compter les sections uniques)
    sections_ids = set()
    for f in frais:
        if f.section:
            sections_ids.add(f.section.id)
    frais_par_section = len(sections_ids)

    # Nombre total de classes concernées par les frais (uniques)
    classes_concernees = set()
    for f in frais:
        for classe in f.classes.all():
            classes_concernees.add(classe.id)
    nb_classes_concernees = len(classes_concernees)
    context = {
        'frais': frais,
        'sections': sections,
        'classes': classes,
        'options': options,
        'request': request,  # Pour conserver la sélection dans le template
        'total_frais': total_frais,
        'frais_par_section': frais_par_section,
        'nb_classes_concernees': nb_classes_concernees
    }

    return render(request, 'gestion/liste_frais.html', context)


from .forms import FraisForm


@login_required
def ajouter_frais(request):
    """
    Vue pour ajouter un ou plusieurs frais scolaires
    """
    # Récupérer toutes les sections et l'année scolaire en cours
    sections = Section.objects.all()
    current_year = AnneeScolaire.objects.get_or_create(
        annee=AnneeScolaire.obtenir_annee_courante()
    )[0]

    # Récupérer la section ITM si elle existe
    itm_section = Section.objects.filter(nom__iexact="ITM").first()

    if request.method == 'POST':
        # Compter le nombre de formulaires soumis
        form_count = sum(1 for key in request.POST.keys() if key.startswith('form-') and '-predefined_nom' in key)

        if form_count == 0:
            # Mode formulaire unique (rétrocompatibilité)
            form = FraisForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "✅ Frais ajouté avec succès !")
                return redirect('liste_frais')
            else:
                messages.error(request, "❌ Erreur lors de l'ajout du frais.")
        else:
            # Mode multi-formulaire
            success_count = 0
            errors = []

            for i in range(form_count):
                form_data = {
                    'predefined_nom': request.POST.get(f'form-{i}-predefined_nom'),
                    'custom_nom': request.POST.get(f'form-{i}-custom_nom'),
                    'montant': request.POST.get(f'form-{i}-montant'),
                    'type_frais': request.POST.get(f'form-{i}-type_frais'),
                    'annee_scolaire': current_year.id,
                    'section': request.POST.get(f'form-{i}-section'),
                    'option': request.POST.get(f'form-{i}-option'),
                    'classes': request.POST.getlist(f'form-{i}-classes')
                }

                form = FraisForm(form_data)
                if form.is_valid():
                    try:
                        form.save()
                        success_count += 1
                    except Exception as e:
                        errors.append(f"Erreur lors de l'enregistrement du frais {i + 1}: {str(e)}")
                else:
                    errors.append(f"Erreur dans le formulaire {i + 1}: {form.errors.as_text()}")

            if success_count > 0:
                messages.success(request, f"✅ {success_count} frais ajoutés avec succès !")
                if errors:
                    for error in errors:
                        messages.warning(request, error)
            else:
                for error in errors:
                    messages.error(request, error)
                messages.error(request, "❌ Aucun frais n'a pu être enregistré")

            return redirect('liste_frais')
    else:
        form = FraisForm(initial={'annee_scolaire': current_year})

    context = {
        'form': form,
        'sections': sections,
        'itm_section_id': itm_section.id if itm_section else '',
        'annee_scolaire_en_cours': current_year.annee,
        'multi_form': True
    }

    return render(request, 'gestion/ajouter_frais.html', context)


@login_required
def modifier_frais(request, frais_id):
    """ Modifier un frais existant """
    frais = get_object_or_404(Frais, id=frais_id)
    if request.method == 'POST':
        form = FraisForm(request.POST, instance=frais)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Frais modifié avec succès !")
            return redirect('liste_frais')
    else:
        form = FraisForm(instance=frais)
    return render(request, 'gestion/modifier_frais.html', {'form': form, 'frais': frais})


@login_required
def supprimer_frais(request, frais_id):
    """ Supprimer un frais scolaire """
    frais = get_object_or_404(Frais, id=frais_id)
    if request.method == 'POST':
        frais.delete()
        messages.success(request, "✅ Frais supprimé avec succès !")
        return redirect('liste_frais')
    return render(request, 'gestion/supprimer_frais.html', {'frais': frais})


# liste des pqrents
@login_required
def liste_parents(request):
    parents = Parent.objects.all()  # Récupère tous les parents
    return render(request, "gestion/liste_parents.html", {"parents": parents})


# detail parent
@login_required
def detail_parent(request, parent_id):
    """ Affiche les détails d'un parent avec ses enfants (élèves). """
    parent = get_object_or_404(Parent, id=parent_id)
    return render(request, "gestion/detail_parent.html", {"parent": parent})


# vue paiement
@login_required
def liste_paiements(request):
    paiements = Paiement.objects.all().order_by()  # Paiements par défaut
    form = FiltragePaiementForm(request.GET)  # Charger les critères de filtrage

    if form.is_valid():
        # Filtres appliqués si le formulaire est valide
        if form.cleaned_data['section']:
            paiements = paiements.filter(eleve__classe__section=form.cleaned_data['section'])

        if form.cleaned_data['option']:
            paiements = paiements.filter(eleve__classe__option=form.cleaned_data['option'])

        if form.cleaned_data['classe']:
            paiements = paiements.filter(eleve__classe=form.cleaned_data['classe'])

        if form.cleaned_data['frais']:
            paiements = paiements.filter(frais=form.cleaned_data['frais'])

        if form.cleaned_data['mois']:
            paiements = paiements.filter(mois=form.cleaned_data['mois'])

        if form.cleaned_data['matricule']:
            paiements = paiements.filter(eleve__matricule__icontains=form.cleaned_data['matricule'])

    # Statistiques sur les paiements filtrés
    stats = {
        'total_paye': paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0,  # Total payé
        'nombre_paiements': paiements.count(),  # Nombre total de paiements
        'par_frais': paiements.values('frais__nom').annotate(total=Sum('montant_paye')),  # Montants groupés par frais
        'par_mois': paiements.values('mois').annotate(total=Sum('montant_paye')),  # Montants groupés par mois
    }
    paiements_mensuels = (
        Paiement.objects.annotate(mois_calcule=TruncMonth('date_paiement'))
        .values('mois_calcule')
        .annotate(total=Sum('montant_paye'))
        .order_by('mois_calcule')
    )
    print("Paiements mensuels:", paiements_mensuels)
    print(list(
        paiements_mensuels))  # Doit afficher quelque chose comme [{'mois_calcule': datetime.date(2023, 1, 1), 'total': Decimal('150000')}, ...]

    return render(request, 'liste_paiements.html', {
        'paiements': paiements,
        'form': form,
        'paiements_mensuel': paiements_mensuels,
        'stats': stats,  # Envoyer les statistiques au template
    })


# Données pour le graphique "Évolution des paiements mensuels"

@login_required
def detail_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)

    # Récupérer tous les paiements de l'élève
    paiements_eleve = Paiement.objects.filter(eleve=paiement.eleve)

    # Calcul du solde restant
    total_frais = sum(paiement.frais.montant for paiement in paiements_eleve)
    total_paye = sum(paiement.montant_paye for paiement in paiements_eleve)
    solde_restant = total_frais - total_paye
    anneeScolaire = AnneeScolaire.obtenir_annee_courante()

    return render(request, 'gestion/detail_paiement.html', {
        'paiement': paiement,
        'solde_restant': solde_restant,
        'anneeScolaire': anneeScolaire,
        'utilisateur_connecte': request.user,  # Ajout de l'utilisateur connecté dans le contexte du template

    })


# vu modifier apaiement
from .forms import ModifierPaiementForm


@login_required
def modifier_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)

    if request.method == 'POST':
        form = ModifierPaiementForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('liste_paiements')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = ModifierPaiementForm(instance=paiement)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'gestion/modifier_paiement.html', {
            'form': form
        })
    else:
        return render(request, 'gestion/modifier_paiement.html', {'form': form})


# vu supprimer apiement

@login_required  # Nécessite que l'utilisateur soit connecté
def supprimer_paiement(request, paiement_id):
    # Récupérer l'objet Paiement
    paiement = get_object_or_404(Paiement, id=paiement_id)

    # Vérifier si l'utilisateur est administrateur
    if not request.user.is_superuser:  # Ou utilisez une permission personnalisée si nécessaire
        messages.error(request, "Vous n'avez pas la permission de supprimer un paiement.")
        return redirect('liste_paiements')  # Rediriger vers la liste des paiements

    if request.method == 'POST':
        # Vérifier le mot de passe fourni par l'administrateur
        mot_de_passe = request.POST.get('password')  # Obtenir le mot de passe depuis le formulaire
        user = authenticate(username=request.user.username, password=mot_de_passe)

        if user is not None:
            # Utilisateur authentifié avec succès, supprimer le paiement
            paiement.delete()
            messages.success(request, "Paiement supprimé avec succès.")
            return redirect('liste_paiements')
        else:
            # Mot de passe incorrect
            messages.error(request, "Mot de passe incorrect. Paiement non supprimé.")

    # Afficher une page de confirmation avec demande de mot de passe
    return render(request, 'supprimer_paiement.html', {'paiement': paiement})


@login_required
def ajouter_paiement(request):
    if request.method == 'POST':
        # form = PaiementForm(request.POST)
        form = PaiementForm(user=request.user)

        if form.is_valid():
            try:
                with transaction.atomic():
                    paiement = form.save(commit=False)

                    # Vérifications de base
                    if not paiement.eleve or not paiement.frais:
                        raise ValueError("Veuillez sélectionner un élève et un frais")

                    # Gestion spécifique selon le type de frais
                    if paiement.frais.type_frais == "Mensuel":
                        if not paiement.mois:
                            raise ValueError("Veuillez sélectionner un mois pour les frais mensuels")
                        paiement.tranche = None
                    elif paiement.frais.type_frais == "Trimestriel":
                        tranche = request.POST.get('tranche')
                        if not tranche:
                            raise ValueError("Veuillez sélectionner une tranche pour les frais trimestriels")
                        paiement.tranche = tranche
                        paiement.mois = None
                    else:  # Annuel
                        paiement.mois = None
                        paiement.tranche = None

                    # Vérification du montant
                    if paiement.montant_paye <= 0:
                        messages.error(request, "Le montant du paiement doit être supérieur à 0.")
                        return render(request, 'gestion/ajouter_paiement.html', {'form': form})

                    # Calcul et sauvegarde
                    paiement.calculate_solde()
                    if not paiement.date_paiement:
                        paiement.date_paiement = datetime.now().date()
                    paiement.save()

                    messages.success(request,
                                     f"Paiement enregistré avec succès! Numéro de reçu: {paiement.recu_numero}")
                    return redirect('liste_paiements')

            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
    else:
        form = PaiementForm()

    return render(request, 'gestion/ajouter_paiement.html', {
        'form': form,
        'mois_choices': MoisPaiement.choices,
        'tranche_choices': TRANCHE_CHOICES
    })


@login_required
def calcul_solde(request):
    eleve_id = request.GET.get('eleve_id')
    frais_id = request.GET.get('frais_id')
    mois = request.GET.get('mois')

    try:
        eleve = Eleve.objects.get(pk=eleve_id)
        frais = Frais.objects.get(pk=frais_id)

        solde_info = Paiement.objects.calculer_solde(eleve, frais, mois)

        return JsonResponse({
            'success': True,
            'montant_frais': str(solde_info['montant_frais']),
            'solde_precedent': str(solde_info['solde_precedent']),
            'montant_net': str(solde_info['montant_net']),
            'solde_restant': str(solde_info['solde_restant']),
            'type_frais': frais.type_frais
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# recu paiement
@login_required
def recu_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    return render(request, 'gestion/recu_paiement.html', {'paiement': paiement})


# ********************************************************************************************************************
#                                API
# ********************************************************************************************************************

# API pour récupérer les options et classes dynamiquement *
@login_required
def get_options(request, section_id):
    try:
        # Vérifier les permissions de la section
        section = Section.objects.get(id=section_id)
        if not check_section_access(request.user, section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Filtrer selon les permissions
        options = Option.objects.filter(section_id=section_id)
        if not (request.user.is_superuser or request.user.role == 'admin'):
            options = filter_by_user_role(options, request.user, 'section__nom')

        return JsonResponse({'options': list(options.values('id', 'nom'))})
    except Section.DoesNotExist:
        return JsonResponse({'error': 'Section introuvable'}, status=404)


@login_required
def get_classes_by_section(request, section_id):
    try:
        # Vérifier les permissions
        section = Section.objects.get(id=section_id)
        if not check_section_access(request.user, section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Appliquer le filtrage selon les permissions
        classes = Classe.objects.filter(section_id=section_id, option__isnull=True)
        if not (request.user.is_superuser or request.user.role == 'admin'):
            classes = filter_by_user_role(classes, request.user, 'section__nom')

        return JsonResponse({'classes': list(classes.values('id', 'nom'))})
    except Section.DoesNotExist:
        return JsonResponse({'error': 'Section introuvable'}, status=404)


@login_required
def get_classes_dynamique(request, section_id, option_id=None):
    try:
        # Vérifier les permissions de la section
        section = Section.objects.get(id=section_id)
        if not check_section_access(request.user, section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Appliquer le filtrage selon les permissions
        if option_id and option_id != 'null':
            classes = Classe.objects.filter(section_id=section_id, option_id=option_id)
        else:
            classes = Classe.objects.filter(section_id=section_id, option__isnull=True)

        if not (request.user.is_superuser or request.user.role == 'admin'):
            classes = filter_by_user_role(classes, request.user, 'section__nom')

        return JsonResponse(list(classes.values('id', 'nom')), safe=False)
    except Section.DoesNotExist:
        return JsonResponse({'error': 'Section introuvable'}, status=404)


@login_required
def get_eleves(request, classe_id):
    try:
        # Vérifier les permissions de la classe
        classe = Classe.objects.get(id=classe_id)
        if not check_section_access(request.user, classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Appliquer le filtrage selon les permissions
        eleves = Eleve.objects.filter(classe_id=classe_id)
        if not (request.user.is_superuser or request.user.role == 'admin'):
            eleves = filter_by_user_role(eleves, request.user, 'classe__section__nom')

        return JsonResponse(list(eleves.values("id", "nom", "post_nom", "matricule")), safe=False)
    except Classe.DoesNotExist:
        return JsonResponse({'error': 'Classe introuvable'}, status=404)


@login_required
def get_classes(request, section_id, option_id=None):
    try:
        # Vérifier les permissions de la section
        section = Section.objects.get(id=section_id)
        if not check_section_access(request.user, section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Convertir option_id en None si nécessaire
        option_id = None if option_id in ['null', ''] else option_id

        # Appliquer le filtrage selon les permissions
        if option_id is not None:
            classes = Classe.objects.filter(
                section_id=section_id,
                option_id=option_id
            ).order_by('nom')
        else:
            classes = Classe.objects.filter(
                section_id=section_id,
                option__isnull=True
            ).order_by('nom')

        if not (request.user.is_superuser or request.user.role == 'admin'):
            classes = filter_by_user_role(classes, request.user, 'section__nom')

        return JsonResponse({'classes': list(classes.values('id', 'nom'))})
    except Section.DoesNotExist:
        return JsonResponse({'error': 'Section introuvable'}, status=404)


@login_required
def get_eleve_by_matricule(request, matricule):
    try:
        eleve = Eleve.objects.get(matricule=matricule)

        # Vérifier les permissions de la section de l'élève
        if not check_section_access(request.user, eleve.classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        data = {
            'id': eleve.id,
            'nom': f"{eleve.nom} {eleve.post_nom}",
            'classe_id': eleve.classe.id,
            'classe_nom': eleve.classe.nom,
            'section_id': eleve.classe.section.id,
            'section_nom': eleve.classe.section.nom,
            'option_id': eleve.classe.option.id if eleve.classe.option else None,
            'option_nom': eleve.classe.option.nom if eleve.classe.option else None
        }
        return JsonResponse(data)
    except Eleve.DoesNotExist:
        return JsonResponse({'error': 'Élève introuvable'}, status=404)
    # *************************************************
    # API pour récupérer le solde restant d'un élève *
    # *************************************************


@login_required
def get_dashboard_stats(request):
    """
    API AJAX pour charger dynamiquement les statistiques du dashboard selon la période.
    """
    period = request.GET.get('period', 'month')  # Par défaut: mois
    today = datetime.today()

    start_date = None
    end_date = None

    if period == 'month':
        start_date = today.replace(day=1)
        end_date = (start_date + relativedelta(months=1)) - datetime.timedelta(days=1)
    elif period == 'trimestre':
        quarter = (today.month - 1) // 3 + 1
        start_month = (quarter - 1) * 3 + 1
        start_date = datetime(today.year, start_month, 1)
        end_date = (start_date + relativedelta(months=3)) - datetime.timedelta(days=1)
    elif period == 'year':
        start_date = datetime(today.year, 1, 1)
        end_date = datetime(today.year, 12, 31)

    # Récupérer tous les élèves
    eleves = Eleve.objects.all()
    total_eleves = eleves.count() if eleves.exists() else 0

    # Paiements dans la période sélectionnée
    paiements = Paiement.objects.filter(date_paiement__range=[start_date, end_date])
    total_recettes = paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal(0)

    # Dépenses dans la période
    depenses = Depense.objects.filter(date_depense__range=[start_date, end_date])
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or Decimal(0)

    # Solde
    solde = total_recettes - total_depenses

    # Taux de paiement et taux de retard
    total_frais_dus = Decimal(0)
    for eleve in eleves:
        frais_classe = Frais.objects.filter(classes=eleve.classe).aggregate(Sum('montant'))['montant__sum'] or Decimal(
            0)
        total_frais_dus += frais_classe

    total_paye = paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal(0)
    taux_paiement = (total_paye / total_frais_dus * Decimal(100)) if total_frais_dus > 0 else Decimal(0)
    taux_retard = Decimal(100) - taux_paiement

    # Évolution vs période précédente
    previous_start_date = None
    previous_end_date = None

    if period == 'month':
        previous_month = today.replace(day=1) - datetime.timedelta(days=1)
        previous_start_date = previous_month.replace(day=1)
        previous_end_date = (previous_start_date + relativedelta(months=1)) - datetime.timedelta(days=1)
    elif period == 'trimestre':
        previous_start_date = start_date - relativedelta(months=3)
        previous_end_date = start_date - datetime.timedelta(days=1)
    elif period == 'year':
        previous_start_date = datetime(today.year - 1, 1, 1)
        previous_end_date = datetime(today.year - 1, 12, 31)

    # Paiements période précédente
    previous_paiements = Paiement.objects.filter(
        date_paiement__range=[previous_start_date, previous_end_date]
    )
    previous_total_recettes = previous_paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal(0)

    # Calcul de l'évolution
    evolution_recettes = Decimal(0)
    if previous_total_recettes > 0:
        evolution_recettes = ((total_recettes - previous_total_recettes) / previous_total_recettes) * Decimal(100)

    # Évolution du taux de retard
    previous_paiements_global = Paiement.objects.filter(
        eleve__in=Eleve.objects.all(),
        date_paiement__range=[previous_start_date, previous_end_date]
    ).aggregate(Sum('montant_paye'))['montant_paye__sum'] or Decimal(0)

    previous_total_frais_dus = Decimal(0)
    for eleve in Eleve.objects.all():
        previous_total_frais_dus += Frais.objects.filter(classes=eleve.classe).aggregate(Sum('montant'))[
                                        'montant__sum'] or Decimal(0)

    previous_taux_paiement = (previous_total_recettes / previous_total_frais_dus * Decimal(
        100)) if previous_total_frais_dus > 0 else Decimal(0)
    previous_taux_retard = Decimal(100) - previous_taux_paiement

    evolution_taux_retard = Decimal(0)
    if previous_taux_retard != Decimal(0):
        evolution_taux_retard = ((taux_retard - previous_taux_retard) / previous_taux_retard) * Decimal(100)
    else:
        evolution_taux_retard = Decimal(0) if taux_retard == Decimal(0) else Decimal(100)

    return JsonResponse({
        "total_eleves": total_eleves,
        "total_recettes": float(total_recettes),
        "total_depenses": float(total_depenses),
        "solde": float(solde),
        "taux_retard": float(taux_retard),
        "evolution_taux_retard": float(evolution_taux_retard),
        "evolution_solde": float(evolution_recettes),
    })


@login_required
def get_solde(request, eleve_id):
    try:
        eleve = Eleve.objects.get(id=eleve_id)
        paiements = Paiement.objects.filter(eleve=eleve)
        total_paye = sum(p.montant_paye for p in paiements)
        total_frais = sum(f.montant for f in Frais.objects.filter(classes=eleve.classe))
        solde = total_frais - total_paye
        return JsonResponse({"solde": float(solde)})
    except Eleve.DoesNotExist:
        return JsonResponse({"error": "Élève introuvable."}, status=404)


# Dans views.py
@login_required
def get_historique_paiements(request, eleve_id):
    try:
        historique = Paiement.objects.filter(
            eleve_id=eleve_id
        ).select_related('frais').values(
            'id',  # Ajout de ce champ crucial
            'mois',
            'frais__nom',
            'montant_paye',
            'solde_restant',
            'date_paiement'
        ).order_by('date_paiement')

        # Convertir Decimal en float pour JSON
        historique_list = list(historique)
        for item in historique_list:
            if isinstance(item['montant_paye'], Decimal):
                item['montant_paye'] = float(item['montant_paye'])
            if isinstance(item['solde_restant'], Decimal):
                item['solde_restant'] = float(item['solde_restant'])

        return JsonResponse(historique_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# API pour récupérer le prochain mois à payer pour un élève et un frais
@login_required
def get_mois_suivant(request, eleve_id, frais_id):
    try:
        eleve = Eleve.objects.get(id=eleve_id)
        frais = Frais.objects.get(id=frais_id)

        mois_payes = list(Paiement.objects.filter(
            eleve=eleve,
            frais=frais
        ).values_list('mois', flat=True))

        tranches_payees = list(Paiement.objects.filter(
            eleve=eleve,
            frais=frais
        ).values_list('tranche', flat=True))

        mois_ordre = [m[0] for m in MoisPaiement.choices]

        if frais.type_frais == "Mensuel":
            for mois in mois_ordre:
                if mois not in mois_payes:
                    return JsonResponse({
                        'mois_suivant': mois,
                        'mois_payes': mois_payes
                    })

            return JsonResponse({'message': "Tous les mois ont été payés"})

        elif frais.type_frais == "Trimestriel":
            tranches_disponibles = ["1ère Tranche", "2ème Tranche", "3ème Tranche"]
            for tranche in tranches_disponibles:
                if tranche not in tranches_payees:
                    return JsonResponse({
                        'tranche_suivante': tranche,
                        'tranches_payees': tranches_payees
                    })

            return JsonResponse({'message': "Toutes les tranches ont été payées"})

        elif frais.type_frais == "Annuel":
            return JsonResponse({'message': "Ce frais est annuel."})

    except Eleve.DoesNotExist:
        return JsonResponse({'error': 'Élève introuvable.'}, status=404)
    except Frais.DoesNotExist:
        return JsonResponse({'error': 'Frais introuvable.'}, status=404)


# ✅ API pour obtenir le solde restant d'un élève
@login_required
def get_solde_restant(request, eleve_id, frais_id):
    try:
        eleve = Eleve.objects.get(id=eleve_id)
        frais = Frais.objects.get(id=frais_id)

        # Récupérer tous les paiements pour cet élève et ce frais
        paiements = Paiement.objects.filter(
            eleve=eleve,
            frais=frais
        ).order_by('date_paiement')

        # Récupérer le dernier mois payé
        mois_ordre = MoisPaiement.values
        mois_payes = list(paiements.values_list('mois', flat=True))

        # Déterminer le mois actuel ou le mois à évaluer
        mois_cible = request.GET.get('mois_cible')

        if mois_cible and mois_cible in mois_ordre:
            mois_index = mois_ordre.index(mois_cible)

            # Vérifier s'il y a un mois précédent
            if mois_index > 0:
                mois_precedent = mois_ordre[mois_index - 1]
                paiement_precedent = paiements.filter(mois=mois_precedent).first()

                if paiement_precedent and paiement_precedent.solde_restant > Decimal('0'):
                    # Calculer le montant net avec le solde restant du mois précédent
                    montant_net = frais.montant + paiement_precedent.solde_restant
                    solde_apres_paiement = montant_net - Decimal(request.GET.get('montant_paye', '0'))
                    return JsonResponse({
                        "solde": float(solde_apres_paiement),
                        "montant_net": float(montant_net),
                        "solde_precedent": float(paiement_precedent.solde_restant)
                    })

        # Cas normal sans solde restant du mois précédent
        return JsonResponse({"solde": float(frais.montant)})

    except Eleve.DoesNotExist:
        return JsonResponse({"error": "Élève introuvable."}, status=404)
    except Frais.DoesNotExist:
        return JsonResponse({"error": "Frais introuvable."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ API AJAX pour récupérer les frais d'une classe spécifique

@login_required
def get_frais(request, classe_id):
    """ Retourne les frais disponibles pour une classe spécifique """
    try:
        classe = Classe.objects.get(id=classe_id)
        frais = list(Frais.objects.filter(classes=classe).values("id", "nom", "montant", "type_frais"))
        if frais:
            return JsonResponse(frais, safe=False)
        else:
            return JsonResponse({"message": "Aucun frais disponible pour cette classe."}, status=404)
    except Classe.DoesNotExist:
        return JsonResponse({"error": "Classe introuvable."}, status=400)


@login_required
def get_frais_details(request, frais_id):
    try:
        frais = Frais.objects.get(id=frais_id)
        return JsonResponse({
            "type_frais": frais.type_frais,
            "montant": float(frais.montant),
            "nom": frais.nom
        })
    except Frais.DoesNotExist:
        return JsonResponse({"error": "Frais introuvable."}, status=404)


# ✅ API AJAX pour récupérer l'historique des paiements d'un élève

# views.py


from datetime import datetime
import json


@login_required
def suivi_financier(request):
    form = SuiviFinancierForm(request.GET or None)
    paiements = Paiement.objects.all()
    depenses = Depense.objects.all()

    # Appliquer un SEUL filtre à la fois
    if form.is_valid():
        date = form.cleaned_data.get('date')
        mois = form.cleaned_data.get('mois')
        annee_scolaire = form.cleaned_data.get('annee_scolaire')
        section = form.cleaned_data.get('section')
        option = form.cleaned_data.get('option')
        classe = form.cleaned_data.get('classe')

        if date:
            paiements = paiements.filter(date_paiement=date)
            depenses = depenses.filter(date_depense=date)
        elif mois:
            paiements = paiements.filter(mois=mois)
            depenses = depenses.filter(date_depense__month=mois)
        elif annee_scolaire:
            paiements = paiements.filter(frais__annee_scolaire=annee_scolaire)
            depenses = depenses.filter(annee_scolaire=annee_scolaire)
        elif classe:
            paiements = paiements.filter(eleve__classe=classe)
        elif option:
            paiements = paiements.filter(eleve__classe__option=option)
        elif section:
            paiements = paiements.filter(eleve__classe__section=section)

    total_paiements = paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_paiements - total_depenses

    # Données pour le graphique : Évolution des recettes et dépenses par mois
    today = datetime.today()
    start_date = today.replace(year=today.year - 1, day=1)  # 12 mois

    # Récupérer les paiements par mois
    evolution_paiements = (
        paiements.annotate(month=TruncMonth("date_paiement"))
        .values("month")
        .annotate(total=Sum("montant_paye"))
        .order_by("month")
    )

    # Récupérer les dépenses par mois
    evolution_depenses = (
        depenses.annotate(month=TruncMonth("date_depense"))
        .values("month")
        .annotate(total=Sum("montant"))
        .order_by("month")
    )

    # Créer un dictionnaire avec les totaux par mois
    from collections import defaultdict
    monthly_data = defaultdict(lambda: {"paiements": 0, "depenses": 0})

    for item in evolution_paiements:
        month_key = item["month"].strftime("%Y-%m")
        monthly_data[month_key]["paiements"] = float(item["total"])

    for item in evolution_depenses:
        month_key = item["month"].strftime("%Y-%m")
        monthly_data[month_key]["depenses"] = float(item["total"])

    # Calculer le solde et trier les mois
    chart_data = []
    for month in sorted(monthly_data.keys()):
        row = monthly_data[month]
        row["solde"] = row["paiements"] - row["depenses"]
        row["month"] = month
        chart_data.append(row)

    chart_json = json.dumps(chart_data)

    context = {
        'form': form,
        'paiements': paiements,
        'depenses': depenses,
        'total_paiements': total_paiements,
        'total_depenses': total_depenses,
        'solde': solde,

        # Pour les listes déroulantes
        'sections': Section.objects.all(),
        'classes': Classe.objects.all(),
        'options': Option.objects.all(),
        'annees_scolaires': AnneeScolaire.objects.all(),
        'MoisPaiement': MoisPaiement.choices,
        'chart_json': chart_json
    }

    return render(request, 'gestion/suivi_financier.html', context)


@login_required
def ajouter_depense(request):
    """
    Vue pour ajouter une nouvelle dépense en prenant en compte l'année scolaire courante.
    """
    # Récupérer ou créer l'année scolaire courante
    annee_scolaire_courante = AnneeScolaire.obtenir_annee_courante()

    if request.method == "POST":
        form = DepenseForm(request.POST)
        if form.is_valid():
            # Associer l'année scolaire courante à la dépense
            depense = form.save(commit=False)
            depense.annee_scolaire = annee_scolaire_courante
            depense.save()

            messages.success(request, "✅ Dépense ajoutée avec succès !")
            return redirect('liste_depenses')
    else:
        # Pré-remplir le champ 'annee_scolaire' avec l'année scolaire courante
        initial_data = {'annee_scolaire': annee_scolaire_courante}
        form = DepenseForm(initial=initial_data)

    return render(request, 'gestion/ajouter_depense.html', {'form': form})


# views.py


from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Paiement, Depense
from datetime import datetime
import json

from django.db.models.functions import TruncMonth

# views.py

from django.shortcuts import render
from .models import Paiement, Depense, Classe, Frais, AnneeScolaire
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from collections import defaultdict
import json


@login_required
def bilan_financier(request):
    annee_courante = request.GET.get('annee_scolaire') or '2024-2025'

    # Base Querysets
    paiements = Paiement.objects.filter(frais__annee_scolaire__annee=annee_courante)
    depenses = Depense.objects.filter(annee_scolaire__annee=annee_courante)

    # Calculs de base
    total_encaisse = paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
    solde_final = total_encaisse - total_depenses

    # Répartition des dépenses par motif
    repartition_depenses = (
        depenses.values('motif')
        .annotate(total=Sum('montant'))
        .order_by('-total')[:10]
    )

    # Évolution mensuelle des recettes et dépenses
    evolution_paiements = (
        paiements.annotate(mois_paiement=TruncMonth('date_paiement'))
        .values('mois_paiement')
        .annotate(total_recette=Sum('montant_paye'))
        .order_by('mois_paiement')
    )
    evolution_depenses = (
        depenses.annotate(mois_depense=TruncMonth('date_depense'))
        .values('mois_depense')
        .annotate(total_depense=Sum('montant'))
        .order_by('mois_depense')
    )

    # Fusionner les deux séries en un seul dictionnaire
    monthly_data = defaultdict(lambda: {"recette": 0, "depense": 0})

    for item in evolution_paiements:
        mois_key = item["mois_paiement"].strftime("%Y-%m") if item["mois_paiement"] else "Inconnu"
        monthly_data[mois_key]["recette"] = float(item["total_recette"])

    for item in evolution_depenses:
        mois_key = item["mois_depense"].strftime("%Y-%m") if item["mois_depense"] else "Inconnu"
        monthly_data[mois_key]["depense"] = float(item["total_depense"])

    chart_labels = sorted(monthly_data.keys())
    chart_recettes = [monthly_data[m]["recette"] for m in chart_labels]
    chart_depenses = [monthly_data[m]["depense"] for m in chart_labels]
    chart_solde = [r - d for r, d in zip(chart_recettes, chart_depenses)]

    chart_json = json.dumps({
        "labels": chart_labels,
        "recettes": chart_recettes,
        "depenses": chart_depenses,
        "solde": chart_solde
    })

    # Top 5 des frais les plus payés
    top_frais = (
        paiements.values('frais__nom')
        .annotate(total=Sum('montant_paye'))
        .order_by('-total')[:5]
    )

    # Taux d'élèves en retard
    eleves_en_retard = (
        Eleve.objects.filter(paiement__solde_restant__gt=0, paiement__frais__annee_scolaire__annee=annee_courante)
        .distinct()
        .count()
    )
    total_eleves = Eleve.objects.filter(
        paiement__frais__annee_scolaire__annee=annee_courante
    ).distinct().count()

    taux_retard = round((eleves_en_retard / total_eleves * 100), 2) if total_eleves > 0 else 0

    # Recettes par classe
    repartition_par_classe = (
        paiements.values('eleve__classe__nom')
        .annotate(total=Sum('montant_paye'), count=Count('id'))
        .order_by('-total')
    )

    context = {
        'total_encaisse': total_encaisse,
        'total_depenses': total_depenses,
        'solde_final': solde_final,

        'repartition_depenses': repartition_depenses,
        'top_frais': top_frais,
        'taux_retard': taux_retard,
        'repartition_par_classe': repartition_par_classe,

        'chart_json': chart_json,
        'annee_courante': annee_courante,
        'annees_scolaires': AnneeScolaire.objects.all(),
    }

    return render(request, 'gestion/bilan_financier.html', context)


"""def bilan_financier(request):

    total_encaisse = Paiement.objects.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0
    total_depenses = Depense.objects.aggregate(Sum('montant'))['montant__sum'] or 0
    solde_final = total_encaisse - total_depenses

    return render(request, 'gestion/bilan_financier.html', {
        'total_encaisse': total_encaisse,
        'total_depenses': total_depenses,
        'solde_final': solde_final
    })"""


@login_required
def liste_depenses(request):
    mois = range(1, 13)  # ✅ Liste de 1 à 12 pour les mois
    depenses = Depense.objects.all()
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum']

    return render(request, 'gestion/liste_depenses.html',
                  {'depenses': depenses, 'mois': mois, 'total_depenses': total_depenses})


"""@login_required
def ajouter_depense(request):

    if request.method == "POST":
        form = DepenseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Dépense ajoutée avec succès !")
            return redirect('liste_depenses')
    else:
        form = DepenseForm()

    return render(request, 'gestion/ajouter_depense.html', {'form': form})
"""


@login_required
def supprimer_depense(request, depense_id):
    """ Supprimer une dépense """
    depense = get_object_or_404(Depense, id=depense_id)
    if request.method == "POST":
        depense.delete()
        messages.success(request, "✅ Dépense supprimée avec succès !")
        return redirect('liste_depenses')

    return render(request, 'gestion/supprimer_depense.html', {'depense': depense})


def statistiques(request):
    user = request.user
    annee_scolaire = AnneeScolaire.obtenir_annee_courante()

    # Debugging
    print("Rôle de l'utilisateur:", user.role)

    # Filtrage des statistiques selon le rôle de l'utilisateur
    sections = []
    if user.role == "admin":
        eleves = Eleve.objects.all()
        paiements = Paiement.objects.filter(frais__annee_scolaire=annee_scolaire)
        depenses = Depense.objects.filter(annee_scolaire=annee_scolaire)
    else:
        if user.role == "directeur":
            sections = ["Maternelle", "Primaire"]
        elif user.role == "prefet":
            sections = ["Secondaire", "Humanités"]
        elif user.role == "prefet_itm":
            sections = ["ITM"]

        eleves = Eleve.objects.filter(classe__section__nom__in=sections)
        paiements = Paiement.objects.filter(eleve__classe__section__nom__in=sections,
                                            frais__annee_scolaire=annee_scolaire)

        # Si sections est vide, inclure toutes les dépenses de l'année scolaire courante
        if sections:
            depenses = Depense.objects.filter(section__nom__in=sections, annee_scolaire=annee_scolaire)
        else:
            depenses = Depense.objects.filter(annee_scolaire=annee_scolaire)

    # Debugging
    print("Sections:", sections)
    print("Année scolaire courante:", annee_scolaire)
    print("Dépenses filtrées:", depenses)

    # Calcul des statistiques
    total_eleves = eleves.count()
    total_paiements = paiements.aggregate(total=Sum("montant_paye"))["total"] or 0
    total_depenses = depenses.aggregate(total=Sum("montant"))["total"] or 0
    solde_global = total_paiements - total_depenses

    # Calcul du total des frais dus
    # Calcul des frais dus
    total_frais_dus = 0
    for eleve in eleves:
        # Récupérer les frais associés à la classe de l'élève
        frais_classe = Frais.objects.filter(
            classes=eleve.classe,
            annee_scolaire=annee_scolaire
        ).aggregate(total=Sum("montant"))["total"] or 0

        # Récupérer les frais associés à la section de l'élève
        frais_section = Frais.objects.filter(
            section=eleve.section,
            annee_scolaire=annee_scolaire
        ).aggregate(total=Sum("montant"))["total"] or 0

        # Ajouter les frais de la classe et de la section
        total_frais_dus += frais_classe + frais_section

        # Calcul du taux de paiement
        taux_paiement = (total_paiements / total_frais_dus) * 100 if total_frais_dus > 0 else 0

    repartition_par_sexe = (
        eleves.values("sexe")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    repartition_par_section = (
        eleves.values("classe__section__nom")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    context = {
        "paiements": {"total_paiements": total_paiements},
        "depenses": {"total_depenses": total_depenses},
        "total_eleves": total_eleves,
        "solde_global": solde_global,
        "repartition_par_sexe": json.dumps(list(repartition_par_sexe), cls=DjangoJSONEncoder),
        "repartition_par_section": json.dumps(list(repartition_par_section), cls=DjangoJSONEncoder),

        "sections": Section.objects.all(),
        "taux_paiement": taux_paiement,  # Ajout du taux de paiement au contexte
    }

    # Debugging
    print("Contexte passé au template:", context)

    return render(request, "gestion/statistiques.html", context)


def dashboard(request):
    user = request.user
    today = datetime.now()
    mois_courant = str(today.month)
    annee_courante = today.year
    # mois_precedent = today - datetime.timedelta(days=today.day)

    # Récupérer l'année scolaire courante
    annee_scolaire = AnneeScolaire.obtenir_annee_courante()

    # Initialisation du formulaire
    form = FiltragePaiementForm(request.GET or None)

    # Filtrage des paiements et élèves
    paiements = Paiement.objects.filter(frais__annee_scolaire=annee_scolaire)
    eleves_recap_query = Eleve.objects.all()

    # Application des filtres
    form = FiltragePaiementForm(request.GET)  # Charger les critères de filtrage

    if form.is_valid():
        # Filtres appliqués si le formulaire est valide
        if form.cleaned_data['section']:
            paiements = paiements.filter(eleve__classe__section=form.cleaned_data['section'])

        if form.cleaned_data['option']:
            paiements = paiements.filter(eleve__classe__option=form.cleaned_data['option'])

        if form.cleaned_data['classe']:
            paiements = paiements.filter(eleve__classe=form.cleaned_data['classe'])

        if form.cleaned_data['frais']:
            paiements = paiements.filter(frais=form.cleaned_data['frais'])

        if form.cleaned_data['mois']:
            paiements = paiements.filter(mois=form.cleaned_data['mois'])

        if form.cleaned_data['matricule']:
            paiements = paiements.filter(eleve__matricule__icontains=form.cleaned_data['matricule'])

    # 1. Statistiques de base
    total_eleves = eleves_recap_query.count()
    total_recettes = paiements.aggregate(total=Sum("montant_paye"))["total"] or 0
    depenses = Depense.objects.all()
    # Calcul du total des dépenses pour l'année scolaire courante
    total_depenses = depenses.filter(annee_scolaire=annee_scolaire).aggregate(total=Sum("montant"))["total"] or \
                     depenses.aggregate(Sum('montant'))['montant__sum'] or 0

    chiffre_affaires = total_recettes - total_depenses

    # 2. Calcul des retards
    eleves_en_retard_count = Eleve.objects.filter(
        Q(paiement__solde_restant__gt=0) & Q(paiement__frais__annee_scolaire=annee_scolaire)
    ).distinct().count()

    # Pourcentage d'élèves en retard
    taux_retard = (eleves_en_retard_count / total_eleves) * 100 if total_eleves > 0 else 0

    # 3. Analyse Financière Avancée
    # Prévisions de trésorerie (6 mois)
    date_fin = today + relativedelta(months=6)
    paiements_futurs = (
        paiements.filter(date_paiement__range=[today, date_fin])
        .annotate(mois_calcule=TruncMonth('date_paiement'))
        .values('mois_calcule')
        .annotate(total=Sum('montant_paye'))
        .order_by('mois_calcule')
    )
    paiements_mensuels = (
        paiements.values('mois')
        .annotate(total=Sum('montant_paye'))
        .order_by('mois')
    )
    # Formatage des prévisions
    previsions_tresorerie = defaultdict(float)
    for pf in paiements_futurs:
        mois = pf['mois_calcule'].strftime("%Y-%m")
        previsions_tresorerie[mois] = float(pf['total'] or 0)

    # Comparatif période à période
    # Mois précédent
    mois_precedent = today - relativedelta(months=1)
    recette_mois_precedent = paiements.filter(
        date_paiement__month=mois_precedent.month,
        date_paiement__year=mois_precedent.year
    ).aggregate(total=Sum("montant_paye"))["total"] or 0

    # Année précédente
    annee_precedente = today - relativedelta(years=1)
    recette_annee_precedente = paiements.filter(
        date_paiement__month=today.month,
        date_paiement__year=annee_precedente.year
    ).aggregate(total=Sum("montant_paye"))["total"] or 0

    # Carte thermique des paiements par classe
    retards_par_classe = (
        paiements.filter(solde_restant__gt=0)
        .values('eleve__classe__nom')
        .annotate(total_retard=Sum('solde_restant'), count=Count('id'))
        .order_by('-total_retard')
    )

    heatmap_data = [
        {
            'classe': item['eleve__classe__nom'],
            'montant_retard': float(item['total_retard'] or 0),
            'nombre_eleves': item['count']
        }
        for item in retards_par_classe
    ]

    # Top 5 des frais les plus payés avec tendances
    top_frais = (
        paiements.values('frais__nom')
        .annotate(total=Sum('montant_paye'), count=Count('id'))
        .order_by('-total')[:5]
    )

    tendances_frais = []
    for frais in top_frais:
        nom_frais = frais['frais__nom']
        total_actuel = frais['total']

        total_mois_precedent = paiements.filter(
            frais__nom=nom_frais,
            date_paiement__month=mois_precedent.month,
            date_paiement__year=mois_precedent.year
        ).aggregate(total=Sum("montant_paye"))["total"] or 0

        evolution = ((
                             total_actuel - total_mois_precedent) / total_mois_precedent * 100) if total_mois_precedent > 0 else 100

        # Conversion explicite des valeurs Decimal en float
        tendances_frais.append({
            'nom': nom_frais,
            'total': float(total_actuel),  # Convertir Decimal en float
            'evolution': float(round(evolution, 2)),  # Convertir Decimal en float
            'tendance': 'up' if evolution >= Decimal(0) else 'down'
        })

    # Évolution des paiements par mois
    paiements_mensuels = (
        paiements.annotate(mois_calcule=TruncMonth("date_paiement"))
        .values("mois_calcule")
        .annotate(total=Sum("montant_paye"))
        .order_by("mois_calcule")
    )
    stats = {
        'total_paye': paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0,  # Total payé
        'nombre_paiements': paiements.count(),  # Nombre total de paiements
        'par_frais': paiements.values('frais__nom').annotate(total=Sum('montant_paye')),  # Montants groupés par frais
        'par_mois': paiements.values('mois').annotate(total=Sum('montant_paye')),  # Montants groupés par mois
    }

    # Répartition des élèves par section
    eleves_par_section = (
        eleves_recap_query.values("classe__section__nom")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Liste des élèves avec leurs paiements
    eleves_recap = eleves_recap_query.annotate(
        montant_total_paye=Sum("paiement__montant_paye"),
        solde_restant=Sum("paiement__solde_restant")
    ).values("nom", "classe__nom", "montant_total_paye", "solde_restant")

    # Conversion des données en JSON
    top_frais_json = json.dumps(tendances_frais)

    # Contexte complet
    context = {
        "form": form,
        "total_eleves": total_eleves,
        "total_recettes": total_recettes,
        "total_depenses": total_depenses,
        "chiffre_affaires": chiffre_affaires,
        "taux_retard": taux_retard,

        # Nouvelles données d'analyse financière
        "previsions_tresorerie": dict(previsions_tresorerie),
        "recette_mois_precedent": recette_mois_precedent,
        "recette_annee_precedente": recette_annee_precedente,
        "heatmap_data": heatmap_data,
        "top_frais": top_frais_json,

        # Données existantes
        "paiements_mensuels": paiements_mensuels,
        "eleves_par_section": eleves_par_section,
        "eleves_recap": eleves_recap,
        "role_message": f"Bienvenue, {user.first_name}.",
        "annee_scolaire": annee_scolaire,
        'stats': stats,  # Envoyer les statistiques au templat
        'paiements_mensuels': paiements_mensuels,
    }

    return render(request, "gestion/dashboard.html", context)


@login_required
def menu_sections(request):
    user = request.user
    sections = {}

    # Mapping des sections selon le rôle de l'utilisateur
    role_mapping = {
        "admin": ["Maternelle", "Primaire", "Secondaire", "Humanités", "ITM"],
        "directeur": ["Maternelle", "Primaire"],
        "prefet": ["Secondaire", "Humanités"],
        "prefet_itm": ["ITM"]
    }

    # Récupérer toutes les sections autorisées
    allowed_sections = []
    if user.is_superuser or user.role == "admin":
        allowed_sections = Section.objects.all()
    elif user.role in role_mapping:
        allowed_sections = Section.objects.filter(nom__in=role_mapping[user.role])

    # Construire la structure filtrée
    for section in allowed_sections:
        section_data = {}

        # Filtrer les options de la section
        options = Option.objects.filter(section=section)
        if options.exists():
            section_data["Options"] = {}
            for option in options:
                section_data["Options"][option.nom] = Classe.objects.filter(option=option)
        else:
            section_data = Classe.objects.filter(section=section)

        sections[section.nom] = section_data

    return {"sections": sections}

    return {"sections": sections}


# Mapping des mois numériques (interface utilisateur) vers les noms des mois dans MoisPaiement
MOIS_MAPPING = {
    "1": MoisPaiement.SEPTEMBRE,
    "2": MoisPaiement.OCTOBRE,
    "3": MoisPaiement.NOVEMBRE,
    "4": MoisPaiement.DECEMBRE,
    "5": MoisPaiement.JANVIER,
    "6": MoisPaiement.FEVRIER,
    "7": MoisPaiement.MARS,
    "8": MoisPaiement.AVRIL,
    "9": MoisPaiement.MAI,
    "10": MoisPaiement.JUIN,
}


@login_required
def details_classe(request, classe_id):
    # Récupérer la classe actuelle
    classe = get_object_or_404(Classe, id=classe_id)
    eleves = Eleve.objects.filter(classe=classe).select_related("parent").prefetch_related("paiement_set")
    frais = Frais.objects.filter(classes=classe)

    # Mois disponibles
    mois_de_paiement = MoisPaiement
    # Récupérer les paiements associés aux élèves de cette classe
    paiements = Paiement.objects.filter(eleve__classe=classe)

    # Appliquer les filtres si pertinents
    frais_selectionne = request.GET.get('frais')
    mois_selectionne = request.GET.get('mois')
    tranche_selectionnee = request.GET.get('tranche')

    if frais_selectionne:
        frais = frais.filter(id=frais_selectionne)
        paiements = paiements.filter(frais_id=frais_selectionne)
    if mois_selectionne:
        paiements = paiements.filter(mois=mois_selectionne)
    if tranche_selectionnee:
        paiements = paiements.filter(tranche=tranche_selectionnee)

    # Calculer le dernier mois payé pour chaque élève
    paiements_recents = paiements.values('eleve__id', 'eleve__matricule').annotate(
        mois_recent=Max('mois')
    )
    paiements_dict = {
        paiement['eleve__matricule']: paiement['mois_recent']
        for paiement in paiements_recents
    }

    # Ajouter le dernier mois payé à chaque élève
    for eleve in eleves:
        eleve.mois_recent = paiements_dict.get(eleve.matricule, "-")  # "-" s'il n'y a pas de paiements

    # Statistiques
    stats = {}

    # Nombre d'élèves en ordre/non en ordre
    eleves_en_ordre = paiements.values('eleve_id').distinct().count()
    stats['en_ordre'] = eleves_en_ordre
    stats['non_en_ordre'] = eleves.count() - eleves_en_ordre

    # Montant total payé
    stats['total_paye'] = paiements.aggregate(total=Sum('montant_paye'))['total'] or 0

    # Répartition par type de frais
    stats['par_frais'] = paiements.values('frais__nom').annotate(total=Sum('montant_paye')).order_by('-total')

    # Répartition par mois
    stats['par_mois'] = paiements.values('mois').annotate(
        total=Sum('montant_paye'),
        nombre_eleves=Count('eleve_id', distinct=True)
    ).order_by('mois')

    # Données pour le graphique "Répartition des élèves par section"
    eleves_par_section = (
        eleves.values('classe__section__nom')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Données pour le graphique "Évolution des paiements mensuels"
    paiements_mensuels = (
        paiements.values('mois')
        .annotate(total=Sum('montant_paye'))
        .order_by('mois')
    )

    # Retour au template
    return render(request, 'details_classe.html', {
        'classe': classe,
        'eleves': eleves,
        'frais': frais,
        'mois_de_paiement': mois_de_paiement,
        'stats': stats,
        'eleves_par_section': eleves_par_section,  # Ajout des données pour le graphique
        'paiements_mensuels': paiements_mensuels,  # Ajout des données pour le graphique
    })


def charger_champs_ajax(request):
    """Charge dynamiquement le type de frais ou mois/tranche en fonction des sélections."""
    frais_id = request.GET.get("frais_id")
    if not frais_id:  # Aucun frais sélectionné
        return JsonResponse({"types": [], "mois_tranches": []})

    # Récupérer le frais sélectionné
    frais = get_object_or_404(Frais, id=frais_id)
    type_frais = frais.type_frais

    # Définir la logique en fonction du type de frais
    if type_frais == "Mensuel":
        mois_tranches = [
            {"id": mois, "nom": nom}
            for mois, nom in {
                9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
                1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin"
            }.items()
        ]
    elif type_frais == "Trimestriel":
        mois_tranches = [
            {"id": "1er Trimestre", "nom": "1ère Tranche"},
            {"id": "2ème Trimestre", "nom": "2ème Tranche"},
            {"id": "3ème Trimestre", "nom": "3ème Tranche"}
        ]
    else:  # Annuel
        mois_tranches = []  # Aucune tranche ou mois

    return JsonResponse({
        "type": type_frais,
        "mois_tranches": mois_tranches
    })


@login_required
def export_classe_csv(request, classe_id):
    classe = get_object_or_404(Classe, id=classe_id)
    paiements = Paiement.objects.filter(eleve__classe=classe)

    # Appliquer les mêmes filtres que la vue principale
    frais_id = request.GET.get('frais')
    mois = request.GET.get('mois')
    tranche = request.GET.get('tranche')

    if frais_id:
        paiements = paiements.filter(frais__id=frais_id)
    if mois:
        paiements = paiements.filter(mois=mois)
    if tranche:
        paiements = paiements.filter(tranche=tranche)

    paiements = paiements.order_by('eleve__nom', '-date_paiement')

    response = HttpResponse(content_type='text/csv')
    filename = f"paiements_classe_{classe.nom}"

    # Ajouter les filtres au nom du fichier
    if frais_id or mois or tranche:
        filename += "_filtre"

    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Matricule', 'Nom', 'Post-nom', 'Prénom',
        'Type de frais', 'Mois/Tranche', 'Frais',
        'Montant (FC)', 'Date de paiement', 'Numéro de reçu'
    ])

    for paiement in paiements:
        writer.writerow([
            paiement.eleve.matricule,
            paiement.eleve.nom,
            paiement.eleve.post_nom,
            paiement.eleve.prenom,
            paiement.frais.get_type_frais_display(),
            paiement.mois if paiement.frais.type_frais == "Mensuel" else paiement.tranche,
            paiement.frais.nom,
            paiement.montant_paye,
            paiement.date_paiement.strftime("%d/%m/%Y"),
            paiement.recu_numero
        ])

    return response


@login_required
def export_eleve_csv(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    paiements = Paiement.objects.filter(eleve=eleve).order_by('-date_paiement')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="paiements_{eleve.matricule}.csv"'

    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Type de frais', 'Mois/Tranche', 'Frais',
        'Montant (FC)', 'Date de paiement', 'Numéro de reçu'
    ])

    for paiement in paiements:
        writer.writerow([
            paiement.frais.get_type_frais_display(),
            paiement.mois if paiement.frais.type_frais == "Mensuel" else paiement.tranche,
            paiement.frais.nom,
            paiement.montant_paye,
            paiement.date_paiement.strftime("%d/%m/%Y"),
            paiement.recu_numero
        ])

    return response