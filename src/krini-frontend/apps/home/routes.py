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
import json

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

    fv_extra_information = {"f1": 322, 
                            "f2": '@',
                            "f3": 56,
                            "f4": 'login',
                            "f5": '.cat', #TDL extra encontrado
                            "f6": 'No',
                            "f7": 'Google',
                            "f8": 'No',
                            "f9": 'asterisco',
                            "f10": '5',
                            "f11": 'No', #vacia
                            "f12": 2,
                            "f13": 3,
                            "f14": 4,
                            "f15": 5,
                            "f16": 'No',
                            "f17": 'Natura',
                            "f18": 'Natura',
                            "f19": 'No'
                            }

    # Enviamos el vector al dashboard
    session["messages"] = {
        "fv": fv.tolist(),
        "fv_extra_information": fv_extra_information,
        "url": url,
        "models_ids": models_ids,
    }
    return redirect(url_for("home_blueprint.dashboard"))


def translate_array_js(selected):
    if bool(re.search(r"\d", selected)):
        splitted = selected.split(",")
        return [int(elem) for elem in splitted]

    # Get default model control aquí
    return [1]


@blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    messages = session.get("messages", None)

    if messages:
        url = messages["url"]
        fv = np.array(messages["fv"])
        selected_models = translate_array_js(messages["models_ids"])

        classifiers_info_tuples = [get_model(model_id) for model_id in selected_models]

        model_names = [tupla[0] for tupla in classifiers_info_tuples]
        classifiers = [tupla[1] for tupla in classifiers_info_tuples]
        model_scores = [tupla[2] for tupla in classifiers_info_tuples]

        predicted_tags = [int(cls.predict(fv)[0]) for cls in classifiers]
        count = np.bincount(predicted_tags)
        models_confidence = [
            int(100 * cls.predict_proba(fv)[0][prediction])
            for cls, prediction in zip(classifiers, predicted_tags)
        ]

        # Todo en arrays por orden
        information_to_display = {
            "url": url,
            "fv": list(fv),
            "fv_extra_information": messages["fv_extra_information"],
            "class": translate_tag(count.argmax()),
            "colour-list": "white-list",
            "model_names": make_array_safe(model_names),  # evitar string slicing
            "sum_tags_numeric": make_array_safe([int(count[0]), int(count[1])]),
            "predicted_tags_labeled": make_array_safe(
                [translate_tag(tag, True) for tag in predicted_tags]
            ),
            "model_scores": json.dumps(model_scores),
            "model_confidence": make_array_safe(models_confidence),  # sobre 100
        }

        return render_template(
            "home/dashboard.html",
            segment=get_segment(request),
            information_to_display=information_to_display,
        )

    return redirect(url_for("home_blueprint.index"))


def make_array_safe(vector):
    return json.loads(json.dumps(vector))


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
        model_scores = requested_model.model_scores

    else:
        model_name = "Default model"
        model_file = "default.pkl"
        model_scores = (
            Available_models.query.filter_by(model_name="Default").first().model_scores
        )

    cls, file_found = obtain_model(model_file)

    if not file_found:
        model_name = "Default model"
        model_scores = (
            Available_models.query.filter_by(model_name="Default").first().model_scores
        )

    return model_name, cls, model_scores
