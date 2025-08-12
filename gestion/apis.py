from gestion.library import *
import logging
logger = logging.getLogger(__name__)

def get_annee_scolaire(request):
    """Fonction utilitaire pour récupérer l'année scolaire active"""
    # Priorité : paramètre GET > session > année courante
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

    if not annee_id:
        annee = AnneeScolaire.obtenir_annee_courante()
        annee_id = annee.id
        request.session['annee_scolaire_id'] = annee_id
    else:
        try:
            annee = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
            request.session['annee_scolaire_id'] = annee_id

    return annee


from rest_framework.decorators import api_view
def get_annees_scolaires(request):
    annees = AnneeScolaire.objects.all().order_by('-annee')
    annee_courante = AnneeScolaire.obtenir_annee_courante()

    data = {
        'success': True,
        'annees': [{
            'id': annee.id,
            'annee': annee.annee,
            'is_current': annee.id == annee_courante.id
        } for annee in annees]
    }
    return JsonResponse(data)


# API pour récupérer les options et classes dynamiquement *
@login_required
def get_options(request, section_id):
    print(f"Demande d'options pour section_id: {section_id}")  # Debug
    try:
        options = Option.objects.filter(section_id=section_id).values('id', 'nom')
        return JsonResponse({'options': list(options)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def get_classes(request, section_id, option_id=None):
    try:
        # Convertir option_id en None si c'est 'null' ou vide
        option_id = None if option_id in ['null', ''] else option_id

        if option_id is not None:
            # Cas où une option est spécifiée
            classes = Classe.objects.filter(
                section_id=section_id,
                option_id=option_id
            ).order_by('nom').values('id', 'nom')
        else:
            # Cas où aucune option n'est spécifiée
            classes = Classe.objects.filter(
                section_id=section_id,
                option__isnull=True
            ).order_by('nom').values('id', 'nom')

        return JsonResponse({'classes': list(classes)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_classes_dynamique(request, section_id, option_id=None):
    try:
        if option_id and option_id != 'null':
            classes = Classe.objects.filter(section_id=section_id, option_id=option_id).values('id', 'nom')
        else:
            classes = Classe.objects.filter(section_id=section_id, option__isnull=True).values('id', 'nom')
        return JsonResponse(list(classes), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def get_eleves(request, classe_id):
    try:
        # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

        if not annee_id:
            # Utiliser l'année courante si aucune année n'est sélectionnée
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
        else:
            # Vérifier que l'année existe
            try:
                annee = AnneeScolaire.objects.get(id=annee_id)
            except AnneeScolaire.DoesNotExist:
                annee = AnneeScolaire.obtenir_annee_courante()
                annee_id = annee.id

        # Récupérer la classe
        classe = Classe.objects.get(id=classe_id)

        # Vérifier les permissions de la section
        if not check_section_access(request.user, classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Appliquer le filtrage selon les permissions et l'année scolaire
        eleves = Eleve.objects.filter(classe_id=classe_id, annee_scolaire_id=annee_id)

        if not (request.user.is_superuser or request.user.role == 'admin'):
            eleves = filter_by_user_role(eleves, request.user, 'classe__section__nom')

        eleves_list = list(eleves.values("id", "nom", "post_nom", "matricule"))

        return JsonResponse({
            'eleves': eleves_list,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Classe.DoesNotExist:
        return JsonResponse({'error': 'Classe introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur : {str(e)}'}, status=500)


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
        # Récupérer l'année scolaire active
        annee = get_annee_scolaire(request)

        # Rechercher l'élève par matricule pour l'année scolaire actuelle
        eleve = Eleve.objects.get(
            matricule=matricule,
            annee_scolaire=annee
        )

        # Vérifier les permissions de la section
        if not check_section_access(request.user, eleve.classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Préparer les données de réponse
        data = {
            'success': True,
            'id': eleve.id,
            'matricule': eleve.matricule,
            'nom': eleve.nom,
            'post_nom': eleve.post_nom,
            'classe_id': eleve.classe.id,
            'classe_nom': eleve.classe.nom,
            'section_id': eleve.classe.section.id,
            'section_nom': eleve.classe.section.nom,
            'option_id': eleve.classe.option.id if eleve.classe.option else None,
            'option_nom': eleve.classe.option.nom if eleve.classe.option else None,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id,
            'solde_restant': float(eleve.solde_restant) if hasattr(eleve, 'solde_restant') else 0
        }

        return JsonResponse(data)

    except Eleve.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': f'Aucun élève trouvé avec le matricule {matricule} pour l\'année scolaire courante'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur : {str(e)}'
        }, status=500)

@login_required
def get_dashboard_stats(request):
    try:
        # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

        if not annee_id:
            # Utiliser l'année courante si aucune année n'est sélectionnée
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
            request.session['annee_scolaire_id'] = annee_id
        else:
            # Vérifier que l'année existe
            try:
                annee = AnneeScolaire.objects.get(id=annee_id)
            except AnneeScolaire.DoesNotExist:
                annee = AnneeScolaire.obtenir_annee_courante()
                annee_id = annee.id
                request.session['annee_scolaire_id'] = annee_id

        period = request.GET.get('period', 'month')
        today = datetime.today()

        # Initialisation des variables
        current_total = 0
        previous_total = 0
        evolution_percentage = 0
        current_year_total = 0
        previous_year_total = 0
        yearly_evolution = 0

        # Calcul des périodes selon le type de période sélectionné
        if period == 'month':
            # Période actuelle (mois en cours)
            current_start = today.replace(day=1)
            current_end = (current_start + relativedelta(months=1)) - timedelta(days=1)

            # Période précédente (mois précédent)
            previous_start = (current_start - relativedelta(months=1)).replace(day=1)
            previous_end = current_start - timedelta(days=1)

        elif period == 'trimestre':
            # Calcul pour le trimestre en cours et le précédent
            quarter = (today.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            current_start = datetime(today.year, start_month, 1)
            current_end = (current_start + relativedelta(months=3)) - timedelta(days=1)

            previous_start = (current_start - relativedelta(months=3))
            previous_end = current_start - timedelta(days=1)

        else:  # year
            # Période actuelle (année civile)
            current_start = datetime(today.year, 1, 1)
            current_end = datetime(today.year, 12, 31)

            # Période précédente (année civile)
            previous_start = datetime(today.year - 1, 1, 1)
            previous_end = datetime(today.year - 1, 12, 31)

        # Calculs des recettes pour les périodes avec filtre par année
        current_total = Paiement.objects.filter(
            date_paiement__range=[current_start, current_end],
            annee_scolaire_id=annee_id
        ).aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0

        previous_total = Paiement.objects.filter(
            date_paiement__range=[previous_start, previous_end],
            annee_scolaire_id=annee_id
        ).aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0

        # Calcul de l'évolution en pourcentage
        if previous_total > 0:
            evolution_percentage = ((current_total - previous_total) / previous_total) * 100

        # Calcul pour l'année scolaire actuelle
        current_year_total = Paiement.objects.filter(
            date_paiement__gte=annee.debut,
            date_paiement__lte=annee.fin,
            annee_scolaire_id=annee_id
        ).aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0

        # Calcul de l'année scolaire précédente
        try:
            previous_school_year_obj = AnneeScolaire.obtenir_annee_precedente()
            previous_year_total = Paiement.objects.filter(
                date_paiement__gte=previous_school_year_obj.debut,
                date_paiement__lte=previous_school_year_obj.fin,
                annee_scolaire_id=previous_school_year_obj.id
            ).aggregate(Sum('montant_paye'))['montant_paye__sum'] or 0

            if previous_year_total > 0:
                yearly_evolution = ((current_year_total - previous_year_total) / previous_year_total) * 100

        except Exception as e:
            # Gestion des erreurs pour l'année précédente
            print(f"Erreur année précédente: {str(e)}")
            previous_year_total = 0
            yearly_evolution = 0

        # Calcul du top 5 des classes par recettes avec filtre par année
        top_classes = Paiement.objects.filter(
            date_paiement__range=[current_start, current_end],
            annee_scolaire_id=annee_id
        ).values('eleve__classe__nom').annotate(
            total_recettes=Sum('montant_paye')
        ).order_by('-total_recettes')[:5]

        # Calcul du top 5 des sections par recettes avec filtre par année
        top_sections = Paiement.objects.filter(
            date_paiement__range=[current_start, current_end],
            annee_scolaire_id=annee_id
        ).values('eleve__classe__section__nom').annotate(
            total_recettes=Sum('montant_paye')
        ).order_by('-total_recettes')[:5]

        return JsonResponse({
            'success': True,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id,
            'current_total': float(current_total),
            'previous_total': float(previous_total),
            'evolution_percentage': float(evolution_percentage),
            'current_year_total': float(current_year_total),
            'previous_year_total': float(previous_year_total),
            'yearly_evolution': float(yearly_evolution),
            'top_classes': list(top_classes),  # Convert QuerySet to list for JSON serialization
            'top_sections': list(top_sections),  # Convert QuerySet to list for JSON serialization
        })

    except Exception as e:
        # Journalisation de l'erreur
        print(f"Erreur dans get_dashboard_stats: {str(e)}")

        return JsonResponse({
            'success': False,
            'error': str(e),
            'annee_scolaire': annee.annee if 'annee' in locals() else None,
            'annee_scolaire_id': annee.id if 'annee' in locals() else None,
            'current_total': 0,
            'previous_total': 0,
            'evolution_percentage': 0,
            'current_year_total': 0,
            'previous_year_total': 0,
            'yearly_evolution': 0,
            'top_classes': [],
            'top_sections': [],
        }, status=500)


@login_required
def get_solde(request, eleve_id):
    try:
        # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
        annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

        if not annee_id:
            # Utiliser l'année courante si aucune année n'est sélectionnée
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
            request.session['annee_scolaire_id'] = annee_id
        else:
            # Vérifier que l'année existe
            try:
                annee = AnneeScolaire.objects.get(id=annee_id)
            except AnneeScolaire.DoesNotExist:
                annee = AnneeScolaire.obtenir_annee_courante()
                annee_id = annee.id
                request.session['annee_scolaire_id'] = annee_id

        # Récupérer l'élève avec vérification d'existence
        eleve = Eleve.objects.get(id=eleve_id)

        # Vérifier que l'élève appartient à l'année scolaire sélectionnée
        if eleve.annee_scolaire_id != annee_id:
            return JsonResponse({
                'error': 'L\'élève n\'existe pas pour l\'année scolaire sélectionnée.'
            }, status=400)

        # Récupérer les paiements pour cette année scolaire
        paiements = Paiement.objects.filter(eleve=eleve, annee_scolaire_id=annee_id)
        total_paye = sum(p.montant_paye for p in paiements)

        # Récupérer les frais pour cette année scolaire
        frais = Frais.objects.filter(classes=eleve.classe, annee_scolaire_id=annee_id)
        total_frais = sum(f.montant for f in frais)

        solde = total_frais - total_paye

        return JsonResponse({
            "solde": float(solde),
            "annee_scolaire": annee.annee,
            "annee_scolaire_id": annee.id
        })

    except Eleve.DoesNotExist:
        return JsonResponse({"error": "Élève introuvable."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Erreur serveur : {str(e)}"}, status=500)



# Dans views.py
@login_required
def get_historique_paiements(request, eleve_id):
    try:
        # 1. Gestion de l'année scolaire (comme dans detail_eleve)
        try:
            annee_id = request.session.get('annee_scolaire_id')
            selected_annee = AnneeScolaire.objects.get(
                id=annee_id) if annee_id else AnneeScolaire.obtenir_annee_courante()
        except Exception as e:
            selected_annee = AnneeScolaire.obtenir_annee_courante()
            logger.error(f"Erreur sélection année scolaire: {str(e)}")

        # 2. Récupération de l'élève (sans filtre sur l'année scolaire)
        eleve = get_object_or_404(Eleve, id=eleve_id)

        # 3. Vérification des permissions (comme dans votre version originale)
        if not check_section_access(request.user, eleve.classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # 4. Récupération des paiements (comme dans detail_eleve mais avec plus de champs)
        paiements = Paiement.objects.filter(
            eleve=eleve,
            frais__annee_scolaire=selected_annee
        ).select_related('frais').order_by('-date_paiement')

        # 5. Préparation des données avec plus d'informations
        historique = paiements.values(
            'id',
            'mois',
            'tranche',
            'frais__nom',
            'frais__type_frais',  # Ajout du type de frais
            'montant_paye',
            'solde_restant',
            'date_paiement',
            'frais__montant',  # Ajout du montant total du frais

        )

        # 6. Calcul des totaux (comme dans detail_eleve)
        total_paye = paiements.aggregate(total=Sum('montant_paye'))['total'] or 0
        stats_paiements = paiements.values('frais__type_frais').annotate(
            total=Sum('montant_paye'),
            count=Count('id')
        )

        # 7. Conversion des Decimal en float et préparation de la réponse
        historique_list = list(historique)
        for item in historique_list:
            for field in ['montant_paye', 'solde_restant', 'frais__montant']:
                if isinstance(item.get(field), Decimal):
                    item[field] = float(item[field])

        # 8. Préparation des stats par type de frais
        paiements_stats = {
            'mensuel': {'count': 0, 'total': 0},
            'trimestriel': {'count': 0, 'total': 0},
            'annuel': {'count': 0, 'total': 0}
        }

        for stat in stats_paiements:
            type_frais = stat['frais__type_frais'].lower()
            if type_frais in paiements_stats:
                paiements_stats[type_frais]['count'] = stat['count']
                paiements_stats[type_frais]['total'] = float(stat['total'] or 0)

        return JsonResponse({
            'success': True,
            'historique': historique_list,
            'total_paye': float(total_paye),
            'stats_paiements': paiements_stats,
            'annee_scolaire': selected_annee.annee,
            'annee_scolaire_id': selected_annee.id,
            'eleve_nom': f"{eleve.nom} {eleve.prenom}",
            'eleve_classe': eleve.classe.nom,
            'has_inscription': eleve.annee_scolaire_id == selected_annee.id
        })

    except Eleve.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Élève introuvable.'}, status=404)
    except Exception as e:
        logger.error(f"Erreur dans get_historique_paiements: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)
# API pour récupérer le prochain mois à payer pour un élève et un frais
@login_required
def get_mois_suivant(request, eleve_id, frais_id):
    try:
        annee = get_annee_scolaire(request) or request.session.get('annee_scolaire_id')
        eleve = Eleve.objects.get(id=eleve_id)
        frais = Frais.objects.get(id=frais_id)

        # Vérifier l'année scolaire
        if eleve.annee_scolaire_id != annee.id or frais.annee_scolaire_id != annee.id:
            return JsonResponse({
                'error': 'L\'élève ou les frais ne correspondent pas à l\'année scolaire sélectionnée.'
            }, status=400)

        # Récupérer les paiements existants
        paiements = Paiement.objects.filter(
            eleve=eleve,
            frais=frais,
            annee_scolaire=annee
        )

        response_data = {
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        }
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
        # Récupérer l'année scolaire active
        annee = get_annee_scolaire(request)
        mois = request.GET.get('mois', None)

        # Récupérer les objets avec vérification d'existence
        eleve = Eleve.objects.get(pk=eleve_id)
        frais = Frais.objects.get(pk=frais_id)

        # Vérifier que l'élève et les frais appartiennent à l'année scolaire sélectionnée
        if eleve.annee_scolaire_id != annee.id or frais.annee_scolaire_id != annee.id:
            return JsonResponse({
                'success': False,
                'error': 'L\'élève ou les frais ne correspondent pas à l\'année scolaire sélectionnée.'
            }, status=400)

        # Calculer le solde
        solde_info = Paiement.objects.calculer_solde(eleve, frais, mois)

        return JsonResponse({
            'success': True,
            'montant_frais': float(solde_info['montant_frais']),
            'solde_precedent': float(solde_info.get('solde_precedent', 0)),
            'montant_net': float(solde_info.get('montant_net', solde_info['montant_frais'])),
            'solde_restant': float(solde_info.get('solde_restant', solde_info['montant_frais'])),
            'type_frais': frais.type_frais,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Eleve.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Élève introuvable.'}, status=404)
    except Frais.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Frais introuvable.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)

@login_required
def get_frais(request, classe_id):
    """Retourne les frais disponibles pour une classe spécifique et l'année scolaire sélectionnée"""
    try:
        # Récupérer l'année scolaire active
        annee = get_annee_scolaire(request)

        # Récupérer la classe avec vérification d'accès
        classe = Classe.objects.get(id=classe_id)

        # Vérifier les permissions
        if not check_section_access(request.user, classe.section.nom):
            return JsonResponse({'error': 'Accès refusé'}, status=403)

        # Récupérer les frais pour cette classe et cette année scolaire
        frais = Frais.objects.filter(
            classes=classe,
            annee_scolaire=annee
        ).values("id", "nom", "montant", "type_frais")

        return JsonResponse({
            'frais': list(frais),
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Classe.DoesNotExist:
        return JsonResponse({"error": "Classe introuvable."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Erreur serveur : {str(e)}"}, status=500)

@login_required
def get_frais_details(request, frais_id):
    try:
        # Récupérer l'année scolaire active
        annee = get_annee_scolaire(request)

        # Récupérer les détails du frais avec vérification de l'année
        frais = Frais.objects.get(id=frais_id)

        # Vérifier que le frais appartient à l'année scolaire sélectionnée
        if frais.annee_scolaire != annee:
            return JsonResponse({
                'error': 'Les informations de ce frais ne correspondent pas à l\'année scolaire sélectionnée.'
            }, status=400)

        return JsonResponse({
            "type_frais": frais.type_frais,
            "montant": float(frais.montant),
            "nom": frais.nom,
            "annee_scolaire": annee.annee,
            "annee_scolaire_id": annee.id
        })

    except Frais.DoesNotExist:
        return JsonResponse({"error": "Frais introuvable."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Erreur serveur : {str(e)}"}, status=500)

def get_latest_notifications(self, limit=5):
    return self.notifications.select_related('historique_action').all().order_by('-date_creation')[:limit]

@login_required
def eleves_par_classe(request, classe_id):
    # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

    if not annee_id:
        # Utiliser l'année courante si aucune année n'est sélectionnée
        annee = AnneeScolaire.obtenir_annee_courante()
        annee_id = annee.id
        request.session['annee_scolaire_id'] = annee_id
    else:
        # Vérifier que l'année existe
        try:
            annee = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
            request.session['annee_scolaire_id'] = annee_id

    # Récupérer la classe avec vérification d'existence
    classe = get_object_or_404(Classe, id=classe_id)

    # Récupérer les élèves de cette classe et de cette année scolaire
    eleves = Eleve.objects.filter(classe=classe, annee_scolaire_id=annee_id)

    # Appliquer les permissions utilisateur si ce n'est pas un admin ou superuser
    if not (request.user.is_superuser or request.user.role == 'admin'):
        eleves = filter_by_user_role(eleves, request.user, 'classe__section__nom')

    return render(request, 'gestion/liste_eleves.html', {
        'eleves': eleves,
        'classe': classe,
        'annee_selectionnee': annee,
        'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
        'annee_courante': annee.est_courante
    })

@login_required
def eleves_par_section(request, section_id):
    # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

    if not annee_id:
        # Utiliser l'année courante si aucune année n'est sélectionnée
        annee = AnneeScolaire.obtenir_annee_courante()
        annee_id = annee.id
        request.session['annee_scolaire_id'] = annee_id
    else:
        # Vérifier que l'année existe
        try:
            annee = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
            request.session['annee_scolaire_id'] = annee_id

    # Récupérer la section avec vérification d'existence
    section = get_object_or_404(Section, id=section_id)

    # Récupérer les élèves de cette section et de cette année scolaire
    eleves = Eleve.objects.filter(section=section, annee_scolaire_id=annee_id)

    # Appliquer les permissions utilisateur si ce n'est pas un admin ou superuser
    if not (request.user.is_superuser or request.user.role == 'admin'):
        eleves = filter_by_user_role(eleves, request.user, 'section__nom')

    return render(request, 'gestion/liste_eleves.html', {
        'eleves': eleves,
        'section': section,
        'annee_selectionnee': annee,
        'annees_disponibles': AnneeScolaire.objects.all().order_by('-annee'),
        'annee_courante': annee.est_courante
    })

@login_required
def calcul_solde(request):
    # Récupérer l'année scolaire active (priorité : paramètre URL > session > année courante)
    annee_id = request.GET.get('annee_scolaire') or request.session.get('annee_scolaire_id')

    if not annee_id:
        # Utiliser l'année courante si aucune année n'est sélectionnée
        annee = AnneeScolaire.obtenir_annee_courante()
        annee_id = annee.id
        request.session['annee_scolaire_id'] = annee_id
    else:
        # Vérifier que l'année existe
        try:
            annee = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            annee = AnneeScolaire.obtenir_annee_courante()
            annee_id = annee.id
            request.session['annee_scolaire_id'] = annee_id

    eleve_id = request.GET.get('eleve_id')
    frais_id = request.GET.get('frais_id')
    mois = request.GET.get('mois')

    try:
        # Récupérer les objets Eleve et Frais avec vérification de l'année scolaire
        eleve = Eleve.objects.get(pk=eleve_id)
        frais = Frais.objects.get(pk=frais_id)

        # Vérifier que l'élève et les frais appartiennent à l'année scolaire sélectionnée
        if eleve.annee_scolaire_id != annee_id or frais.annee_scolaire_id != annee_id:
            return JsonResponse({
                'success': False,
                'error': 'L\'élève ou les frais ne correspondent pas à l\'année scolaire sélectionnée.'
            }, status=400)

        # Calculer le solde en passant l'année scolaire
        solde_info = Paiement.objects.calculer_solde(eleve, frais, mois, annee_id)

        return JsonResponse({
            'success': True,
            'montant_frais': str(solde_info['montant_frais']),
            'solde_precedent': str(solde_info['solde_precedent']),
            'montant_net': str(solde_info['montant_net']),
            'solde_restant': str(solde_info['solde_restant']),
            'type_frais': frais.type_frais,
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Eleve.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Élève introuvable.'
        }, status=404)
    except Frais.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Frais introuvables.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur : {str(e)}'
        }, status=500)


