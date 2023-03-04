from flask import Blueprint, redirect, render_template, request, url_for, session


bp = Blueprint('scanner', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    """Scan a website and checks if phishing"""

    if request.method == 'POST':
        session['messages'] = {'url' : request.form['url']}
        return redirect(url_for('results.general_results'))

    return render_template('scanner/index.html')
