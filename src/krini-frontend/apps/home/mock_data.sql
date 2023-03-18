DROP TABLE "Available_models" CASCADE;
DROP TABLE "Available_instances" CASCADE;
DROP TABLE "Candidate_instances" CASCADE;
DROP TABLE "Users" CASCADE;

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

UPDATE "Users" SET user_rol = 'admin' WHERE username = 'admin';





INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Default', 'default.pkl', '2020-01-01', true, true, ARRAY [0.6, 0.8, 0.7], 5, 'Default model');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Co-Forest v1.0.0', 'cf_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [0.9, 0.85, 0.8], 5, 'Nothing');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Tri-Training v1.0.0', 'tt_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [0.7, 1.0, 1.0], 5, 'kNN neightbors = 5');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Democratic-co v1.0.0', 'dc_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [1.0, 1.0, 1.0], 5, 'kNN neightbors = 5');

INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss)
VALUES (1, 3, ARRAY ['kNN', 'NB', 'Tree']);

INSERT INTO "Available_co_forests" (model_id, n_trees, thetha, max_features)
VALUES (2, 6, 0.75, 'log2');

INSERT INTO "Available_tri_trainings" (model_id, cls_one, cls_two, cls_three)
VALUES (3, 'kNN', 'NB', 'Tree');

INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss)
VALUES (4, 3, ARRAY ['kNN', 'NB', 'Tree']);