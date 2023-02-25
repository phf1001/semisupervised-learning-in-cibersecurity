import click
from flask import current_app, g
import psycopg2

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
                            database="white_fountain",
                            user="dev",
                            password="123",
                            host="127.0.0.1"
                        )

    return g.db

def close_db():
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
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
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
