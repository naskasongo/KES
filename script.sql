-- Create sequences for auto-increment fields
CREATE SEQUENCE auth_group_id_seq;
CREATE SEQUENCE django_content_type_id_seq;
CREATE SEQUENCE auth_permission_id_seq;
CREATE SEQUENCE auth_group_permissions_id_seq;
CREATE SEQUENCE django_migrations_id_seq;
CREATE SEQUENCE gestion_anneescolaire_id_seq;
CREATE SEQUENCE gestion_customuser_id_seq;
CREATE SEQUENCE django_admin_log_id_seq;
CREATE SEQUENCE gestion_customuser_groups_id_seq;
CREATE SEQUENCE gestion_customuser_user_permissions_id_seq;
CREATE SEQUENCE gestion_historiqueaction_id_seq;
CREATE SEQUENCE gestion_notification_id_seq;
CREATE SEQUENCE gestion_parent_id_seq;
CREATE SEQUENCE gestion_section_id_seq;
CREATE SEQUENCE gestion_depense_id_seq;
CREATE SEQUENCE gestion_option_id_seq;
CREATE SEQUENCE gestion_classe_id_seq;
CREATE SEQUENCE gestion_eleve_id_seq;
CREATE SEQUENCE gestion_frais_id_seq;
CREATE SEQUENCE gestion_frais_classes_id_seq;
CREATE SEQUENCE gestion_inscription_id_seq;
CREATE SEQUENCE gestion_paiement_id_seq;
CREATE SEQUENCE gestion_compensation_id_seq;
CREATE SEQUENCE gestion_userprofile_id_seq;
CREATE SEQUENCE old_gestion_eleve_id_seq;
CREATE SEQUENCE otp_static_staticdevice_id_seq;
CREATE SEQUENCE otp_static_statictoken_id_seq;
CREATE SEQUENCE otp_totp_totpdevice_id_seq;

-- Create tables with PostgreSQL syntax
CREATE TABLE auth_group (
    id integer NOT NULL DEFAULT nextval('auth_group_id_seq') PRIMARY KEY,
    name varchar(150) NOT NULL UNIQUE
);

CREATE TABLE django_content_type (
    id integer NOT NULL DEFAULT nextval('django_content_type_id_seq') PRIMARY KEY,
    app_label varchar(100) NOT NULL,
    model varchar(100) NOT NULL
);

CREATE TABLE auth_permission (
    id integer NOT NULL DEFAULT nextval('auth_permission_id_seq') PRIMARY KEY,
    content_type_id integer NOT NULL REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED,
    codename varchar(100) NOT NULL,
    name varchar(255) NOT NULL
);

