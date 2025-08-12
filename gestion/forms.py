from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# from .access_control import get_user_model
from .models import Frais, Classe, Option, Section, AnneeScolaire, CustomUser, ROLE_CHOICES, Eleve, Paiement, Parent, \
    TRANCHE_CHOICES

from .models import Section, Option, Classe, AnneeScolaire

from django import forms
from .models import Depense, Section
from django.contrib.auth import get_user_model
from .access_control import filter_by_user_role
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser


# =============================================================================

# Formulaire d'inscription
class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Rôle",
        widget=forms.Select(attrs={
            'class': 'form-control',  # Applique le style similaire
            'placeholder': 'Sélectionnez votre rôle'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prénom'
        }),
        label="Prénom"
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom'
        }),
        label="Nom"
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


# forms.py
class PasswordResetForm(forms.Form):
    """Formulaire de vérification des informations utilisateur"""
    first_name = forms.CharField(label="Prénom")
    last_name = forms.CharField(label="Nom")
    email = forms.EmailField(label="Email")

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')

        if not all([first_name, last_name, email]):
            raise forms.ValidationError("Veuillez remplir tous les champs.")

        return cleaned_data


class NewPasswordForm(forms.Form):
    """Formulaire de saisie du nouveau mot de passe"""
    password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput,
        help_text="Minimum 8 caractères"
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        if password1 and len(password1) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        return cleaned_data


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'role']  # Tu peux ajouter d'autres champs si nécessaire

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
        self.fields['role'].widget.attrs.update({'class': 'form-select'})
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

    # Optionnel : retire le mot de passe du formulaire
    def clean_password(self):
        return self.initial["password"]  # Ne change pas le mot de passe via ce formulaire


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Votre nom d’utilisateur',
            'required': 'required'
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Votre mot de passe',
            'required': 'required'
        })
    )


# formulaire parent


