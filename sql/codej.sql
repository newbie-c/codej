CREATE TABLE captchas (
    picture bytea      NOT NULL,
    val     varchar(5) UNIQUE,
    suffix  varchar(7) UNIQUE
);
