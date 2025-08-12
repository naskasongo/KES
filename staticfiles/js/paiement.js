//script pour la fiche de paiement
console.log("Fichier paiement.js chargé et exécuté");

document.addEventListener("DOMContentLoaded", function() {
    // Initialisation des éléments du DOM
    const elements = {
        section: document.getElementById("id_section"),
        option: document.getElementById("id_option"),
        classe: document.getElementById("id_classe"),
        eleve: document.getElementById("id_eleve"),
        frais: document.getElementById("id_frais"),
        mois: document.getElementById("id_mois"),
        tranche: document.getElementById("id_tranche"),
        matricule: document.getElementById("id_matricule"),
        btnRecherche: document.getElementById("btn-recherche-matricule"),
        montantAPayer: document.getElementById("id_montant_a_payer"),
        montantPaye: document.getElementById("id_montant_paye"),
        soldeRestant: document.getElementById("id_solde_restant"),
        typeFrais: document.getElementById("id_type_frais"),
        soldeInfo: document.getElementById("solde-precedent-info"),
        paymentProgress: document.getElementById("payment-progress"),
        progressBar: document.querySelector("#payment-progress .progress-bar"),
        messageContainer: document.getElementById("matricule-message"),
        grillePaiement: document.getElementById("grille-paiement")
    };

    // Désactiver les champs mois/tranche par défaut
    elements.mois.disabled = true;
    elements.tranche.disabled = true;

    // Initialiser les tooltips Bootstrap
    $(function () {
        $('[data-bs-toggle="tooltip"]').tooltip();
    });

    // 1. Fonction utilitaire pour les appels API
    async function fetchData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Erreur fetch:', error);
            showMessage('danger', 'Erreur de connexion au serveur');
            throw error;
        }
    }

    // 2. Fonction pour afficher les messages
    function showMessage(type, message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type} mt-2`;
        messageDiv.textContent = message;
        messageDiv.setAttribute('role', 'alert');
        messageDiv.setAttribute('aria-live', 'assertive');

        elements.messageContainer.innerHTML = '';
        elements.messageContainer.appendChild(messageDiv);

        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    // 3. Barre de progression du paiement
    function updatePaymentProgress() {
        const montantNet = parseFloat(elements.montantAPayer.value.replace(' FC', '')) || 0;
        const montantPaye = parseFloat(elements.montantPaye.value) || 0;

        if (montantNet > 0) {
            const progress = Math.min(100, (montantPaye / montantNet) * 100);

            if (elements.paymentProgress) {
                elements.paymentProgress.style.display = 'block';
                elements.progressBar.style.width = `${progress}%`;

                if (progress >= 100) {
                    elements.progressBar.classList.remove('bg-warning');
                    elements.progressBar.classList.add('bg-success');
                } else {
                    elements.progressBar.classList.remove('bg-success');
                    elements.progressBar.classList.add('bg-warning');
                }
            }
        } else if (elements.paymentProgress) {
            elements.paymentProgress.style.display = 'none';
        }
    }

    // 4. Badge visuel pour le type de frais
    function updateFraisBadge(typeFrais) {
        const badge = document.getElementById('type-frais-badge');
        if (!badge) return;

        badge.textContent = typeFrais;
        badge.className = 'badge ';

        switch(typeFrais) {
            case 'Mensuel':
                badge.classList.add('bg-primary');
                break;
            case 'Trimestriel':
                badge.classList.add('bg-warning', 'text-dark');
                break;
            case 'Annuel':
                badge.classList.add('bg-success');
                break;
            default:
                badge.classList.add('bg-secondary');
        }
    }

    // 5. Fonction pour charger les options
    async function updateOptions() {
        const sectionId = elements.section.value;
        const isHumanitesOrITM = ["4", "5"].includes(sectionId);

        elements.option.disabled = !isHumanitesOrITM;
        elements.option.innerHTML = '<option value="">-- Sélectionner --</option>';

        if (isHumanitesOrITM) {
            try {
                const data = await fetchData(`/api/get-options/${sectionId}/`);
                data.options.forEach(option => {
                    elements.option.add(new Option(option.nom, option.id));
                });
            } catch (error) {
                console.error('Erreur options:', error);
            }
        }
    }

    // 6. Fonction pour charger les classes
    async function updateClasses() {
        const sectionId = elements.section.value;
        const optionId = elements.option.value;

        if (!sectionId) return;

        const url = optionId
            ? `/api/get-classes/${sectionId}/${optionId}/`
            : `/api/get-classes/${sectionId}/`;

        try {
            const data = await fetchData(url);
            elements.classe.innerHTML = '<option value="">-- Sélectionner --</option>';
            data.classes.forEach(classe => {
                elements.classe.add(new Option(classe.nom, classe.id));
            });
        } catch (error) {
            console.error('Erreur classes:', error);
        }
    }

    // 7. Fonction pour charger les élèves
    async function updateEleves() {
        const classeId = elements.classe.value;

        if (!classeId) return;

        try {
            const data = await fetchData(`/api/get-eleves/${classeId}/`);
            elements.eleve.innerHTML = '<option value="">-- Sélectionner --</option>';
            data.eleves.forEach(eleve => {
                elements.eleve.add(new Option(
                    `${eleve.nom} ${eleve.post_nom} (${eleve.matricule})`,
                    eleve.id
                ));
            });
        } catch (error) {
            console.error('Erreur élèves:', error);
        }
    }

    // 8. Fonction pour charger les frais
    async function updateFrais() {
        const classeId = elements.classe.value;
        if (!classeId) return;

        try {
            const data = await fetchData(`/api/get-frais/${classeId}/`);
            elements.frais.innerHTML = '<option value="">-- Sélectionner --</option>';

            // Gestion des deux formats de réponse possibles
            const fraisList = data.frais || data;

            fraisList.forEach(frais => {
                elements.frais.add(new Option(
                    `${frais.nom} - ${frais.montant} FC`,
                    frais.id
                ));
            });

            // Gestion du changement de frais
            elements.frais.onchange = async function() {
                if (this.value) {
                    await updateFraisDetails(this.value);
                }
            };
        } catch (error) {
            console.error('Erreur frais:', error);
        }
    }

    // 9. Fonction pour charger les détails d'un frais
    async function updateFraisDetails(fraisId) {
        try {
            const data = await fetchData(`/api/get-frais-details/${fraisId}/`);
            const typeFrais = data.type_frais;

            elements.typeFrais.value = typeFrais;
            updateFraisBadge(typeFrais);

            // Gestion des champs mois/tranche
            elements.mois.disabled = typeFrais !== "Mensuel";
            elements.tranche.disabled = typeFrais !== "Trimestriel";

            if (typeFrais === "Mensuel") {
                elements.tranche.value = "";
            } else if (typeFrais === "Trimestriel") {
                elements.mois.value = "";
            } else {
                elements.mois.value = "";
                elements.tranche.value = "";
            }

            elements.montantAPayer.value = data.montant + " FC";
            updatePaymentProgress();

            if (elements.eleve.value) {
                await updateMoisTranche();
            }
        } catch (error) {
            console.error('Erreur détails frais:', error);
        }
    }

     // 10. Fonction pour charger l'historique - Version corrigée
    async function updateHistorique() {
        const eleveId = elements.eleve.value;
        if (!eleveId) {
            elements.grillePaiement.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4 text-muted">
                        Veuillez sélectionner un élève
                    </td>
                </tr>`;
            return;
        }

        try {
            const response = await fetch(`/api/get-historique/${eleveId}/`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Erreur lors du chargement de l\'historique');
            }

            // Vérifier si la réponse contient une erreur
            if (data.error) {
                elements.grillePaiement.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center py-4 text-danger">
                            ${data.error}
                        </td>
                    </tr>`;
                return;
            }

            // Vérifier si l'historique est vide
            if (!data.historique || data.historique.length === 0) {
                elements.grillePaiement.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center py-4 text-muted">
                            Aucun paiement enregistré pour cet élève
                        </td>
                    </tr>`;
                return;
            }

            // Afficher les paiements
            elements.grillePaiement.innerHTML = data.historique.map(paiement => `
                <tr>
                    <td>${paiement.id}</td>
                    <td>${paiement.mois || paiement.tranche || 'N/A'}</td>
                    <td>${paiement.frais__nom}</td>
                    <td>${paiement.montant_paye.toFixed(2)} FC</td>
                    <td>${paiement.solde_restant.toFixed(2)} FC</td>
                    <td>${paiement.date_paiement}</td>
                    <td class="text-end">
                        <div class="d-flex gap-2 justify-content-end">
                            <button onclick="showEditModal(${paiement.id})" class="btn btn-sm btn-warning">
                                <i class="bi bi-pencil"></i> Modifier
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');

        } catch (error) {
            console.error('Erreur historique:', error);
            elements.grillePaiement.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center py-4 text-danger">
                        ${error.message}
                    </td>
                </tr>`;
        }
    }
     // 11. Fonction pour charger le mois/tranche suivant
    async function updateMoisTranche() {
    const fraisId = elements.frais.value;
        const eleveId = elements.eleve.value;

        if (!fraisId || !eleveId) {
            resetMoisTrancheFields();
            return;
        }

        try {
            resetMoisTrancheFields();

            const [moisData, fraisData] = await Promise.all([
                fetchData(`/api/get-mois-suivant/${eleveId}/${fraisId}/`),
                fetchData(`/api/get-frais-details/${fraisId}/`)
            ]);

            if (moisData.error) {
                throw new Error(moisData.error);
            }

            const typeFrais = fraisData.type_frais;

            if (typeFrais === "Mensuel") {
                if (moisData.message) {
                    showMessage('warning', moisData.message);
                } else if (moisData.mois_suivant) {
                    elements.mois.value = moisData.mois_suivant;
                }
            }
            else if (typeFrais === "Trimestriel") {
                if (moisData.message) {
                    showMessage('warning', moisData.message);
                } else if (moisData.tranche_suivante) {
                    elements.tranche.value = moisData.tranche_suivante;
                }
            }
            else if (typeFrais === "Annuel" && moisData.message) {
                showMessage('info', moisData.message);
            }

            await updateMontantAPayer();

        } catch (error) {
            console.error('Erreur mois/tranche:', error);
            showMessage('danger', error.message || 'Erreur lors de la récupération du mois/tranche');
            resetMoisTrancheFields();
        }
    }
        // Fonctions utilitaires
        function resetMoisTrancheFields() {
            elements.mois.value = '';
            elements.tranche.value = '';
        }

        function handleMensuel(data) {
            if (data.mois_suivant) {
                // Crée une nouvelle option si elle n'existe pas déjà
                if (![...elements.mois.options].some(opt => opt.value === data.mois_suivant)) {
                    const option = new Option(data.mois_suivant, data.mois_suivant);
                    elements.mois.add(option);
                }
                elements.mois.value = data.mois_suivant;
            } else if (data.message) {
                showMessage('info', data.message);
            }
        }

        function handleTrimestriel(data) {
            if (data.tranche_suivante) {
                elements.tranche.value = data.tranche_suivante;
            } else if (data.message) {
                showMessage('info', data.message);
            }
        }

        function handleAnnuel(data) {
            if (data.message) {
                showMessage('info', data.message);
            }
        }

        // Fonction fetchData améliorée avec gestion d'erreur
        async function fetchData(url) {
            const response = await fetch(url);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Erreur HTTP: ${response.status}`);
            }
            return await response.json();
        }

    // 12. Fonction pour mettre à jour le montant à payer
       async function updateMontantAPayer() {
        const eleveId = elements.eleve.value;
        const fraisId = elements.frais.value;
        const mois = elements.mois.value;

        if (!eleveId || !fraisId) return;

        try {
            const url = `/api/get-solde-restant/${eleveId}/${fraisId}/?mois=${encodeURIComponent(mois || '')}`;
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error('Erreur lors de la récupération du solde');
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Erreur inconnue');
            }

            const montantNet = data.montant_net;
            const soldePrecedent = data.solde_precedent || 0;

            elements.montantAPayer.value = montantNet.toFixed(2) + ' FC';

            if (soldePrecedent > 0 && elements.soldeInfo) {
                elements.soldeInfo.textContent = `Solde précédent: ${soldePrecedent.toFixed(2)} FC`;
                elements.soldeInfo.classList.remove("d-none");
            } else if (elements.soldeInfo) {
                elements.soldeInfo.classList.add("d-none");
            }

            updateSoldeRestant();
        } catch (error) {
            console.error('Erreur solde:', error);
            showMessage('danger', error.message || 'Erreur lors du calcul du solde');
            elements.montantAPayer.value = '0.00 FC';
            if (elements.soldeInfo) elements.soldeInfo.classList.add("d-none");
        }
    }

    // 13. Fonction pour mettre à jour le solde restant
    function updateSoldeRestant() {
        const montantNet = parseFloat(elements.montantAPayer.value.replace(' FC', '')) || 0;
        const montantPaye = parseFloat(elements.montantPaye.value) || 0;
        const soldeRestant = montantNet - montantPaye;

        elements.soldeRestant.value = soldeRestant.toFixed(2) + ' FC';
        updatePaymentProgress();
    }

    // 14. Recherche par matricule
async function searchByMatricule() {
    const matricule = elements.matricule.value.trim();
    if (!matricule) {
        showMessage('danger', 'Veuillez entrer un matricule');
        return;
    }

    try {
        const response = await fetch(`/api/get-eleve-by-matricule/${matricule}/`);
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Élève introuvable');
        }

        // Mise à jour en cascade
        elements.section.value = data.section_id;
        await updateOptions();

        if (data.option_id) {
            elements.option.value = data.option_id;
            await updateClasses();
        } else {
            elements.option.value = '';
            await updateClasses();
        }

        elements.classe.value = data.classe_id;
        await updateEleves();

        // Sélectionner l'élève trouvé
        elements.eleve.value = data.id;

        // Mettre à jour les frais et l'historique
        await updateFrais();
        await updateHistorique();

        // Si un frais est déjà sélectionné, mettre à jour le mois/tranche
        if (elements.frais.value) {
            await updateMoisTranche();
        }

        showMessage('success', `Élève trouvé : ${data.nom} ${data.post_nom} (${data.matricule})`);

    } catch (error) {
        console.error('Erreur recherche:', error);
        showMessage('danger', error.message);
        resetForm();
    }
}
    // 15. Fonction pour réinitialiser le formulaire
    function resetForm() {
        elements.section.value = '';
        elements.option.value = '';
        elements.classe.value = '';
        elements.eleve.innerHTML = '<option value="">-- Sélectionner --</option>';
        elements.frais.innerHTML = '<option value="">-- Sélectionner --</option>';
        elements.mois.innerHTML = '<option value="">-- Sélectionner --</option>';
        elements.tranche.value = '';
        elements.montantAPayer.value = '';
        elements.montantPaye.value = '';
        elements.soldeRestant.value = '';
        elements.typeFrais.value = '';
        if (elements.soldeInfo) elements.soldeInfo.classList.add("d-none");
        if (elements.paymentProgress) elements.paymentProgress.style.display = 'none';
    }

    // 16. Configuration des écouteurs d'événements
    function setupEventListeners() {
        elements.section.addEventListener("change", async () => {
            await updateOptions();
            await updateClasses();
        });

        elements.option.addEventListener("change", updateClasses);

        elements.classe.addEventListener("change", async () => {
            await updateEleves();
            await updateFrais();
        });

        elements.eleve.addEventListener("change", async () => {
            await updateHistorique();
            if (elements.frais.value) await updateMoisTranche();
        });

        elements.montantPaye?.addEventListener("input", function() {
            const montantAPayer = parseFloat(elements.montantAPayer.value.replace(' FC', '')) || 0;
            const valeurSaisie = parseFloat(this.value) || 0;

            if (valeurSaisie > montantAPayer) {
                this.value = montantAPayer.toFixed(2);
                showMessage('warning', 'Le montant payé ne peut pas dépasser le montant à payer');
            }

            updateSoldeRestant();
        });

        elements.btnRecherche.addEventListener("click", searchByMatricule);
    }

    // Initialisation
    setupEventListeners();

    // Initialisation des champs si déjà remplis
    if (elements.section.value) updateOptions();
    if (elements.classe.value) {
        updateEleves();
        updateFrais();
    }
});

// Fonctions globales pour la modification des paiements
async function showEditModal(paiementId) {
    try {
        const response = await fetch(`/paiements/modifier/${paiementId}/`);
        if (!response.ok) throw new Error('Erreur lors du chargement');

        const html = await response.text();

        Swal.fire({
            title: 'Modifier le Paiement',
            html: html,
            width: '80%',
            showConfirmButton: false,
            showCloseButton: true,
            willOpen: () => {
                const form = document.getElementById('modifier-paiement-form');
                if (form) {
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();
                        submitEditForm(paiementId);
                    });
                }
            }
        });
    } catch (error) {
        Swal.fire('Erreur!', error.message, 'error');
    }
}

async function submitEditForm(paiementId) {
    const form = document.getElementById('modifier-paiement-form');
    if (!form) return;

    const formData = new FormData(form);

    try {
        const response = await fetch(`/paiements/modifier/${paiementId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        });

        if (!response.ok) throw new Error('Erreur lors de la modification');

        const data = await response.json();

        if (data.success) {
            Swal.fire({
                title: 'Succès!',
                text: 'Paiement modifié avec succès',
                icon: 'success'
            }).then(() => {
                Swal.close();
                // Rafraîchir l'historique
                const updateHistorique = document.querySelector('#grille-paiement') ?
                    () => document.querySelector('#grille-paiement').dispatchEvent(new Event('change')) :
                    () => {};
                updateHistorique();
            });
        } else {
            throw new Error(data.error || 'Erreur inconnue');
        }
    } catch (error) {
        Swal.fire('Erreur!', error.message, 'error');
    }
}