class EleveForm(forms.ModelForm):
    # Champs du parent intégrés dans le formulaire d'élève
    parent_nom = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    parent_telephone = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    parent_email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    parent_adresse = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    parent_profession = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    parent_relation = forms.ChoiceField(
        choices=[("Père", "Père"), ("Mère", "Mère"), ("Tuteur", "Tuteur")],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Eleve
        exclude = ['parents', 'annee_scolaire']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'post_nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control form-select', 'id': 'section-select'}),
            'option': forms.Select(attrs={'class': 'form-control', 'id': 'option-select'}),
            'classe': forms.Select(attrs={'class': 'form-control', 'id': 'classe-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if self.instance and self.instance.parent:
            # Pré-remplir les champs avec les données du parent existant
            parent = self.instance.parent
            self.fields['parent_nom'].initial = parent.nom
            self.fields['parent_telephone'].initial = parent.telephone
            self.fields['parent_email'].initial = parent.email
            self.fields['parent_adresse'].initial = parent.adresse
            self.fields['parent_profession'].initial = parent.profession
            self.fields['parent_relation'].initial = parent.relation

    def save(self, commit=True):
        eleve = super().save(commit=False)

        # Création ou mise à jour du parent
        parent_data = {
            'nom': self.cleaned_data['parent_nom'],
            'telephone': self.cleaned_data['parent_telephone'],
            'email': self.cleaned_data.get('parent_email'),
            'adresse': self.cleaned_data.get('parent_adresse'),
            'profession': self.cleaned_data.get('parent_profession'),
            'relation': self.cleaned_data['parent_relation']
        }

        if hasattr(eleve, 'parent') and eleve.parent:
            # Mise à jour du parent existant
            for key, value in parent_data.items():
                setattr(eleve.parent, key, value)
            if commit:
                eleve.parent.save()
        else:
            # Création d’un nouveau parent si aucun n’existe
            parent, created = Parent.objects.get_or_create(
                telephone=parent_data['telephone'],
                defaults=parent_data
            )
            if not created:
                # Si déjà existant, on met à jour ses informations
                for key, value in parent_data.items():
                    setattr(parent, key, value)
            if commit:
                parent.save()
            eleve.parent = parent

        if commit:
            eleve.save()
            self.save_m2m()

        return eleve


class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = '__all__'


# dmulaire frais
from django import forms
from .models import Frais, Classe, Option, Section, AnneeScolaire, Eleve, Paiement

# forms.py
from django import forms
from .access_control import get_accessible_sections


class FraisForm(forms.ModelForm):
    # Liste des frais prédéfinis
    PREDEFINED_FRAIS = [
        ('', '-- Choisir un frais --'),
        ('FIP', 'FIP'),
        ('ETAT', 'ETAT'),
        ('connexe', 'connexe'),
        ('frais connexe', 'frais connexe'),
        ('inscription', 'inscription'),
        ('bulletin', 'bulletin'),
        ('sonas', 'sonas'),
        ('Quotite DPS', 'Quotite DPS'),
        ('Stage', 'Stage'),
        ("jury fin d'annee", "jury fin d'annee"),
        ('Minerval', 'Minerval'),
        ('macaron', 'macaron'),
        ('Planification familiale', 'Planification familiale'),
        ('fiche de renseignement', 'fiche de renseignement'),
        ('carnet de renseignement', 'carnet de renseignement'),
        ("carnet d'apprenant", "carnet d'apprenant"),
        ('autres', 'Autres'),
    ]

    FRAIS_MAPPING = {
        'FIP': {'type_frais': 'Mensuel', 'section': None},
        'ETAT': {'type_frais': 'Trimestriel', 'section': None},
        'connexe': {'type_frais': 'Trimestriel', 'section': None},
        'frais connexe': {'type_frais': 'Annuel', 'section': None},
        'inscription': {'type_frais': 'Annuel', 'section': None},
        'bulletin': {'type_frais': 'Annuel', 'section': None},
        'sonas': {'type_frais': 'Annuel', 'section': None},
        'Quotite DPS': {'type_frais': 'Trimestriel', 'section': 'ITM'},
        'Stage': {'type_frais': 'Trimestriel', 'section': 'ITM'},
        "jury fin d'annee": {'type_frais': 'Annuel', 'section': 'ITM'},
        'Minerval': {'type_frais': 'Annuel', 'section': 'ITM'},
        'macaron': {'type_frais': 'Annuel', 'section': 'ITM'},
        'Planification familiale': {'type_frais': 'Annuel', 'section': 'ITM'},
        'fiche de renseignement': {'type_frais': 'Annuel', 'section': 'ITM'},
        'carnet de renseignement': {'type_frais': 'Annuel', 'section': 'ITM'},
        "carnet d'apprenant": {'type_frais': 'Annuel', 'section': 'ITM'},
    }

    predefined_nom = forms.ChoiceField(
        choices=PREDEFINED_FRAIS,
        required=True,
        label="Nom du Frais",
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'id_predefined_nom'
        })
    )

    custom_nom = forms.CharField(
        required=False,
        label="Nom du Frais personnalisé",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_custom_nom',
            'placeholder': 'Entrez le nom du frais'
        })
    )

    class Meta:
        model = Frais
        fields = ['montant', 'type_frais', 'section', 'option', 'classes', 'annee_scolaire']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'type_frais': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'option': forms.Select(attrs={'class': 'form-control'}),
            'classes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control', 'readonly': 'readonly'})
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Définir l'année scolaire courante comme valeur initiale
        current_year = AnneeScolaire.obtenir_annee_courante()
        self.fields['annee_scolaire'].initial = current_year
        self.fields['annee_scolaire'].disabled = True  # Empêche la modification

        # Récupérer les sections accessibles à l'utilisateur
        accessible_sections = get_accessible_sections(self.user) if self.user else Section.objects.all()

        # Filtrer les champs disponibles
        self.fields['section'].queryset = accessible_sections
        self.fields['option'].queryset = Option.objects.filter(section__in=accessible_sections)
        self.fields['classes'].queryset = Classe.objects.filter(section__in=accessible_sections)

        # Si données POST, mettre à jour les querysets dynamiquement
        if self.data:
            try:
                section_id = int(self.data.get('section'))
                self.fields['option'].queryset = Option.objects.filter(section_id=section_id)
                self.fields['classes'].queryset = Classe.objects.filter(section_id=section_id)
            except (ValueError, TypeError, Section.DoesNotExist):
                pass

            try:
                option_id = int(self.data.get('option'))
                self.fields['classes'].queryset = Classe.objects.filter(option_id=option_id)
            except (ValueError, TypeError, Option.DoesNotExist):
                pass

        elif self.instance.pk:
            # Pour l'édition, on charge les classes liées au frais existant
            if self.instance.option:
                self.fields['classes'].queryset = Classe.objects.filter(option=self.instance.option)
            elif self.instance.section:
                self.fields['classes'].queryset = Classe.objects.filter(section=self.instance.section)

    def clean(self):
        cleaned_data = super().clean()
        predefined = cleaned_data.get('predefined_nom')
        custom = cleaned_data.get('custom_nom')

        # Déterminer le nom final du frais
        if predefined == 'autres':
            if not custom:
                raise forms.ValidationError("Veuillez entrer le nom du frais personnalisé.")
            cleaned_data['nom'] = custom
        else:
            cleaned_data['nom'] = predefined

        # Appliquer les mappings
        if predefined and predefined != 'autres':
            mapping = self.FRAIS_MAPPING.get(predefined)
            if mapping:
                cleaned_data['type_frais'] = mapping['type_frais']
                if mapping['section']:
                    itm_section = Section.objects.filter(nom__iexact=mapping['section']).first()
                    if itm_section:
                        cleaned_data['section'] = itm_section
                    else:
                        raise forms.ValidationError("Section configurée introuvable.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.nom = self.cleaned_data.get('nom')
        if commit:
            instance.save()
            self.save_m2m()
        return instance
# forms.py
from django import forms
from .models import Paiement, Eleve, Frais, MoisPaiement, Section, Option, Classe, TRANCHE_CHOICES
from django.contrib.auth import get_user_model
from .access_control import get_accessible_sections  # Utiliser cette fonction à la place

CustomUser = get_user_model()


class FiltragePaiementForm(forms.Form):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Initialisation des champs avec filtrage par rôle
        self.fields['section'].queryset = Section.objects.all()
        self.fields['option'].queryset = Option.objects.all()
        self.fields['classe'].queryset = Classe.objects.all()
        self.fields['frais'].queryset = Frais.objects.all()

        # Appliquer le filtrage si l'utilisateur n'est pas admin/superuser
        if self.user and not (self.user.is_superuser or getattr(self.user, 'role', None) == 'admin'):
            # Obtenir les sections accessibles via la fonction existante
            allowed_sections = get_accessible_sections(self.user)

            # Filtrer les sections selon les droits de l'utilisateur
            self.fields['section'].queryset = allowed_sections

            # Filtrer les options selon les sections autorisées
            allowed_options = Option.objects.filter(section__in=allowed_sections.values_list('id', flat=True))
            self.fields['option'].queryset = allowed_options

            # Filtrer les classes selon les sections/options autorisées
            allowed_classes = Classe.objects.filter(
                models.Q(section__in=allowed_sections) |
                models.Q(option__in=allowed_options)
            ).distinct()
            self.fields['classe'].queryset = allowed_classes

            # Filtrer les frais selon les classes autorisées
            allowed_frais = Frais.objects.filter(classes__in=allowed_classes).distinct()
            self.fields['frais'].queryset = allowed_frais


class PaiementForm(forms.ModelForm):
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_section'})
    )
    option = forms.ModelChoiceField(
        queryset=Option.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_option'})
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_classe'})
    )
    eleve = forms.ModelChoiceField(
        queryset=Eleve.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_eleve'})
    )
    frais = forms.ModelChoiceField(
        queryset=Frais.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_frais'})
    )
    type_frais = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_type_frais', 'readonly': 'readonly'})
    )
    mois = forms.ChoiceField(
        choices=[('', 'Non applicable')] + list(MoisPaiement.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_mois'})
    )
    tranche = forms.ChoiceField(
        choices=TRANCHE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_tranche'})
    )
    montant_a_payer = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_montant_a_payer', 'readonly': 'readonly'})
    )
    montant_paye = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_montant_paye'})
    )
    solde_restant = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'id_solde_restant', 'readonly': 'readonly'})
    )

    class Meta:
        model = Paiement
        fields = ['section', 'option', 'classe', 'eleve', 'frais', 'type_frais', 'mois', 'montant_a_payer',
                  'montant_paye', 'solde_restant']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PaiementForm, self).__init__(*args, **kwargs)

        # Initialiser les querysets selon les permissions
        if self.user and not (self.user.is_superuser or getattr(self.user, 'role', None) == 'admin'):
            accessible_sections = get_accessible_sections(self.user)
            self.fields['section'].queryset = accessible_sections

            # Initialiser les autres champs avec les sections accessibles
            self.fields['option'].queryset = Option.objects.filter(section__in=accessible_sections)
            self.fields['classe'].queryset = Classe.objects.filter(section__in=accessible_sections)
        else:
            self.fields['section'].queryset = Section.objects.all()
            self.fields['option'].queryset = Option.objects.all()
            self.fields['classe'].queryset = Classe.objects.all()

        # Gestion des requêtes POST
        if 'section' in self.data:
            try:
                section_id = int(self.data.get('section'))
                self.fields['option'].queryset = Option.objects.filter(section_id=section_id)
                self.fields['classe'].queryset = Classe.objects.filter(section_id=section_id)

                if 'option' in self.data and self.data.get('option'):
                    option_id = int(self.data.get('option'))
                    self.fields['classe'].queryset = Classe.objects.filter(section_id=section_id, option_id=option_id)

                if 'classe' in self.data and self.data.get('classe'):
                    classe_id = int(self.data.get('classe'))
                    self.fields['eleve'].queryset = Eleve.objects.filter(classe_id=classe_id)
                    self.fields['frais'].queryset = Frais.objects.filter(classes__id=classe_id)

            except (ValueError, TypeError):
                pass

    def update_dependent_fields(self, section_id):
        """Met à jour les champs option, classe, eleve et frais en fonction de la section"""
        # Options pour la section sélectionnée
        self.fields['option'].queryset = Option.objects.filter(section_id=section_id)

        # Classes pour la section (et option si disponible)
        option_id = None
        if 'option' in self.data and self.data.get('option'):
            try:
                option_id = int(self.data.get('option'))
                self.fields['classe'].queryset = Classe.objects.filter(
                    section_id=section_id, option_id=option_id)
            except (ValueError, TypeError):
                pass

        if not option_id:
            self.fields['classe'].queryset = Classe.objects.filter(section_id=section_id)

        # Élèves et frais si classe est sélectionnée
        if 'classe' in self.data and self.data.get('classe'):
            try:
                classe_id = int(self.data.get('classe'))
                self.fields['eleve'].queryset = Eleve.objects.filter(classe_id=classe_id)
                self.fields['frais'].queryset = Frais.objects.filter(classes__id=classe_id)
            except (ValueError, TypeError):
                pass


class ModifierPaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['eleve', 'frais', 'mois', 'tranche', 'montant_paye', 'recu_numero']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marquer les autres champs comme readonly
        for field_name, field in self.fields.items():
            if field_name != 'montant_paye':  # Seul `montant_paye` peut être modifié
                field.widget.attrs['readonly'] = True  # Lecture seule
                field.widget.attrs['class'] = 'form-control readonly-bg'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_montant_paye(self):
        montant_paye = self.cleaned_data.get('montant_paye')

        # Récupérer l'objet frais relié au paiement
        frais = self.instance.frais  # `self.instance` correspond au Paiement actuel
        montant_total = frais.montant  # Montant total des frais définis dans la base de données

        if montant_paye > montant_total:
            raise forms.ValidationError(
                f"Le montant payé ({montant_paye} FC) ne peut pas dépasser le montant du frais ({montant_total} FC)."
            )

        return montant_paye


class SuiviFinancierForm(forms.Form):
    PERIODE_CHOICES = [
        ('jour', 'Par Jour'),
        ('mois', 'Par Mois'),
        ('annee', 'Par Année'),
        ('personnalise', 'Période personnalisée'),
    ]

    periode = forms.ChoiceField(
        choices=PERIODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        label="Date précise",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    mois = forms.ChoiceField(
        choices=[('', 'Non applicable')] + list(MoisPaiement.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    date_debut = forms.DateField(
        label="Date de début",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_fin = forms.DateField(
        label="Date de fin",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    annee_scolaire = forms.ModelChoiceField(
        queryset=AnneeScolaire.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),  # Initialisé vide
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_section'})
    )
    option = forms.ModelChoiceField(
        queryset=Option.objects.none(),  # Initialisé vide
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_option'})
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),  # Initialisé vide
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_classe'})
    )

    def clean(self):
        cleaned_data = super().clean()
        periode = cleaned_data.get("periode")
        date = cleaned_data.get("date")
        mois = cleaned_data.get("mois")
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")

        if periode == "jour" and not date:
            raise forms.ValidationError("La date est obligatoire pour la période 'par jour'.")

        elif periode == "mois" and not mois:
            raise forms.ValidationError("Le mois est obligatoire pour la période 'par mois'.")

        elif periode == "personnalise":
            if not date_debut or not date_fin:
                raise forms.ValidationError("Veuillez indiquer une date de début et une date de fin.")
            if date_debut > date_fin:
                raise forms.ValidationError("La date de fin ne peut pas être antérieure à la date de début.")

        return cleaned_data

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user:
            # Filtrer les sections selon le rôle
            accessible_sections = get_accessible_sections(user)
            self.fields['section'].queryset = accessible_sections

            # Filtrer les options et classes
            section_ids = accessible_sections.values_list('id', flat=True)
            self.fields['option'].queryset = Option.objects.filter(section__id__in=section_ids)
            self.fields['classe'].queryset = Classe.objects.filter(section__id__in=section_ids)


# D:\Projects\wantashi\gestion\forms.py

class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ['motif', 'montant', 'section']  # ⬅️ 确保没有包含 date_depense
        widgets = {
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'section': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filtrer les sections selon les droits de l'utilisateur
        if self.user and not (self.user.is_superuser or self.user.role == 'admin'):
            self.fields['section'].queryset = get_accessible_sections(self.user)

            # Si une seule section est disponible, la sélectionner par défaut
            if self.fields['section'].queryset.count() == 1:
                self.initial['section'] = self.fields['section'].queryset.first()


class FiltragePaiementForm(forms.Form):
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(),  # Initialisé vide, sera rempli dans __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Section"
    )
    option = forms.ModelChoiceField(
        queryset=Option.objects.none(),  # Initialisé vide
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Option"
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),  # Initialisé vide
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    frais = forms.ModelChoiceField(
        queryset=Frais.objects.none(),  # Initialisé vide
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Types de frais"
    )
    mois = forms.ChoiceField(
        choices=[
            ('', '--- Mois ---'),
            ('1', 'Janvier'),
            ('2', 'Février'),
            ('3', 'Mars'),
            ('4', 'Avril'),
            ('5', 'Mai'),
            ('6', 'Juin'),
            ('7', 'Juillet'),
            ('8', 'Août'),
            ('9', 'Septembre'),
            ('10', 'Octobre'),
            ('11', 'Novembre'),
            ('12', 'Décembre'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Mois"
    )
    matricule = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Matricule de l’élève'}),
        label="Matricule"
    )
    mois_tranche = forms.ChoiceField(
        choices=MoisPaiement.choices,
        required=False,
        label="Mois ou Tranche",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    statut = forms.ChoiceField(
        choices=[("", "--- Statut ---"), ("Payé", "Payé"), ("Impayé", "Impayé")],
        required=False,
        label="Statut",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user:
            # Pour les superusers et admins, tout est accessible
            if user.is_superuser or user.role == 'admin':
                self.fields['section'].queryset = Section.objects.all()
                self.fields['option'].queryset = Option.objects.all()
                self.fields['classe'].queryset = Classe.objects.all()
                self.fields['frais'].queryset = Frais.objects.all()
            else:
                # Pour les autres rôles, on filtre selon les sections accessibles
                accessible_sections = get_accessible_sections(user)
                section_ids = accessible_sections.values_list('id', flat=True)

                # Sections accessibles
                self.fields['section'].queryset = accessible_sections

                # Options des sections accessibles
                self.fields['option'].queryset = Option.objects.filter(section__id__in=section_ids)

                # Classes des sections accessibles
                self.fields['classe'].queryset = Classe.objects.filter(section__id__in=section_ids)

                # Frais des classes accessibles
                classe_ids = self.fields['classe'].queryset.values_list('id', flat=True)
                self.fields['frais'].queryset = Frais.objects.filter(classes__id__in=classe_ids).distinct()

        # Gestion des dépendances dynamiques si des données sont déjà envoyées
        if 'section' in self.data:
            try:
                section_id = int(self.data.get('section'))
                self.fields['option'].queryset = Option.objects.filter(section_id=section_id)
                self.fields['classe'].queryset = Classe.objects.filter(section_id=section_id)
            except (ValueError, TypeError):
                pass

        if 'option' in self.data:
            try:
                option_id = int(self.data.get('option'))
                self.fields['classe'].queryset = Classe.objects.filter(option_id=option_id)
            except (ValueError, TypeError):
                pass

        if 'classe' in self.data:
            try:
                classe_id = int(self.data.get('classe'))
                self.fields['frais'].queryset = Frais.objects.filter(classes__id=classe_id)
            except (ValueError, TypeError):
                pass


class InscriptionForm:
    pass


# forms.py

# forms.py
from django import forms
from .models import Section, Option


class AjouterSectionOptionForm(forms.Form):
    OPERATION_CHOICES = [
        ('section', 'Ajouter une nouvelle section'),
        ('option', 'Ajouter une nouvelle option')
    ]

    operation = forms.ChoiceField(
        choices=OPERATION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label="Type d'opération"
    )

    # Champs pour une nouvelle section
    nom_section = forms.CharField(
        max_length=50,
        required=False,
        label="Nom de la section",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: ITM, Humanités'
        })
    )

    type_section = forms.ChoiceField(
        choices=Section.TYPE_SECTION_CHOICES,
        required=False,
        label="Type de section",
        widget=forms.Select(attrs={
            'class': 'form-select form-control',
            'data-toggle': 'select'
        })
    )

    # Champs pour une nouvelle option
    # forms.py

    section_existant = forms.ModelChoiceField(
        queryset=Section.objects.all().order_by('nom'),  # ✅ Changé ici
        required=False,
        label="Section existante",
        empty_label="Sélectionnez une section",
        widget=forms.Select(attrs={
            'class': 'form-select form-control',
            'data-toggle': 'select'
        })
    )

    nom_option = forms.CharField(
        max_length=50,
        required=False,
        label="Nom de l'option",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Informatique, Électronique'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        operation = cleaned_data.get('operation')

        if operation == 'section':
            if not cleaned_data.get('nom_section'):
                self.add_error('nom_section', "Ce champ est requis pour l'ajout d'une section.")
            if not cleaned_data.get('type_section'):
                self.add_error('type_section', "Ce champ est requis pour l'ajout d'une section.")
        elif operation == 'option':
            if not cleaned_data.get('section_existant'):
                self.add_error('section_existant', "Vous devez sélectionner une section existante.")
            if not cleaned_data.get('nom_option'):
                self.add_error('nom_option', "Ce champ est requis pour l'ajout d'une option.")

        return cleaned_data
