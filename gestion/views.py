from gestion.library import *
MOIS_ORDRE = {
    'septembre': 1,
    'octobre': 2,
    'novembre': 3,
    'décembre': 4,
    'janvier': 5,
    'février': 6,
    'mars': 7,
    'avril': 8,
    'mai': 9,
    'juin': 10,
}

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


CustomUser = get_user_model()


class PasswordResetView(View):
    """Vue principale pour la réinitialisation du mot de passe"""
    template_name = 'gestion/password_reset_form.html'
    step = 1  # Étape actuelle (1: vérification, 2: réinitialisation)

    def get(self, request):
        if 'reset_user_id' in request.session:
            self.step = 2
            form = NewPasswordForm()
        else:
            form = PasswordResetForm()

        return render(request, self.template_name, {
            'form': form,
            'step': self.step
        })

    def post(self, request):
        if 'reset_user_id' in request.session:
            # Étape 2: Réinitialisation du mot de passe
            form = NewPasswordForm(request.POST)

            if form.is_valid():
                try:
                    user = CustomUser.objects.get(id=request.session['reset_user_id'])
                    user.set_password(form.cleaned_data['password1'])
                    user.save()

                    del request.session['reset_user_id']
                    messages.success(request, "✅ Mot de passe réinitialisé avec succès !")
                    return redirect('login')

                except CustomUser.DoesNotExist:
                    messages.error(request, "❌ Utilisateur introuvable.")
                    return redirect('password_reset')

        else:
            # Étape 1: Vérification des informations
            form = PasswordResetForm(request.POST)

            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']

                try:
                    user = CustomUser.objects.get(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                        email__iexact=email
                    )
                    request.session['reset_user_id'] = user.id
                    return redirect('password_reset')

                except CustomUser.DoesNotExist:
                    messages.error(request, "❌ Aucun utilisateur trouvé avec ces informations.")

        return render(request, self.template_name, {
            'form': form,
            'step': self.step
        })


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
@admin_required
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
@admin_required
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
    return render(request, 'gestion/detail_utilisateur.html', context)


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


# views.py
@login_required
def changer_annee_scolaire(request):
    if request.method == 'POST':
        annee_id = request.POST.get('annee_scolaire_id')
        try:
            annee = AnneeScolaire.objects.get(id=annee_id)
            request.session['annee_scolaire_id'] = annee.id
            messages.success(request, f"✅ Année changée en {annee.annee}")
        except AnneeScolaire.DoesNotExist:
            messages.error(request, "❌ Année invalide.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# views eleves

@login_required
def valider_documents(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)  # Récupère l'élève correspondant
    return render(request, 'valider_documents.html', {'eleve': eleve})  # Retourne un gabarit


# modiifer eleve
@login_required
@directeur_required
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
@login_required
def liste_eleves(request):
    # Récupérer l'année scolaire active depuis la session
    annee_id = request.session.get('annee_scolaire_id') or request.session.get('annee_scolaire_id')

    if not annee_id:
        # Si aucune année n'est dans la session, utiliser l'année courante
        annee = AnneeScolaire.obtenir_annee_courante()
        annee_id = annee.id
        request.session['annee_scolaire_id'] = annee_id

    # Récupérer les paramètres de filtre
    section_id = request.GET.get('section')
    option_id = request.GET.get('option')
    classe_id = request.GET.get('classe')
    sexe = request.GET.get('sexe')
    matricule = request.GET.get('matricule')

    # Filtrage de base selon les permissions
    if request.user.is_superuser or request.user.role == 'admin':
        # Admin a accès à tous les élèves de l'année sélectionnée
        eleves = Eleve.objects.filter(annee_scolaire_id=annee_id).select_related('annee_scolaire', 'classe')
    else:
        # Utilisateurs non-admin filtrent par sections accessibles
        sections_access = []
        if request.user.role == 'directeur':
            sections_access = ['Maternelle', 'Primaire']
        elif request.user.role == 'prefet':
            sections_access = ['Secondaire', 'Humanités']
        elif request.user.role == 'prefet_itm':
            sections_access = ['ITM']

        eleves = Eleve.objects.filter(
            classe__section__nom__in=sections_access,
            annee_scolaire_id=annee_id
        ).select_related('annee_scolaire', 'classe')

    # Application des filtres supplémentaires
    if section_id:
        section = get_object_or_404(Section, id=section_id)
        if not check_section_access(request.user, section.nom):
            raise PermissionDenied
        eleves = eleves.filter(classe__section_id=section_id)

    if option_id:
        eleves = eleves.filter(classe__option_id=option_id)

    if classe_id:
        eleves = eleves.filter(classe_id=classe_id)

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
        'annee_selectionnee': AnneeScolaire.objects.get(id=annee_id),
        'stats': {
            'total': total_eleves,
            'garcons': garcons,
            'filles': filles
        }
    }

    return render(request, 'gestion/liste_eleves.html', context)


# views.py
@login_required
def ajouter_eleve(request):
    # Toujours utiliser l'année scolaire courante par défaut
    annee_courante = AnneeScolaire.obtenir_annee_courante()

    if request.method == 'POST':
        form = EleveForm(request.POST, user=request.user)
        if form.is_valid():
            eleve = form.save(commit=False)

            # Assigner impérativement l'année scolaire courante
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

            # Recherche du dernier ID utilisé pour cette combinaison dans l'année courante
            derniere_sequence = Eleve.objects.filter(
                matricule__startswith=f"{annee_courte}{initiales}",
                annee_scolaire=annee_courante
            ).order_by('-id').first()

            numero = 1
            if derniere_sequence:
                # Extraction du numéro à partir du matricule existant
                try:
                    numero = int(derniere_sequence.matricule[-3:]) + 1
                except ValueError:
                    numero = 1

            eleve.matricule = f"{annee_courte}{initiales}{numero:03d}"

            # Sauvegarde et création inscription
            eleve.save()

            Inscription.objects.create(
                eleve=eleve,
                annee_scolaire=annee_courante,
                classe=eleve.classe,
                est_reinscription=False
            )

            messages.success(request,
                             f"Nouvel élève {eleve.nom} {eleve.post_nom} ({eleve.matricule}) inscrit avec succès en {eleve.classe.nom}")

            return redirect('details_eleve', eleve.id)
    else:
        form = EleveForm(user=request.user)

    return render(request, 'gestion/ajouter_eleve.html', {
        'form': form,
        'annee_courante': annee_courante,
        # Pour le template si besoin d'afficher les années
        'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee')
    })


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
@admin_required
def supprimer_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)
    if request.method == 'POST':
        eleve.delete()
        return redirect('liste_eleves')
    return render(request, 'gestion/supprimer_eleve.html', {'eleve': eleve})



