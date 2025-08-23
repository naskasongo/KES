create table auth_group
(
    id   integer      not null
        primary key autoincrement,
    name varchar(150) not null
        unique
);

create table django_content_type
(
    id        integer      not null
        primary key autoincrement,
    app_label varchar(100) not null,
    model     varchar(100) not null
);

create table auth_permission
(
    id              integer      not null
        primary key autoincrement,
    content_type_id integer      not null
        references django_content_type
            deferrable initially deferred,
    codename        varchar(100) not null,
    name            varchar(255) not null
);

create table auth_group_permissions
(
    id            integer not null
        primary key autoincrement,
    group_id      integer not null
        references auth_group
            deferrable initially deferred,
    permission_id integer not null
        references auth_permission
            deferrable initially deferred
);

create index auth_group_permissions_group_id_b120cbf9
    on auth_group_permissions (group_id);

create unique index auth_group_permissions_group_id_permission_id_0cd325b0_uniq
    on auth_group_permissions (group_id, permission_id);

create index auth_group_permissions_permission_id_84c5c92e
    on auth_group_permissions (permission_id);

create index auth_permission_content_type_id_2f476e4b
    on auth_permission (content_type_id);

create unique index auth_permission_content_type_id_codename_01ab375a_uniq
    on auth_permission (content_type_id, codename);

create unique index django_content_type_app_label_model_76bd3d3b_uniq
    on django_content_type (app_label, model);

create table django_migrations
(
    id      integer      not null
        primary key autoincrement,
    app     varchar(255) not null,
    name    varchar(255) not null,
    applied datetime     not null
);

create table django_session
(
    session_key  varchar(40) not null
        primary key,
    session_data text        not null,
    expire_date  datetime    not null
);

create index django_session_expire_date_a5c62663
    on django_session (expire_date);

create table gestion_anneescolaire
(
    id    integer    not null
        primary key autoincrement,
    annee varchar(9) not null
        unique
);

create table gestion_customuser
(
    id           integer      not null
        primary key autoincrement,
    password     varchar(128) not null,
    last_login   datetime,
    is_superuser bool         not null,
    username     varchar(150) not null
        unique,
    first_name   varchar(150) not null,
    last_name    varchar(150) not null,
    email        varchar(254) not null,
    is_staff     bool         not null,
    is_active    bool         not null,
    date_joined  datetime     not null,
    role         varchar(20)  not null
);

create table django_admin_log
(
    id              integer           not null
        primary key autoincrement,
    object_id       text,
    object_repr     varchar(200)      not null,
    action_flag     smallint unsigned not null,
    change_message  text              not null,
    content_type_id integer
        references django_content_type
            deferrable initially deferred,
    user_id         bigint            not null
        references gestion_customuser
            deferrable initially deferred,
    action_time     datetime          not null,
    check ("action_flag" >= 0)
);

create index django_admin_log_content_type_id_c4bce8eb
    on django_admin_log (content_type_id);

create index django_admin_log_user_id_c564eba6
    on django_admin_log (user_id);

create table gestion_customuser_groups
(
    id            integer not null
        primary key autoincrement,
    customuser_id bigint  not null
        references gestion_customuser
            deferrable initially deferred,
    group_id      integer not null
        references auth_group
            deferrable initially deferred
);

create index gestion_customuser_groups_customuser_id_00a4ba1a
    on gestion_customuser_groups (customuser_id);

create unique index gestion_customuser_groups_customuser_id_group_id_15e0a562_uniq
    on gestion_customuser_groups (customuser_id, group_id);

create index gestion_customuser_groups_group_id_5b375038
    on gestion_customuser_groups (group_id);

create table gestion_customuser_user_permissions
(
    id            integer not null
        primary key autoincrement,
    customuser_id bigint  not null
        references gestion_customuser
            deferrable initially deferred,
    permission_id integer not null
        references auth_permission
            deferrable initially deferred
);

create index gestion_customuser_user_permissions_customuser_id_6eb7dbd3
    on gestion_customuser_user_permissions (customuser_id);

create unique index gestion_customuser_user_permissions_customuser_id_permission_id_5bc4e360_uniq
    on gestion_customuser_user_permissions (customuser_id, permission_id);

create index gestion_customuser_user_permissions_permission_id_99727279
    on gestion_customuser_user_permissions (permission_id);

create table gestion_historiqueaction
(
    id             integer      not null
        primary key autoincrement,
    modele         varchar(100) not null,
    objet_id       integer unsigned,
    action         varchar(20)  not null,
    details        text         not null,
    date_action    datetime     not null,
    utilisateur_id bigint
        references gestion_customuser
            deferrable initially deferred,
    username       varchar(150),
    check ("objet_id" >= 0)
);

