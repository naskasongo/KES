from time import sleep

from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

# Définition des rôles
ROLE_CHOICES = [
    ('admin', 'Administrateur'),
    ('directeur', 'Directeur'),
    ('prefet', 'Préfet'),
    ('prefet_itm', 'Préfet ITM'),
    ('directeur_financier', 'Directeur Financier'),
    ('prefet_financier', 'Prefet Financier'),
    ('ITM_financier', 'ITM Financier'),

]


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')

    def get_unread_notifications_count(self):
        return self.notifications.filter(est_lue=False).count()

    def get_latest_notifications(self, limit=5):
        return self.notifications.select_related('historique_action').filter(est_lue=False).order_by('-date_creation')[
               :limit]

    class Meta:
        permissions = [
            ("can_manage_maternelle_primaire", "Peut gérer Maternelle & Primaire"),
            ("can_manage_secondaire_humanites", "Peut gérer Secondaire & Humanités"),
            ("can_manage_itm", "Peut gérer ITM"),
            ("can_manage_finances", "Peut gérer les finances"),
        ]

    def has_access_to_section(self, section):
        """
        Vérifie si l'utilisateur a accès à une section donnée
        """
        role_permissions_map = {
            "admin": [
                "can_manage_maternelle_primaire",
                "can_manage_secondaire_humanites",
                "can_manage_itm",
                "can_manage_finances",
            ],
            "directeur": ["can_manage_maternelle_primaire"],
            "prefet": ["can_manage_secondaire_humanites"],
            "prefet_ITM": ["can_manage_itm"],
            "directeur_finances": [],  # Hérite dynamiquement dans la vue
        }

        user_permissions = role_permissions_map.get(self.role, [])

        # Traitement spécial pour le rôle "directeur_finances"
        if self.role == "directeur_finances":
            # Vérifie si l'utilisateur appartient à une "direction"
            parent_role = self.get_finance_subordinate_role()
            if parent_role:
                user_permissions = role_permissions_map.get(parent_role, [])

        return section in user_permissions

    def get_finance_subordinate_role(self):
        """
        Retourne le rôle des subordonnés que gère un directeur financier.
        Exemple: directeur_finances lié à "directeur" ou "prefet"
        """
        finance_role_map = {
            "direction_finances_maternelles": "directeur",
            "direction_finances_secondaires": "prefet",
            "direction_finances_itm": "prefet_ITM",
        }
        # Ajoutez ici la logique pour mapper
        return finance_role_map.get(self.role)


# Modèle AnneeScolaire

# Modèle AnneeScolaire
from django.db import models
from datetime import date