@login_required
def detail_eleve(request, eleve_id):
    """
    Détail d'un élève avec gestion des années scolaires
    Affiche les données même si l'élève n'a pas de paiements pour l'année sélectionnée
    """
    try:
        # 1. Gestion de l'année scolaire
        annee_id = request.session.get('annee_scolaire_id')
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except Exception as e:
        selected_annee = AnneeScolaire.obtenir_annee_courante()
        logger.error(f"Erreur sélection année scolaire: {str(e)}")

    # 2. Récupération de l'élève (sans filtre sur l'année scolaire)
    eleve = get_object_or_404(Eleve, id=eleve_id)

    # 3. Vérifier si l'élève a une inscription pour l'année sélectionnée
    inscription_exists = Eleve.objects.filter(
        id=eleve_id,
        annee_scolaire=selected_annee
    ).exists()

    if not inscription_exists:
        messages.warning(request, f"Cet élève n'est pas inscrit pour l'année scolaire {selected_annee.annee}")

    # 4. Récupération des frais pour l'année et section (même si élève non inscrit)
    frais_query = Frais.objects.filter(
        section=eleve.classe.section,
        annee_scolaire=selected_annee
    )

    frais_mensuels = frais_query.filter(type_frais="Mensuel").order_by('nom')
    frais_trimestriels = frais_query.filter(type_frais="Trimestriel").order_by("tranche", "nom")
    frais_annuels = frais_query.filter(type_frais="Annuel").order_by('nom')

    # 5. Récupération des paiements (vide si pas d'inscription)
    paiements = Paiement.objects.filter(
        eleve=eleve,
        frais__annee_scolaire=selected_annee
    ).select_related('frais').order_by('-date_paiement')

    # 6. Calcul des totaux
    total_paye = paiements.aggregate(total=Sum('montant_paye'))['total'] or 0
    stats_paiements = paiements.values('frais__type_frais').annotate(
        total=Sum('montant_paye'),
        count=Count('id')
    )

    # 7. Initialisation des variables
    paiements_stats = {
        'mensuel': {'count': 0, 'total': 0},
        'trimestriel': {'count': 0, 'total': 0},
        'annuel': {'count': 0, 'total': 0}
    }

    for stat in stats_paiements:
        type_frais = stat['frais__type_frais'].lower()
        if type_frais in paiements_stats:
            paiements_stats[type_frais]['count'] = stat['count']
            paiements_stats[type_frais]['total'] = stat['total'] or 0

    # 8. Mois scolaires
    months = ["Septembre", "Octobre", "Novembre", "Décembre",
              "Janvier", "Février", "Mars", "Avril", "Mai", "Juin"]

    # 9. Contexte
    context = {
        'eleve': eleve,
        'frais_mensuels': frais_mensuels,
        'frais_trimestriels': frais_trimestriels,
        'frais_annuels': frais_annuels,
        'months': months,
        'col_missing_mensuel': range(max(0, 10 - frais_mensuels.count())),
        'col_missing_trimestriel': range(max(0, 3 - frais_trimestriels.count())),
        'paiements': paiements,
        'total_paye': total_paye,
        'paiements_mensuels_count': paiements_stats['mensuel']['count'],
        'paiements_trimestriels_count': paiements_stats['trimestriel']['count'],
        'paiements_annuels_count': paiements_stats['annuel']['count'],
        'dernier_paiement': paiements.first(),
        'annee_courante': selected_annee.annee,
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'selected_annee': selected_annee,
        'user_role': request.user.role,
        'has_inscription': inscription_exists,
    }
    paiements_mensuels = [p for p in context['paiements'] if p.frais.type_frais == 'Mensuel']
    paiements_trimestriels = [p for p in context['paiements'] if p.frais.type_frais == 'Trimestriel']
    print("Mensuels:", [{'mois': p.mois, 'montant': p.montant_paye} for p in paiements_mensuels])
    print("Trimestriels:", [{'tranche': p.tranche, 'montant': p.montant_paye} for p in paiements_trimestriels])

    return render(request, 'details_eleve.html', context)
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


@login_required
def liste_frais(request):
    """Affiche tous les frais scolaires avec filtres hiérarchiques, gestion des droits d'accès et année scolaire"""

    try:
        # 1. Gestion de l'année scolaire
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except Exception as e:
        selected_annee = AnneeScolaire.obtenir_annee_courante()
        logger.error(f"Erreur sélection année scolaire: {str(e)}")

    # 2. Récupérer les paramètres de filtre
    section_id = request.GET.get('section')
    option_id = request.GET.get('option')
    classe_id = request.GET.get('classe')

    # 3. Récupérer les sections accessibles par l'utilisateur
    accessible_sections = get_accessible_sections(request.user)

    # 4. Base Query: frais liés aux sections accessibles pour l'année scolaire sélectionnée
    frais_base = Frais.objects.filter(
        (Q(section__in=accessible_sections) | Q(classes__section__in=accessible_sections)),
        annee_scolaire=selected_annee
    ).distinct().select_related('section').prefetch_related('classes')

    # 5. Appliquer les filtres hiérarchiques
    if section_id and section_id.isdigit():
        frais_base = frais_base.filter(
            Q(section_id=int(section_id)) | Q(classes__section_id=int(section_id))
        ).distinct()

    if option_id and option_id.isdigit():
        frais_base = frais_base.filter(classes__option_id=int(option_id)).distinct()

    if classe_id and classe_id.isdigit():
        frais_base = frais_base.filter(classes__id=int(classe_id)).distinct()

    # 6. Récupérer les données pour les listes déroulantes
    sections = Section.objects.all() if request.user.is_superuser or request.user.role == 'admin' \
        else accessible_sections.distinct()

    options = Option.objects.filter(classes__frais__in=frais_base).distinct()
    classes = Classe.objects.filter(frais__in=frais_base).distinct()

    # 7. Filtrage supplémentaire des options et classes si section sélectionnée
    if section_id and section_id.isdigit():
        options = options.filter(classes__section_id=int(section_id)).distinct()
        classes = classes.filter(section_id=int(section_id)).distinct()

    # 8. Filtrage supplémentaire des classes si option sélectionnée
    if option_id and option_id.isdigit():
        classes = classes.filter(option_id=int(option_id)).distinct()

    # 9. Calcul des statistiques
    total_frais = frais_base.aggregate(total=Sum('montant'))['total'] or 0
    frais_par_section = frais_base.filter(section__in=accessible_sections).count()

    classes_concernees = set()
    for f in frais_base:
        classes_concernees.update(c.id for c in f.classes.all())
    nb_classes_concernees = len(classes_concernees)

    # 10. Préparation du contexte
    context = {
        'frais': frais_base,
        'sections': sections,
        'options': options,
        'classes': classes,
        'total_frais': total_frais,
        'frais_par_section': frais_par_section,
        'nb_classes_concernees': nb_classes_concernees,
        'annee_courante': selected_annee.annee,
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'selected_annee': selected_annee,
        'user_role': request.user.role,
        'request': request,  # Conservé pour compatibilité avec l'ancien template
    }

    return render(request, 'gestion/liste_frais.html', context)

# views.py


@login_required
def ajouter_frais(request):
    """Vue pour ajouter un ou plusieurs frais scolaires"""
    # 1. Initialisation de l'année scolaire
    try:
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except Exception as e:
        selected_annee = AnneeScolaire.obtenir_annee_courante()
        logger.error(f"Erreur sélection année scolaire: {str(e)}")
        messages.warning(request, "Utilisation de l'année scolaire courante par défaut")

    # 2. Récupération des sections accessibles (DÉPLACÉ AVANT TOUTE UTILISATION)
    accessible_sections = get_accessible_sections(request.user) if hasattr(request, 'user') else Section.objects.none()
    itm_section = Section.objects.filter(nom='ITM').first()

    if request.method == 'POST':
        form_data_list = []
        i = 0
        while True:
            prefix = f'form-{i}-'
            if not any(key.startswith(prefix) for key in request.POST.keys()):
                break

            form_data = {
                'predefined_nom': request.POST.get(f'{prefix}predefined_nom'),
                'custom_nom': request.POST.get(f'{prefix}custom_nom'),
                'montant': request.POST.get(f'{prefix}montant'),
                'type_frais': request.POST.get(f'{prefix}type_frais'),
                'section': request.POST.get(f'{prefix}section'),
                'option': request.POST.get(f'{prefix}option'),
                'classes': request.POST.getlist(f'{prefix}classes'),
                'annee_scolaire': selected_annee.id,
            }
            form_data_list.append(form_data)
            i += 1

        if not form_data_list:
            form_data_list.append({
                'predefined_nom': request.POST.get('predefined_nom'),
                'custom_nom': request.POST.get('custom_nom'),
                'montant': request.POST.get('montant'),
                'type_frais': request.POST.get('type_frais'),
                'section': request.POST.get('section'),
                'option': request.POST.get('option'),
                'classes': request.POST.getlist('classes'),
                'annee_scolaire': selected_annee.id,
            })

        success_count = 0
        errors = []

        try:
            with transaction.atomic():
                for form_data in form_data_list:
                    form = FraisForm(data=form_data, user=request.user)
                    if form.is_valid():
                        frais = form.save(commit=False)
                        frais.annee_scolaire = selected_annee
                        frais.nom = form.cleaned_data.get('custom_nom') or form.cleaned_data.get('predefined_nom')
                        frais.save()
                        form.save_m2m()
                        success_count += 1
                    else:
                        errors.append(form.errors.as_json())

                if not success_count:
                    if errors:
                        error_messages = [json.loads(e) for e in errors]
                        raise ValueError(f"Erreurs de validation: {error_messages}")
                    raise ValueError("Aucun formulaire valide")

        except Exception as e:
            logger.error(f"Erreur transaction frais: {str(e)}")
            messages.error(request, f"❌ Erreur lors de l'ajout des frais: {str(e)}")
        else:
            if success_count > 0:
                msg = f"✅ {success_count} frais enregistrés pour {selected_annee.annee}"
                messages.success(request, msg)
                if errors:
                    messages.warning(request, "⚠ Certains frais n'ont pas pu être enregistrés")
                return redirect('liste_frais')

    # Préparation du contexte
    context = {
        'annee_scolaire_en_cours': selected_annee,
        'sections': accessible_sections,
        'itm_section_id': itm_section.id if itm_section else None,
    }
    return render(request, 'gestion/ajouter_frais.html', context)