create index gestion_historiqueaction_utilisateur_id_32430e70
    on gestion_historiqueaction (utilisateur_id);

create table gestion_notification
(
    id                   integer  not null
        primary key autoincrement,
    est_lue              bool     not null,
    date_creation        datetime not null,
    historique_action_id bigint   not null
        references gestion_historiqueaction
            deferrable initially deferred,
    utilisateur_id       bigint   not null
        references gestion_customuser
            deferrable initially deferred
);

create index gestion_notification_historique_action_id_a3b79330
    on gestion_notification (historique_action_id);

create index gestion_notification_utilisateur_id_bb840a16
    on gestion_notification (utilisateur_id);

create table gestion_parent
(
    id         integer     not null
        primary key autoincrement,
    nom        varchar(50) not null,
    telephone  varchar(20) not null
        unique,
    email      varchar(254),
    adresse    text,
    profession varchar(100),
    relation   varchar(20) not null
);

create table gestion_section
(
    id           integer     not null
        primary key autoincrement,
    nom          varchar(50) not null
        unique,
    type_section varchar(10) not null
);

create table gestion_depense
(
    id                integer      not null
        primary key autoincrement,
    motif             varchar(255) not null,
    montant           decimal      not null,
    date_depense      date         not null,
    section_id        bigint
        references gestion_section
            deferrable initially deferred,
    annee_scolaire_id integer      not null
);

create index gestion_depense_section_id_98574d67
    on gestion_depense (section_id);

create table gestion_option
(
    id         integer     not null
        primary key autoincrement,
    nom        varchar(50) not null,
    section_id bigint      not null
        references gestion_section
            deferrable initially deferred
);

create table gestion_classe
(
    id         integer     not null
        primary key autoincrement,
    nom        varchar(50) not null,
    option_id  bigint
        references gestion_option
            deferrable initially deferred,
    section_id bigint      not null
        references gestion_section
            deferrable initially deferred
);

create index gestion_classe_option_id_b5944e05
    on gestion_classe (option_id);

create index gestion_classe_section_id_7abf4bb1
    on gestion_classe (section_id);

create table gestion_eleve
(
    id                INTEGER
        primary key autoincrement,
    nom               TEXT             not null,
    post_nom          TEXT             not null,
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
    id                integer      not null
        primary key autoincrement,
    nom               varchar(255) not null,
    montant           decimal      not null,
    type_frais        varchar(20)  not null,
    annee_scolaire_id bigint       not null
        references gestion_anneescolaire
            deferrable initially deferred,
    option_id         bigint
        references gestion_option
            deferrable initially deferred,
    section_id        bigint
        references gestion_section
            deferrable initially deferred,
    tranche           varchar(50),
    mois              varchar(20)
);

create index gestion_frais_annee_scolaire_id_2185d9d0
    on gestion_frais (annee_scolaire_id);

create index gestion_frais_option_id_b2a2168c
    on gestion_frais (option_id);

create index gestion_frais_section_id_0043a576
    on gestion_frais (section_id);

create table gestion_frais_classes
(
    id        integer not null
        primary key autoincrement,
    frais_id  bigint  not null
        references gestion_frais
            deferrable initially deferred,
    classe_id bigint  not null
        references gestion_classe
            deferrable initially deferred
);

create index gestion_frais_classes_classe_id_968eaa48
    on gestion_frais_classes (classe_id);

create index gestion_frais_classes_frais_id_6cef1dab
    on gestion_frais_classes (frais_id);

create unique index gestion_frais_classes_frais_id_classe_id_8944eda8_uniq
    on gestion_frais_classes (frais_id, classe_id);

create table gestion_inscription
(
    id                integer     not null
        primary key autoincrement,
    annee_scolaire    varchar(10) not null,
    date_inscription  date        not null,
    eleve_id          bigint      not null
        references gestion_eleve
            deferrable initially deferred,
    classe_id         integer,
    est_reinscription integer TEXT
);

create index gestion_inscription_eleve_id_866146b2
    on gestion_inscription (eleve_id);

create index gestion_option_section_id_d92e4807
    on gestion_option (section_id);

create table gestion_paiement
(
    id                integer      not null
        primary key autoincrement,
    montant_paye      decimal      not null,
    date_paiement     date         not null,
    recu_numero       varchar(255) not null
        unique,
    eleve_id          bigint       not null
        references gestion_eleve
            deferrable initially deferred,
    frais_id          bigint       not null
        references gestion_frais
            deferrable initially deferred,
    mois              varchar(255),
    solde_restant     decimal      not null,
    tranche           varchar(50),
    annee_scolaire_id bigint
        references gestion_anneescolaire
            deferrable initially deferred
);

