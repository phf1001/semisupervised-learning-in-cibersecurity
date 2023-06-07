import psycopg2
import pandas as pd
import os
import hashlib
import binascii
import time
from datetime import datetime

DB_USER = os.getenv("POSTGRES_USER", "dev")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
DB_HOST = os.getenv("SQL_HOST", "db")
DB_PORT = os.getenv("SQL_PORT", "5432")
DB_DATABASE = os.getenv("POSTGRES_DB", "krini")

MODEL_DESCRIPTION = "Example model, please not delete."


def hash_pass(password):
    """
    Hash a password for storing. Return bytes.

    Args:
        password (str): password to hash

    Returns:
        bytes: encoded password
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode("ascii")
    pwdhash = hashlib.pbkdf2_hmac(
        "sha512", password.encode("utf-8"), salt, 100000
    )
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash


def last_insert_id(connection, table_name, pk_name):
    """Return the last id inserted in a table.
    SQLi safe, not user input is introduced.

    Args:
        connection (psycopg2.connection): database connection
        table_name (str): database table name
        pk_name (str): primary key name

    Returns:
        int: last id inserted in the table
    """
    try:
        cursor = connection.cursor()
        sequence = f"{table_name}_{pk_name}_seq"
        # skipcq: BAN-B608
        cursor.execute(f'SELECT last_value from "{sequence}"')
        last_id = cursor.fetchone()[0]
        cursor.close()
        return last_id

    except (Exception, psycopg2.Error):
        connection.rollback()
        raise psycopg2.Error(
            f"Error while getting last id from table {table_name}"
        )


def insert_users(connection):
    """
    Insert a dummy admin into the database.

    Args:
        connection (psycopg2.connection): database connection
    """
    try:
        cursor = connection.cursor()
        postgres_insert_query = """ 
        INSERT INTO "Users" 
            (username, email, password, user_first_name, user_last_name, user_rol) 
        VALUES (%s,%s,%s,%s,%s,%s)
        """

        records_to_insert = [
            (
                "admin",
                "admin@admin.es",
                hash_pass("admin"),
                "Admin",
                "Admin",
                "admin",
            ),
            (
                "user",
                "user@user.es",
                hash_pass("user"),
                "User",
                "User",
                "standard",
            ),
        ]

        for record_to_insert in records_to_insert:
            cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error):
        connection.rollback()
        print("Error while inserting data to table Users")


def insert_models(connection):
    """
    Insert dummy models into the database.

    Args:
        connection (psycopg2.connection): database connection
    """
    try:
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO "Available_models" 
                (created_by, model_name, file_name, creation_date, is_default, 
                is_visible, model_scores, random_state, model_notes, model_algorithm) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        records_to_insert = [
            (
                1,
                "co-forest 1",
                "co-forest_1.pkl",
                "2023-05-05",
                True,
                True,
                [0.8989, 0.8421, 0.9796, 0.9057, 0.9261],
                5,
                MODEL_DESCRIPTION,
                "cf",
            ),
            (
                1,
                "tri-training 1",
                "tri-training_1.pkl",
                "2023-05-05",
                False,
                True,
                [0.8989, 0.8824, 0.9184, 0.9, 0.9648],
                5,
                MODEL_DESCRIPTION,
                "tt",
            ),
            (
                1,
                "democratic-co 1",
                "democratic-co_1.pkl",
                "2023-05-05",
                False,
                True,
                [0.949, 0.9231, 0.9796, 0.9505, 0.9382],
                5,
                MODEL_DESCRIPTION,
                "dc",
            ),
        ]

        for record_to_insert in records_to_insert:
            cursor.execute(postgres_insert_query, record_to_insert)

        cursor.close()
        last_id = last_insert_id(connection, "Available_models", "model_id")

        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO "Available_co_forests" 
                                    (model_id, n_trees, thetha, max_features) 
                                    VALUES (%s, %s, %s, %s);"""
        record_to_insert = (last_id - 2, 6, 0.75, "log2")
        cursor.execute(postgres_insert_query, record_to_insert)

        postgres_insert_query = """INSERT INTO "Available_tri_trainings" 
                                    (model_id, cls_one, cls_two, cls_three) 
                                    VALUES (%s, %s, %s, %s);"""
        record_to_insert = (last_id - 1, "kNN", "NB", "DT")
        cursor.execute(postgres_insert_query, record_to_insert)

        postgres_insert_query = """INSERT INTO "Available_democratic_cos" 
                                    (model_id, n_clss, base_clss) 
                                    VALUES (%s, %s, %s);"""
        record_to_insert = (last_id, 3, ["kNN", "NB", "DT"])
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error):
        connection.rollback()
        print("Error while inserting data to table Available_models")


