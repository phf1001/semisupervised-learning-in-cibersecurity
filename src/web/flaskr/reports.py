from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('reports', __name__)

@bp.route('/general_report', methods=['GET'])
def general_report():
    return render_template('reports/general_report.html')