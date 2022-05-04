CREATE TABLE articles (
    id serial PRIMARY KEY,
    title     varchar(100),
    slug      varchar(128) UNIQUE,
    suffix    varchar(13)  UNIQUE,
    html      text         DEFAULT NULL,
    summary   varchar(512) DEFAULT NULL,
    meta      varchar(160) DEFAULT NULL,
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
    article_id integer REFERENCES articles(id)
);