def build_form_context(request, annee_scolaire, accessible_sections, itm_section=None, multi_form=False):
    """Construit le contexte commun pour le formulaire"""
    return {
        'form': FraisForm(user=request.user),
        'sections': accessible_sections,
        'annee_scolaire_en_cours': annee_scolaire.annee,
        'selected_annee': annee_scolaire,
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'multi_form': multi_form,
        'itm_section_id': itm_section.id if itm_section else None,
        'user_role': request.user.role
    }

# views.py


@login_required
def modifier_frais(request, frais_id):
    """
    Vue pour modifier un frais scolaire existant.
    L'utilisateur ne peut modifier que les frais liés aux sections/classes/options accessibles.
    """
    frais = get_object_or_404(Frais, id=frais_id)

    # Vérifier si l'utilisateur a accès à la section du frais ou à ses classes
    has_access = False

    if request.user.is_superuser or request.user.role == 'admin':
        has_access = True
    else:
        # Vérifier si le frais est lié à une section accessible
        if frais.section:
            has_access = check_section_access(request.user, frais.section.nom)

        # Si pas de section mais des classes, vérifier si au moins une classe est accessible
        if not has_access and frais.classes.exists():
            accessible_sections = get_accessible_sections(request.user)
            accessible_class_ids = Classe.objects.filter(section__in=accessible_sections).values_list('id', flat=True)
            has_access = frais.classes.filter(id__in=accessible_class_ids).exists()

        # Si toujours pas d'accès, refuser la modification
        if not has_access:
            messages.error(request, "❌ Vous n'avez pas le droit de modifier ce frais.")
            return redirect('liste_frais')

    if request.method == 'POST':
        form = FraisForm(request.POST, instance=frais, user=request.user)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "✅ Frais modifié avec succès !")
                return redirect('liste_frais')
            except Exception as e:
                messages.error(request, f"❌ Erreur lors de la modification : {str(e)}")
        else:
            messages.error(request, "❌ Formulaire invalide. Veuillez corriger les erreurs.")

    else:
        form = FraisForm(instance=frais, user=request.user)

    return render(request, 'gestion/modifier_frais.html', {
        'form': form,
        'frais': frais
    })


@login_required
@admin_required
def supprimer_frais(request, frais_id):
    """ Supprimer un frais scolaire """
    frais = get_object_or_404(Frais, id=frais_id)
    if request.method == 'POST':
        frais.delete()
        messages.success(request, "✅ Frais supprimé avec succès !")
        return redirect('liste_frais')
    return render(request, 'gestion/supprimer_frais.html', {'frais': frais})


from .forms import AjouterSectionOptionForm
from .models import Section, Option, Classe


@transaction.atomic
@login_required
@admin_required
def ajouter_section_ou_option(request):
    if request.method == 'POST':
        form = AjouterSectionOptionForm(request.POST)
        if form.is_valid():
            operation = form.cleaned_data['operation']

            try:
                if operation == 'section':
                    # Création d'une nouvelle section
                    section = Section.objects.create(
                        nom=form.cleaned_data['nom_section'],
                        type_section=form.cleaned_data['type_section']
                    )

                    # Création des classes selon le type de section
                    if form.cleaned_data['type_section'] == 'itm':
                        # Classes de 1ère à 4ème année pour ITM
                        for i in range(1, 5):
                            Classe.objects.create(
                                nom=f"{i}ème année",
                                section=section
                            )
                    else:  # humanite
                        # Classes de 3ème à 6ème année pour Humanités
                        for i in range(3, 7):
                            Classe.objects.create(
                                nom=f"{i}ème année",
                                section=section
                            )

                    message = f"Section '{form.cleaned_data['nom_section']}' ajoutée avec succès."

                else:  # operation == 'option'
                    # Création d'une nouvelle option
                    section = form.cleaned_data['section_existant']
                    option = Option.objects.create(
                        nom=form.cleaned_data['nom_option'],
                        section=section
                    )

                    # Création des classes selon le type de section
                    if section.type_section == 'itm':
                        # Classes de 1ère à 4ème année pour ITM
                        for i in range(1, 5):
                            Classe.objects.create(
                                nom=f"{i}ème année",
                                section=section,
                                option=option
                            )
                    else:  # humanite
                        # Classes de 3ème à 6ème année pour Humanités
                        for i in range(3, 7):
                            Classe.objects.create(
                                nom=f"{i}ème année",
                                section=section,
                                option=option
                            )

                    message = f"Option '{form.cleaned_data['nom_option']}' ajoutée avec succès à la section '{section.nom}'."

                # Redirection après traitement réussi
                messages.success(request, message)
                return redirect('ajouter_section_ou_option')  # Redirigez vers la même page ou une autre

            except Exception as e:
                messages.error(request, f"Une erreur s'est produite : {str(e)}")
                return redirect('ajouter_section_ou_option')

    else:
        form = AjouterSectionOptionForm()

    context = {
        'form': form,
        'sections': Section.objects.all()
    }

    return render(request, 'gestion/ajouter_section_option.html', context)


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


@login_required
def liste_parents(request):
    """
    Liste des parents dont les élèves sont inscrits pour une année scolaire donnée
    Affiche les noms de sections dans les statistiques
    """
    try:
        # Gestion de l'année scolaire
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except Exception as e:
        selected_annee = AnneeScolaire.obtenir_annee_courante()
        logger.error(f"Erreur sélection année scolaire: {str(e)}")

    # Récupération des sections accessibles
    accessible_sections = get_accessible_sections(request.user)

    # Paramètre de recherche
    query = request.GET.get('q', '').strip()

    # Construction de la requête de base
    parents_list = Parent.objects.filter(
        eleves__classe__section__in=accessible_sections,
        eleves__annee_scolaire=selected_annee
    ).distinct().order_by('nom')

    # Application des filtres de recherche
    if query:
        parents_list = parents_list.filter(
            Q(nom__icontains=query) |
            Q(telephone__icontains=query) |
            Q(email__icontains=query) |
            Q(eleves__nom__icontains=query) |
            Q(eleves__matricule__icontains=query)
        ).distinct()

    # Statistiques par section avec noms
    parents_par_section = Parent.objects.filter(
        eleves__classe__section__in=accessible_sections,
        eleves__annee_scolaire=selected_annee
    ).values(
        section_name=F('eleves__classe__section__nom')  # Utilisation du nom directement
    ).annotate(
        total=Count('id', distinct=True)
    ).order_by('section_name')

    # Pagination
    paginator = Paginator(parents_list, 25)
    page_number = request.GET.get('page')

    try:
        parents = paginator.page(page_number)
    except PageNotAnInteger:
        parents = paginator.page(1)
    except EmptyPage:
        parents = paginator.page(paginator.num_pages)

    # Préparation du contexte
    context = {
        'parents': parents,
        'query': query,
        'total_parents': parents_list.count(),
        'parents_par_section': parents_par_section,
        'annee_courante': selected_annee.annee,
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'selected_annee': selected_annee,
        'user_role': request.user.role,
    }

    return render(request, "gestion/liste_parents.html", context)
# detail parent
@login_required
def detail_parent(request, parent_id):
    """ Affiche les détails d'un parent avec ses enfants (élèves). """
    parent = get_object_or_404(Parent, id=parent_id)
    return render(request, "gestion/detail_parent.html", {"parent": parent})


