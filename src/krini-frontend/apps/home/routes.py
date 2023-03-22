# -*- coding: utf-8 -*-

# Web dependencies
from apps.home import blueprint
from apps import db
from flask import render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from datetime import datetime
from sqlalchemy.orm import load_only
from apps.home.models import Available_models, Available_co_forests, Available_democratic_cos, Available_tri_trainings
from apps.authentication.models import Users
import json
from werkzeug.utils import secure_filename
from os import path

# DB Models
from apps.home.forms import ReportURLForm, SearchURLForm, NewModelForm, NewCoforestForm
from apps.home.models import (
    Available_instances,
    Candidate_instances,
    Available_models,
    Available_tags,
)

# ML dependencies
import re
import numpy as np
import pandas as pd
import time
from apps.ssl_utils.ml_utils import obtain_model, translate_tag, get_temporary_train_files_directory, get_fv_and_info, get_mock_values_fv


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

    # Get feature vector and extra information

    try:
        fv, fv_extra_information = get_fv_and_info(url)

        # Enviamos el vector al dashboard
        session["messages"] = {
            "fv": fv.tolist(),
            "fv_extra_information": fv_extra_information,
            "url": url,
            "models_ids": models_ids,
        }

        return redirect(url_for("home_blueprint.dashboard"))

    except Exception as e:

        time.sleep(2)
        fv, fv_extra_information = get_mock_values_fv()

        # Enviamos el vector al dashboard
        session["messages"] = {
            "fv": fv.tolist(),
            "fv_extra_information": fv_extra_information,
            "url": url,
            "models_ids": models_ids,
        }

        flash("Ha saltado una excepción. Mostrando resultados de mockeo.")
        return redirect(url_for("home_blueprint.dashboard"))


def translate_array_js(selected):
    if bool(re.search(r"\d", selected)):
        splitted = selected.split(",")
        return [int(elem) for elem in splitted]

    # Get default model control aquí
    return [1]


def get_sum_tags_numeric(predicted_tags):
    """
    Devuelve un array con la suma de los tags numéricos.
    En el index 0 están las votaciones para 0, en el
    1 las votaciones para 1. Devuelve también la
    etiqueta mayoritaria.
    """

    count = [0, 0]

    for tag in predicted_tags:
        if tag == 0:
            count[0] += 1
        elif tag == 1:
            count[1] += 1

    if count[0] <= count[1]:
        return count, 1

    return count, 0


@blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    messages = session.get("messages", None)

    if messages:
        url = messages["url"]
        fv = np.array(messages["fv"])
        selected_models = translate_array_js(messages["models_ids"])

        classifiers_info_tuples = [
            get_model(model_id) for model_id in selected_models]

        model_names = [tupla[0] for tupla in classifiers_info_tuples]
        classifiers = [tupla[1] for tupla in classifiers_info_tuples]
        model_scores = [tupla[2] for tupla in classifiers_info_tuples]

        predicted_tags = [int(cls.predict(fv)[0]) for cls in classifiers]
        count, numeric_class = get_sum_tags_numeric(predicted_tags)

        models_confidence = [
            int(100 * cls.predict_proba(fv)[0][prediction])
            for cls, prediction in zip(classifiers, predicted_tags)
        ]

        # Todo en arrays por orden
        information_to_display = {
            "url": url,
            "fv": list(fv),
            "fv_extra_information": messages["fv_extra_information"],
            "class": translate_tag(numeric_class),
            "colour-list": "white-list",
            # evitar string slicing
            "model_names": make_array_safe(model_names),
            "sum_tags_numeric": make_array_safe(count),
            "predicted_tags_labeled": make_array_safe(
                [translate_tag(tag, True) for tag in predicted_tags]
            ),
            "model_scores": json.dumps(model_scores),
            # sobre 100
            "model_confidence": make_array_safe(models_confidence),
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
    users_reports = Candidate_instances.query.options(
        load_only("reported_by")).all()
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

    
    information_to_display = []

    algorithms = [(Available_co_forests, 'CO-FOREST'), 
                  (Available_tri_trainings, 'TRI-TRAINING'), 
                  (Available_democratic_cos, 'DEMOCRATIC-CO')]
    
    for algorithm in algorithms:
        for model in algorithm[0].query.all():
            information_to_display.append(get_model_dict(model, algorithm[1]))

    return render_template(
        "home/models-administration.html", segment=get_segment(request), information_to_display=information_to_display
    )


def get_parameters(model, algorithm="Unsupervised"):
    if algorithm == "Unsupervised":
        return [], 'red'

    elif algorithm == "CO-FOREST":
        return ["Max features = {}".format(model.max_features), 
                "Thetha = {}".format(model.thetha), 
                "Nº árboles = {}".format(model.n_trees)], 'pink'

    elif algorithm == "TRI-TRAINING":
        return ["Clasificador 1: {}".format(model.cls_one), 
                "Clasificador 2: {}".format(model.cls_two), 
                "Clasificador 3: {}".format(model.cls_three)], 'yellow'

    elif algorithm == "DEMOCRATIC-CO":

        information = cls_to_string_list(model.base_clss)
        information.append("Nº clasificadores = {}".format(model.n_clss))
        return information, 'cyan'


def cls_to_string_list(mutable_clss):
    return ["Clasificador {}: {}".format(i+1, cls) for i, cls in enumerate(mutable_clss)]

def get_username(user_id):
    user = Users.query.filter_by(id=user_id).first()
    
    if user:
        return user.username.upper()
    else:
        return "?"

def get_model_dict(model, algorithm="Unsupervised"):

    params = get_parameters(model, algorithm)
    return {
        "model_name": model.model_name.upper(),
        "model_parameters":  params[0],
        "algorithm": algorithm,
        "badge_colour": params[1],
        "created_by": get_username(model.created_by), 
        "creation_date": model.creation_date,
        "is_default": model.is_default,
        "is_visible": model.is_visible,
        "model_scores": model.model_scores,
        "random_state": model.random_state,
        "model_notes": model.model_notes,
    }


@blueprint.route("/nuevomodelo", methods=["GET", "POST"])
def new_model():

    form = NewCoforestForm()

    if not current_user.is_authenticated:
        return redirect(url_for("authentication_blueprint.login"))

    if "siguiente" in request.form:

        flash("Pulsado siguiente")

        f = form.uploaded_csv.data
        filename = secure_filename(f.filename)
        path_one = get_temporary_train_files_directory()
        file_path = path.join(path_one, filename)
        f.save(file_path)

        return redirect(url_for('home_blueprint.models'))

    return render_template(
            "home/new-model.html", form=form, algorithm='coforest', segment=get_segment(request)
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
    requested_model = Available_models.query.filter_by(
        model_id=model_id).first()

    if requested_model:
        model_name = requested_model.model_name
        model_file = requested_model.file_name
        model_scores = requested_model.model_scores

    else:
        model_name = "Default model"
        model_file = "default.pkl"
        model_scores = (
            Available_models.query.filter_by(
                model_name="Default").first().model_scores
        )

    cls, file_found = obtain_model(model_file)

    if not file_found:
        model_name = "Default model"
        model_scores = (
            Available_models.query.filter_by(
                model_name="Default").first().model_scores
        )

    return model_name, cls, model_scores