CREATE TABLE auth_group_permissions (
    id integer NOT NULL DEFAULT nextval('auth_group_permissions_id_seq') PRIMARY KEY,
    group_id integer NOT NULL REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED,
    permission_id integer NOT NULL REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE django_migrations (
    id integer NOT NULL DEFAULT nextval('django_migrations_id_seq') PRIMARY KEY,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);

CREATE TABLE django_session (
    session_key varchar(40) NOT NULL PRIMARY KEY,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);

CREATE TABLE gestion_anneescolaire (
    id integer NOT NULL DEFAULT nextval('gestion_anneescolaire_id_seq') PRIMARY KEY,
    annee varchar(9) NOT NULL UNIQUE
);

CREATE TABLE gestion_customuser (
    id integer NOT NULL DEFAULT nextval('gestion_customuser_id_seq') PRIMARY KEY,
    password varchar(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username varchar(150) NOT NULL UNIQUE,
    first_name varchar(150) NOT NULL,
    last_name varchar(150) NOT NULL,
    email varchar(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    role varchar(20) NOT NULL
);

CREATE TABLE django_admin_log (
    id integer NOT NULL DEFAULT nextval('django_admin_log_id_seq') PRIMARY KEY,
    object_id text,
    object_repr varchar(200) NOT NULL,
    action_flag smallint NOT NULL CHECK (action_flag >= 0),
    change_message text NOT NULL,
    content_type_id integer REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED,
    user_id bigint NOT NULL REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    action_time timestamp with time zone NOT NULL
);

CREATE TABLE gestion_customuser_groups (
    id integer NOT NULL DEFAULT nextval('gestion_customuser_groups_id_seq') PRIMARY KEY,
    customuser_id bigint NOT NULL REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    group_id integer NOT NULL REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_customuser_user_permissions (
    id integer NOT NULL DEFAULT nextval('gestion_customuser_user_permissions_id_seq') PRIMARY KEY,
    customuser_id bigint NOT NULL REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    permission_id integer NOT NULL REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_historiqueaction (
    id integer NOT NULL DEFAULT nextval('gestion_historiqueaction_id_seq') PRIMARY KEY,
    modele varchar(100) NOT NULL,
    objet_id bigint,
    action varchar(20) NOT NULL,
    details text NOT NULL,
    date_action timestamp with time zone NOT NULL,
    utilisateur_id bigint REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    username varchar(150)
);

CREATE TABLE gestion_notification (
    id integer NOT NULL DEFAULT nextval('gestion_notification_id_seq') PRIMARY KEY,
    est_lue boolean NOT NULL,
    date_creation timestamp with time zone NOT NULL,
    historique_action_id bigint NOT NULL REFERENCES gestion_historiqueaction(id) DEFERRABLE INITIALLY DEFERRED,
    utilisateur_id bigint NOT NULL REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_parent (
    id integer NOT NULL DEFAULT nextval('gestion_parent_id_seq') PRIMARY KEY,
    nom varchar(50) NOT NULL,
    telephone varchar(20) NOT NULL UNIQUE,
    email varchar(254),
    adresse text,
    profession varchar(100),
    relation varchar(20) NOT NULL
);

CREATE TABLE gestion_section (
    id integer NOT NULL DEFAULT nextval('gestion_section_id_seq') PRIMARY KEY,
    nom varchar(50) NOT NULL UNIQUE,
    type_section varchar(10) NOT NULL
);

CREATE TABLE gestion_depense (
    id integer NOT NULL DEFAULT nextval('gestion_depense_id_seq') PRIMARY KEY,
    motif varchar(255) NOT NULL,
    montant numeric NOT NULL,
    date_depense date NOT NULL,
    section_id bigint REFERENCES gestion_section(id) DEFERRABLE INITIALLY DEFERRED,
    annee_scolaire_id integer NOT NULL
);

CREATE TABLE gestion_option (
    id integer NOT NULL DEFAULT nextval('gestion_option_id_seq') PRIMARY KEY,
    nom varchar(50) NOT NULL,
    section_id bigint NOT NULL REFERENCES gestion_section(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_classe (
    id integer NOT NULL DEFAULT nextval('gestion_classe_id_seq') PRIMARY KEY,
    nom varchar(50) NOT NULL,
    option_id bigint REFERENCES gestion_option(id) DEFERRABLE INITIALLY DEFERRED,
    section_id bigint NOT NULL REFERENCES gestion_section(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_eleve (
    id integer NOT NULL DEFAULT nextval('gestion_eleve_id_seq') PRIMARY KEY,
    nom text NOT NULL,
    post_nom text NOT NULL,
    matricule text UNIQUE,
    section_id integer REFERENCES gestion_section(id),
    classe_id integer REFERENCES gestion_classe(id),
    annee_scolaire text,
    parent_id integer REFERENCES gestion_parent(id),
    prenom text,
    sexe text DEFAULT 'M' NOT NULL CHECK (sexe IN ('M', 'F')),
    date_naissance date,
    lieu_naissance text,
    option_id integer,
    date_inscription timestamp with time zone,
    annee_scolaire_id integer
);

CREATE TABLE gestion_frais (
    id integer NOT NULL DEFAULT nextval('gestion_frais_id_seq') PRIMARY KEY,
    nom varchar(255) NOT NULL,
    montant numeric NOT NULL,
    type_frais varchar(20) NOT NULL,
    annee_scolaire_id bigint NOT NULL REFERENCES gestion_anneescolaire(id) DEFERRABLE INITIALLY DEFERRED,
    option_id bigint REFERENCES gestion_option(id) DEFERRABLE INITIALLY DEFERRED,
    section_id bigint REFERENCES gestion_section(id) DEFERRABLE INITIALLY DEFERRED,
    tranche varchar(50),
    mois varchar(20)
);

CREATE TABLE gestion_frais_classes (
    id integer NOT NULL DEFAULT nextval('gestion_frais_classes_id_seq') PRIMARY KEY,
    frais_id bigint NOT NULL REFERENCES gestion_frais(id) DEFERRABLE INITIALLY DEFERRED,
    classe_id bigint NOT NULL REFERENCES gestion_classe(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_inscription (
    id integer NOT NULL DEFAULT nextval('gestion_inscription_id_seq') PRIMARY KEY,
    annee_scolaire varchar(10) NOT NULL,
    date_inscription date NOT NULL,
    eleve_id bigint NOT NULL REFERENCES gestion_eleve(id) DEFERRABLE INITIALLY DEFERRED,
    classe_id integer,
    est_reinscription integer
);

CREATE TABLE gestion_paiement (
    id integer NOT NULL DEFAULT nextval('gestion_paiement_id_seq') PRIMARY KEY,
    montant_paye numeric NOT NULL,
    date_paiement date NOT NULL,
    recu_numero varchar(255) NOT NULL UNIQUE,
    eleve_id bigint NOT NULL REFERENCES gestion_eleve(id) DEFERRABLE INITIALLY DEFERRED,
    frais_id bigint NOT NULL REFERENCES gestion_frais(id) DEFERRABLE INITIALLY DEFERRED,
    mois varchar(255),
    solde_restant numeric NOT NULL,
    tranche varchar(50),
    annee_scolaire_id bigint REFERENCES gestion_anneescolaire(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_compensation (
    id integer NOT NULL DEFAULT nextval('gestion_compensation_id_seq') PRIMARY KEY,
    mois varchar(20) NOT NULL,
    montant_compense numeric NOT NULL,
    solde_avant numeric NOT NULL,
    solde_apres numeric NOT NULL,
    date_creation timestamp with time zone NOT NULL,
    paiement_id bigint NOT NULL REFERENCES gestion_paiement(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE gestion_userprofile (
    id integer NOT NULL DEFAULT nextval('gestion_userprofile_id_seq') PRIMARY KEY,
    totp_secret varchar(100),
    is_2fa_enabled boolean NOT NULL,
    user_id bigint NOT NULL UNIQUE REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    session_key varchar(40)
);

CREATE TABLE old_gestion_eleve (
    id integer NOT NULL DEFAULT nextval('old_gestion_eleve_id_seq') PRIMARY KEY,
    nom varchar(50) NOT NULL,
    post_nom varchar(50) NOT NULL,
    prenom varchar(50),
    sexe varchar(1) NOT NULL,
    date_naissance date NOT NULL,
    lieu_naissance varchar(100) NOT NULL,
    matricule varchar(20) NOT NULL UNIQUE,
    annee_scolaire varchar(10) NOT NULL,
    classe_id bigint NOT NULL REFERENCES gestion_classe(id) DEFERRABLE INITIALLY DEFERRED,
    option_id bigint REFERENCES gestion_option(id) DEFERRABLE INITIALLY DEFERRED,
    parent_id bigint REFERENCES gestion_parent(id) DEFERRABLE INITIALLY DEFERRED,
    section_id bigint NOT NULL REFERENCES gestion_section(id) DEFERRABLE INITIALLY DEFERRED,
    frais_paye numeric NOT NULL,
    frais_payer numeric NOT NULL,
    reste_payer numeric NOT NULL
);

CREATE TABLE otp_static_staticdevice (
    id integer NOT NULL DEFAULT nextval('otp_static_staticdevice_id_seq') PRIMARY KEY,
    name varchar(64) NOT NULL,
    confirmed boolean NOT NULL,
    user_id bigint NOT NULL REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    throttling_failure_count integer NOT NULL CHECK (throttling_failure_count >= 0),
    throttling_failure_timestamp timestamp with time zone,
    created_at timestamp with time zone,
    last_used_at timestamp with time zone
);

CREATE TABLE otp_static_statictoken (
    id integer NOT NULL DEFAULT nextval('otp_static_statictoken_id_seq') PRIMARY KEY,
    token varchar(16) NOT NULL,
    device_id integer NOT NULL REFERENCES otp_static_staticdevice(id) DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE otp_totp_totpdevice (
    id integer NOT NULL DEFAULT nextval('otp_totp_totpdevice_id_seq') PRIMARY KEY,
    name varchar(64) NOT NULL,
    confirmed boolean NOT NULL,
    key varchar(80) NOT NULL,
    step smallint NOT NULL CHECK (step >= 0),
    t0 bigint NOT NULL,
    digits smallint NOT NULL CHECK (digits >= 0),
    tolerance smallint NOT NULL CHECK (tolerance >= 0),
    drift smallint NOT NULL,
    last_t bigint NOT NULL,
    user_id bigint NOT NULL REFERENCES gestion_customuser(id) DEFERRABLE INITIALLY DEFERRED,
    throttling_failure_count integer NOT NULL CHECK (throttling_failure_count >= 0),
    throttling_failure_timestamp timestamp with time zone,
    created_at timestamp with time zone,
    last_used_at timestamp with time zone
);

-- Create indexes
CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions (group_id);
CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id_0cd325b0_uniq ON auth_group_permissions (group_id, permission_id);
CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions (permission_id);
CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission (content_type_id);
CREATE UNIQUE INDEX auth_permission_content_type_id_codename_01ab375a_uniq ON auth_permission (content_type_id, codename);
CREATE UNIQUE INDEX django_content_type_app_label_model_76bd3d3b_uniq ON django_content_type (app_label, model);
CREATE INDEX django_session_expire_date_a5c62663 ON django_session (expire_date);
CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log (content_type_id);
CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log (user_id);
CREATE INDEX gestion_customuser_groups_customuser_id_00a4ba1a ON gestion_customuser_groups (customuser_id);
CREATE UNIQUE INDEX gestion_customuser_groups_customuser_id_group_id_15e0a562_uniq ON gestion_customuser_groups (customuser_id, group_id);
CREATE INDEX gestion_customuser_groups_group_id_5b375038 ON gestion_customuser_groups (group_id);
CREATE INDEX gestion_customuser_user_permissions_customuser_id_6eb7dbd3 ON gestion_customuser_user_permissions (customuser_id);
CREATE UNIQUE INDEX gestion_customuser_user_permissions_customuser_id_permission_id_5bc4e360_uniq ON gestion_customuser_user_permissions (customuser_id, permission_id);
CREATE INDEX gestion_customuser_user_permissions_permission_id_99727279 ON gestion_customuser_user_permissions (permission_id);
CREATE INDEX gestion_historiqueaction_utilisateur_id_32430e70 ON gestion_historiqueaction (utilisateur_id);
CREATE INDEX gestion_notification_historique_action_id_a3b79330 ON gestion_notification (historique_action_id);
CREATE INDEX gestion_notification_utilisateur_id_bb840a16 ON gestion_notification (utilisateur_id);
CREATE INDEX gestion_depense_section_id_98574d67 ON gestion_depense (section_id);
CREATE INDEX gestion_classe_option_id_b5944e05 ON gestion_classe (option_id);
CREATE INDEX gestion_classe_section_id_7abf4bb1 ON gestion_classe (section_id);
CREATE INDEX gestion_frais_annee_scolaire_id_2185d9d0 ON gestion_frais (annee_scolaire_id);
CREATE INDEX gestion_frais_option_id_b2a2168c ON gestion_frais (option_id);
CREATE INDEX gestion_frais_section_id_0043a576 ON gestion_frais (section_id);
CREATE INDEX gestion_frais_classes_classe_id_968eaa48 ON gestion_frais_classes (classe_id);
CREATE INDEX gestion_frais_classes_frais_id_6cef1dab ON gestion_frais_classes (frais_id);
CREATE UNIQUE INDEX gestion_frais_classes_frais_id_classe_id_8944eda8_uniq ON gestion_frais_classes (frais_id, classe_id);
CREATE INDEX gestion_inscription_eleve_id_866146b2 ON gestion_inscription (eleve_id);
CREATE INDEX gestion_option_section_id_d92e4807 ON gestion_option (section_id);
CREATE INDEX gestion_compensation_paiement_id_36d099b9 ON gestion_compensation (paiement_id);
CREATE INDEX gestion_paiement_annee_scolaire_id_85cf36ec ON gestion_paiement (annee_scolaire_id);
CREATE INDEX gestion_paiement_eleve_id_6fdeb0b7 ON gestion_paiement (eleve_id);
CREATE INDEX gestion_paiement_frais_id_0e7c3b14 ON gestion_paiement (frais_id);
CREATE INDEX gestion_eleve_classe_id_503264c9 ON old_gestion_eleve (classe_id);
CREATE INDEX gestion_eleve_option_id_f524af09 ON old_gestion_eleve (option_id);
CREATE INDEX gestion_eleve_parent_id_7909cdbe ON old_gestion_eleve (parent_id);
CREATE INDEX gestion_eleve_section_id_4286a51f ON old_gestion_eleve (section_id);
CREATE INDEX otp_static_staticdevice_user_id_7f9cff2b ON otp_static_staticdevice (user_id);
CREATE INDEX otp_static_statictoken_device_id_74b7c7d1 ON otp_static_statictoken (device_id);
CREATE INDEX otp_static_statictoken_token_d0a51866 ON otp_static_statictoken (token);
CREATE INDEX otp_totp_totpdevice_user_id_0fb18292 ON otp_totp_totpdevice (user_id);

-- Set sequence values to match the maximum IDs in your data
SELECT setval('auth_group_id_seq', (SELECT MAX(id) FROM auth_group));
SELECT setval('django_content_type_id_seq', (SELECT MAX(id) FROM django_content_type));
SELECT setval('auth_permission_id_seq', (SELECT MAX(id) FROM auth_permission));
SELECT setval('auth_group_permissions_id_seq', (SELECT MAX(id) FROM auth_group_permissions));
SELECT setval('django_migrations_id_seq', (SELECT MAX(id) FROM django_migrations));
SELECT setval('gestion_anneescolaire_id_seq', (SELECT MAX(id) FROM gestion_anneescolaire));
SELECT setval('gestion_customuser_id_seq', (SELECT MAX(id) FROM gestion_customuser));
SELECT setval('django_admin_log_id_seq', (SELECT MAX(id) FROM django_admin_log));
SELECT setval('gestion_customuser_groups_id_seq', (SELECT MAX(id) FROM gestion_customuser_groups));
SELECT setval('gestion_customuser_user_permissions_id_seq', (SELECT MAX(id) FROM gestion_customuser_user_permissions));
SELECT setval('gestion_historiqueaction_id_seq', (SELECT MAX(id) FROM gestion_historiqueaction));
SELECT setval('gestion_notification_id_seq', (SELECT MAX(id) FROM gestion_notification));
SELECT setval('gestion_parent_id_seq', (SELECT MAX(id) FROM gestion_parent));
SELECT setval('gestion_section_id_seq', (SELECT MAX(id) FROM gestion_section));
SELECT setval('gestion_depense_id_seq', (SELECT MAX(id) FROM gestion_depense));
SELECT setval('gestion_option_id_seq', (SELECT MAX(id) FROM gestion_option));
SELECT setval('gestion_classe_id_seq', (SELECT MAX(id) FROM gestion_classe));
SELECT setval('gestion_eleve_id_seq', (SELECT MAX(id) FROM gestion_eleve));
SELECT setval('gestion_frais_id_seq', (SELECT MAX(id) FROM gestion_frais));
SELECT setval('gestion_frais_classes_id_seq', (SELECT MAX(id) FROM gestion_frais_classes));
SELECT setval('gestion_inscription_id_seq', (SELECT MAX(id) FROM gestion_inscription));
SELECT setval('gestion_paiement_id_seq', (SELECT MAX(id) FROM gestion_paiement));
SELECT setval('gestion_compensation_id_seq', (SELECT MAX(id) FROM gestion_compensation));
SELECT setval('gestion_userprofile_id_seq', (SELECT MAX(id) FROM gestion_userprofile));
SELECT setval('old_gestion_eleve_id_seq', (SELECT MAX(id) FROM old_gestion_eleve));
SELECT setval('otp_static_staticdevice_id_seq', (SELECT MAX(id) FROM otp_static_staticdevice));
SELECT setval('otp_static_statictoken_id_seq', (SELECT MAX(id) FROM otp_static_statictoken));
SELECT setval('otp_totp_totpdevice_id_seq', (SELECT MAX(id) FROM otp_totp_totpdevice));
