-- Insertion des parents (25 enregistrements)
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (1, 'hamuli', '0970338991', 'hamuli@gmail.com', 'f', 'cultivatrice', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (2, 'KABEYA', '0998222111', 'kabeya@gmail.com', 'Lubumbashi', 'Enseignant', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (3, 'MUKENDI', '0977123456', 'mukendi@yahoo.fr', 'Q. Kenya', 'Commerçant', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (4, 'KASONGO', '0900111222', 'kasongo@hotmail.com', 'Q. Golf', 'Infirmier', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (5, 'MWAMBA', '0999333444', 'mwamba@gmail.com', 'Q. Industriel', 'Chauffeur', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (6, 'LUBOYA', '0977555666', 'luboya@yahoo.fr', 'Q. Katuba', 'Agriculteur', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (7, 'KAPENGA', '0900444555', 'kapenga@gmail.com', 'Q. Kamalondo', 'Menuisier', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (8, 'MBUYI', '0998666777', 'mbuyi@hotmail.com', 'Q. Ruashi', 'Maçon', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (9, 'KABANGE', '0977888999', 'kabange@gmail.com', 'Q. Lubumbashi', 'Electricien', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (10, 'MUTOMBO', '0900222333', 'mutombo@yahoo.fr', 'Q. Annexé', 'Plombier', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (11, 'KALALA', '0999444555', 'kalala@gmail.com', 'Q. Gécamines', 'Mécanicien', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (12, 'LUNGU', '0977666777', 'lungu@hotmail.com', 'Q. Kasapa', 'Cuisinier', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (13, 'MWANZA', '0900888999', 'mwanza@gmail.com', 'Q. Karavia', 'Gardien', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (14, 'KABUYA', '0999111222', 'kabuya@yahoo.fr', 'Q. Kipushi', 'Peintre', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (15, 'MPIANA', '0977222333', 'mpiana@gmail.com', 'Q. Likasi', 'Soudeur', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (16, 'NTUMBA', '0900555666', 'ntumba@hotmail.com', 'Q. Kolwezi', 'Tailleur', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (17, 'KASONGO', '0999777888', 'kasongo2@gmail.com', 'Q. Lubumbashi', 'Informaticien', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (18, 'MUKENA', '0977999000', 'mukena@yahoo.fr', 'Q. Kenya', 'Comptable', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (19, 'KABWE', '0900111333', 'kabwe@gmail.com', 'Q. Golf', 'Ingénieur', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (20, 'MWEPU', '0999222444', 'mwepu@hotmail.com', 'Q. Kamalondo', 'Architecte', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (21, 'KALUMBA', '0977333555', 'kalumba@gmail.com', 'Q. Ruashi', 'Médecin', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (22, 'MUSONDA', '0900444666', 'musonda@yahoo.fr', 'Q. Katuba', 'Avocat', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (23, 'KAPATA', '0999555777', 'kapata@gmail.com', 'Q. Annexé', 'Journaliste', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (24, 'MWAMBA', '0977666888', 'mwamba2@hotmail.com', 'Q. Gécamines', 'Professeur', 'Père');
INSERT INTO gestion_parent (id, nom, telephone, email, adresse, profession, relation) VALUES (25, 'LUBASHI', '0900777999', 'lubashi@gmail.com', 'Q. Kasapa', 'Infirmière', 'Mère');

-- Insertion des années scolaires
INSERT INTO gestion_anneescolaire (id, annee) VALUES (1, '2023-2024');
INSERT INTO gestion_anneescolaire (id, annee) VALUES (2, '2024-2025');
INSERT INTO gestion_anneescolaire (id, annee) VALUES (3, '2025-2026');
INSERT INTO gestion_anneescolaire (id, annee) VALUES (4, '2026-2027');

-- Insertion des sections
INSERT INTO gestion_section (id, nom, type_section) VALUES (1, 'Maternelle', 'maternelle');
INSERT INTO gestion_section (id, nom, type_section) VALUES (2, 'Primaire', 'primaire');
INSERT INTO gestion_section (id, nom, type_section) VALUES (3, 'Secondaire', 'secondaire');
INSERT INTO gestion_section (id, nom, type_section) VALUES (4, 'ITM', 'itm');
INSERT INTO gestion_section (id, nom, type_section) VALUES (5, 'Humanités', 'humanite');

-- Insertion des options
INSERT INTO gestion_option (id, nom, section_id) VALUES (1, 'Générale', 3);
INSERT INTO gestion_option (id, nom, section_id) VALUES (2, 'Scientifique', 3);
INSERT INTO gestion_option (id, nom, section_id) VALUES (3, 'Littéraire', 3);
INSERT INTO gestion_option (id, nom, section_id) VALUES (4, 'Commerciale', 4);
INSERT INTO gestion_option (id, nom, section_id) VALUES (5, 'Technique', 4);

-- Insertion des classes
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (1, '1ère Année', NULL, 1);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (2, '2ème Année', NULL, 1);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (3, '3ème Année', NULL, 1);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (4, '1ère Primaire', NULL, 2);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (5, '2ème Primaire', NULL, 2);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (6, '3ème Primaire', NULL, 2);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (7, '4ème Primaire', NULL, 2);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (8, '5ème Primaire', NULL, 2);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (9, '6ème Primaire', NULL, 2);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (10, '1ère Secondaire', 1, 3);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (11, '2ème Secondaire', 1, 3);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (12, '3ème Secondaire', 1, 3);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (13, '4ème Secondaire', 2, 3);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (14, '5ème Secondaire', 2, 3);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (15, '6ème Secondaire', 2, 3);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (16, '1ère ITM', 4, 4);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (17, '2ème ITM', 4, 4);
INSERT INTO gestion_classe (id, nom, option_id, section_id) VALUES (18, '3ème ITM', 4, 4);

-- Insertion des élèves (47 enregistrements - premiers exemples)
INSERT INTO gestion_eleve (id, nom, post_nom, prenom, sexe, date_naissance, lieu_naissance, matricule, section_id, option_id, classe_id, annee_scolaire_id, parent_id) VALUES (1, 'KAKUMBI', 'BATWALA', 'John', 'M', '2015-03-15', 'Lubumbashi', '25KB003', 3, 1, 10, 2, 1);
INSERT INTO gestion_eleve (id, nom, post_nom, prenom, sexe, date_naissance, lieu_naissance, matricule, section_id, option_id, classe_id, annee_scolaire_id, parent_id) VALUES (2, 'MWAMBA', 'KABEYA', 'Sarah', 'F', '2016-07-22', 'Lubumbashi', '25MK001', 2, NULL, 5, 2, 2);
INSERT INTO gestion_eleve (id, nom, post_nom, prenom, sexe, date_naissance, lieu_naissance, matricule, section_id, option_id, classe_id, annee_scolaire_id, parent_id) VALUES (3, 'KASONGO', 'MUKENDI', 'David', 'M', '2014-11-30', 'Lubumbashi', '25KM002', 3, 1, 11, 2, 3);
INSERT INTO gestion_eleve (id, nom, post_nom, prenom, sexe, date_naissance, lieu_naissance, matricule, section_id, option_id, classe_id, annee_scolaire_id, parent_id) VALUES (4, 'LUBOYA', 'KAPENGA', 'Marie', 'F', '2017-01-14', 'Lubumbashi', '25LK004', 1, NULL, 2, 2, 4);
INSERT INTO gestion_eleve (id, nom, post_nom, prenom, sexe, date_naissance, lieu_naissance, matricule, section_id, option_id, classe_id, annee_scolaire_id, parent_id) VALUES (5, 'MBUYI', 'KABANGE', 'Patrick', 'M', '2013-09-08', 'Lubumbashi', '25MK005', 3, 2, 13, 2, 5);

-- Insertion des frais (17 enregistrements)
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (1, 'Frais de scolarité Maternelle', 50000, 'Trimestriel', 2, NULL, 1, '1ère Tranche', NULL);
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (2, 'Frais de scolarité Primaire', 75000, 'Trimestriel', 2, NULL, 2, '1ère Tranche', NULL);
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (3, 'Frais de scolarité Secondaire', 100000, 'Trimestriel', 2, NULL, 3, '1ère Tranche', NULL);
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (4, 'Frais de scolarité ITM', 120000, 'Trimestriel', 2, NULL, 4, '1ère Tranche', NULL);
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (5, 'Frais d inscription', 25000, 'Annuel', 2, NULL, NULL, NULL, NULL);
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (6, 'Frais de tenue', 35000, 'Annuel', 2, NULL, NULL, NULL, NULL);
INSERT INTO gestion_frais (id, nom, montant, type_frais, annee_scolaire_id, option_id, section_id, tranche, mois) VALUES (7, 'Frais de photocopies', 15000, 'Mensuel', 2, NULL, NULL, NULL, 'Septembre');

-- Insertion des paiements (111 enregistrements - premiers exemples)
INSERT INTO gestion_paiement (id, montant_paye, date_paiement, recu_numero, eleve_id, frais_id, mois, solde_restant, tranche, annee_scolaire_id) VALUES (1, 50000, '2024-09-15', 'REC-2024-0001', 1, 3, NULL, 0, '1ère Tranche', 2);
INSERT INTO gestion_paiement (id, montant_paye, date_paiement, recu_numero, eleve_id, frais_id, mois, solde_restant, tranche, annee_scolaire_id) VALUES (2, 25000, '2024-09-16', 'REC-2024-0002', 1, 5, NULL, 0, NULL, 2);
INSERT INTO gestion_paiement (id, montant_paye, date_paiement, recu_numero, eleve_id, frais_id, mois, solde_restant, tranche, annee_scolaire_id) VALUES (3, 35000, '2024-09-17', 'REC-2024-0003', 1, 6, NULL, 0, NULL, 2);
INSERT INTO gestion_paiement (id, montant_paye, date_paiement, recu_numero, eleve_id, frais_id, mois, solde_restant, tranche, annee_scolaire_id) VALUES (4, 15000, '2024-09-18', 'REC-2024-0004', 1, 7, 'Septembre', 0, NULL, 2);

-- Insertion des inscriptions (22 enregistrements)
INSERT INTO gestion_inscription (id, annee_scolaire, date_inscription, eleve_id, classe_id, est_reinscription) VALUES (1, '2024-2025', '2024-09-01', 1, 10, 0);
INSERT INTO gestion_inscription (id, annee_scolaire, date_inscription, eleve_id, classe_id, est_reinscription) VALUES (2, '2024-2025', '2024-09-01', 2, 5, 0);
INSERT INTO gestion_inscription (id, annee_scolaire, date_inscription, eleve_id, classe_id, est_reinscription) VALUES (3, '2024-2025', '2024-09-01', 3, 11, 0);
INSERT INTO gestion_inscription (id, annee_scolaire, date_inscription, eleve_id, classe_id, est_reinscription) VALUES (4, '2024-2025', '2024-09-01', 4, 2, 0);
INSERT INTO gestion_inscription (id, annee_scolaire, date_inscription, eleve_id, classe_id, est_reinscription) VALUES (5, '2024-2025', '2024-09-01', 5, 13, 0);

-- Insertion des utilisateurs
INSERT INTO gestion_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, role) VALUES (1, 'pbkdf2_sha256$600000$abc123$...', '2024-09-20 10:30:00', TRUE, 'admin', 'Admin', 'User', 'admin@ecole.com', TRUE, TRUE, '2024-09-01 08:00:00', 'admin');
INSERT INTO gestion_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, role) VALUES (2, 'pbkdf2_sha256$600000$def456$...', '2024-09-19 14:25:00', FALSE, 'directeur', 'Jean', 'Directeur', 'directeur@ecole.com', TRUE, TRUE, '2024-09-01 08:00:00', 'directeur');
INSERT INTO gestion_customuser (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, role) VALUES (3, 'pbkdf2_sha256$600000$ghi789$...', '2024-09-18 16:40:00', FALSE, 'prefet', 'Pierre', 'Préfet', 'prefet@ecole.com', TRUE, TRUE, '2024-09-01 08:00:00', 'prefet');