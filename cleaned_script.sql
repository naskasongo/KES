create table auth_group
(
    id   SERIAL PRIMARY KEY,
    name VARCHAR(150) not null
        unique
);

create table django_content_type
(
    id        SERIAL PRIMARY KEY,
    app_label VARCHAR(100) not null,
    model     VARCHAR(100) not null
);

create table auth_permission
(
    id              SERIAL PRIMARY KEY,
    content_type_id integer      not null
        REFERENCES django_content_type,
    codename        VARCHAR(100) not null,
    name            VARCHAR(255) not null
);

create table auth_group_permissions
(
    id            SERIAL PRIMARY KEY,
    group_id      integer not null
        REFERENCES auth_group,
    permission_id integer not null
        REFERENCES auth_permission
);













create table django_migrations
(
    id      SERIAL PRIMARY KEY,
    app     VARCHAR(255) not null,
    name    VARCHAR(255) not null,
    applied TIMESTAMP     not null
);

create table django_session
(
    session_key  VARCHAR(40) not null
        primary key,
    session_data TEXT NOT NULL,
    expire_date  TIMESTAMP    not null
);



create table gestion_anneescolaire
(
    id    SERIAL PRIMARY KEY,
    annee VARCHAR(9) not null
        unique
);

create table gestion_customuser
(
    id           SERIAL PRIMARY KEY,
    password     VARCHAR(128) not null,
    last_login   TIMESTAMP,
    is_superuser BOOLEAN         not null,
    username     VARCHAR(150) not null
        unique,
    first_name   VARCHAR(150) not null,
    last_name    VARCHAR(150) not null,
    email        VARCHAR(254) not null,
    is_staff     BOOLEAN         not null,
    is_active    BOOLEAN         not null,
    date_joined  TIMESTAMP     not null,
    role         VARCHAR(20)  not null
);

create table django_admin_log
(
    id              SERIAL PRIMARY KEY,
    object_id       text,
    object_repr     VARCHAR(200)      not null,
    action_flag     smallint  not null,
    change_message  TEXT NOT NULL,
    content_type_id integer
        REFERENCES django_content_type,
    user_id         bigint            not null
        REFERENCES gestion_customuser,
    action_time     TIMESTAMP          not null,
    check (action_flag >= 0)
);





create table gestion_customuser_groups
(
    id            SERIAL PRIMARY KEY,
    customuser_id bigint  not null
        REFERENCES gestion_customuser,
    group_id      integer not null
        REFERENCES auth_group
);







create table gestion_customuser_user_permissions
(
    id            SERIAL PRIMARY KEY,
    customuser_id bigint  not null
        REFERENCES gestion_customuser,
    permission_id integer not null
        REFERENCES auth_permission
);







create table gestion_historiqueaction
(
    id             SERIAL PRIMARY KEY,
    modele         VARCHAR(100) not null,
    objet_id       integer ,
    action         VARCHAR(20)  not null,
    details        TEXT NOT NULL,
    date_action    TIMESTAMP     not null,
    utilisateur_id bigint
        REFERENCES gestion_customuser,
    username       VARCHAR(150),
    check (objet_id >= 0)
);



create table gestion_notification
(
    id                   SERIAL PRIMARY KEY,
    est_lue              BOOLEAN     not null,
    date_creation        TIMESTAMP not null,
    historique_action_id bigint   not null
        REFERENCES gestion_historiqueaction,
    utilisateur_id       bigint   not null
        REFERENCES gestion_customuser
);





create table gestion_parent
(
    id         SERIAL PRIMARY KEY,
    nom        VARCHAR(50) not null,
    telephone  VARCHAR(20) not null
        unique,
    email      VARCHAR(254),
    adresse    text,
    profession VARCHAR(100),
    relation   VARCHAR(20) not null
);

create table gestion_section
(
    id           SERIAL PRIMARY KEY,
    nom          VARCHAR(50) not null
        unique,
    type_section VARCHAR(10) not null
);

create table gestion_depense
(
    id                SERIAL PRIMARY KEY,
    motif             VARCHAR(255) not null,
    montant           NUMERIC(10, 2)      not null,
    date_depense      date         not null,
    section_id        bigint
        REFERENCES gestion_section,
    annee_scolaire_id integer      not null
);



create table gestion_option
(
    id         SERIAL PRIMARY KEY,
    nom        VARCHAR(50) not null,
    section_id bigint      not null
        REFERENCES gestion_section
);

create table gestion_classe
(
    id         SERIAL PRIMARY KEY,
    nom        VARCHAR(50) not null,
    option_id  bigint
        REFERENCES gestion_option,
    section_id bigint      not null
        REFERENCES gestion_section
);





create table gestion_eleve
(
    id                INTEGER
        primary key ,
    nom               TEXT NOT NULL,
    post_nom          TEXT NOT NULL,
    matricule         TEXT
        unique,
    section_id        INTEGER
        references gestion_section,
    classe_id         INTEGER
        references gestion_classe,
    annee_scolaire    TEXT,
    parent_id         INTEGER
        references gestion_parent,
    prenom            TEXT,
    sexe              TEXT default 'M' not null,
    date_naissance    DATE,
    lieu_naissance    TEXT,
    option_id         INTEGER,
    date_inscription  TIMESTAMP,
    annee_scolaire_id integer,
    check (sexe IN ('M', 'F'))
);

