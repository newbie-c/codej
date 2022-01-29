CREATE TABLE permissions (
    permission varchar(32)  NOT NULL,
    name       varchar(32),
    init       boolean      NOT NULL
);

CREATE TABLE users (
    id             serial         PRIMARY KEY,
    username       varchar(16)    UNIQUE NOT NULL,
    registered     timestamp,
    last_visit     timestamp,
    password_hash  varchar(128),
    permissions    varchar(32)[],
    sessions       varchar(13)[],
    description    varchar(500)   DEFAULT NULL,
    last_published timestamp      DEFAULT NULL
);

CREATE TABLE accounts (
    id        serial        PRIMARY KEY,
    address   varchar(128)  UNIQUE,
    swap      varchar(128),
    ava_hash  varchar(32),
    requested timestamp,
    user_id   integer       REFERENCES users(id) UNIQUE
);
