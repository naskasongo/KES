-- Table: auth_group
CREATE TABLE auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Table: django_content_type
CREATE TABLE django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL
);

-- Table: auth_permission
CREATE TABLE auth_permission (
    id SERIAL PRIMARY KEY,
    content_type_id INTEGER NOT NULL REFERENCES django_content_type,
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL
);

-- Table: auth_group_permissions
CREATE TABLE auth_group_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES auth_group,
    permission_id INTEGER NOT NULL REFERENCES auth_permission
);

-- Table: django_migrations
CREATE TABLE django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL
);

-- Table: django_session
CREATE TABLE django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);

-- Table: gestion_anneescolaire
CREATE TABLE gestion_anneescolaire (
    id SERIAL PRIMARY KEY,
    annee VARCHAR(9) NOT NULL UNIQUE
);

-- Table: gestion_customuser
CREATE TABLE gestion_customuser (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP NOT NULL,
    role VARCHAR(20) NOT NULL
);

-- Table: django_admin_log
CREATE TABLE django_admin_log (
    id SERIAL PRIMARY KEY,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL,
    change_message TEXT NOT NULL,
    content_type_id INTEGER REFERENCES django_content_type,
    user_id BIGINT NOT NULL REFERENCES gestion_customuser,
    action_time TIMESTAMP NOT NULL
);

-- Table: gestion_customuser_groups
CREATE TABLE gestion_customuser_groups (
    id SERIAL PRIMARY KEY,
    customuser_id BIGINT NOT NULL REFERENCES gestion_customuser,
    group_id INTEGER NOT NULL REFERENCES auth_group
);

-- Table: gestion_customuser_user_permissions
CREATE TABLE gestion_customuser_user_permissions (
    id SERIAL PRIMARY KEY,
    customuser_id BIGINT NOT NULL REFERENCES gestion_customuser,
    permission_id INTEGER NOT NULL REFERENCES auth_permission
);

-- Table: gestion_historiqueaction
CREATE TABLE gestion_historiqueaction (
    id SERIAL PRIMARY KEY,
    modele VARCHAR(100) NOT NULL,
    objet_id INTEGER,
    action VARCHAR(20) NOT NULL,
    details TEXT NOT NULL,
    date_action TIMESTAMP NOT NULL,
    utilisateur_id BIGINT REFERENCES gestion_customuser,
    username VARCHAR(150)
);

-- Table: gestion_notification
CREATE TABLE gestion_notification (
    id SERIAL PRIMARY KEY,
    est_lue BOOLEAN NOT NULL,
    date_creation TIMESTAMP NOT NULL,
    historique_action_id BIGINT NOT NULL REFERENCES gestion_historiqueaction,
    utilisateur_id BIGINT NOT NULL REFERENCES gestion_customuser
);

-- Table: gestion_parent
CREATE TABLE gestion_parent (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    telephone VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(254),
    adresse TEXT,
    profession VARCHAR(100),
    relation VARCHAR(20) NOT NULL
);

-- Table: gestion_section
CREATE TABLE gestion_section (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL UNIQUE,
    type_section VARCHAR(10) NOT NULL
);

-- Table: gestion_depense
CREATE TABLE gestion_depense (
    id SERIAL PRIMARY KEY,
    motif VARCHAR(255) NOT NULL,
    montant NUMERIC(10,2) NOT NULL,
    date_depense DATE NOT NULL,
    section_id BIGINT REFERENCES gestion_section,
    annee_scolaire_id INTEGER NOT NULL
);

-- Table: gestion_option
CREATE TABLE gestion_option (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    section_id BIGINT NOT NULL REFERENCES gestion_section
);

-- Table: gestion_classe
CREATE TABLE gestion_classe (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    option_id BIGINT REFERENCES gestion_option,
    section_id BIGINT NOT NULL REFERENCES gestion_section
);

-- Table: gestion_eleve
CREATE TABLE gestion_eleve (
    id SERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    post_nom TEXT NOT NULL,
    matricule TEXT UNIQUE,
    section_id INTEGER REFERENCES gestion_section,
    classe_id INTEGER REFERENCES gestion_classe,
    annee_scolaire TEXT,
    parent_id INTEGER REFERENCES gestion_parent,
    prenom TEXT,
    sexe TEXT DEFAULT 'M' NOT NULL,
    date_naissance DATE,
    lieu_naissance TEXT,
    option_id INTEGER,
    date_inscription TIMESTAMP,
    annee_scolaire_id INTEGER,
    CHECK (sexe IN ('M', 'F'))
);

