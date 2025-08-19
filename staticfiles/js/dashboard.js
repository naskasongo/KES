
    // Graphique Évolution des paiements mensuels
    var ctx1 = document.getElementById("paiementsMensuelsChart").getContext("2d");
    var gradientStroke1 = ctx1.createLinearGradient(0, 230, 0, 50);
    gradientStroke1.addColorStop(1, 'rgba(94, 114, 228, 0.2)');
    gradientStroke1.addColorStop(0.2, 'rgba(94, 114, 228, 0.0)');
    gradientStroke1.addColorStop(0, 'rgba(94, 114, 228, 0)');
    new Chart(ctx1, {
        type: "line",
        data: {
            labels: [{% for paiement in paiements_mensuels %}'{{ paiement.mois_calcule|date:"F Y" }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                label: "Montant Payé",
                tension: 0.4,
                borderWidth: 0,
                pointRadius: 0,
                borderColor: "#5e72e4",
                backgroundColor: gradientStroke1,
                borderWidth: 3,
                fill: true,
                data: [{% for paiement in paiements_mensuels %}{{ paiement.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                maxBarThickness: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false,
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false,
                        display: true,
                        drawOnChartArea: true,
                        drawTicks: false,
                        borderDash: [5, 5]
                    },
                    ticks: {
                        callback: function(value) {
                            return value + ' FC';
                        }
                    }
                },
                x: {
                    grid: {
                        drawBorder: false,
                        display: false,
                        drawOnChartArea: false,
                        drawTicks: false,
                        borderDash: [5, 5]
                    }
                },
            },
        }
    });

    // Graphique Répartition des élèves par section
    var ctx2 = document.getElementById("elevesParSectionChart").getContext("2d");
    new Chart(ctx2, {
        type: "doughnut",
        data: {
            labels: [{% for section in eleves_par_section %}'{{ section.classe__section__nom }}'{% if not forloop.last %}, {% endif %}{% endfor %}],
            datasets: [{
                data: [{% for section in eleves_par_section %}{{ section.total }}{% if not forloop.last %}, {% endif %}{% endfor %}],
                backgroundColor: ['#5e72e4', '#2dce89', '#f5365c', '#fb6340'],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });

    // Animation des cartes
    document.addEventListener("DOMContentLoaded", function () {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 10px 20px rgba(0,0,0,0.1)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
                card.style.boxShadow = '';
            });
        });
    });


    // Récupérer les données depuis Django
    const topFraisData = {{ top_frais|safe }};

    // Vérifier si des données existent
    if (topFraisData && topFraisData.length > 0) {
        console.log("Données reçues :", topFraisData);

        // Extraire les labels et les valeurs
        const labels = topFraisData.map(item => item.nom);
        const dataValues = topFraisData.map(item => parseFloat(item.total));
        const evolution = topFraisData.map(item => parseFloat(item.evolution));

        // Initialiser le graphique
        const ctx = document.getElementById('topFraisChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Montant Total (FC)',
                    data: dataValues,
                    backgroundColor: [
                        'rgba(94, 114, 228, 0.7)', // Bleu
                        'rgba(45, 206, 137, 0.7)', // Vert
                        'rgba(245, 54, 92, 0.7)',  // Rouge
                        'rgba(17, 205, 239, 0.7)', // Cyan
                        'rgba(253, 126, 20, 0.7)'  // Orange
                    ],
                    borderColor: [
                        'rgba(94, 114, 228, 1)',
                        'rgba(45, 206, 137, 1)',
                        'rgba(245, 54, 92, 1)',
                        'rgba(17, 205, 239, 1)',
                        'rgba(253, 126, 20, 1)'
                    ],
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed.y || 0;
                                const evol = evolution[context.dataIndex];
                                return `${label}: ${value} FC (${evol}% d'évolution)`;
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 12
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value + ' FC';
                            },
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    } else {
        console.error("Aucune donnée disponible pour l'histogramme.");
    }



