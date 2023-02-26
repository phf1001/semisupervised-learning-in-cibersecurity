from flask import Blueprint, render_template, session


bp = Blueprint('reports', __name__)


@bp.route('/general_report', methods=['GET'])
def general_report():
    messages = session['messages']
    url = messages.get('url')
    return render_template('reports/general_report.html', url=url)
