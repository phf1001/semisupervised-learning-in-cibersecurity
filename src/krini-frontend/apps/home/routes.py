# -*- coding: utf-8 -*-

# Web dependencies
from apps.home import blueprint
from apps import db
from flask import render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from datetime import datetime
from sqlalchemy.orm import load_only
from apps.home.models import Available_models

# DB Models
from apps.home.forms import ReportURLForm, SearchURLForm
from apps.home.models import (
    Available_instances,
    Candidate_instances,
    Available_models,
    Available_tags,
)

# ML dependencies
import re
import numpy as np
import time
from apps.ssl_utils.ml_utils import obtain_model, translate_tag


@blueprint.route("/index", methods=["GET", "POST"])
def index():
    form = SearchURLForm(request.form)

    if not form.validate_on_submit():
        return render_template(
            "home/index.html",
            form=form,
            segment=get_segment(request),
            available_models=Available_models.get_models_ids_and_names_list(),
        )

    url = request.form["url"]
    models = request.form["selected_models"]
    session["messages"] = {"url": url, "models": models}

    return render_template("home/loading.html")


@blueprint.route("/task", methods=["POST", "GET"])
def task():
    messages = session.get("messages", None)
    url = messages["url"]
    models_ids = messages["models"]

    # Generas vector características
    time.sleep(2)
    fv = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 1, 0, 0, 0, 1, 1, 1, 1])

    # Enviamos el vector al dashboard
    session["messages"] = {"fv": fv.tolist(), "url": url, "models_ids": models_ids}
    return redirect(url_for("home_blueprint.dashboard"))


def translate_array_js(selected):
    if bool(re.search(r"\d", selected)):
        splitted = selected.split(",")
        return [int(elem) for elem in splitted]

    # Get default model control aquí
    return []


@blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    messages = session.get("messages", None)

    if messages:
        url = messages["url"]
        fv = np.array(messages["fv"])

        selected_models = translate_array_js(messages["models_ids"])

        classifiers_tuples = [get_model(model_id) for model_id in selected_models]
        classifiers = [cls for cls, model_name in classifiers_tuples]
        model_names = [model_name for cls, model_name in classifiers_tuples]
        predicted_tags = [cls.predict(fv) for cls in classifiers]

        information = "Selected models: {} ".format(selected_models)
        for model_name, predicted_tag in zip(model_names, predicted_tags):
            information += (
                "RESULTS: URL '"
                + url
                + "' is "
                + translate_tag(predicted_tag)
                + " according to '"
                + model_name
                + "' classifier.\n"
            )

        flash(information)

        info_cls = {'tt': [0.98, 0.86, 0.12],
                    'cf': [0.33, 0.82, 0.62],
                    'dc': [0.12, 0.22, 0.32],
                    }
        
        tags_cls = {'tt': 0,
                    'cf': 1,
                    'dc': 1,
                    }

        information_to_display = {
            "url": url,
            "fv": list(fv),
            "class": 'phishing',
            "info_cls": info_cls,
            "tags_cls": tags_cls,
        }

        return render_template("home/dashboard.html", segment=get_segment(request), information_to_display=information_to_display)

    return redirect(url_for("home_blueprint.index"))


@login_required
@blueprint.route("/profile", methods=["GET"])
def profile():
    n_reports_accepted = Available_instances.query.filter_by(
        reported_by=current_user.id
    ).count()

    n_reports_reviewing = 0
    users_reports = Candidate_instances.query.options(load_only("reported_by")).all()
    users_reports = [report.reported_by for report in users_reports]

    for user_report in users_reports:
        if current_user.id in user_report:
            n_reports_reviewing += 1

    return render_template(
        "home/profile.html",
        n_reports_accepted=n_reports_accepted,
        n_reports_reviewing=n_reports_reviewing,
        segment=get_segment(request),
    )


@login_required
@blueprint.route("/instances", methods=["GET"])
def instances():
    return render_template(
        "home/instances-administration.html", segment=get_segment(request)
    )


@login_required
@blueprint.route("/models", methods=["GET"])
def models():
    return render_template(
        "home/models-administration.html", segment=get_segment(request)
    )


@blueprint.route("/report_url", methods=["GET", "POST"])
@login_required
def report_url():
    form = ReportURLForm(request.form)

    if not current_user.is_authenticated:
        return redirect(url_for("authentication_blueprint.login"))

    if "report" in request.form:
        url = request.form["url"]
        type = request.form["type"]

        if type == "blacklist":
            type = Available_tags.black_list
        elif type == "whitelist":
            type = Available_tags.white_list

        date = datetime.now()
        user_ID = current_user.id
        existing_instance = Candidate_instances.query.filter_by(
            instance_URL=url
        ).first()

        if existing_instance:
            existing_instance.reported_by.append(user_ID)
            existing_instance.date.append(date)
            existing_instance.suggestions.append(type)
            db.session.flush()
            db.session.commit()
            flash(
                "URL reported succesfully! Our admins will review it soon."
                + str(existing_instance)
            )

        else:
            db.session.add(
                Candidate_instances(
                    instance_URL=url,
                    reported_by=([user_ID],),
                    date=([date],),
                    suggestions=([type],),
                )
            )
            db.session.commit()
            flash("URL reported succesfully!")

        return render_template(
            "home/report_url.html", form=form, segment=get_segment(request)
        )

    return render_template(
        "home/report_url.html", form=form, segment=get_segment(request)
    )


@blueprint.route("/map", methods=["GET", "POST"])
def map():
    return render_template("home/map.html", segment=get_segment(request))


@blueprint.route("/<template>")
def route_template(template):
    try:
        if not template.endswith(".html"):
            template += ".html"

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template("home/page-404.html"), 404

    except:
        return render_template("home/page-500.html"), 500


def get_segment(request):
    try:
        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except:
        return None


def get_model(model_id):
    requested_model = Available_models.query.filter_by(model_id=model_id).first()

    if requested_model:
        model_name = requested_model.model_name
        model_file = requested_model.file_name

    else:
        model_name = "Default model"
        model_file = "default_model.pkl"

    cls, file_found = obtain_model(model_file)

    if not file_found:
        model_name = "Default model"

    return cls, model_name