#voici la version qui passe correctement
def liste_paiements(request):
    # 1. Récupérer l'année scolaire sélectionnée ou utiliser celle en cours
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
    try:
        if annee_id:
            selected_annee = AnneeScolaire.objects.get(id=annee_id)
        else:
            selected_annee = AnneeScolaire.obtenir_annee_courante()
    except AnneeScolaire.DoesNotExist:
        selected_annee = AnneeScolaire.obtenir_annee_courante()

    # 2. Récupération des sections accessibles
    accessible_sections = get_accessible_sections(request.user)

    # 3. Filtrage initial strict par rôle ET par année scolaire (CORRIGÉ ICI)
    paiements = filter_by_user_role(
        Paiement.objects.filter(
            Q(frais__annee_scolaire=selected_annee) |
            Q(annee_scolaire=selected_annee)  # Ajout de ce filtre crucial
        )
        .select_related(
            'eleve__classe__section',
            'eleve__classe__option',
            'frais'
        ),
        user=request.user,
        section_field='eleve__classe__section__nom'
    ).order_by('-date_paiement').distinct()

    # 4. Initialisation du formulaire avec filtrage par rôle
    form = FiltragePaiementForm(request.GET or None, user=request.user)

    # 5. Application sécurisée des filtres
    if form.is_valid():
        # Vérification section
        if form.cleaned_data['section']:
            if not check_section_access(request.user, form.cleaned_data['section'].nom):
                raise PermissionDenied("Accès refusé à cette section")
            paiements = paiements.filter(eleve__classe__section=form.cleaned_data['section'])

        # Vérification option
        if form.cleaned_data['option']:
            if not check_section_access(request.user, form.cleaned_data['option'].section.nom):
                raise PermissionDenied("Accès refusé à cette option")
            paiements = paiements.filter(eleve__classe__option=form.cleaned_data['option'])

        # Vérification classe
        if form.cleaned_data['classe']:
            if not check_section_access(request.user, form.cleaned_data['classe'].section.nom):
                raise PermissionDenied("Accès refusé à cette classe")
            paiements = paiements.filter(eleve__classe=form.cleaned_data['classe'])

        # Vérification frais (doit appartenir aux classes accessibles)
        if form.cleaned_data['frais']:
            frais = form.cleaned_data['frais']
            if not frais.classes.filter(section__in=accessible_sections).exists():
                raise PermissionDenied("Accès refusé à ce type de frais")
            paiements = paiements.filter(frais=frais)

        # Filtres sans contrôle de permission
        if form.cleaned_data['mois']:
            paiements = paiements.filter(mois=form.cleaned_data['mois'])
        if form.cleaned_data['matricule']:
            paiements = paiements.filter(eleve__matricule__icontains=form.cleaned_data['matricule'])

    # 6. Agrégation des paiements par mois
    paiements_par_mois = (
        paiements
        .annotate(mois_calcule=TruncMonth('date_paiement'))
        .values('mois_calcule')
        .annotate(total=Sum('montant_paye'), count=Count('id'))
        .order_by('mois_calcule')
    )

    # Conversion en format utilisable dans le template
    paiements_par_mois_for_template = [
        {
            'mois': item['mois_calcule'].strftime('%Y-%m'),
            'total': float(item['total']),
            'nombre': item['count']
        }
        for item in paiements_par_mois
    ]

    # Mise à jour du stats dict
    stats = {
        'total_paye': paiements.aggregate(total=Sum('montant_paye'))['total'] or 0,
        'nombre_paiements': paiements.count(),
        'par_frais': paiements.values('frais__nom').annotate(total=Sum('montant_paye')),
        'par_mois': paiements_par_mois_for_template,
    }

    # Adaptation des données pour le template
    paiements_mensuels = (
        paiements.filter(frais__type_frais="Mensuel")
        .annotate(mois_calcule=TruncMonth('date_paiement'))
        .values('mois_calcule')
        .annotate(total=Sum('montant_paye'))
        .order_by('mois_calcule')
    )

    paiements_mensuels_list = [
        {
            'mois': item['mois_calcule'].strftime('%Y-%m'),
            'total': float(item['total'] or 0)
        }
        for item in paiements_mensuels
    ]

    # Liste des années disponibles pour le filtre
    annees_disponibles = AnneeScolaire.objects.all().order_by('-annee')

    return render(request, 'liste_paiements.html', {
        'paiements': paiements,
        'form': form,
        'stats': stats,
        'paiements_mensuels': paiements_mensuels_list,
        'annee_scolaire': selected_annee,
        'annees_disponibles': annees_disponibles,
        'user_role': request.user.role
    })
# Données pour le graphique "Évolution des paiements mensuels"

@login_required
@financier_required
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

@login_required
@prefets_required  # Nécessite que l'utilisateur soit connecté
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
    # Récupération de l'année scolaire
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
    try:
        if annee_id:
            selected_annee = AnneeScolaire.objects.get(id=annee_id)
        else:
            selected_annee = AnneeScolaire.obtenir_annee_courante()
    except AnneeScolaire.DoesNotExist:
        selected_annee = AnneeScolaire.obtenir_annee_courante()

    if request.method == 'POST':
        form = PaiementForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    paiement = form.save(commit=False)
                    paiement.annee_scolaire = selected_annee

                    # Vérification des doublons avant sauvegarde
                    if paiement.frais.type_frais == "Mensuel" and paiement.mois:
                        existe_deja = Paiement.objects.filter(
                            eleve=paiement.eleve,
                            frais=paiement.frais,
                            mois=paiement.mois,
                            annee_scolaire=selected_annee
                        ).exists()

                        if existe_deja:
                            messages.error(request, f"Un paiement existe déjà pour ce mois ({paiement.mois})")
                            return render(request, 'gestion/ajouter_paiement.html', {
                                'form': form,
                                'annee_scolaire': selected_annee,
                                'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
                                'mois_choices': MoisPaiement.choices,
                                'tranche_choices': TRANCHE_CHOICES
                            })

                    elif paiement.frais.type_frais == "Trimestriel" and paiement.tranche:
                        existe_deja = Paiement.objects.filter(
                            eleve=paiement.eleve,
                            frais=paiement.frais,
                            tranche=paiement.tranche,
                            annee_scolaire=selected_annee
                        ).exists()

                        if existe_deja:
                            messages.error(request, f"Un paiement existe déjà pour cette tranche ({paiement.tranche})")
                            return render(request, 'gestion/ajouter_paiement.html', {
                                'form': form,
                                'annee_scolaire': selected_annee,
                                'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
                                'mois_choices': MoisPaiement.choices,
                                'tranche_choices': TRANCHE_CHOICES
                            })

                    elif paiement.frais.type_frais == "Annuel":
                        existe_deja = Paiement.objects.filter(
                            eleve=paiement.eleve,
                            frais=paiement.frais,
                            annee_scolaire=selected_annee
                        ).exists()

                        if existe_deja:
                            messages.error(request, "Les frais annuels ont déjà été payés pour cet élève")
                            return render(request, 'gestion/ajouter_paiement.html', {
                                'form': form,
                                'annee_scolaire': selected_annee,
                                'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
                                'mois_choices': MoisPaiement.choices,
                                'tranche_choices': TRANCHE_CHOICES
                            })

                    # Si aucun doublon, procéder au paiement
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
        form = PaiementForm(user=request.user)

    return render(request, 'gestion/ajouter_paiement.html', {
        'form': form,
        'mois_choices': MoisPaiement.choices,
        'tranche_choices': TRANCHE_CHOICES,
        'annee_scolaire': selected_annee,
        'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee')
    })
# recu paiement
@login_required
def recu_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    return render(request, 'gestion/recu_paiement.html', {'paiement': paiement})


# ********************************************************************************************************************
#                                API
# ********************************************************************************************************************

# API pour récupérer les options et classes dynamiquement *
# views.py
from django.http import JsonResponse


# ✅ API AJAX pour récupérer l'historique des paiements d'un élève

# views.py


