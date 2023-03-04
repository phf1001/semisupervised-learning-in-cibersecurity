# -*- coding: utf-8 -*-
from apps.home import blueprint
from apps import db
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from datetime import datetime

from apps.home.forms import ReportURLForm, SearchURLForm
from apps.home.models import Reported_URL, Repeated_URL

@blueprint.route('/report_url', methods=['GET', 'POST'])
@login_required
def report_url():

    form = ReportURLForm(request.form)

    if not current_user.is_authenticated:
        return redirect(url_for('authentication_blueprint.login'))

    if 'report' in request.form:
        url = request.form['url']
        type = request.form['type']
        date = datetime.now()
        user_ID = current_user.id
        existing_url = Reported_URL.query.filter_by(url=url).first()

        if existing_url:
            previous_type = existing_url.type

            if previous_type != type:
                repeated_url = Repeated_URL.query.filter_by(url=url).first()

                if not repeated_url:
                    db.session.add(Repeated_URL(url=url, previous_type=previous_type,
                               date=date, user_id=user_ID))
                    db.session.commit()
                    flash('URL reported succesfully! Our admins will review it soon.')

        else:
            db.session.add(Reported_URL(
                url=url, type=type, date=date, user_id=user_ID))
            db.session.commit()
            flash('URL reported succesfully!')

        return redirect(url_for('home_blueprint.report_url'))

    return render_template('home/report_url.html', form=form)


@blueprint.route('/index', methods=['GET', 'POST'])
def index():

    form = SearchURLForm(request.form)

    if 'search' in request.form:
        url = request.form['url']
        flash(url)
        return redirect(url_for('home_blueprint.dashboard'))

    return render_template('home/index.html', form=form)


@blueprint.route('/map', methods=['GET', 'POST'])
def map():
    return render_template('home/map.html')


@blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('home/dashboard.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
