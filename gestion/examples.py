# Dans apis.py

# Modifier get_frais pour bien filtrer par année scolaire
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



# Modifier get_frais_details pour vérifier l'année scolaire
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


# Modifier get_mois_suivant pour bien filtrer par année scolaire
@login_required
def get_mois_suivant(request, eleve_id, frais_id):
    try:
        # Récupérer l'année scolaire active
        annee = get_annee_scolaire(request)

        eleve = Eleve.objects.get(id=eleve_id)
        frais = Frais.objects.get(id=frais_id)

        # Vérifier que l'élève et les frais appartiennent à la même année scolaire
        if eleve.annee_scolaire != annee or frais.annee_scolaire != annee:
            return JsonResponse({
                'error': 'L\'élève ou les frais ne correspondent pas à l\'année scolaire sélectionnée.'
            }, status=400)

        # Récupérer les paiements existants pour cette année scolaire
        paiements = Paiement.objects.filter(
            eleve=eleve,
            frais=frais,
            annee_scolaire=annee
        ).values_list('mois', 'tranche')

        mois_payes = [p[0] for p in paiements if p[0]]
        tranches_payees = [p[1] for p in paiements if p[1]]

        if frais.type_frais == "Mensuel":
            mois_ordre = [m[0] for m in MoisPaiement.choices]

            for mois in mois_ordre:
                if mois not in mois_payes:
                    return JsonResponse({
                        'mois_suivant': mois,
                        'mois_payes': mois_payes,
                        'annee_scolaire': annee.annee
                    })

            return JsonResponse({
                'message': "Tous les mois ont été payés",
                'annee_scolaire': annee.annee
            })

        elif frais.type_frais == "Trimestriel":
            tranches_disponibles = ["1ère Tranche", "2ème Tranche", "3ème Tranche"]

            for tranche in tranches_disponibles:
                if tranche not in tranches_payees:
                    return JsonResponse({
                        'tranche_suivante': tranche,
                        'tranches_payees': tranches_payees,
                        'annee_scolaire': annee.annee
                    })

            return JsonResponse({
                'message': "Toutes les tranches ont été payées",
                'annee_scolaire': annee.annee
            })

        elif frais.type_frais == "Annuel":
            return JsonResponse({
                'message': "Ce frais est annuel.",
                'annee_scolaire': annee.annee
            })

    except Eleve.DoesNotExist:
        return JsonResponse({'error': 'Élève introuvable.'}, status=404)
    except Frais.DoesNotExist:
        return JsonResponse({'error': 'Frais introuvable.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur : {str(e)}'}, status=500)

    return JsonResponse({'error': 'Type de frais non reconnu.'}, status=400)


# Modifier get_solde_restant pour bien calculer avec l'année scolaire
@login_required
def get_solde_restant(request):
    try:
        # Récupérer l'année scolaire active
        annee = get_annee_scolaire(request)

        eleve_id = request.GET.get('eleve_id')
        frais_id = request.GET.get('frais_id')
        mois = request.GET.get('mois')

        if not eleve_id or not frais_id:
            return JsonResponse({'error': 'Paramètres manquants'}, status=400)

        # Récupérer les objets Eleve et Frais
        eleve = Eleve.objects.get(id=eleve_id)
        frais = Frais.objects.get(id=frais_id)

        # Vérifier que l'élève et les frais appartiennent à la même année scolaire
        if eleve.annee_scolaire != annee or frais.annee_scolaire != annee:
            return JsonResponse({
                'error': 'L\'élève ou les frais ne correspondent pas à l\'année scolaire sélectionnée.'
            }, status=400)

        # Calculer le solde restant en fonction de l'année scolaire
        solde_info = Paiement.objects.calculer_solde(eleve, frais, mois, annee.id)

        return JsonResponse({
            'success': True,
            'montant_frais': float(solde_info['montant_frais']),
            'solde_precedent': float(solde_info['solde_precedent']),
            'montant_net': float(solde_info['montant_net']),
            'solde_restant': float(solde_info['solde_restant']),
            'annee_scolaire': annee.annee,
            'annee_scolaire_id': annee.id
        })

    except Eleve.DoesNotExist:
        return JsonResponse({'error': 'Élève introuvable.'}, status=404)
    except Frais.DoesNotExist:
        return JsonResponse({'error': 'Frais introuvables.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': f'Erreur serveur : {str(e)}'}, status=500)