class AnneeScolaire(models.Model):
    """
    Modèle pour représenter une année scolaire au format "2024-2025".
    """
    annee = models.CharField(max_length=9, unique=True)  # Par exemple "2024-2025"

    @staticmethod
    def obtenir_annee_courante():
        """
        Méthode statique pour récupérer ou créer l'année scolaire en cours.
        - Exemple : si nous sommes en octobre 2024, elle retourne "2024-2025".
        - Après juin, retourne l'année scolaire suivante.
        """
        today = date.today()
        current_year = today.year
        current_month = today.month

        # Déterminer l'année scolaire actuelle
        if current_month >= 9:  # Septembre à décembre → année en cours
            annee_scolaire_str = f"{current_year}-{current_year + 1}"
        else:  # Janvier à août → année précédente
            annee_scolaire_str = f"{current_year - 1}-{current_year}"

        # Récupérer ou créer l'année scolaire courante
        obj, created = AnneeScolaire.objects.get_or_create(annee=annee_scolaire_str)
        if created:
            print(f"L'année scolaire {annee_scolaire_str} a été créée.")

        # Si on est après juin, vérifier si l'année suivante existe
        if current_month > 6:
            next_year = current_year + 1
            next_annee_scolaire_str = f"{next_year}-{next_year + 1}"
            next_obj, next_created = AnneeScolaire.objects.get_or_create(annee=next_annee_scolaire_str)
            if next_created:
                print(f"L'année scolaire {next_annee_scolaire_str} a été créée.")
            return next_obj  # Retourner la nouvelle année après juin

        return obj  # Sinon, retourner l'année courante

    @property
    def debut(self):
        """Calcule la date de début de l'année scolaire."""
        debut_annee = int(self.annee.split('-')[0])
        return date(debut_annee, 9, 1)  # 1er septembre de l'année de début

    @property
    def fin(self):
        """Calcule la date de fin de l'année scolaire."""
        fin_annee = int(self.annee.split('-')[1])
        return date(fin_annee, 6, 30)  # 30 juin de l'année de fin


    @staticmethod
    def obtenir_annee_precedente():
        """
        Méthode statique pour récupérer l'année scolaire précédente.
        - Exemple : si l'année courante est "2024-2025", elle retourne "2023-2024".
        """
        # Obtenir l'année scolaire actuelle
        annee_courante = AnneeScolaire.obtenir_annee_courante()

        # Extraire les années de l'année scolaire (par exemple, "2024-2025" devient [2024, 2025])
        debut, fin = map(int, annee_courante.annee.split('-'))

        # Calculer l'année scolaire précédente
        annee_precedente_str = f"{debut - 1}-{fin - 1}"

        # Récupérer ou créer l'année scolaire précédente dans la base de données
        obj, created = AnneeScolaire.objects.get_or_create(annee=annee_precedente_str)
        if created:
            print(f"L'année scolaire {annee_precedente_str} a été créée.")
        return obj



    def clean(self):
        annees = self.annee.split('-')
        if len(annees) != 2 or not (annees[0].isdigit() and annees[1].isdigit()):
            raise ValidationError("Le format de l'année scolaire doit être 'YYYY-YYYY'.")
        debut, fin = map(int, annees)
        if fin - debut != 1:
            raise ValidationError("Les deux années doivent être consécutives.")

    def __str__(self):
        """
        Représentation en chaîne de caractères du modèle AnneeScolaire.
        """
        return self.annee


# Modèles Section et Option
class Section(models.Model):
    nom = models.CharField(max_length=50, unique=True)
    TYPE_SECTION_CHOICES = [
        ('maternelle', 'maternelle'),
        ('primaire', 'primaire'),
        ('secondaire', 'secondaire'),
        ('itm', 'ITM'),
        ('humanite', 'Humanités')
    ]

    type_section = models.CharField(
        max_length=10,
        choices=TYPE_SECTION_CHOICES,
        default='itm'
    )

    def __str__(self):
        return self.nom


class Option(models.Model):
    nom = models.CharField(max_length=50)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="options")

    def __str__(self):
        return f"{self.nom} ({self.section.nom if self.section else 'Toutes sections'})"


# Modèle Classe
class Classe(models.Model):
    nom = models.CharField(max_length=50)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="classes")
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="classes", null=True, blank=True)

    def __str__(self):
        if self.option:
            return f"{self.nom} - {self.option.nom}"
        return f"{self.nom} ({self.section.nom})"

class MoisPaiement(models.TextChoices):
    SEPTEMBRE = "Septembre", "Septembre"
    OCTOBRE = "Octobre", "Octobre"
    NOVEMBRE = "Novembre", "Novembre"
    DECEMBRE = "Décembre", "Décembre"
    JANVIER = "Janvier", "Janvier"
    FEVRIER = "Février", "Février"
    MARS = "Mars", "Mars"
    AVRIL = "Avril", "Avril"
    MAI = "Mai", "Mai"
    JUIN = "Juin", "Juin"

# Modèle Parent
class Parent(models.Model):
    nom = models.CharField(max_length=50)
    telephone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    relation = models.CharField(
        max_length=20,
        choices=[("Père", "Père"), ("Mère", "Mère"), ("Tuteur", "Tuteur")],
    )

    def __str__(self):
        return f"{self.nom} ({self.relation})"
# Modèle Eleve
# Fonctions utilitaires pour les valeurs par défaut
def get_default_annee_scolaire():
    """Retourne l'année scolaire courante comme objet AnneeScolaire"""
    return AnneeScolaire.obtenir_annee_courante()