document.addEventListener("DOMContentLoaded", function () {
    const sectionSelect = document.getElementById("id_section");
    const optionSelect = document.getElementById("id_option");
    const classeSelect = document.getElementById("id_classe");
    const fraisSelect = document.getElementById("id_frais");

    // Fonction pour charger les options selon la section
    function updateOptions() {
        const sectionId = sectionSelect.value;
        if (!sectionId) return;

        fetch(`/api/get-options/${sectionId}/`)
            .then(res => res.json())
            .then(data => {
                // Vider les champs précédents
                optionSelect.innerHTML = '<option value="">-- Choisir --</option>';
                classeSelect.innerHTML = '<option value="">-- Choisir --</option>';

                // Activer/désactiver l'option selon la section
                if (["Humanités", "ITM"].includes(sectionSelect.options[sectionSelect.selectedIndex]?.text)) {
                    data.options.forEach(opt => {
                        const option = new Option(opt.nom, opt.id);
                        optionSelect.add(option);
                    });
                    optionSelect.disabled = false;
                } else {
                    optionSelect.disabled = true;
                }

                // Charger les classes en fonction de la section
                updateClasses();
            })
            .catch(err => console.error("Erreur lors du chargement des options:", err));
    }

    // Fonction pour charger les classes selon la section et l'option
    function updateClasses() {
        const sectionId = sectionSelect.value;
        const optionId = optionSelect.value || null;

        let url = `/api/get-classes/${sectionId}/`;
        if (optionId && ["Humanités", "ITM"].includes(sectionSelect.options[sectionSelect.selectedIndex]?.text)) {
            url += `${optionId}/`;
        }

        fetch(url)
            .then(res => res.json())
            .then(data => {
                classeSelect.innerHTML = '<option value="">-- Choisir --</option>';
                data.classes.forEach(classe => {
                    const option = new Option(classe.nom, classe.id);
                    classeSelect.add(option);
                });
            })
            .catch(err => console.error("Erreur lors du chargement des classes:", err));
    }
    // Fonction pour charger les frais selon la classe (utilisation de l'API existante)
    function updateFrais(classeId) {
        fetch(`/api/get-frais/${classeId}/`)
            .then(res => res.json())
            .then(data => {
                fraisSelect.innerHTML = '<option value="">-- Choisir --</option>';

                // Vérifier si la réponse contient un message (ex: pas de frais)
                if (Array.isArray(data)) {
                    data.forEach(frais => {
                        const option = new Option(`${frais.nom} (${frais.type_frais})`, frais.id);
                        fraisSelect.add(option);
                    });
                } else if (data.message) {
                    const option = new Option(data.message, "");
                    option.disabled = true;
                    fraisSelect.add(option);
                }
            })
            .catch(err => console.error("Erreur lors du chargement des frais:", err));
    }


    // Gestion des événements
    sectionSelect.addEventListener("change", function () {
        updateOptions();
    });

    optionSelect.addEventListener("change", function () {
        updateClasses();
    });

    // Chargement initial si une section est déjà sélectionnée
    if (sectionSelect.value) {
        updateOptions();
    }

    classeSelect.addEventListener("change", function () {
        if (classeSelect.value) {
            updateFrais(classeSelect.value);
        }
    });

    // Chargement initial si une section est déjà sélectionnée
    if (sectionSelect.value) {
        updateOptions();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const periodButtons = document.querySelectorAll(".period-option");
    const evolutionSpan = document.getElementById("evolution_recettes");
    const totalRecettesSpan = document.getElementById("total_recettes");

    function updateDashboardStats(period) {
        fetch(`/api/dashboard-stats/?period=${period}`)
            .then(res => res.json())
            .then(data => {
                // Mise à jour du texte des stats
                totalRecettesSpan.textContent = `${data.total_recettes.toFixed(2)} FC`;
                evolutionSpan.innerHTML = `
                    ${data.evolution >= 0 ? '+' : ''}${data.evolution.toFixed(2)}%
                    depuis la période précédente
                `;
                evolutionSpan.className = data.evolution >= 0 ? 'text-sm text-success mb-0' : 'text-sm text-danger mb-0';
            })
            .catch(err => console.error("Erreur lors du chargement des stats:", err));
    }

    // Gestion des clics sur les options de période
    periodButtons.forEach(button => {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            const period = this.getAttribute("data-period");
            updateDashboardStats(period);
        });
    });

    // Chargement initial avec "ce mois"
    updateDashboardStats("month");
});

