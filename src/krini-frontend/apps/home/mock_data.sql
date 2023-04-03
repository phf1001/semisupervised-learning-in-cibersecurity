DROP TABLE "Available_models" CASCADE;
DROP TABLE "Available_co_forests" CASCADE;
DROP TABLE "Available_democratic_cos" CASCADE;
DROP TABLE "Available_tri_trainings" CASCADE;


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


-- INSERT INTO "Users" (username, email, password, user_first_name, user_last_name, user_rol)
-- VALUES ('a', 'a@gmail.com', 'a', 'Nombre', 'Apellidos', 'standard');

-- INSERT INTO "Users" (username, email, password, user_first_name, user_last_name, user_rol)
-- VALUES ('ams', 'ams@gmail.com', 'ams', 'Nombre', 'Apellidos', 'admin');

-- INSERT INTO "Reported_URLs" (url, type, date, user_id)
-- VALUES ('https://www.youtube.com/', 'white-list', '2020-01-01', 1);

-- INSERT INTO "Reported_URLs" (url, type, date, user_id)
-- VALUES ('https://www.youtube.es/', 'white-list', '2020-01-01', 2);

-- INSERT INTO "Reported_URLs" (url, type, date, user_id)
-- VALUES ('https://www.youtube.fr/', 'white-list', '2020-01-01', 2);


UPDATE "Users" SET user_rol = 'admin' WHERE username = 'admin';



INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'https://ubuvirtual.ubu.es/', ARRAY [0,0,0,0,0,0,0,0,0,270,0,0,0,0,0,0,1,1,0], 0, 'white-list', ARRAY ['white-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, instance_labels)
VALUES (1, 'https://www.naturaselection.com/es/', ARRAY [0,0,0,0,0,0,0,1,0,591,0,1,0,0,0,1,0,0,1], 0, ARRAY ['reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'http:/phishing.super.cantoso.es/', ARRAY [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0], 1, 'black-list', ARRAY ['black-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class)
VALUES (1, 'http://phishing.discreto.net/', ARRAY [0,1,0,0,0,0,0,1,0,29,0,1,0,0,1,0,1,1,0], 1);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'https://ubuvirtual.ubu.es/2', ARRAY [0,0,0,0,0,0,0,0,0,270,0,0,0,0,0,0,1,1,0], 0, 'white-list', ARRAY ['white-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, instance_labels)
VALUES (1, 'https://www.naturaselection.com/es/2', ARRAY [0,0,0,0,0,0,0,1,0,591,0,1,0,0,0,1,0,0,1], 0, ARRAY ['reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'http:/phishing.super.cantoso.es/2', ARRAY [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0], 1, 'black-list', ARRAY ['black-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class)
VALUES (1, 'http://phishing.discreto.net/2', ARRAY [0,1,0,0,0,0,0,1,0,29,0,1,0,0,1,0,1,1,0], 1);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'https://ubuvirtual.ubu.es/3', ARRAY [0,0,0,0,0,0,0,0,0,270,0,0,0,0,0,0,1,1,0], 0, 'white-list', ARRAY ['white-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, instance_labels)
VALUES (1, 'https://www.naturaselection.com/es/3', ARRAY [0,0,0,0,0,0,0,1,0,591,0,1,0,0,0,1,0,0,1], 0, ARRAY ['reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'http:/phishing.super.cantoso.es/3', ARRAY [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0], 1, 'black-list', ARRAY ['black-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class)
VALUES (1, 'http://phishing.discreto.net/3', ARRAY [0,1,0,0,0,0,0,1,0,29,0,1,0,0,1,0,1,1,0], 1);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'https://ubuvirtual.ubu.es/4', ARRAY [0,0,0,0,0,0,0,0,0,270,0,0,0,0,0,0,1,1,0], 0, 'white-list', ARRAY ['white-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, instance_labels)
VALUES (1, 'https://www.naturaselection.com/es/4', ARRAY [0,0,0,0,0,0,0,1,0,591,0,1,0,0,0,1,0,0,1], 0, ARRAY ['reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'http:/phishing.super.cantoso.es/4', ARRAY [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0], 1, 'black-list', ARRAY ['black-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class)
VALUES (1, 'http://phishing.discreto.net/4', ARRAY [0,1,0,0,0,0,0,1,0,29,0,1,0,0,1,0,1,1,0], 1);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'https://ubuvirtual.ubu.es/5', ARRAY [0,0,0,0,0,0,0,0,0,270,0,0,0,0,0,0,1,1,0], 0, 'white-list', ARRAY ['white-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, instance_labels)
VALUES (1, 'https://www.naturaselection.com/es/5', ARRAY [0,0,0,0,0,0,0,1,0,591,0,1,0,0,0,1,0,0,1], 0, ARRAY ['reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'http:/phishing.super.cantoso.es/5', ARRAY [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0], 1, 'black-list', ARRAY ['black-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class)
VALUES (1, 'http://phishing.discreto.net/5', ARRAY [0,1,0,0,0,0,0,1,0,29,0,1,0,0,1,0,1,1,0], 1);



INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Default', 'default.pkl', '2020-01-01', true, true, ARRAY [0.6, 0.8, 0.7, 0.9, 0.5], 5, 'Default model');

INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss)
VALUES (1, 3, ARRAY ['kNN', 'NB', 'Tree']);


INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Co-Forest v1.0.0', 'cf_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [0.9, 0.85, 0.8, 0.87, 0.9], 5, 'Nothing');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Tri-Training v1.0.0', 'tt_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [0.7, 1.0, 1.0, 0.92, 1], 5, 'kNN neightbors = 5');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes)
VALUES (1, 'Democratic-co v1.0.0', 'dc_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [1.0, 1.0, 1.0, 0.55, 0.5], 5, 'kNN neightbors = 5');


INSERT INTO "Available_co_forests" (model_id, n_trees, thetha, max_features)
VALUES (2, 6, 0.75, 'log2');

INSERT INTO "Available_tri_trainings" (model_id, cls_one, cls_two, cls_three)
VALUES (3, 'kNN', 'NB', 'Tree');

INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss)
VALUES (4, 3, ARRAY ['kNN', 'NB', 'Tree']);