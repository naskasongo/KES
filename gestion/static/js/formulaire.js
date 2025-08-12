document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("ajouterEleveForm");

    // Gestion des sélecteurs Section/Option/Classe
    const sectionSelect = document.getElementById("section-select");
    const optionSelect = document.getElementById("option-select");
    const classeSelect = document.getElementById("classe-select");

    function updateOptions() {
        const selectedSection = sectionSelect.value;
        const isHumanitesOrITM = selectedSection == "4" || selectedSection == "5";

        // Gestion de l'option
        optionSelect.disabled = !isHumanitesOrITM;
        if (!isHumanitesOrITM) optionSelect.value = "";

        // Filtrer les options
        Array.from(optionSelect.options).forEach(option => {
            option.hidden = !(option.dataset.section === selectedSection || option.value === "");
        });

        // Filtrer les classes
        Array.from(classeSelect.options).forEach(classe => {
            const classeSection = classe.getAttribute("data-section");
            const classeOption = classe.getAttribute("data-option");
            classe.hidden = !(classeSection === selectedSection &&
                            (!classeOption || classeOption === optionSelect.value || optionSelect.value === ""));
        });

        // Sélection automatique de la première classe valide
        const firstVisibleClass = Array.from(classeSelect.options).find(option => !option.hidden);
        if (firstVisibleClass) classeSelect.value = firstVisibleClass.value;
    }

    sectionSelect.addEventListener("change", updateOptions);
    optionSelect.addEventListener("change", updateOptions);
    updateOptions();

    // Intercepter la soumission du formulaire
    form.addEventListener('submit', function (event) {
        if (form.checkValidity()) {
            event.preventDefault(); // Empêcher l'envoi immédiat

            // Récupération des valeurs
            const nom = document.getElementById("{{ form.nom.id_for_label }}").value.trim();
            const postNom = document.getElementById("{{ form.post_nom.id_for_label }}").value.trim();
            const prenom = document.getElementById("{{ form.prenom.id_for_label }}").value.trim();
            const matricule = document.getElementById("{{ form.matricule.id_for_label }}").value.trim();
            const classe = classeSelect.options[classeSelect.selectedIndex].text;
            const option = optionSelect.options[optionSelect.selectedIndex].text || 'Aucune';
            const parentNom = document.getElementById("{{ form.parent_nom.id_for_label }}").value.trim();

            // Affichage de SweetAlert
            Swal.fire({
                title: 'Confirmez les informations',
                html: `
                    <div style="text-align: left; font-size: 1.1rem;">
                        <p><strong>Nom complet :</strong> ${nom} ${postNom} ${prenom}</p>
                        <p><strong>Matricule :</strong> <span style="font-size: 1.3rem; font-weight: bold;">${matricule}</span></p>
                        <p><strong>Classe :</strong> ${classe}</p>
                        <p><strong>Option :</strong> ${option}</p>
                        <p><strong>Sexe :</strong> ${document.getElementById("{{ form.sexe.id_for_label }}").value}</p>
                        <p><strong>Date de naissance :</strong> ${document.getElementById("{{ form.date_naissance.id_for_label }}").value}</p>
                        <p><strong>Lieu de naissance :</strong> ${document.getElementById("{{ form.lieu_naissance.id_for_label }}").value}</p>
                        <p><strong>Adresse du parent :</strong> ${document.getElementById("{{ form.parent_adresse.id_for_label }}").value}</p>
                        <p><strong>Téléphone du parent :</strong> ${document.getElementById("{{ form.parent_telephone.id_for_label }}").value}</p>
                        <p><strong>Email du parent :</strong> ${document.getElementById("{{ form.parent_email.id_for_label }}").value}</p>
                        <p><strong>Profession du parent :</strong> ${document.getElementById("{{ form.parent_profession.id_for_label }}").value}</p>
                        <p><strong>Relation avec l'élève :</strong> ${document.getElementById("{{ form.parent_relation.id_for_label }}").value}</p>
                    </div>
                `,
                icon: 'info',
                showCancelButton: true,
                confirmButtonText: 'Confirmer',
                cancelButtonText: 'Modifier',
                customClass: {
                    popup: 'swal2-popup swal2-radius swal2-fontsize-md'
                },
                width: '600px',
                allowOutsideClick: false
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit(); // Envoi du formulaire si confirmé
                }
            });
        } else {
            event.stopPropagation();
        }
        form.classList.add('was-validated');
    });
});
