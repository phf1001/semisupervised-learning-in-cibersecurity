from flask import Blueprint, render_template, session


bp = Blueprint('results', __name__)


@bp.route('/general_results', methods=['GET'])
def general_results():
    """Display the general results page."""
    messages = session['messages']
    url = messages.get('url')
    return render_template('results/general_results.html', url=url)
