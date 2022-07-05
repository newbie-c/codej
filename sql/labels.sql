CREATE TABLE labels (
    id serial PRIMARY KEY,
    label varchar(32) UNIQUE
);

CREATE TABLE als (
    article_id integer REFERENCES articles(id),
    label_id integer REFERENCES labels(id),
    CONSTRAINT art_label_uni UNIQUE (article_id, label_id)
);
