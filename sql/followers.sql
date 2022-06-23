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
