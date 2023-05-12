import psycopg2
import pandas as pd
import os
import hashlib
import binascii


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


def insert_users(connection):
    """
    Insert a dummy admin into the database.

    Args:
        connection (psycopg2.connection): database connection
    """
    try:
        cursor = connection.cursor()
        postgres_insert_query = """ INSERT INTO "Users" (username, email, password, user_first_name, user_last_name, user_rol) VALUES (%s,%s,%s,%s,%s,%s)"""

        records_to_insert = [
            (
                "admin",
                "admin@admin.es",
                hash_pass("admin"),
                "Admin",
                "Admin",
                "admin",
            )
        ]

        for record_to_insert in records_to_insert:
            cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error):
        connection.rollback()
        print("Error while inserting data to table Users")


def last_insert_id(connection, table_name, pk_name):
    """Return the last id inserted in a table.

    Args:
        connection (psycopg2.connection): database connection
        table_name (str): database table name
        pk_name (str): primary key name

    Returns:
        int: last id inserted in the table
    """
    try:
        cursor = connection.cursor()
        sequence = "{table_name}_{pk_name}_seq".format(
            table_name=table_name, pk_name=pk_name
        )
        cursor.execute(
            'SELECT last_value from "{sequence}"'.format(sequence=sequence)
        )
        last_id = cursor.fetchone()[0]
        cursor.close()
        return last_id

    except (Exception, psycopg2.Error):
        connection.rollback()
        print(
            "Error while getting last id from table {table_name}".format(
                table_name=table_name
            )
        )


def insert_models(connection):
    """
    Insert dummy models into the database.

    Args:
        connection (psycopg2.connection): database connection
    """
    try:
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO "Available_models" (created_by, model_name, file_name, creation_date, is_default, is_visible, model_scores, random_state, model_notes, model_algorithm) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        records_to_insert = [
            (
                1,
                "co-forest 100.1.2",
                "co-forest_100-1-2.pkl",
                "2020-01-01",
                False,
                True,
                [0.9, 0.85, 0.8, 0.87, 0.9],
                5,
                "Example model, please not delete.",
                "cf",
            ),
            (
                1,
                "tri-training 1",
                "tri-training_1.pkl",
                "2020-01-01",
                False,
                True,
                [0.7, 1.0, 1.0, 0.92, 1],
                5,
                "Example model, please not delete.",
                "tt",
            ),
            (
                1,
                "democratic-co 1",
                "democratic-co_1.pkl",
                "2020-01-01",
                False,
                True,
                [1.0, 1.0, 1.0, 0.55, 0.5],
                5,
                "Example model, please not delete.",
                "dc",
            ),
        ]

        for record_to_insert in records_to_insert:
            cursor.execute(postgres_insert_query, record_to_insert)

        cursor.close()
        last_id = last_insert_id(connection, "Available_models", "model_id")

        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO "Available_co_forests" (model_id, n_trees, thetha, max_features) VALUES (%s, %s, %s, %s);"""
        record_to_insert = (last_id - 2, 6, 0.75, "log2")
        cursor.execute(postgres_insert_query, record_to_insert)

        postgres_insert_query = """INSERT INTO "Available_tri_trainings" (model_id, cls_one, cls_two, cls_three) VALUES (%s, %s, %s, %s);"""
        record_to_insert = (last_id - 1, "kNN", "NB", "DT")
        cursor.execute(postgres_insert_query, record_to_insert)

        postgres_insert_query = """INSERT INTO "Available_democratic_cos" (model_id, n_clss, base_clss) VALUES (%s, %s, %s);"""
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
    postgres_insert_query = """ INSERT INTO "Available_instances" ("instance_URL", instance_fv, instance_class, colour_list, instance_labels, reviewed_by) VALUES (%s,%s,%s,%s,%s,%s)"""

    df = pd.read_csv("instances_db.csv", delimiter=";")

    for index, row in df.iterrows():
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
            print("Failed to insert {}".format(row["url"]))


if __name__ == "__main__":
    """Entry point for the script."""
    try:
        connection = psycopg2.connect(
            user="dev",
            password="123",
            host="0.0.0.0",
            port="5432",
            database="krini",
        )

        insert_users(connection)
        insert_models(connection)
        insert_instances(connection)

    except (Exception, psycopg2.Error) as e:
        print(str(e))
        print("Error while connecting to PostgreSQL")
        connection.rollback()

    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed")