<!-- top 5 classes -->

    // Variable pour stocker l'instance du graphique
    let topClassesChart = null;

    // Fonction pour formater les nombres
    function formatNumber(num) {
        return new Intl.NumberFormat('fr-FR').format(num);
    }

    // Fonction pour afficher les messages d'erreur
    function showError(message) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.innerHTML = `<strong>Erreur :</strong> ${message}`;
        errorDiv.style.display = 'block';
    }

    // Fonction pour charger les données
    async function loadTopClassesData() {
        const loadingDiv = document.getElementById('loading');
        const apiUrl = '/api/dashboard-stats/?top_class'; // Assurez-vous que cette URL est correcte

        try {
            // Afficher le chargement
            loadingDiv.style.display = 'block';
            document.getElementById('error-message').style.display = 'none';

            // Appel API
            const response = await fetch(apiUrl);

            // Vérifier la réponse
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            // Récupérer les données
            const data = await response.json();
            console.log('Données reçues:', data);

            // Cacher le chargement
            loadingDiv.style.display = 'none';

            // Vérifier la structure des données
            if (!data || !data.top_classes) {
                throw new Error('Structure de données invalide');
            }

            // Mettre à jour le graphique
            updateChart(data.top_classes);

        } catch (error) {
            console.error('Erreur lors du chargement:', error);
            loadingDiv.style.display = 'none';
            showError(`Impossible de charger les données. ${error.message}`);

            // Afficher un graphique vide avec message
            updateChart([]);
        }
    }

    // Fonction pour créer/mettre à jour le graphique
    function updateChart(topClassesData) {
        const ctx = document.getElementById('topClassesChart');
        if (!ctx) {
            console.error("Canvas non trouvé");
            return;
        }

        // Préparer les données
        const labels = topClassesData.map(item => item.eleve__classe__nom || 'Classe Inconnue');
        const dataValues = topClassesData.map(item => Number(item.total_recettes) || 0);

        // Si aucune donnée, afficher un message
        if (topClassesData.length === 0) {
            labels.push('Aucune donnée disponible');
            dataValues.push(1); // Valeur minimale pour afficher la barre
        }

        // Détruire l'ancien graphique s'il existe
        if (topClassesChart) {
            topClassesChart.destroy();
        }

        // Créer le nouveau graphique
        try {
            topClassesChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Recettes (FC)',
                        data: dataValues,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 206, 86, 0.7)'
                        ].slice(0, labels.length),
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(255, 159, 64, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 206, 86, 1)'
                        ].slice(0, labels.length),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Montant (FC)',
                                font: {
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Classes',
                                font: {
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${formatNumber(context.raw)} FC`;
                                }
                            }
                        },
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erreur création graphique:', error);
            showError('Erreur lors de la création du graphique');
        }
    }

    // Charger les données au démarrage
    document.addEventListener('DOMContentLoaded', loadTopClassesData);


<!-- dashboard.html - Mise à jour de l'affichage -->

document.addEventListener("DOMContentLoaded", function () {
    const currentPeriodValue = document.getElementById("current_period_value");
    const previousPeriodValue = document.getElementById("previous_period_value");
    const currentYearValue = document.getElementById("current_year_value");
    const previousYearValue = document.getElementById("previous_year_value");
    const evolutionRecettes = document.getElementById("evolution_recettes");
    const evolutionAnnee = document.getElementById("evolution_annee");

    function updateDashboardStats(period) {
        fetch(`/api/dashboard-stats/?period=${period}`)
            .then(res => res.json())
            .then(data => {
                console.log("Data received:", data); // Debugging line

                // Update period values
                currentPeriodValue.textContent = `${data.current_total.toFixed(2)} FC`;
                previousPeriodValue.textContent = `${data.previous_total.toFixed(2)} FC`;

                // Update year values
                currentYearValue.textContent = `${data.current_year_total.toFixed(2)} FC`;
                previousYearValue.textContent = `${data.previous_year_total.toFixed(2)} FC`;

                // Update evolution text
                const evolutionText = data.evolution_percentage >= 0
                    ? `+${data.evolution_percentage.toFixed(2)}% vs période précédente`
                    : `${data.evolution_percentage.toFixed(2)}% vs période précédente`;
                evolutionRecettes.textContent = evolutionText;
                evolutionRecettes.className = data.evolution_percentage >= 0
                    ? "text-sm text-success mb-0"
                    : "text-sm text-danger mb-0";

                // Update yearly evolution text
                const yearlyEvolutionText = data.yearly_evolution >= 0
                    ? `+${data.yearly_evolution.toFixed(2)}%`
                    : `${data.yearly_evolution.toFixed(2)}%`;
                evolutionAnnee.textContent = yearlyEvolutionText;
                evolutionAnnee.className = data.yearly_evolution >= 0
                    ? "text-sm text-success mb-0"
                    : "text-sm text-danger mb-0";
            })
            .catch(err => {
                console.error("Erreur lors du chargement des stats:", err);
                evolutionRecettes.textContent = "Erreur de chargement";
                evolutionRecettes.className = "text-sm text-warning mb-0";
            });
    }

    // Initial call to update stats for the current month
    updateDashboardStats("month");
});


    // Variable pour stocker l'instance du graphique
    let topSectionsChart = null;

    // Fonction pour charger les données des sections
    async function loadTopSectionsData() {
        const apiUrl = '/api/dashboard-stats/?top_section'; // Assurez-vous que cette URL est correcte

        try {
            // Appel API
            const response = await fetch(apiUrl);

            // Vérifier la réponse
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }

            // Récupérer les données
            const data = await response.json();
            console.log('Données reçues pour les sections:', data);

            // Vérifier la structure des données
            if (!data || !data.top_sections) {
                throw new Error('Structure de données invalide');
            }

            // Mettre à jour le graphique
            updateSectionsChart(data.top_sections);

        } catch (error) {
            console.error('Erreur lors du chargement des sections:', error);
            showError(`Impossible de charger les données des sections. ${error.message}`);

            // Afficher un graphique vide avec message
            updateSectionsChart([]);
        }
    }

    // Fonction pour créer/mettre à jour le graphique des sections
    function updateSectionsChart(topSectionsData) {
        const ctx = document.getElementById('topSectionsChart');
        if (!ctx) {
            console.error("Canvas non trouvé pour les sections");
            return;
        }

        // Préparer les données
        const labels = topSectionsData.map(item => item.eleve__classe__section__nom || 'Section Inconnue');
        const dataValues = topSectionsData.map(item => Number(item.total_recettes) || 0);

        // Si aucune donnée, afficher un message
        if (topSectionsData.length === 0) {
            labels.push('Aucune donnée disponible');
            dataValues.push(1); // Valeur minimale pour afficher la barre
        }

        // Détruire l'ancien graphique s'il existe
        if (topSectionsChart) {
            topSectionsChart.destroy();
        }

        // Créer le nouveau graphique
        try {
            topSectionsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Recettes (FC)',
                        data: dataValues,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 206, 86, 0.7)'
                        ].slice(0, labels.length),
                        borderColor: [
                            'rgb(35,214,59)',
                            'rgb(248,151,11)',
                            'rgb(255,203,75)',
                            'rgba(18,80,198,0.95)',
                            'rgba(255, 206, 86, 1)'
                        ].slice(0, labels.length),
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Montant (FC)',
                                font: {
                                    weight: 'bold'
                                }
                            },
                            ticks: {
                                callback: function(value) {
                                    return formatNumber(value);
                                }
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Sections',
                                font: {
                                    weight: 'bold'
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${formatNumber(context.raw)} FC`;
                                }
                            }
                        },
                        legend: {
                            display: false
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Erreur création graphique des sections:', error);
            showError('Erreur lors de la création du graphique des sections');
        }
    }

    // Charger les données des sections au démarrage
    document.addEventListener('DOMContentLoaded', loadTopSectionsData);

