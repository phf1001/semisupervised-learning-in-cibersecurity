# -*- coding: utf-8 -*-

# Web dependencies
from apps.home import blueprint
from apps import db
from flask import render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from datetime import datetime

# DB Models
from apps.home.forms import ReportURLForm, SearchURLForm
from apps.home.models import Reported_URL, Repeated_URL

# ML dependencies
import pickle
import numpy as np
import time
from apps.ssl_utils.ml_utils import obtain_model


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

        return redirect(url_for('home_blueprint.report_url'), segment=get_segment(request))

    return render_template('home/report_url.html', form=form, segment=get_segment(request))


@blueprint.route('/index', methods=['GET', 'POST'])
def index():

    form = SearchURLForm(request.form)

    if 'search' in request.form:
        url = request.form['url']
        return render_template ("home/loading.html", url=url)

    return render_template('home/index.html', form=form, segment=get_segment(request))


@blueprint.route('/task/<url>', methods=['POST', 'GET'])
def task(url):

    #Generas vector características
    time.sleep(5)
    fv = np.array([0,0,0,0,0,0,0,0,0,8,0,1,0,0,0,1,1,1,1])


    #Enviamos el vector al dashboard
    session['messages'] = {"fv": fv.tolist(), "url": url, "model": 'dc_v1'}
    return redirect(url_for('home_blueprint.dashboard'))


@blueprint.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    messages = session.get('messages', None)
    url = messages['url']
    fv = np.array(messages['fv'])
    model = messages['model']

    cls = obtain_model(model)
    predicted_tag = cls.predict(fv)

    if messages:
        flash(predicted_tag)

    return render_template('home/dashboard.html', segment=get_segment(request))


@blueprint.route('/map', methods=['GET', 'POST'])
def map():
    return render_template('home/map.html', segment=get_segment(request))


@blueprint.route('/<template>')
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
