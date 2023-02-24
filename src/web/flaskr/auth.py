import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flaskr.db import get_db
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:

            try:
                cursor = db.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, generate_password_hash(password)))
                db.commit()
                cursor.close()

            except psycopg2.IntegrityError:
                error = f"User {username} is already registered."

            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        cursor = db.cursor()

        user = cursor.execute('SELECT * FROM users WHERE username = %s', [
            username,
        ])

        user = cursor.fetchone()
        cursor.close()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user[2], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE userID = %s', (user_id, ))
        g.user = cursor.fetchone()
        cursor.close()


def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
