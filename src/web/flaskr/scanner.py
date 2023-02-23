from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('scanner', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        print(request.form["url"])
        return redirect(url_for('reports.general_report'))

    return render_template('scanner/index.html')