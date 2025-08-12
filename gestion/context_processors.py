from django.core.exceptions import PermissionDenied
from .models import Classe, Option

def menu_sections(request):
    if not request.user.is_authenticated:
        return {}  # Si l'utilisateur n'est pas connecté, ne rien renvoyer

    user = request.user
    sections = {}

    if user.is_superuser or user.role == "admin":
        sections = {
            "Maternelle": Classe.objects.filter(section__nom="Maternelle"),
            "Primaire": Classe.objects.filter(section__nom="Primaire"),
            "Secondaire": Classe.objects.filter(section__nom="Secondaire"),
            "Humanités": {
                "Options": {
                    option.nom: Classe.objects.filter(option=option)
                    for option in Option.objects.filter(section__nom="Humanités")
                }
            },
            "ITM": {
                "Options": {
                    option.nom: Classe.objects.filter(option=option)
                    for option in Option.objects.filter(section__nom="ITM")
                }
            },
        }
    elif user.role == "directeur" or user.role =="directeur_financier":
        sections = {
            "Maternelle": Classe.objects.filter(section__nom="Maternelle"),
            "Primaire": Classe.objects.filter(section__nom="Primaire"),
        }
    elif user.role == "prefet" or user.role =="prefet_financier":
        sections = {
            "Secondaire": Classe.objects.filter(section__nom="Secondaire"),
            "Humanités": {
                "Options": {
                    option.nom: Classe.objects.filter(option=option)
                    for option in Option.objects.filter(section__nom="Humanités")
                }
            },
        }
    elif user.role == "prefet_itm" or user.role == "ITM_financier":
        sections = {
            "ITM": {
                "Options": {
                    option.nom: Classe.objects.filter(option=option)
                    for option in Option.objects.filter(section__nom="ITM")
                }
            },
        }
    else:
        raise PermissionDenied("Vous n'avez pas la permission d'accéder aux menus.")

    return {"sections": sections}



from gestion.models import AnneeScolaire

def annee_scolaire_context(request):
    annee = None
    annees = AnneeScolaire.objects.all().order_by('-annee')

    if request.user.is_authenticated:
        try:
            annee_id = request.session.get('annee_scolaire_id')
            annee = AnneeScolaire.objects.get(id=annee_id) if annee_id else None
        except AnneeScolaire.DoesNotExist:
            annee = None

    return {
        'annee_scolaire_active': annee,
        'annees_scolaires': annees,
    }

