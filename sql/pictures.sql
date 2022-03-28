CREATE TABLE albums (
    id        serial        PRIMARY KEY,
    title     varchar(100),
    created   timestamp,
    changed   timestamp,
    suffix    varchar(8)    UNIQUE,
    state     varchar(8),
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
