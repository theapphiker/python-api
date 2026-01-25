CREATE DATABASE fastapi;

CREATE SCHEMA dev;

CREATE TABLE dev.posts
(id SERIAL PRIMARY KEY,
title VARCHAR NOT NULL,
content VARCHAR NOT NULL,
published BOOLEAN DEFAULT TRUE NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE USER fastapi_user WITH PASSWORD 'secretpassword';

GRANT CONNECT ON DATABASE fastapi TO fastapi_user;

GRANT USAGE ON SCHEMA dev TO fastapi_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dev TO fastapi_user;

CREATE TABLE dev.users
(email VARCHAR(255) NOT NULL UNIQUE,
password VARCHAR(255) NOT NULL,
id SERIAL PRIMARY KEY,
created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


BEGIN;
ALTER TABLE dev.posts ADD COLUMN user_id INT NOT NULL;
ALTER TABLE dev.posts ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES dev.users (id) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;


'''
Votes model
post_id and user_id are both foreign keys

post_id and user_id must be unique combinations in the table so primary key that spans both columns

users must also be able to delete posts
'''

CREATE TABLE dev.votes (
    post_id INT NOT NULL REFERENCES dev.posts(id),
    user_id INT NOT NULL REFERENCES dev.users(id),
    PRIMARY KEY (post_id, user_id)
);