# Modèle Eleve



class Eleve(models.Model):
    GENRE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

    nom = models.CharField(max_length=50)
    post_nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50, blank=True, null=True)
    sexe = models.CharField(max_length=1, choices=GENRE_CHOICES)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    matricule = models.CharField(max_length=20, unique=True)

    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.SET_NULL, null=True, blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

    annee_scolaire = models.ForeignKey(
        AnneeScolaire,
        on_delete=models.CASCADE,
        editable=False,
        default=get_default_annee_scolaire

    )
    parent = models.ForeignKey('Parent', on_delete=models.CASCADE, related_name='eleves', null=True, blank=True)
    #documents_fournis = models.ManyToManyField("DocumentRequis", blank=True)  # 🔹 Nouveau champ

    def save(self, *args, **kwargs):
        if not self.annee_scolaire_id:
            self.annee_scolaire = AnneeScolaire.obtenir_annee_courante()

        if not self.matricule:
            annee_actuelle = self.annee_scolaire.annee[2:4]  # "2024" -> "24"
            initiales = f"{self.nom[0]}{self.post_nom[0]}".upper()

            dernier_eleve = Eleve.objects.filter(
                annee_scolaire=self.annee_scolaire
            ).order_by('-matricule').first()

            if dernier_eleve:
                import re
                match = re.search(r'(\d+)$', dernier_eleve.matricule)
                dernier_num = int(match.group(1)) if match else 0
            else:
                dernier_num = 0

            nouvel_id = f"{dernier_num + 1:03d}"
            self.matricule = f"{annee_actuelle}{initiales}{nouvel_id}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.post_nom} {self.prenom} ({self.matricule})"




TRANCHE_CHOICES = [
    ("1ère Tranche", "1ère Tranche"),
    ("2ème Tranche", "2ème Tranche"),
    ("3ème Tranche", "3ème Tranche"),
]

# Modèle Frais
from decimal import Decimal
class Frais(models.Model):
    TYPE_FRAIS_CHOICES = [
        ('Mensuel', 'Mensuel'),
        ('Trimestriel', 'Trimestriel'),
        ('Annuel', 'Annuel'),
        ('Occasionnel', 'Occasionnel'),
    ]
    nom = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    type_frais = models.CharField(max_length=20, choices=TYPE_FRAIS_CHOICES)

    mois = models.CharField(max_length=20, null=True, blank=True)
    section = models.ForeignKey("Section", on_delete=models.CASCADE, null=True, blank=True, related_name="frais")
    option = models.ForeignKey("Option", on_delete=models.CASCADE, null=True, blank=True, related_name="frais")
    classes = models.ManyToManyField("Classe", blank=True, related_name="frais")
    tranche = models.CharField(max_length=50, choices=TRANCHE_CHOICES, blank=True, null=True)  # Pour Trimestriel
    annee_scolaire = models.ForeignKey(
        "AnneeScolaire",
        on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nom} - {self.type_frais} FC"


from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

class PaiementManager(models.Manager):
    def calculer_solde(self, eleve, frais, mois_cible=None):
        """Version améliorée avec meilleure gestion des soldes précédents"""
        montant_frais = frais.montant
        paiements = self.filter(eleve=eleve, frais=frais).order_by('mois')

        if frais.type_frais != "Mensuel":
            total_paye = sum(p.montant_paye for p in paiements)
            return {
                'montant_frais': montant_frais,
                'total_paye': total_paye,
                'solde_restant': montant_frais - total_paye,
                'solde_precedent': 0,
                'soldes_precedents': {},
                'montant_net': montant_frais
            }

        # Pour les frais mensuels
        mois_ordre = [m.value for m in MoisPaiement]
        soldes_precedents = {}
        total_soldes_precedents = Decimal('0.00')

        if mois_cible in mois_ordre:
            index_mois = mois_ordre.index(mois_cible)

            for i in range(index_mois):
                mois_precedent = mois_ordre[i]
                paiement = paiements.filter(mois=mois_precedent).first()

                if paiement and paiement.solde_restant > Decimal('0'):
                    soldes_precedents[mois_precedent] = paiement.solde_restant
                    total_soldes_precedents += paiement.solde_restant

        montant_net = montant_frais + total_soldes_precedents

        return {
            'montant_frais': montant_frais,
            'montant_net': montant_net,
            'soldes_precedents': soldes_precedents,
            'total_soldes_precedents': total_soldes_precedents,
            'solde_precedent': total_soldes_precedents,
        }