create table gestion_frais
(
    id                SERIAL PRIMARY KEY,
    nom               VARCHAR(255) not null,
    montant           NUMERIC(10, 2)      not null,
    type_frais        VARCHAR(20)  not null,
    annee_scolaire_id bigint       not null
        REFERENCES gestion_anneescolaire,
    option_id         bigint
        REFERENCES gestion_option,
    section_id        bigint
        REFERENCES gestion_section,
    tranche           VARCHAR(50),
    mois              VARCHAR(20)
);







create table gestion_frais_classes
(
    id        SERIAL PRIMARY KEY,
    frais_id  bigint  not null
        REFERENCES gestion_frais,
    classe_id bigint  not null
        REFERENCES gestion_classe
);







create table gestion_inscription
(
    id                SERIAL PRIMARY KEY,
    annee_scolaire    VARCHAR(10) not null,
    date_inscription  date        not null,
    eleve_id          bigint      not null
        REFERENCES gestion_eleve,
    classe_id         integer,
    est_reinscription integer TEXT
);





create table gestion_paiement
(
    id                SERIAL PRIMARY KEY,
    montant_paye      NUMERIC(10, 2)      not null,
    date_paiement     date         not null,
    recu_numero       VARCHAR(255) not null
        unique,
    eleve_id          bigint       not null
        REFERENCES gestion_eleve,
    frais_id          bigint       not null
        REFERENCES gestion_frais,
    mois              VARCHAR(255),
    solde_restant     NUMERIC(10, 2)      not null,
    tranche           VARCHAR(50),
    annee_scolaire_id bigint
        REFERENCES gestion_anneescolaire
);

create table gestion_compensation
(
    id               SERIAL PRIMARY KEY,
    mois             VARCHAR(20) not null,
    montant_compense NUMERIC(10, 2)     not null,
    solde_avant      NUMERIC(10, 2)     not null,
    solde_apres      NUMERIC(10, 2)     not null,
    date_creation    TIMESTAMP    not null,
    paiement_id      bigint      not null
        REFERENCES gestion_paiement
);









create table gestion_userprofile
(
    id             SERIAL PRIMARY KEY,
    totp_secret    VARCHAR(100),
    is_2fa_enabled BOOLEAN    not null,
    user_id        bigint  not null
        unique
        REFERENCES gestion_customuser,
    session_key    VARCHAR(40)
);

create table old_gestion_eleve
(
    id             SERIAL PRIMARY KEY,
    nom            VARCHAR(50)  not null,
    post_nom       VARCHAR(50)  not null,
    prenom         VARCHAR(50),
    sexe           VARCHAR(1)   not null,
    date_naissance date         not null,
    lieu_naissance VARCHAR(100) not null,
    matricule      VARCHAR(20)  not null
        unique,
    annee_scolaire VARCHAR(10)  not null,
    classe_id      bigint       not null
        REFERENCES gestion_classe,
    option_id      bigint
        REFERENCES gestion_option,
    parent_id      bigint
        REFERENCES gestion_parent,
    section_id     bigint       not null
        REFERENCES gestion_section,
    frais_paye     NUMERIC(10, 2)      not null,
    frais_payer    NUMERIC(10, 2)      not null,
    reste_payer    NUMERIC(10, 2)      not null
);









create table otp_static_staticdevice
(
    id                           SERIAL PRIMARY KEY,
    name                         VARCHAR(64)      not null,
    confirmed                    BOOLEAN             not null,
    user_id                      bigint           not null
        REFERENCES gestion_customuser,
    throttling_failure_count     integer  not null,
    throttling_failure_timestamp TIMESTAMP,
    created_at                   TIMESTAMP,
    last_used_at                 TIMESTAMP,
    check (throttling_failure_count >= 0)
);



create table otp_static_statictoken
(
    id        SERIAL PRIMARY KEY,
    token     VARCHAR(16) not null,
    device_id integer     not null
        REFERENCES otp_static_staticdevice
);





create table otp_totp_totpdevice
(
    id                           SERIAL PRIMARY KEY,
    name                         VARCHAR(64)       not null,
    confirmed                    BOOLEAN              not null,
    key                          VARCHAR(80)       not null,
    step                         smallint  not null,
    t0                           bigint            not null,
    digits                       smallint  not null,
    tolerance                    smallint  not null,
    drift                        smallint          not null,
    last_t                       bigint            not null,
    user_id                      bigint            not null
        REFERENCES gestion_customuser,
    throttling_failure_count     integer   not null,
    throttling_failure_timestamp TIMESTAMP,
    created_at                   TIMESTAMP,
    last_used_at                 TIMESTAMP,
    check (digits >= 0),
    check (step >= 0),
    check (throttling_failure_count >= 0),
    check (tolerance >= 0)
);








