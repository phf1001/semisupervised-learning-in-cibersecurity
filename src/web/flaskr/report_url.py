from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.db import get_db
from psycopg2 import IntegrityError

bp = Blueprint('reports', __name__)


@bp.route('/report_url', methods=['GET', 'POST'])
def report_url():
    """
    Report a new URL.
    Stores the corresponding URL in the
    white_list or black_list table.
    """
    
    if request.method == 'POST':
        db = get_db()
        error = None
    
        type_url = request.form['type_url']
        url = request.form['txt_url']

        if not type_url or not url:
            error = 'Data missing.'

        if error is None:
            try:
                cursor = db.cursor()

                if type_url == 'whitelist':

                    row = cursor.execute('SELECT url FROM black_list WHERE url = %s', (url,))
                    row = cursor.fetchone()

                    if row is None:
                        cursor.execute(
                            "INSERT INTO white_list (url) VALUES (%s)",
                            (url,))
                        
                    else:
                        cursor.execute(
                            "INSERT INTO to_check_list (url, previous) VALUES (%s, %s)",
                            (url, 'black'))
                        

                elif type_url == 'blacklist':
                    row = cursor.execute('SELECT url FROM white_list WHERE url = %s', (url,))
                    row = cursor.fetchone()

                    if row is None:
                        cursor.execute(
                            "INSERT INTO black_list (url) VALUES (%s)",
                            (url,))
                        
                    else:
                        cursor.execute(
                            "INSERT INTO to_check_list (url, previous) VALUES (%s, %s)",
                            (url, 'white'))
                    
                db.commit()
                cursor.close()
                flash("URL enviada. Gracias por su colaboración.")
                return redirect(url_for('reports.report_url'))

            except IntegrityError:
                db.rollback()
                cursor.close()
                error = f"URL {url} is already registered."

        flash(error)

    return render_template('reports/report_url.html')
