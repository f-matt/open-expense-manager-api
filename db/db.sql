CREATE USER oem WITH PASSWORD '123456';

CREATE DATABASE oem WITH OWNER oem;

CREATE TABLE users (
    id SERIAL,
    username VARCHAR (50) NOT NULL,
    password VARCHAR (256) NOT NULL,
    PRIMARY KEY (id)
);

INSERT INTO users (username, password)
VALUES ('admin', '$argon2id$v=19$m=65536,t=3,p=4$M1eldHErkjbAaxNed8vbOQ$iXMKR6QzkAae5vBUgOMoOdvUV4BrpQ+mzesNwNS+l1g');