@login_required
def suivi_financier(request):
    # 1. Gestion de l'année scolaire
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
    try:
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except AnneeScolaire.DoesNotExist:
        selected_annee = AnneeScolaire.obtenir_annee_courante()

    # 2. Initialiser le formulaire
    form = SuiviFinancierForm(request.GET or None, initial={'annee_scolaire': selected_annee})

    # 3. Requêtes de base
    paiements = Paiement.objects.filter(frais__annee_scolaire=selected_annee)
    depenses = Depense.objects.filter(annee_scolaire=selected_annee)

    # 4. Appliquer les filtres
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
            try:
                month_number = datetime.strptime(mois, "%B").month
                paiements = paiements.filter(date_paiement__month=month_number)
                depenses = depenses.filter(date_depense__month=month_number)
            except ValueError:
                pass

        if annee_scolaire:
            paiements = paiements.filter(frais__annee_scolaire=annee_scolaire)
            depenses = depenses.filter(annee_scolaire=annee_scolaire)
            selected_annee = annee_scolaire

        if classe:
            paiements = paiements.filter(eleve__classe=classe)
        elif option:
            paiements = paiements.filter(eleve__classe__option=option)
        elif section:
            paiements = paiements.filter(eleve__classe__section=section)

    # 5. Calcul des totaux
    total_paiements = paiements.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
    solde = total_paiements - total_depenses

    # 6. Préparation des données pour le graphique (version corrigée)

    # Dictionnaire de correspondance mois anglais -> français
    MOIS_TRADUCTION = {
        'january': 'janvier',
        'february': 'février',
        'march': 'mars',
        'april': 'avril',
        'may': 'mai',
        'june': 'juin',
        'july': 'juillet',
        'august': 'août',
        'september': 'septembre',
        'october': 'octobre',
        'november': 'novembre',
        'december': 'décembre'
    }

    # Récupérer les paiements et dépenses par mois
    paiements_mensuels = (
        paiements.annotate(month=TruncMonth('date_paiement'))
        .values('month')
        .annotate(total=Sum('montant_paye'))
        .order_by('month')
    )

    depenses_mensuelles = (
        depenses.annotate(month=TruncMonth('date_depense'))
        .values('month')
        .annotate(total=Sum('montant'))
        .order_by('month')
    )

    # Données annuelles (par année scolaire)
    annees_disponibles = AnneeScolaire.objects.all().order_by('annee')

    paiements_annuels = (
        paiements.values('frais__annee_scolaire__annee')
        .annotate(total=Sum('montant_paye'))
        .order_by('frais__annee_scolaire__annee')
    )

    depenses_annuelles = (
        depenses.values('annee_scolaire__annee')
        .annotate(total=Sum('montant'))
        .order_by('annee_scolaire__annee')
    )

    # Préparer les données pour le graphique
    # Préparer les données pour les graphiques
    chart_data = {
        'mensuel': {
            'labels': [],
            'recettes': [],
            'depenses': [],
            'soldes': []
        },
        'annuel': {
            'labels': [annee.annee for annee in annees_disponibles],
            'recettes': [0] * annees_disponibles.count(),
            'depenses': [0] * annees_disponibles.count(),
            'soldes': [0] * annees_disponibles.count()
        }
    }

    # Remplir les données mensuelles
    for mois, ordre in sorted(MOIS_ORDRE.items(), key=lambda x: x[1]):
        p_total = next((float(p['total']) for p in paiements_mensuels
                        if p['month'] and MOIS_TRADUCTION.get(p['month'].strftime("%B").lower()) == mois), 0)
        d_total = next((float(d['total']) for d in depenses_mensuelles
                        if d['month'] and MOIS_TRADUCTION.get(d['month'].strftime("%B").lower()) == mois), 0)

        chart_data['mensuel']['labels'].append(mois.capitalize())
        chart_data['mensuel']['recettes'].append(p_total)
        chart_data['mensuel']['depenses'].append(d_total)
        chart_data['mensuel']['soldes'].append(p_total - d_total)

    # Remplir les données annuelles
    for p in paiements_annuels:
        annee = p['frais__annee_scolaire__annee']
        if annee in chart_data['annuel']['labels']:
            index = chart_data['annuel']['labels'].index(annee)
            chart_data['annuel']['recettes'][index] = float(p['total'])

    for d in depenses_annuelles:
        annee = d['annee_scolaire__annee']
        if annee in chart_data['annuel']['labels']:
            index = chart_data['annuel']['labels'].index(annee)
            chart_data['annuel']['depenses'][index] = float(d['total'])
            chart_data['annuel']['soldes'][index] = (
                    chart_data['annuel']['recettes'][index] - float(d['total'])
            )

    # 7. Contexte
    context = {
        'form': form,
        'paiements': paiements,
        'depenses': depenses,
        'total_paiements': total_paiements,
        'total_depenses': total_depenses,
        'solde': solde,
        'chart_json': json.dumps(chart_data),
        'annee_scolaire': selected_annee,
        'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
    }

    return render(request, 'gestion/suivi_financier.html', context)
@login_required
def ajouter_depense(request):
    # 1. Gestion de l'année scolaire
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
    try:
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except AnneeScolaire.DoesNotExist:
        selected_annee = AnneeScolaire.obtenir_annee_courante()

    # 2. Initialisation du formulaire
    if request.method == "POST":
        form = DepenseForm(request.POST, user=request.user)
        if form.is_valid():
            # 3. Vérification des permissions
            section = form.cleaned_data.get('section')
            if section and not check_section_access(request.user, section.nom):
                messages.error(request, "❌ Accès refusé à cette section.")
                return redirect('ajouter_depense')

            # 4. Création de la dépense
            try:
                with transaction.atomic():
                    depense = form.save(commit=False)
                    depense.annee_scolaire = selected_annee
                    depense.utilisateur = request.user
                    depense.save()

                    messages.success(request, "✅ Dépense enregistrée avec succès !")
                    return redirect('liste_depenses')

            except Exception as e:
                messages.error(request, f"❌ Erreur lors de l'enregistrement: {str(e)}")
                logger.error(f"Erreur ajout dépense: {str(e)}")
    else:
        form = DepenseForm(user=request.user, initial={'annee_scolaire': selected_annee})
        # Filtrage des sections accessibles
        form.fields['section'].queryset = get_accessible_sections(request.user)

    # 5. Préparation du contexte
    context = {
        'form': form,
        'annee_scolaire': selected_annee,
        'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
        'user_role': request.user.role
    }

    return render(request, 'gestion/ajouter_depense.html', context)


@login_required
def bilan_financier(request):
    try:
        # 1. Gestion de l'année scolaire
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except Exception as e:
        selected_annee = AnneeScolaire.obtenir_annee_courante()
        logger.error(f"Erreur sélection année scolaire: {str(e)}")

    # 2. Récupération des sections accessibles
    accessible_sections = get_accessible_sections(request.user)

    # 3. Requêtes filtrées
    paiements = Paiement.objects.filter(
        frais__annee_scolaire=selected_annee,
        eleve__classe__section__in=accessible_sections
    ).select_related('frais', 'eleve__classe__section')

    depenses = Depense.objects.filter(
        annee_scolaire=selected_annee,
        section__in=accessible_sections
    ).select_related('section')

    # 4. Calcul des totaux
    total_encaisse = paiements.aggregate(total=Sum('montant_paye'))['total'] or 0
    total_depenses = depenses.aggregate(total=Sum('montant'))['total'] or 0
    solde_final = total_encaisse - total_depenses

    # 5. Préparation des données pour le graphique
    # Paiements par mois
    paiements_mensuels = (
        paiements.annotate(month=TruncMonth('date_paiement'))
        .values('month')
        .annotate(total=Sum('montant_paye'))
        .order_by('month')
    )

    # Dépenses par mois
    depenses_mensuelles = (
        depenses.annotate(month=TruncMonth('date_depense'))
        .values('month')
        .annotate(total=Sum('montant'))
        .order_by('month')
    )

    # Fusion des données
    monthly_data = defaultdict(lambda: {"recettes": 0, "depenses": 0, "solde": 0})

    # Remplir avec les paiements
    for p in paiements_mensuels:
        if p['month']:
            month_key = p['month'].strftime("%Y-%m")
            monthly_data[month_key]["recettes"] = float(p['total'] or 0)
            monthly_data[month_key]["solde"] += float(p['total'] or 0)

    # Remplir avec les dépenses
    for d in depenses_mensuelles:
        if d['month']:
            month_key = d['month'].strftime("%Y-%m")
            monthly_data[month_key]["depenses"] = float(d['total'] or 0)
            monthly_data[month_key]["solde"] -= float(d['total'] or 0)

    # Trier les mois chronologiquement
    sorted_months = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, "%Y-%m"))

    # Préparer les données pour le template
    chart_data = {
        "labels": sorted_months,
        "recettes": [monthly_data[m]["recettes"] for m in sorted_months],
        "depenses": [monthly_data[m]["depenses"] for m in sorted_months],
        "solde": [monthly_data[m]["solde"] for m in sorted_months]
    }

    # 6. Autres statistiques
    top_frais = (
        paiements.values('frais__nom')
        .annotate(total=Sum('montant_paye'))
        .order_by('-total')[:5]
    )

    repartition_depenses = (
        depenses.values('motif')
        .annotate(total=Sum('montant'))
        .order_by('-total')[:10]
    )

    # 7. Taux d'élèves en retard (CORRIGÉ)
    eleves_query = Eleve.objects.filter(
        classe__section__in=accessible_sections,
        annee_scolaire=selected_annee  # Utilisation directe du champ annee_scolaire
    ).distinct()

    eleves_en_retard = eleves_query.filter(
        paiement__solde_restant__gt=0,
        paiement__frais__annee_scolaire=selected_annee
    ).count()

    taux_retard = round((eleves_en_retard / eleves_query.count() * 100), 2) if eleves_query.exists() else 0

    # 7. Contexte
    context = {
        'total_encaisse': total_encaisse,
        'total_depenses': total_depenses,
        'solde_final': solde_final,
        'chart_json': json.dumps(chart_data),
        'top_frais': top_frais,
        'taux_retard':taux_retard,
        'repartition_depenses': repartition_depenses,
        'annee_courante': selected_annee.annee,  # Modification ici
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'user_role': request.user.role
    }

    return render(request, 'gestion/bilan_financier.html', context)


from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models.functions import TruncMonth  # Utilisation de TruncMonth au lieu d'ExtractMonth
import logging
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


