import click
from flask import current_app, g
import psycopg2


def get_db():
    """
    Connect to the application's 
    configured database.

    Returns
    -------
    database connection.
    """
    if 'db' not in g:
        g.db = psycopg2.connect(
                            database="white_fountain",
                            user="dev",
                            password="123",
                            host="127.0.0.1"
                        )

    return g.db


def close_db(e=None):
    """Close the database connection."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

    if e is not None:
        print(e)


def init_db():
    """Creates new tables if requiered."""
    db = get_db()
    cursor = db.cursor()

    with current_app.open_resource('schema.sql') as f:
        cursor.execute(f.read().decode('utf8'))
        db.commit()
        cursor.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
