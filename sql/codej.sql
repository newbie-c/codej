CREATE TABLE captchas (
    picture bytea      NOT NULL,
    val     varchar(5) UNIQUE,
    suffix  varchar(7) UNIQUE
);

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

CREATE TABLE albums (
    id        serial        PRIMARY KEY,
    title     varchar(100),
    created   timestamp,
    changed   timestamp,
    suffix    varchar(8)    UNIQUE,
    state     varchar(10),
    volume    integer       DEFAULT 0,
    author_id integer       REFERENCES users(id),
    CONSTRAINT author_title_uni UNIQUE (author_id, title)
);

CREATE TABLE pictures (
    uploaded timestamp,
    picture  bytea,
    filename varchar(128),
    width    integer,
    height   integer,
    format   varchar(6),
    volume   integer,
    suffix   varchar(14)   UNIQUE,
    album_id integer       REFERENCES albums(id)
);

CREATE TABLE friends (
    author_id integer REFERENCES users(id),
    friend_id integer REFERENCES users(id),
    CONSTRAINT author_friend_uni UNIQUE (author_id, friend_id)
);

CREATE TABLE articles (
    id serial PRIMARY KEY,
    title     varchar(100),
    slug      varchar(128) UNIQUE,
    suffix    varchar(13)  UNIQUE,
    html      text         DEFAULT NULL,
    summary   varchar(512) DEFAULT NULL,
    meta      varchar(180) DEFAULT NULL,
    published timestamp    DEFAULT NULL,
    edited    timestamp,
    state     varchar(10),
    commented boolean      DEFAULT TRUE,
    viewed    integer      DEFAULT 0,
    author_id integer REFERENCES users(id)
);

CREATE TABLE paragraphs (
    num        integer DEFAULT 0,
    mdtext     text,
    article_id integer REFERENCES articles(id),
    CONSTRAINT article_num_uni UNIQUE (article_id, num)
);

CREATE TABLE followers (
    author_id integer REFERENCES users(id),
    follower_id integer REFERENCES users(id),
    CONSTRAINT author_follower_uni UNIQUE (author_id, follower_id)
);

CREATE TABLE blockers (
    target_id integer REFERENCES users(id),
    blocker_id integer REFERENCES users(id),
    CONSTRAINT target_blocker_uni UNIQUE (target_id, blocker_id)
);

CREATE TABLE art_likes (
    article_id integer REFERENCES articles(id),
    user_id integer REFERENCES users(id),
    CONSTRAINT article_l_user_uni UNIQUE (article_id, user_id)
);

CREATE TABLE art_dislikes (
    article_id integer REFERENCES articles(id),
    user_id integer REFERENCES users(id),
    CONSTRAINT article_d_user_uni UNIQUE (article_id, user_id)
);