-- Table: gestion_frais
CREATE TABLE gestion_frais (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    montant NUMERIC(10,2) NOT NULL,
    type_frais VARCHAR(20) NOT NULL,
    annee_scolaire_id BIGINT NOT NULL REFERENCES gestion_anneescolaire,
    option_id BIGINT REFERENCES gestion_option,
    section_id BIGINT REFERENCES gestion_section,
    tranche VARCHAR(50),
    mois VARCHAR(20)
);

-- Table: gestion_frais_classes
CREATE TABLE gestion_frais_classes (
    id SERIAL PRIMARY KEY,
    frais_id BIGINT NOT NULL REFERENCES gestion_frais,
    classe_id BIGINT NOT NULL REFERENCES gestion_classe
);

-- Table: gestion_inscription
CREATE TABLE gestion_inscription (
    id SERIAL PRIMARY KEY,
    annee_scolaire VARCHAR(10) NOT NULL,
    date_inscription DATE NOT NULL,
    eleve_id BIGINT NOT NULL REFERENCES gestion_eleve,
    classe_id INTEGER,
    est_reinscription INTEGER
);

-- Table: gestion_paiement
CREATE TABLE gestion_paiement (
    id SERIAL PRIMARY KEY,
    montant_paye NUMERIC(10,2) NOT NULL,
    date_paiement DATE NOT NULL,
    recu_numero VARCHAR(255) NOT NULL UNIQUE,
    eleve_id BIGINT NOT NULL REFERENCES gestion_eleve,
    frais_id BIGINT NOT NULL REFERENCES gestion_frais,
    mois VARCHAR(255),
    solde_restant NUMERIC(10,2) NOT NULL,
    tranche VARCHAR(50),
    annee_scolaire_id BIGINT REFERENCES gestion_anneescolaire
);

-- Table: gestion_compensation
CREATE TABLE gestion_compensation (
    id SERIAL PRIMARY KEY,
    mois VARCHAR(20) NOT NULL,
    montant_compense NUMERIC(10,2) NOT NULL,
    solde_avant NUMERIC(10,2) NOT NULL,
    solde_apres NUMERIC(10,2) NOT NULL,
    date_creation TIMESTAMP NOT NULL,
    paiement_id BIGINT NOT NULL REFERENCES gestion_paiement
);

-- Table: gestion_userprofile
CREATE TABLE gestion_userprofile (
    id SERIAL PRIMARY KEY,
    totp_secret VARCHAR(100),
    is_2fa_enabled BOOLEAN NOT NULL,
    user_id BIGINT NOT NULL UNIQUE REFERENCES gestion_customuser,
    session_key VARCHAR(40)
);

-- Table: otp_static_staticdevice
CREATE TABLE otp_static_staticdevice (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    confirmed BOOLEAN NOT NULL,
    user_id BIGINT NOT NULL REFERENCES gestion_customuser,
    throttling_failure_count INTEGER NOT NULL,
    throttling_failure_timestamp TIMESTAMP,
    created_at TIMESTAMP,
    last_used_at TIMESTAMP
);

-- Table: otp_static_statictoken
CREATE TABLE otp_static_statictoken (
    id SERIAL PRIMARY KEY,
    token VARCHAR(16) NOT NULL,
    device_id INTEGER NOT NULL REFERENCES otp_static_staticdevice
);

-- Table: otp_totp_totpdevice
CREATE TABLE otp_totp_totpdevice (
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    confirmed BOOLEAN NOT NULL,
    key VARCHAR(80) NOT NULL,
    step SMALLINT NOT NULL,
    t0 BIGINT NOT NULL,
    digits SMALLINT NOT NULL,
    tolerance SMALLINT NOT NULL,
    drift SMALLINT NOT NULL,
    last_t BIGINT NOT NULL,
    user_id BIGINT NOT NULL REFERENCES gestion_customuser,
    throttling_failure_count INTEGER NOT NULL,
    throttling_failure_timestamp TIMESTAMP,
    created_at TIMESTAMP,
    last_used_at TIMESTAMP
);