create table gestion_compensation
(
    id               integer     not null
        primary key autoincrement,
    mois             varchar(20) not null,
    montant_compense decimal     not null,
    solde_avant      decimal     not null,
    solde_apres      decimal     not null,
    date_creation    datetime    not null,
    paiement_id      bigint      not null
        references gestion_paiement
            deferrable initially deferred
);

create index gestion_compensation_paiement_id_36d099b9
    on gestion_compensation (paiement_id);

create index gestion_paiement_annee_scolaire_id_85cf36ec
    on gestion_paiement (annee_scolaire_id);

create index gestion_paiement_eleve_id_6fdeb0b7
    on gestion_paiement (eleve_id);

create index gestion_paiement_frais_id_0e7c3b14
    on gestion_paiement (frais_id);

create table gestion_userprofile
(
    id             integer not null
        primary key autoincrement,
    totp_secret    varchar(100),
    is_2fa_enabled bool    not null,
    user_id        bigint  not null
        unique
        references gestion_customuser
            deferrable initially deferred,
    session_key    varchar(40)
);

create table old_gestion_eleve
(
    id             integer      not null
        primary key autoincrement,
    nom            varchar(50)  not null,
    post_nom       varchar(50)  not null,
    prenom         varchar(50),
    sexe           varchar(1)   not null,
    date_naissance date         not null,
    lieu_naissance varchar(100) not null,
    matricule      varchar(20)  not null
        unique,
    annee_scolaire varchar(10)  not null,
    classe_id      bigint       not null
        references gestion_classe
            deferrable initially deferred,
    option_id      bigint
        references gestion_option
            deferrable initially deferred,
    parent_id      bigint
        references gestion_parent
            deferrable initially deferred,
    section_id     bigint       not null
        references gestion_section
            deferrable initially deferred,
    frais_paye     decimal      not null,
    frais_payer    decimal      not null,
    reste_payer    decimal      not null
);

create index gestion_eleve_classe_id_503264c9
    on old_gestion_eleve (classe_id);

create index gestion_eleve_option_id_f524af09
    on old_gestion_eleve (option_id);

create index gestion_eleve_parent_id_7909cdbe
    on old_gestion_eleve (parent_id);

create index gestion_eleve_section_id_4286a51f
    on old_gestion_eleve (section_id);

create table otp_static_staticdevice
(
    id                           integer          not null
        primary key autoincrement,
    name                         varchar(64)      not null,
    confirmed                    bool             not null,
    user_id                      bigint           not null
        references gestion_customuser
            deferrable initially deferred,
    throttling_failure_count     integer unsigned not null,
    throttling_failure_timestamp datetime,
    created_at                   datetime,
    last_used_at                 datetime,
    check ("throttling_failure_count" >= 0)
);

create index otp_static_staticdevice_user_id_7f9cff2b
    on otp_static_staticdevice (user_id);

create table otp_static_statictoken
(
    id        integer     not null
        primary key autoincrement,
    token     varchar(16) not null,
    device_id integer     not null
        references otp_static_staticdevice
            deferrable initially deferred
);

create index otp_static_statictoken_device_id_74b7c7d1
    on otp_static_statictoken (device_id);

create index otp_static_statictoken_token_d0a51866
    on otp_static_statictoken (token);

create table otp_totp_totpdevice
(
    id                           integer           not null
        primary key autoincrement,
    name                         varchar(64)       not null,
    confirmed                    bool              not null,
    key                          varchar(80)       not null,
    step                         smallint unsigned not null,
    t0                           bigint            not null,
    digits                       smallint unsigned not null,
    tolerance                    smallint unsigned not null,
    drift                        smallint          not null,
    last_t                       bigint            not null,
    user_id                      bigint            not null
        references gestion_customuser
            deferrable initially deferred,
    throttling_failure_count     integer unsigned  not null,
    throttling_failure_timestamp datetime,
    created_at                   datetime,
    last_used_at                 datetime,
    check ("digits" >= 0),
    check ("step" >= 0),
    check ("throttling_failure_count" >= 0),
    check ("tolerance" >= 0)
);

create index otp_totp_totpdevice_user_id_0fb18292
    on otp_totp_totpdevice (user_id);

create table sqlite_master
(
    type     TEXT,
    name     TEXT,
    tbl_name TEXT,
    rootpage INT,
    sql      TEXT
);

create table sqlite_sequence
(
    name,
    seq
);