@login_required
def liste_depenses(request):
    try:
        # 1. Gestion de l'année scolaire
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
        selected_annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
    except Exception as e:
        selected_annee = AnneeScolaire.obtenir_annee_courante()
        logger.error(f"Erreur sélection année scolaire: {str(e)}")

    # 2. Récupération des sections accessibles
    accessible_sections = get_accessible_sections(request.user)

    # 3. Initialisation des filtres
    date_filter = request.GET.get('date')
    mois_filter = request.GET.get('mois')
    annee_filter = request.GET.get('annee')

    # 4. Construction de la requête de base
    depenses = Depense.objects.filter(
        annee_scolaire=selected_annee,
        section__in=accessible_sections
    ).select_related('section').order_by('-date_depense')

    # 5. Application des filtres supplémentaires
    if date_filter:
        depenses = depenses.filter(date_depense=date_filter)

    if mois_filter:
        depenses = depenses.filter(date_depense__month=mois_filter)

    if annee_filter:
        depenses = depenses.filter(date_depense__year=annee_filter)

    # 6. Calcul du total des dépenses
    total_depenses = depenses.aggregate(total=Sum('montant'))['total'] or 0

    # 7. Statistiques mensuelles
    mois = range(1, 13)  # Liste de 1 à 12 pour les mois

    # Dépenses par mois pour l'année sélectionnée (utilisant TruncMonth)
    depenses_mensuelles = (
        depenses.annotate(month=TruncMonth('date_depense'))
        .values('month')
        .annotate(total=Sum('montant'))
        .order_by('month')
    )

    # Préparation des données pour le graphique
    monthly_expenses = {m: 0 for m in mois}
    for d in depenses_mensuelles:
        if d['month']:
            month_num = d['month'].month
            monthly_expenses[month_num] = float(d['total'] or 0)

    # 8. Contexte
    context = {
        'depenses': depenses,
        'mois': mois,
        'monthly_expenses': monthly_expenses,
        'total_depenses': total_depenses,
        'annee_courante': selected_annee.annee,
        'annees_scolaires': AnneeScolaire.objects.all().order_by('-annee'),
        'user_role': request.user.role,
        'selected_annee': selected_annee,  # Ajout pour affichage dans le template
    }

    return render(request, 'gestion/liste_depenses.html', context)

@login_required
@admin_required
def supprimer_depense(request, depense_id):
    """ Supprimer une dépense """
    depense = get_object_or_404(Depense, id=depense_id)
    if request.method == "POST":
        depense.delete()
        messages.success(request, "✅ Dépense supprimée avec succès !")
        return redirect('liste_depenses')

    return render(request, 'gestion/supprimer_depense.html', {'depense': depense})


@login_required
def statistiques(request):
    user = request.user
    annee_scolaire = AnneeScolaire.obtenir_annee_courante()

    # ✅ Initialisation par défaut
    taux_paiement = 0  # ← Initialisé ici

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

        if sections:
            depenses = Depense.objects.filter(section__nom__in=sections, annee_scolaire=annee_scolaire)
        else:
            depenses = Depense.objects.filter(annee_scolaire=annee_scolaire)

    # Calcul des statistiques
    total_eleves = eleves.count()
    total_paiements = paiements.aggregate(total=Sum("montant_paye"))["total"] or 0
    total_depenses = depenses.aggregate(total=Sum("montant"))["total"] or 0
    solde_global = total_paiements - total_depenses

    # Calcul du total des frais dus
    total_frais_dus = 0
    for eleve in eleves:
        frais_classe = Frais.objects.filter(classes=eleve.classe).aggregate(total=Sum("montant"))["total"] or 0
        frais_section = Frais.objects.filter(section=eleve.section).aggregate(total=Sum("montant"))["total"] or 0
        total_frais_dus += frais_classe + frais_section

    # ✅ Définir le taux de paiement uniquement si total_frais_dus > 0
    if total_frais_dus > 0:
        taux_paiement = (total_paiements / total_frais_dus) * 100
    else:
        taux_paiement = 0  # ou None selon vos besoins

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
        "taux_paiement": taux_paiement,  # ✅ Utilisée en toute sécurité
    }

    return render(request, "gestion/statistiques.html", context)


