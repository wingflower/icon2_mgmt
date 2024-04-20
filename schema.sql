create database `iconfra_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */

create table api_keys
(
    id             int auto_increment
        primary key,
    access_key     varchar(64)                                                     not null,
    secret_key     varchar(64)                                                     not null,
    memo           varchar(50)                                                     null,
    status         enum ('active', 'stopped', 'deleted') default 'active'          not null,
    is_whitelisted tinyint(1)                            default 0                 null,
    user_id        int                                                             not null,
    updated_at     datetime                              default CURRENT_TIMESTAMP null,
    created_at     datetime                              default CURRENT_TIMESTAMP null
);

create index api_keys_access_key_index
    on api_keys (access_key);

create table api_whitelists
(
    id         int auto_increment
        primary key,
    ip_addr    varchar(64)                        not null,
    api_key_id int                                not null,
    updated_at datetime default CURRENT_TIMESTAMP not null,
    created_at datetime default CURRENT_TIMESTAMP not null,
    constraint api_whitelists_api_keys_id_fk
        foreign key (api_key_id) references api_keys (id)
            on delete cascade
);

create table check_urls
(
    id            int auto_increment
        primary key,
    name          varchar(128)                                         not null,
    path          varchar(128)                                         not null,
    endpoint      varchar(128)                                         not null,
    endpoint_name varchar(64)                                          not null,
    term          int                        default 60                not null,
    access_type   enum ('public', 'private') default 'public'          null,
    created_at    datetime                   default CURRENT_TIMESTAMP null,
    updated_at    datetime                   default CURRENT_TIMESTAMP null,
    memo          varchar(128)                                         null
);

create table connections
(
    id              int auto_increment
        primary key,
    name            varchar(64)                        null,
    path            varchar(128)                       null,
    updated_at      datetime default CURRENT_TIMESTAMP null,
    created_at      datetime default CURRENT_TIMESTAMP null,
    pw              varchar(128)                       null,
    memo            varchar(128)                       null,
    connection_type enum ('vm', 'aws', 'gcp')          null
);

create table endpoint_history
(
    id                int auto_increment
        primary key,
    state             enum ('running', 'stopped') default 'stopped'         not null,
    checked_url       varchar(256)                                          not null,
    checked_at        datetime                                              not null,
    checked_set_count int                                                   not null,
    response_time     float                                                 not null,
    region            varchar(32)                                           null,
    url_id            int                                                   not null,
    memo              varchar(128)                                          null,
    updated_at        datetime                    default CURRENT_TIMESTAMP null,
    created_at        datetime                    default CURRENT_TIMESTAMP null,
    constraint endpoint_history_ibfk_1
        foreign key (url_id) references check_urls (id)
);

create table icon_networks
(
    id            int auto_increment
        primary key,
    name          varchar(64)                                     not null,
    connection_id int                                             not null,
    tag_env       varchar(32)                                     not null,
    tag_role      varchar(32)                                     not null,
    updated_at    datetime              default CURRENT_TIMESTAMP null,
    created_at    datetime              default CURRENT_TIMESTAMP null,
    memo          varchar(128)                                    null,
    network_type  enum ('main', 'test') default 'test'            not null,
    endpoint      varchar(128)                                    null,
    nid           int                                             null,
    constraint icon_networks_ibfk_1
        foreign key (connection_id) references connections (id)
            on delete cascade
);

create table icon_services
(
    id          int auto_increment
        primary key,
    name        varchar(64)                                          not null,
    dns         varchar(128)                                         null,
    updated_at  datetime                   default CURRENT_TIMESTAMP null,
    created_at  datetime                   default CURRENT_TIMESTAMP null,
    access_type enum ('public', 'private') default 'public'          null,
    memo        varchar(128)                                         null
);

create table machines
(
    id          int auto_increment
        primary key,
    name        varchar(128)                       not null,
    network_id  int                                null,
    region      varchar(64)                        not null,
    updated_at  datetime default CURRENT_TIMESTAMP null,
    created_at  datetime default CURRENT_TIMESTAMP null,
    instance_id varchar(128)                       null,
    ip          varchar(45)                        not null,
    service_id  int                                null,
    memo        varchar(128)                       null,
    constraint machines_ibfk_1
        foreign key (network_id) references icon_networks (id),
    constraint machines_ibfk_2
        foreign key (service_id) references icon_services (id)
);

create table icon_node_keys
(
    id         int auto_increment
        primary key,
    name       varchar(128)                       not null,
    network_id int                                not null,
    machine_id int                                null,
    updated_at datetime default CURRENT_TIMESTAMP null,
    created_at datetime default CURRENT_TIMESTAMP null,
    memo       varchar(128)                       null,
    path       varchar(256)                       null,
    passwd     varchar(64)                        null,
    pk         varchar(128)                       null,
    constraint icon_node_keys_ibfk_1
        foreign key (network_id) references icon_networks (id),
    constraint icon_node_keys_ibfk_2
        foreign key (machine_id) references machines (id)
);

create index machine_id
    on icon_node_keys (machine_id);

create index network_id
    on icon_node_keys (network_id);

create table users
(
    id              int auto_increment
        primary key,
    status          enum ('active', 'deleted', 'blocked') default 'active'          not null,
    email           varchar(255)                                                    null,
    pw              varchar(2000)                                                   null,
    name            varchar(255)                                                    null,
    phone_number    varchar(20)                                                     null,
    profile_img     varchar(1000)                                                   null,
    sns_type        enum ('FB', 'G', 'K', 'Email')                                  null,
    marketing_agree tinyint(1)                            default 0                 null,
    updated_at      datetime                              default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    created_at      datetime                              default CURRENT_TIMESTAMP not null,
    level           enum ('s', 'a', 'b', 'c', 'd')        default 'd'               null,
    memo            varchar(128)                                                    null,
    service_id      int                                                             null,
    constraint users_ibfk_1
        foreign key (service_id) references icon_services (id)
);