def insert_instances(connection):
    """
    Insert dummy instances into the database.

    Args:
        connection (psycopg2.connection): database connection
    """
    cursor = connection.cursor()
    postgres_insert_query = """ INSERT INTO "Available_instances" 
                                    ("instance_URL", instance_fv, 
                                    instance_class, colour_list, 
                                    instance_labels, reviewed_by) 
                                    VALUES (%s,%s,%s,%s,%s,%s)"""

    df = pd.read_csv("instances_db.csv", delimiter=";")

    for _, row in df.iterrows():
        try:
            tag = int(row["tag"])
            fv = row["fv"].replace('"', "'")
            fv = fv.replace("[", "{")
            fv = fv.replace("]", "}")

            if tag == 1:
                colour = "black-list"
                labels = ["black-list", "reviewed"]

            else:
                colour = "white-list"
                labels = ["white-list", "reviewed"]

            record_to_insert = (
                row["url"],
                fv,
                tag,
                colour,
                labels,
                1,
            )
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()

        except (Exception, psycopg2.Error):
            connection.rollback()
            print(f"Failed to insert {row['url']}")


def insert_reports(connection):
    """
    Insert dummy reports into the database.

    Args:
        connection (psycopg2.connection): database connection
    """
    try:
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO "Candidate_instances" 
                (date_reported, instance_id, user_id, suggestions) 
                VALUES (%s, %s, %s, %s);"""

        records_to_insert = [
            (
                datetime.now(),
                1,
                1,
                "suggestion-white-list",
            ),
            (
                datetime.now(),
                10,
                2,
                "suggestion-white-list",
            ),
            (
                datetime.now(),
                70,
                2,
                "suggestion-black-list",
            ),
            (
                datetime.now(),
                80,
                2,
                "suggestion-black-list",
            ),
            (
                datetime.now(),
                83,
                2,
                "suggestion-legitimate",
            ),
            (
                datetime.now(),
                39,
                2,
                "suggestion-phishing",
            ),
        ]

        for record_to_insert in records_to_insert:
            cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error) as e:
        print(str(e))
        connection.rollback()
        print("Error while inserting data to table Candidate_instances")


def insert_models_trained_with(connection):
    """
    Insert models trained with dummy instances into the relation database.

    Args:
        connection (psycopg2.connection): database connection
    """
    try:
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO "Model_is_trained_with" 
                (instance_id, model_id) 
                VALUES (%s, %s);"""

        last_instance = last_insert_id(
            connection, "Available_instances", "instance_id"
        )

        for model_id in (1, 2, 3):
            for instance_id in range(1, last_instance + 1):
                record_to_insert = (instance_id, model_id)
                cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error) as e:
        print(str(e))
        connection.rollback()
        print("Error while inserting data to table Model_is_trained_with")


def start():
    """Inserts data into the database."""
    tries = 0

    while tries < 5:
        try:
            models_inserted = False
            instances_inserted = False
            users_inserted = False

            connection = None
            connection = psycopg2.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_DATABASE,
            )

            if last_insert_id(connection, "Users", "id") in [0, 1]:
                insert_users(connection)
                users_inserted = True

            if last_insert_id(connection, "Available_models", "model_id") in [
                0,
                1,
            ]:
                insert_models(connection)
                models_inserted = True

            if last_insert_id(
                connection, "Available_instances", "instance_id"
            ) in [0, 1]:
                insert_instances(connection)
                instances_inserted = True

            if users_inserted and instances_inserted:
                insert_reports(connection)

            if models_inserted and instances_inserted:
                insert_models_trained_with(connection)

            break

        except (Exception, psycopg2.Error) as e:
            print(str(e))
            tries += 1
            time.sleep(5)
            if connection:
                connection.rollback()

    if connection:
        connection.close()
        print("PostgreSQL connection is closed")


if __name__ == "__main__":
    start()