# views.py
@login_required
def dashboard(request):
    user = request.user
    today = datetime.now()

    # Récupérer l'année scolaire active depuis la session
    annee_id = request.session.get('annee_scolaire_id')

    if not annee_id:
        # Si aucune année n'est dans la session, utiliser l'année courante
        annee_scolaire = AnneeScolaire.obtenir_annee_courante()
        annee_id = annee_scolaire.id
        request.session['annee_scolaire_id'] = annee_id
    else:
        # Utiliser l'année stockée dans la session
        annee_scolaire = get_object_or_404(AnneeScolaire, id=annee_id)

    # Initialisation du formulaire
    form = FiltragePaiementForm(request.GET or None, user=request.user)

    # Filtrer les paiements et élèves selon les permissions et l'année scolaire
    paiements_base = filter_by_user_role(
        Paiement.objects.filter(frais__annee_scolaire_id=annee_id),
        user,
        'eleve__classe__section__nom'
    )

    eleves_recap_query = filter_by_user_role(
        Eleve.objects.filter(annee_scolaire_id=annee_id),
        user,
        'classe__section__nom'
    )

    # Application des filtres
    if form.is_valid():
        if form.cleaned_data['section']:
            # Vérifier que la section filtrée est accessible
            if check_section_access(user, form.cleaned_data['section'].nom):
                paiements_base = paiements_base.filter(eleve__classe__section=form.cleaned_data['section'])
                eleves_recap_query = eleves_recap_query.filter(classe__section=form.cleaned_data['section'])

        if form.cleaned_data['option']:
            paiements_base = paiements_base.filter(eleve__classe__option=form.cleaned_data['option'])
            eleves_recap_query = eleves_recap_query.filter(classe__option=form.cleaned_data['option'])

        if form.cleaned_data['classe']:
            # Vérifier que la classe filtrée est dans une section accessible
            if check_section_access(user, form.cleaned_data['classe'].section.nom):
                paiements_base = paiements_base.filter(eleve__classe=form.cleaned_data['classe'])
                eleves_recap_query = eleves_recap_query.filter(classe=form.cleaned_data['classe'])

        if form.cleaned_data['frais']:
            paiements_base = paiements_base.filter(frais=form.cleaned_data['frais'])

        if form.cleaned_data['mois']:
            paiements_base = paiements_base.filter(mois=form.cleaned_data['mois'])

        if form.cleaned_data['matricule']:
            paiements_base = paiements_base.filter(eleve__matricule__icontains=form.cleaned_data['matricule'])
            eleves_recap_query = eleves_recap_query.filter(matricule__icontains=form.cleaned_data['matricule'])

    # 1. Statistiques de base
    total_eleves = eleves_recap_query.count()
    total_recettes = paiements_base.aggregate(total=Sum("montant_paye"))["total"] or 0

    # Filtrer les dépenses selon les permissions et l'année scolaire
    depenses = filter_by_user_role(
        Depense.objects.filter(annee_scolaire_id=annee_id),
        user
    )
    total_depenses = depenses.aggregate(total=Sum("montant"))["total"] or 0

    chiffre_affaires = total_recettes - total_depenses

    # 2. Calcul des retards (en utilisant le queryset déjà filtré)
    eleves_en_retard_count = eleves_recap_query.filter(
        Q(paiement__solde_restant__gt=0) &
        Q(paiement__frais__annee_scolaire_id=annee_id)
    ).distinct().count()

    taux_retard = (eleves_en_retard_count / total_eleves * 100) if total_eleves > 0 else 0

    # 3. Analyse Financière Avancée
    date_fin = today + relativedelta(months=6)
    paiements_futurs = (
        paiements_base.filter(date_paiement__range=[today, date_fin])
        .annotate(mois_calcule=TruncMonth('date_paiement'))
        .values('mois_calcule')
        .annotate(total=Sum('montant_paye'))
        .order_by('mois_calcule')
    )

    previsions_tresorerie = defaultdict(float)
    for pf in paiements_futurs:
        mois = pf['mois_calcule'].strftime("%Y-%m")
        previsions_tresorerie[mois] = float(pf['total'] or 0)

    mois_precedent = today - relativedelta(months=1)
    recette_mois_precedent = paiements_base.filter(
        date_paiement__month=mois_precedent.month,
        date_paiement__year=mois_precedent.year
    ).aggregate(total=Sum("montant_paye"))["total"] or 0

    annee_precedente = today - relativedelta(years=1)
    recette_annee_precedente = paiements_base.filter(
        date_paiement__month=today.month,
        date_paiement__year=annee_precedente.year
    ).aggregate(total=Sum("montant_paye"))["total"] or 0

    retards_par_classe = (
        paiements_base.filter(solde_restant__gt=0)
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

    top_frais = (
        paiements_base.values('frais__nom')
        .annotate(total=Sum('montant_paye'), count=Count('id'))
        .order_by('-total')[:5]
    )

    tendances_frais = []
    for frais in top_frais:
        nom_frais = frais['frais__nom']
        total_actuel = frais['total']

        total_mois_precedent = paiements_base.filter(
            frais__nom=nom_frais,
            date_paiement__month=mois_precedent.month,
            date_paiement__year=mois_precedent.year
        ).aggregate(total=Sum("montant_paye"))["total"] or 0

        evolution = ((
                                 total_actuel - total_mois_precedent) / total_mois_precedent * 100) if total_mois_precedent > 0 else 100

        tendances_frais.append({
            'nom': nom_frais,
            'total': float(total_actuel),
            'evolution': float(round(evolution, 2)),
            'tendance': 'up' if evolution >= 0 else 'down'
        })

    paiements_mensuels = (
        paiements_base.annotate(mois_calcule=TruncMonth("date_paiement"))
        .values("mois_calcule")
        .annotate(total=Sum("montant_paye"))
        .order_by("mois_calcule")
    )

    stats = {
        'total_paye': paiements_base.aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0,
        'nombre_paiements': paiements_base.count(),
        'par_frais': paiements_base.values('frais__nom').annotate(total=Sum('montant_paye')),
        'par_mois': paiements_mensuels,
    }

    eleves_par_section = (
        eleves_recap_query.values("classe__section__nom")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    eleves_recap = eleves_recap_query.annotate(
        montant_total_paye=Sum("paiement__montant_paye"),
        solde_restant=Sum("paiement__solde_restant")
    ).values("nom", "classe__nom", "montant_total_paye", "solde_restant")

    try:
        top_frais_json = json.dumps(tendances_frais)
    except Exception as e:
        print(f"Erreur lors de la conversion JSON : {str(e)}")
        top_frais_json = "[]"

    context = {
        "form": form,
        "total_eleves": total_eleves,
        "total_recettes": total_recettes,
        "total_depenses": total_depenses,
        "chiffre_affaires": chiffre_affaires,
        "taux_retard": taux_retard,
        "previsions_tresorerie": dict(previsions_tresorerie),
        "recette_mois_precedent": recette_mois_precedent,
        "recette_annee_precedente": recette_annee_precedente,
        "heatmap_data": heatmap_data,
        "top_frais": top_frais_json,
        "paiements_mensuels": paiements_mensuels,
        "eleves_par_section": eleves_par_section,
        "eleves_recap": eleves_recap,
        "role_message": f"Bienvenue, {user.first_name}.",
        "annee_scolaire": annee_scolaire,
        "annee_selectionnee": annee_scolaire,  # Pour l'affichage dans le template
        "annees_disponibles": AnneeScolaire.objects.all().order_by('-annee'),
        'stats': stats,
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


MOIS_ORDRE = {
    'septembre': 1,
    'octobre': 2,
    'novembre': 3,
    'décembre': 4,
    'janvier': 5,
    'février': 6,
    'mars': 7,
    'avril': 8,
    'mai': 9,
    'juin': 10,
}


def normaliser_mois(mois):
    if not mois:
        return None
    return mois.strip().lower()


@login_required
def details_classe(request, classe_id):
    # 1. Récupérer l'année scolaire sélectionnée ou utiliser celle en cours
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')
    try:
        if annee_id:
            selected_annee = AnneeScolaire.objects.get(id=annee_id)
        else:
            selected_annee = AnneeScolaire.obtenir_annee_courante()
    except AnneeScolaire.DoesNotExist:
        selected_annee = AnneeScolaire.obtenir_annee_courante()

    # 2. Récupérer la classe avec vérification d'accès
    classe = get_object_or_404(Classe, id=classe_id)

    # Vérifier que l'utilisateur a accès à la section de cette classe
    if not check_section_access(request.user, classe.section.nom):
        raise PermissionDenied("Vous n'avez pas accès à cette classe")

    # 3. Récupérer les élèves POUR L'ANNÉE SCOLAIRE SÉLECTIONNÉE
    eleves = Eleve.objects.filter(
        classe=classe,
        annee_scolaire=selected_annee
    ).select_related("parent").prefetch_related("paiement_set")

    # 4. Récupérer les frais pour l'année scolaire sélectionnée
    frais = Frais.objects.filter(classes=classe, annee_scolaire=selected_annee)
    mois_de_paiement = [m[1] for m in MoisPaiement.choices]

    # 5. Filtrer les paiements par année scolaire et élèves de l'année
    paiements = Paiement.objects.filter(
        eleve__in=eleves,  # Seulement les élèves de cette année
        frais__annee_scolaire=selected_annee
    )

    # 6. Appliquer les filtres supplémentaires
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

    # 7. Dernier mois payé par élève
    paiements_recents = paiements.values('eleve__matricule').annotate(mois_recent=Max('mois'))
    paiements_dict = {item['eleve__matricule']: item['mois_recent'] for item in paiements_recents}

    for eleve in eleves:
        eleve.mois_recent = paiements_dict.get(eleve.matricule, "-")

    # 8. Statistiques
    stats = {
        'en_ordre': paiements.values('eleve_id').distinct().count(),
        'non_en_ordre': eleves.count() - paiements.values('eleve_id').distinct().count(),
        'total_paye': round(paiements.aggregate(total=Sum('montant_paye'))['total'] or 0, 2),
    }

    # Répartition par type de frais
    stats['par_frais'] = list(
        paiements.values('frais__nom').annotate(
            total=Sum('montant_paye')
        ).order_by('-total')
    )

    # Répartition par mois (sans doublon + tri chronologique)
    paiements_list = list(paiements.values('mois', 'montant_paye'))

    mois_agreges = defaultdict(float)
    eleves_par_mois = defaultdict(set)

    for p in paiements_list:
        mois_normalise = normaliser_mois(p['mois'])
        if mois_normalise and mois_normalise in MOIS_ORDRE:
            mois_agreges[mois_normalise] += float(p['montant_paye'] or 0)
            eleves_par_mois[mois_normalise].add(p['mois'])

    # Génération des stats.par_mois
    stats['par_mois'] = [
        {
            'mois': mois.capitalize(),
            'total': round(total, 2),
            'nombre_eleves': len(eleves_par_mois[mois])
        }
        for mois, total in sorted(
            mois_agreges.items(),
            key=lambda x: MOIS_ORDRE.get(x[0], 99)
        )
    ]

    # Données pour graphique "Évolution des paiements mensuels"
    stats['paiements_mensuels'] = stats['par_mois']

    # Liste des années disponibles pour le filtre
    annees_disponibles = AnneeScolaire.objects.all().order_by('-annee')

    return render(request, 'details_classe.html', {
        'classe': classe,
        'eleves': eleves,
        'frais': frais,
        'mois_de_paiement': mois_de_paiement,
        'stats': stats,
        'annee_scolaire': selected_annee,
        'annees_disponibles': annees_disponibles,
    })


@method_decorator(csrf_exempt, name='dispatch')
class ExportDataView(View):
    def post(self, request, *args, **kwargs):
        logger.debug("Requête reçue sur /api/export/")
        try:
            data = json.loads(request.body)
            logger.debug(f"Données reçues : {data}")

            format_type = data.get('format')
            columns = data.get('columns', [])
            rows = data.get('rows', [])
            title = data.get('title', 'Export')

            if not format_type or not columns or not rows:
                return HttpResponse("Données incomplètes", status=400)

            # Conversion explicite des valeurs Decimal/datetime
            cleaned_rows = []
            for row in rows:
                cleaned_row = [
                    str(cell) if isinstance(cell, (float, int)) else cell
                    for cell in row
                ]
                cleaned_rows.append(cleaned_row)

            df = pd.DataFrame(cleaned_rows, columns=columns)

            if format_type == 'excel':
                return self.export_excel(df, title)
            elif format_type == 'csv':
                return self.export_csv(df, title)
            elif format_type == 'pdf':
                return self.export_pdf(df, title)
            else:
                return HttpResponse("Format non supporté", status=400)

        except json.JSONDecodeError:
            return HttpResponse("Erreur lors du décodage JSON", status=400)
        except Exception as e:
            logger.error(f"Erreur lors de l'export : {str(e)}")
            return HttpResponse(f"Erreur interne : {str(e)}", status=500)

    def export_csv(self, df, title):
        csv_data = df.to_csv(index=False)
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{title}.csv"'
        return response

    def export_excel(self, df, title):
        try:
            # Conversion explicite des colonnes en string pour éviter les erreurs de type
            df_clean = df.astype(str)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_clean.to_excel(writer, index=False, sheet_name='Sheet1')

            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{title}.xlsx"'
            return response

        except Exception as e:
            logger.error(f"Erreur lors de l'export Excel : {str(e)}")
            return HttpResponse(f"Erreur lors de l'export Excel : {str(e)}", status=500)

    def export_pdf(self, df, title):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'

        # Format paysage avec marges personnalisées (left, right, top, bottom)
        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(letter),
            leftMargin=0.2 * inch,  # Marge gauche
            rightMargin=0.2 * inch,  # Marge droite
            topMargin=0.6 * inch,  # Marge haute
            bottomMargin=0.6 * inch  # Marge basse
        )
        styles = getSampleStyleSheet()
        elements = []

        # Titre
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 0.2 * inch))  # Espace après le titre

        # Données avec en-têtes
        table_data = [df.columns.tolist()] + df.values.tolist()

        # Calcul de la largeur totale disponible pour les colonnes
        available_width = doc.width  # Largeur de la page moins les marges
        num_cols = len(table_data[0])
        col_widths = [available_width / num_cols] * num_cols  # Répartition égale entre toutes les colonnes

        # Création du tableau avec largeurs adaptatives
        t = Table(table_data, colWidths=col_widths)

        # Style du tableau
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), 'CJK')  # Pour forcer le retour à la ligne si nécessaire
        ]))

        elements.append(t)
        doc.build(elements)
        return response


class HistoriqueActionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistoriqueAction.objects.all().order_by('-date_action')
    serializer_class = HistoriqueActionSerializer


@admin_required
def historique_activites(request):
    # Récupérer les filtres depuis les paramètres GET
    modele_filter = request.GET.get('modele')
    utilisateur_filter = request.GET.get('utilisateur')
    action_filter = request.GET.get('action')
    date_debut_filter = request.GET.get('date_debut')
    date_fin_filter = request.GET.get('date_fin')

    # Appliquer les filtres si présents
    # Appliquer les filtres si présents
    historique_list = HistoriqueAction.objects.all().order_by('-date_action')

    if modele_filter:
        historique_list = historique_list.filter(modele=modele_filter)

    # ✅ Correction ici : ignorer si vide ou 'None'
    if utilisateur_filter and utilisateur_filter.strip() and utilisateur_filter.lower() != 'none':
        historique_list = historique_list.filter(utilisateur__username__icontains=utilisateur_filter)

    if action_filter and action_filter.strip():
        historique_list = historique_list.filter(action=action_filter)

    if date_debut_filter:
        try:
            debut = make_aware(datetime.strptime(date_debut_filter, "%Y-%m-%d"))
            historique_list = historique_list.filter(date_action__gte=debut)
        except ValueError:
            pass

    if date_fin_filter:
        try:
            fin = make_aware(datetime.strptime(date_fin_filter, "%Y-%m-%d"))
            historique_list = historique_list.filter(date_action__lte=fin)
        except ValueError:
            pass

    print("Query SQL:", historique_list.query)  # ✅ Afficher la requête SQL générée
    print("Count avant enrichissement:", historique_list.count())
    # Enrichir avec des détails supplémentaires
    enriched_actions = []
    # views.py
    for action in historique_list:
        enriched = {
            'date_action': action.date_action,
            'utilisateur': action.utilisateur,  # Objet utilisateur
            'utilisateur_affichage': action.utilisateur_affichage,  # Nom à afficher
            'action': action.action,
            'modele': action.modele,
            'objet_id': action.objet_id,
            'details': action.details,
            'display_details': action.details,
        }

        # Afficher plus d'information pour les paiements
        if action.modele == "Paiement" and action.objet_id:
            try:
                paiement = Paiement.objects.get(id=action.objet_id)
                enriched['display_details'] = (
                    f"Paiement de {paiement.montant_paye} FC pour "
                    f"'{paiement.frais.nom}' par {paiement.eleve.matricule}"
                )
            except Paiement.DoesNotExist:
                pass

        enriched_actions.append(enriched)

    # Statistiques globales
    stats = {
        'total_actions': len(enriched_actions),
        'par_modele': {},
        'par_action': {},
        'evolution_mensuelle': {}
    }

    for action in enriched_actions:
        stats['par_modele'][action['modele']] = stats['par_modele'].get(action['modele'], 0) + 1
        stats['par_action'][action['action']] = stats['par_action'].get(action['action'], 0) + 1
        mois = action['date_action'].strftime("%Y-%m")
        stats['evolution_mensuelle'][mois] = stats['evolution_mensuelle'].get(mois, 0) + 1

    evolution_mensuelle_triee = sorted(stats['evolution_mensuelle'].items(), key=lambda x: x[0])

    # Pagination
    paginator = Paginator(enriched_actions, 25)
    page = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page)
    except Exception:
        page_obj = paginator.page(1)

    modeles_disponibles = HistoriqueAction.objects.values_list('modele', flat=True).distinct()

    return render(request, 'gestion/historique.html', {
        'historique_list': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,

        'modeles_disponibles': modeles_disponibles,
        'current_modele': modele_filter,
        'current_utilisateur': utilisateur_filter,
        'current_action': action_filter,
        'current_date_debut': date_debut_filter,
        'current_date_fin': date_fin_filter,

        'stats': stats,
        'evolution_mensuelle_triee': evolution_mensuelle_triee,
    })


"""systeme de notification en temps reel"""
from django.shortcuts import render
from .models import Notification


@login_required
def liste_notifications(request):
    notifications = request.user.notifications.select_related('historique_action').order_by('-date_creation')[:50]
    return render(request, 'gestion/notifications.html', {'notifications': notifications})


@login_required
def details_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, utilisateur=request.user)
    notification.est_lue = True
    notification.save()
    return render(request, 'gestion/notification_detail.html', {
        'notification': notification,
        'action': notification.historique_action
    })

def documentation_view(request):
    query = request.GET.get('q', '')
    sections = []
    classes = []
    frais = []
    paiements = []

    if query:
        # Recherche dans les modèles
        sections = Section.objects.filter(
            Q(nom__icontains=query) |
            Q(type_section__icontains=query)
        ).distinct()

        classes = Classe.objects.filter(
            Q(nom__icontains=query) |
            Q(section__nom__icontains=query)
        ).distinct()

        frais = Frais.objects.filter(
            Q(nom__icontains=query) |
            Q(type_frais__icontains=query)
        ).distinct()

        paiements = Paiement.objects.filter(
            Q(eleve__nom__icontains=query) |
            Q(frais__nom__icontains=query)
        ).distinct()
    else:
        # Données par défaut
        sections = Section.objects.all()
        classes = Classe.objects.all()
        frais = Frais.objects.all()
        paiements = Paiement.objects.all()

    error_codes = [
        {
            'code': 'ERR-001',
            'message': "Accès refusé : vous n'avez pas les droits nécessaires.",
            'cause': "Tentative d'accès non autorisé",
            'solution': "Vérifier les permissions de l'utilisateur"
        },
        {
            'code': 'ERR-002',
            'message': "Le montant payé dépasse le montant net à payer",
            'cause': "Paiement supérieur au solde",
            'solution': "Vérifier le montant saisi"
        },
        {
            'code': 'ERR-003',
            'message': "Ce champ est requis pour l'ajout d'une section",
            'cause': "Champs manquants dans le formulaire",
            'solution': "Remplir tous les champs requis"
        },
        {
            'code': 'ERR-004',
            'message': "ObjectDoesNotExist",
            'cause': "Recherche d'objet inexistant",
            'solution': "Vérifier l'ID de l'objet"
        }
    ]

    context = {
        'query': query,
        'sections': sections,
        'classes': classes,
        'frais': frais,
        'paiements': paiements,
        'error_codes': error_codes,
        'histories': HistoriqueAction.objects.all().order_by('-date_action')[:10]
    }

    return render(request, 'gestion/documentation.html', context)


def guide_utilisation_view(request):
    # Récupération des données pour le guide
    paiements_recents = Paiement.objects.all().order_by('-date_paiement')[:5]
    frais_disponibles = Frais.objects.all()

    context = {
        'paiements': paiements_recents,
        'frais': frais_disponibles,
        'historiques': HistoriqueAction.objects.filter(
            modele='Paiement'
        ).order_by('-date_action')[:5]
    }

    return render(request, 'gestion/guide_utilisation.html', context)