class Paiement(models.Model):
    eleve = models.ForeignKey("Eleve", on_delete=models.CASCADE)
    frais = models.ForeignKey("Frais", on_delete=models.CASCADE)
    mois = models.CharField(max_length=255, choices=MoisPaiement.choices, blank=True, null=True)
    tranche = models.CharField(max_length=50, choices=TRANCHE_CHOICES, blank=True, null=True)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=2)
    solde_restant = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    date_paiement = models.DateField(auto_now_add=True)
    recu_numero = models.CharField(max_length=255, unique=True)
    annee_scolaire = models.ForeignKey(
        "AnneeScolaire",
        on_delete=models.CASCADE,
        verbose_name="Année Scolaire",
        null=False,  # Changé à False pour garantir l'intégrité
        blank=False
    )

    objects = PaiementManager()

    def save(self, *args, **kwargs):
        # Générer le reçu uniquement à la création
        if not self.pk and not self.recu_numero:
            self.recu_numero = self.generate_recu_numero()

        # Met à jour le solde avant sauvegarde
        if self.frais.type_frais == "Mensuel":
            self.update_solde_mois_precedent()

        # Calculer le solde final
        self.calculate_solde()

        super().save(*args, **kwargs)

    def calculate_solde(self):
        """
        Calcule automatiquement le solde en fonction du type de frais
        """
        paiements = Paiement.objects.filter(
            eleve=self.eleve,
            frais=self.frais
        ).exclude(pk=self.pk).order_by('date_paiement')

        if self.frais.type_frais == "Mensuel":
            self.handle_mensuel(paiements)
        elif self.frais.type_frais == "Trimestriel":
            self.handle_trimestriel(paiements)
        else:  # Annuel
            self.handle_annuel(paiements)

    def handle_mensuel(self, paiements):
        """
        Gestion spécifique des frais mensuels avec report de solde
        """
        mois_ordre = [m[0] for m in MoisPaiement.choices]
        try:
            current_index = mois_ordre.index(self.mois)
        except ValueError:
            raise ValidationError(f"Mois '{self.mois}' invalide.")

        solde_precedent = Decimal('0.00')
        if current_index > 0:
            prev_month = mois_ordre[current_index - 1]
            prev_payment = paiements.filter(mois=prev_month).first()
            if prev_payment and prev_payment.solde_restant > Decimal('0'):
                solde_precedent = prev_payment.solde_restant
                prev_payment.solde_restant = Decimal('0.00')
                prev_payment.save(update_fields=['solde_restant'])

        montant_net = self.frais.montant + solde_precedent
        self.solde_restant = montant_net - self.montant_paye

        if self.montant_paye > montant_net:
            raise ValidationError(
                f"Le montant payé ({self.montant_paye}) dépasse le montant net à payer ({montant_net}) "
                f"(incluant un solde précédent de {solde_precedent})"
            )

    def handle_trimestriel(self, paiements):
        montant_par_tranche = self.frais.montant

        if paiements.filter(tranche=self.tranche).exists():
            raise ValidationError(f"La tranche {self.tranche} a déjà été payée")

        if self.montant_paye > montant_par_tranche:
            raise ValidationError(
                f"Le montant payé ({self.montant_paye}) dépasse le montant de la tranche ({montant_par_tranche})"
            )

        self.solde_restant = montant_par_tranche - self.montant_paye

    def handle_annuel(self, paiements):
        if paiements.exists():
            raise ValidationError("Les frais annuels ont déjà été payés")
        self.solde_restant = self.frais.montant - self.montant_paye

    def update_solde_mois_precedent(self):
        if self.frais.type_frais == "Mensuel" and self.mois:
            mois_ordre = [m.value for m in MoisPaiement]
            try:
                index_mois = mois_ordre.index(self.mois)
            except ValueError:
                return

            if index_mois > 0:
                mois_precedent = mois_ordre[index_mois - 1]
                paiement_precedent = Paiement.objects.filter(
                    eleve=self.eleve,
                    frais=self.frais,
                    mois=mois_precedent
                ).first()

                if paiement_precedent and paiement_precedent.solde_restant > Decimal('0'):
                    paiement_precedent.solde_restant = Decimal('0.00')
                    paiement_precedent.save(update_fields=['solde_restant'])

    def generate_recu_numero(self):
        annee_paiement = self.date_paiement.year
        dernier_paiement = Paiement.objects.filter(
            date_paiement__year=annee_paiement
        ).order_by('-id').first()

        dernier_id = dernier_paiement.id if dernier_paiement else 0
        return f"REC-{annee_paiement}-{str(dernier_id + 1).zfill(4)}"

    def __str__(self):
        return f"{self.eleve} - {self.frais.nom} - {self.montant_paye} FC"



