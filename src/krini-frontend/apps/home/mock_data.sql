DROP TABLE "Available_models";
DROP TABLE "Repeated_URLs";
DROP TABLE "Reported_URLs";
DROP TABLE "Users";

DROP SEQUENCE Available_models_id_seq;
DROP SEQUENCE Repeated_URLs_id_seq;
DROP SEQUENCE Reported_URLs_id_seq;
DROP SEQUENCE Users_id_seq;

CREATE SEQUENCE Available_models_id_seq;

CREATE TABLE "Available_models" (
    model_id INTEGER PRIMARY KEY DEFAULT nextval('Available_models_id_seq'),
    model_name TEXT UNIQUE NOT NULL,
    file_name TEXT UNIQUE NOT NULL
);

ALTER SEQUENCE Available_models_id_seq OWNED BY "Available_models".model_id; 


INSERT INTO "Users" (username, email, password, user_first_name, user_last_name, user_rol)
VALUES ('a', 'a@gmail.com', 'a', 'Nombre', 'Apellidos', 'standard');

INSERT INTO "Users" (username, email, password, user_first_name, user_last_name, user_rol)
VALUES ('ams', 'ams@gmail.com', 'ams', 'Nombre', 'Apellidos', 'admin');

INSERT INTO "Reported_URLs" (url, type, date, user_id)
VALUES ('https://www.youtube.com/', 'white-list', '2020-01-01', 1);

INSERT INTO "Reported_URLs" (url, type, date, user_id)
VALUES ('https://www.youtube.es/', 'white-list', '2020-01-01', 2);

INSERT INTO "Reported_URLs" (url, type, date, user_id)
VALUES ('https://www.youtube.fr/', 'white-list', '2020-01-01', 2);