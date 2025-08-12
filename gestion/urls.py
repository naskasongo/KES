from django.urls import path, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views
from .views import get_classes, get_frais, get_frais_details, get_solde_restant, get_mois_suivant, \
    get_eleve_by_matricule, CustomPasswordChangeView, detail_utilisateur, modifier_utilisateur, historique_activites
from .views import HistoriqueActionViewSet

from gestion.views import ExportDataView
# Endpoints AJAX pour frais et paiement\n    path('api/get-options/<int:section_id>/', views.get_options, name='get_options'),\n    path('api/get-classes/<int:section_id>/', views.get_classes, name='get_classes'),\n    path('api/get-classes/<int:section_id>/<int:option_id>/', views.get_classes, name='get_classes_option'),\n    path('api/get-eleves/<int:classe_id>/', views.get_eleves, name='get_eleves'),\n    path('api/get-frais/<int:classe_id>/', views.get_frais, name='get_frais'),
from rest_framework.routers import DefaultRouter
from .views import HistoriqueActionViewSet
from .views import liste_notifications, details_notification, PasswordResetView

router = DefaultRouter()
router.register(r'activites', HistoriqueActionViewSet, basename='activite')

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Add the password reset URL
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # Gestion des élèves
    path('eleves/', views.liste_eleves, name='liste_eleves'),
    path('eleves/ajouter/', views.ajouter_eleve, name='ajouter_eleve'),
    path('eleves/modifier/<int:id>/', views.modifier_eleve, name='modifier_eleve'),
    path('eleves/supprimer/<int:id>/', views.supprimer_eleve, name='supprimer_eleve'),
    path('eleves/reinscription/', views.reinscription, name='reinscription'),
    path('profil/', views.profil_utilisateur, name='profil_utilisateur'),
    path('eleves/details/<int:eleve_id>/', views.detail_eleve, name='details_eleve'),
    path('eleves/classe/<int:classe_id>/', views.eleves_par_classe, name='eleves_par_classe'),
    path('eleves/section/<int:section_id>/', views.eleves_par_section, name='eleves_par_section'),
    path('sections/classe/<int:classe_id>/', views.details_classe, name='details_classe'),
    path('valider/documents/', views.valider_documents, name='valider_documents'),
    path('valider/documents/<int:eleve_id>/', views.valider_documents, name='valider_documents'),
 #   path('classes/<int:classe_id>/export/csv/', views.export_classe_csv, name='export_classe_csv'),
    path('ajouter-section/', views.ajouter_section_ou_option, name='ajouter_section_ou_option'),
    path('documentation/', views.documentation_view, name='documentation'),
    path('guide-utilisation/', views.guide_utilisation_view, name='guide_utilisation'),

    #parent
    #path('parents/<int:parent_id>/', views.parent_detail, name='parent_detail'),
    path('parents/<int:parent_id>/', views.detail_parent, name='detail_parent'),


    #users
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    # Inscriptions
    path('inscriptions/', views.liste_inscriptions, name='liste_inscriptions'),
    # Nouvelle vue pour changer le mot de passe d'un autre utilisateur
    path('utilisateurs/<int:user_id>/changer-mot-de-passe/',
         views.AdminPasswordChangeView.as_view(),
         name='change_user_password'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('utilisateurs/<int:user_id>/', detail_utilisateur, name='detail_utilisateur'),
    path('utilisateurs/<int:user_id>/modifier/', modifier_utilisateur, name='modifier_utilisateur'),
    path('utilisateurs/', views.liste_utilisateurs, name='utilisateurs'),  # ✔️ Nom
    path('changer-annee/', views.changer_annee_scolaire, name='changer_annee_scolaire'),
    # Frais
    path('frais/', views.liste_frais, name='liste_frais'),
    path('frais/ajouter/', views.ajouter_frais, name='ajouter_frais'),
    path('frais/modifier/<int:frais_id>/', views.modifier_frais, name='modifier_frais'),
    path('frais/supprimer/<int:frais_id>/', views.supprimer_frais, name='supprimer_frais'),




    # Paiements
    path('paiements/', views.liste_paiements, name='liste_paiements'),
    path('paiements/ajouter/', views.ajouter_paiement, name='ajouter_paiement'),
    path('paiements/<int:paiement_id>/', views.detail_paiement, name='detail_paiement'),
    path('paiements/modifier/<int:paiement_id>/', views.modifier_paiement, name='modifier_paiement'),
    path('modifier-paiement/<int:paiement_id>/', views.modifier_paiement, name='modifier_paiement'),
    path('paiements/supprimer/<int:paiement_id>/', views.supprimer_paiement, name='supprimer_paiement'),

    #recu_paiement
    path('recu_paiement/<int:paiement_id>/', views.recu_paiement, name='recu_paiement'),


    # API AJAX pour paiements
    path('api/get-solde/<int:eleve_id>/', views.get_solde, name='get_solde'),
    path('api/get-historique/<int:eleve_id>/', views.get_historique_paiements, name='get_historique'),
    path('api/get-historique/<int:eleve_id>/', views.get_historique_paiements, name='get_historique_paiements'),
    path('api/get-mois-suivant/<int:eleve_id>/<int:frais_id>/', views.get_mois_suivant, name='get_mois_suivant'),
   # path('ajax/charger-champs/', views.charger_champs_ajax, name='charger_champs_ajax'),
    path('calcul_solde/', views.calcul_solde, name='calcul_solde'),
    path('api/get-classes/<int:section_id>/', get_classes, name='get_classes'),
    path('api/get-classes/<int:section_id>/<int:option_id>/', get_classes, name='get_classes_option'),
    path('api/get-frais/<int:classe_id>/', views.get_frais, name='get_frais'),
    path('api/get-frais-details/<int:frais_id>/', views.get_frais_details, name='get_frais_details'),
    path('api/get-solde-restant/<int:eleve_id>/<int:frais_id>/', get_solde_restant, name='get_solde_restant'),
    path('api/get-solde-restant/<int:eleve_id>/<int:frais_id>/', views.get_solde_restant, name='get_solde_restant'),
    path('api/get-mois-suivant/<int:eleve_id>/<int:frais_id>/', views.get_mois_suivant, name='get_mois_suivant'),
    path('api/get-eleve-by-matricule/<str:matricule>/', get_eleve_by_matricule, name='get_eleve_by_matricule'),
path('api/get-eleve-by-matricule/<str:matricule>/', views.get_eleve_by_matricule, name='get_eleve_by_matricule'),
    path('api/classes/<int:section_id>/', get_classes, name='get_classes_without_option'),  # Pour option null
    # API AJAX pour options, classes, élèves et frais (déjà existants)
    path('api/get-options/<int:section_id>/', views.get_options, name='get_options'),
    path('api/get-classes/<int:section_id>/<int:option_id>/', views.get_classes, name='get_classes_option'),
    path('api/get-classes/<int:section_id>/', views.get_classes, name='get_classes_section'),
    path('api/get-eleves/<int:classe_id>/', views.get_eleves, name='get_eleves'),
    path('api/get-frais/<int:classe_id>/', views.get_frais, name='get_frais'),

    # Route pour obtenir la liste des années scolaires
    path('api/get-annees-scolaires/', views.get_annees_scolaires, name='get_annees_scolaires'),

    path('api/get-classes/<int:section_id>/', views.get_classes_dynamique),
    path('api/get-classes/<int:section_id>/<int:option_id>/', views.get_classes_dynamique),
    path('api/dashboard-stats/', views.get_dashboard_stats, name='get_dashboard_stats'),


path('suivi-financier/', views.suivi_financier, name='suivi_financier'),
    path('ajouter-depense/', views.ajouter_depense, name='ajouter_depense'),
    path('bilan-financier/', views.bilan_financier, name='bilan_financier'),

    path('depenses/', views.liste_depenses, name='liste_depenses'),
    path('depenses/ajouter/', views.ajouter_depense, name='ajouter_depense'),
    path('depenses/supprimer/<int:depense_id>/', views.supprimer_depense, name='supprimer_depense'),
    path('parents/', views.liste_parents, name='liste_parents'),


    path("statistiques/", views.statistiques, name="statistiques"),

    #path("dashboard/", views.dashboard, name="dashboard"),

    #export data
    path('api/export/', ExportDataView.as_view(), name='export_data'),

    path('api/', include(router.urls)),
    path('historique/', historique_activites, name='historique'),

    #notifications
    path('notifications/', liste_notifications, name='liste_notifications'),
    path('notifications/<int:notification_id>/', details_notification, name='details_notification'),
# Admin
    path('admin/', admin.site.urls),
]