from django.db import models

class Depense(models.Model):
    motif = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_depense = models.DateField(auto_now_add=True, editable=False)
    section = models.ForeignKey("Section", on_delete=models.SET_NULL, null=True, blank=True)
    annee_scolaire = models.ForeignKey(
        "AnneeScolaire",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Année scolaire associée à la dépense"
    )
    def __str__(self):
        return f"{self.motif} - {self.montant} FC ({self.date_depense})"


# models.py
class Inscription(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='inscriptions')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, db_column='annee_scolaire')  # Ajout du db_column
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)
    est_reinscription = models.BooleanField(default=False)

    @property
    def est_nouveau(self):
        """
        Retourne True si l'inscription est une nouvelle inscription,
        False si c'est une réinscription.
        """
        return not self.est_reinscription

    class Meta:
        unique_together = ('eleve', 'annee_scolaire')
        ordering = ['-annee_scolaire', 'eleve__nom']

    def __str__(self):
        return f"{self.eleve} - {self.annee_scolaire} ({self.classe})"


# models.py
# models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class HistoriqueAction(models.Model):
    ACTION_CREATION = 'Création'
    ACTION_MODIFICATION = 'Modification'
    ACTION_SUPPRESSION = 'Suppression'

    TYPE_ACTION_CHOICES = (
        (ACTION_CREATION, 'Création'),
        (ACTION_MODIFICATION, 'Modification'),
        (ACTION_SUPPRESSION, 'Suppression'),
    )

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Utilisateur"
    )
    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Nom d'utilisateur au moment de l'action"
    )
    modele = models.CharField(max_length=100, verbose_name="Modèle")
    objet_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID Objet")
    action = models.CharField(max_length=20, choices=TYPE_ACTION_CHOICES, verbose_name="Action")
    details = models.TextField(blank=True, verbose_name="Détails")
    date_action = models.DateTimeField(default=timezone.now, verbose_name="Date")

    def save(self, *args, **kwargs):
        if self.utilisateur and not self.username:
            self.username = self.utilisateur.get_full_name() or self.utilisateur.username
        super().save(*args, **kwargs)

    @property
    def utilisateur_affichage(self):
        if self.username:
            return self.username
        if self.utilisateur:
            return self.utilisateur.get_full_name() or self.utilisateur.username
        return self.utilisateur
# models.py
from django.db import models
from .models import CustomUser, HistoriqueAction


class Notification(models.Model):
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    historique_action = models.ForeignKey(HistoriqueAction, on_delete=models.CASCADE)
    est_lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.historique_action} pour {self.utilisateur}"


from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    totp_secret = models.CharField(max_length=100, blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Créer un UserProfile automatiquement lorsqu'un User est créé
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
