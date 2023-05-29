-- SQL Scripts used during developement. Please, do not use this script in production
-- Note that this tables are out of date and can not reflect the current state of the database
-- Also, models filenames are currently handled by application. This ones will not be found
DROP TABLE "Available_models" CASCADE;
DROP TABLE "Available_co_forests" CASCADE;
DROP TABLE "Available_democratic_cos" CASCADE;
DROP TABLE "Available_tri_trainings" CASCADE;
DROP TABLE "Available_instances" CASCADE;
DROP TABLE "Users" CASCADE;
DROP TABLE "Candidate_instances" CASCADE;
DROP TABLE "Model_is_trained_with" CASCADE;

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

UPDATE "Users" SET user_rol = 'admin' WHERE username = 'admin';

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'https://ubuvirtual.ubu.es/', ARRAY [0,0,0,0,0,0,0,0,0,270,0,0,0,0,0,0,1,1,0], 0, 'white-list', ARRAY ['white-list', 'reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, instance_labels)
VALUES (1, 'https://www.naturaselection.com/es/', ARRAY [0,0,0,0,0,0,0,1,0,591,0,1,0,0,0,1,0,0,1], 0, ARRAY ['reviewed']);

INSERT INTO "Available_instances" (reviewed_by, "instance_URL", instance_fv, instance_class, colour_list, instance_labels)
VALUES (1, 'http:/phishing.super.claro.com.dot.es/', ARRAY [0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,0], 1, 'black-list', ARRAY ['black-list', 'reviewed']);

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes, model_algorithm)
VALUES (1, 'Co-Forest v1.0.0', 'cf_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [0.9, 0.85, 0.8, 0.87, 0.9], 5, 'Nothing', 'cf');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes, model_algorithm)
VALUES (1, 'Tri-Training v1.0.0', 'tt_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [0.7, 1.0, 1.0, 0.92, 1], 5, 'kNN neightbors = 5', 'tt');

INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes, model_algorithm)
VALUES (1, 'Democratic-co v1.0.0', 'dc_v-1-0-0.pkl', '2020-01-01', false, true, ARRAY [1.0, 1.0, 1.0, 0.55, 0.5], 5, 'kNN neightbors = 5', 'dc');

INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss)
VALUES (1, 3, ARRAY ['kNN', 'NB', 'Tree']);

INSERT INTO "Available_co_forests" (model_id, n_trees, thetha, max_features)
VALUES (2, 6, 0.75, 'log2');

INSERT INTO "Available_tri_trainings" (model_id, cls_one, cls_two, cls_three)
VALUES (3, 'kNN', 'NB', 'Tree');

INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss)
VALUES (4, 3, ARRAY ['kNN', 'NB', 'Tree']);