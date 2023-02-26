from flask import Blueprint, redirect, render_template, request, url_for, session

bp = Blueprint('scanner', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        session['messages'] = {'url' : request.form['url']}
        return redirect(url_for('reports.general_report'))

    return render_template('scanner/index.html')
