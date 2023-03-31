#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/03/30 21:06:45
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

# Web dependencies
from sqlalchemy import exc
from apps.home import blueprint
from apps import db
from flask import render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from jinja2 import TemplateNotFound
from datetime import datetime
from sqlalchemy.orm import load_only
from apps.home.models import (
    Available_models,
    Available_co_forests,
    Available_democratic_cos,
    Available_tri_trainings,
)
import json

# DB Models
from apps.home.forms import ReportURLForm, SearchURLForm, NewModelForm
from apps.home.models import (
    Available_instances,
    Candidate_instances,
    Available_models,
    Available_tags,
)

# ML dependencies
import numpy as np
import time
from sklearn.model_selection import train_test_split
from apps.ssl_utils.ml_utils import (
    translate_tag,
    get_fv_and_info,
    get_mock_values_fv,
    get_co_forest,
    get_array_scores,
)

from apps.ssl_utils.ml_utils import get_temporary_download_directory
from apps.home.utils import *
logger = get_logger("krini-frontend")

@blueprint.route("/index", methods=["GET", "POST"])
def index():
    form = SearchURLForm(request.form)

    if not form.validate_on_submit():
        return render_template(
            "home/index.html",
            form=form,
            segment=get_segment(request),
            available_models=Available_models.get_visible_models_ids_and_names_list(),
        )

    url = request.form["url"]
    models = request.form["selected_models"]
    quick_analysis = 0
    if request.form.get("checkbox-quick-scan"):
        quick_analysis = 1

    session["messages"] = {
        "url": url.replace(" ", ""),
        "models": models,
        "quick_analysis": quick_analysis,
    }

    return render_template("specials/processing-url.html")


def trigger_mock_dashboard(url, models_ids, quick_analysis):
    """
    Trigger the dashboard with mock values.
    Coded to make the development process faster.
    """
    time.sleep(2)
    fv, fv_extra_information = get_mock_values_fv()
    session["messages"] = {
        "fv": fv.tolist(),
        "fv_extra_information": fv_extra_information,
        "url": url,
        "models_ids": models_ids,
        "quick_analysis": quick_analysis,
    }
    return redirect(url_for("home_blueprint.dashboard"))


@blueprint.route("/task", methods=["POST", "GET"])
def task():
    """
    Gets the feature vector for an URL.
    If the URL is not callable, it tries to reconstruct it.
    If there is an existing instance on the DB returns the FV.
    """
    try:
        messages = session.get("messages", None)
        url = messages["url"]
        models_ids = messages["models"]
        quick_analysis = messages["quick_analysis"]
        colour_list = ''

        if url == "mock":
            return trigger_mock_dashboard(url, models_ids, quick_analysis)

        callable_url = get_callable_url(url)

        if callable_url is None:
            raise Exception("No se ha podido llamar la url {} ni reconstruir.".format(url))

        # The URL is callable and has protocol
        if quick_analysis == 1:
            previous_instance = Available_instances.query.filter_by(instance_URL=callable_url).first()

            if previous_instance:
                fv = list(previous_instance.instance_fv)
                colour_list = previous_instance.colour_list if previous_instance.colour_list else ''
                fv_extra_information = {}

            else:
                fv, fv_extra_information = get_fv_and_info(callable_url)
                fv = fv.tolist()

        else:
            fv, fv_extra_information = get_fv_and_info(callable_url)
            fv = fv.tolist()

        # Enviamos el vector al dashboard
        session["messages"] = {
            "fv": fv,
            "fv_extra_information": fv_extra_information,
            "url": callable_url,
            "models_ids": models_ids,
            "quick_analysis": quick_analysis,
            "colour_list": colour_list,
        }

        return redirect(url_for("home_blueprint.dashboard"))

    except Exception as e:
        logger.error(e)
        message = "La URL {} no puede ser llamada ni tampoco reconstruída. Comprueba la sintáxis y si la página está disponible e inténtalo de nuevo.".format(
            url
        )
        flash(message, "danger")
        return redirect(url_for("home_blueprint.index"))


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
        count, numeric_class = get_sum_tags_numeric(predicted_tags)

        models_confidence = [
            int(100 * cls.predict_proba(fv)[0][prediction])
            for cls, prediction in zip(classifiers, predicted_tags)
        ]

        # Todo en arrays por orden
        information_to_display = {
            "url": url,
            "quick_analysis": messages["quick_analysis"],
            "fv": list(fv),
            "fv_extra_information": messages["fv_extra_information"],
            "class": translate_tag(numeric_class),
            "colour-list": messages["colour_list"],
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


@login_required
@blueprint.route("/profile", methods=["GET"])
def profile():
    n_reports_accepted = (
        Users.query.filter_by(id=current_user.id).first().n_urls_accepted
    )

    if n_reports_accepted is None:
        n_reports_accepted = 0

    n_reports_reviewing = 0
    users_reports = Candidate_instances.query.options(load_only("user_id")).all()
    users_reports = [report.user_id for report in users_reports]

    for user_report in users_reports:
        if current_user.id == user_report:
            n_reports_reviewing += 1

    return render_template(
        "home/profile.html",
        n_reports_accepted=n_reports_accepted,
        n_reports_reviewing=n_reports_reviewing,
        segment=get_segment(request),
    )


@login_required
@blueprint.route("/models", methods=["GET"])
def models():
    information_to_display = []

    algorithms = [
        (Available_co_forests, "CO-FOREST"),
        (Available_tri_trainings, "TRI-TRAINING"),
        (Available_democratic_cos, "DEMOCRATIC-CO"),
    ]

    for algorithm in algorithms:
        for model in algorithm[0].query.all():
            information_to_display.append(get_model_dict(model, algorithm[1]))

    return render_template(
        "home/models-administration.html",
        segment=get_segment(request),
        information_to_display=information_to_display,
    )


@blueprint.route("/nuevomodelo", methods=["GET", "POST"])
def new_model():
    form = NewModelForm()

    if not current_user.is_authenticated:
        return redirect(url_for("authentication_blueprint.login"))

    if "siguiente" in request.form:
        selected_method = translate_form_select_data_method(
            request.form["form_select_data_method"]
        )

        # Se cargan los archivos del usuario. Si uno de los dos no carga,
        # se pasa a generar los conjuntos aleatoriamente
        if selected_method == "csv":
            selected_method, dataset_tuple = save_files_to_temp(
                form.uploaded_train_csv.data, form.uploaded_test_csv.data
            )

        # Esto no sé si funciona, probar el entero
        # N INSTANCES REFACTORIZAR PARA QUE SEA PORCENTAJE DE TRAIN
        # Si falla la carga también se genera
        if selected_method == "generate":
            dataset_tuple = check_n_instances(request.form["train_n_instances"])

        session["messages"] = {
            "form_data": request.form,
            "dataset_method": dataset_tuple,
        }

        return render_template("specials/creating-model.html")

    return render_template(
        "home/new-model.html", form=form, segment=get_segment(request)
    )


@blueprint.route("/creatingmodel", methods=["POST", "GET"])
def creatingmodel():
    time.sleep(2)

    messages = session.get("messages", None)
    form_data = messages["form_data"]

    # COMPROBAR DICCIONARIO DE ENTRADA Y EL RESTO, PASO A TRATAR LOS DATOS
    # if messages is not None:
    #     form_data = correct_user_input(messages["form_data"])

    # Hasta aquí se tiene un formulario correcto y se supone que
    # se tiene un objeto clasificador para entrenar
    cls = get_co_forest()

    # Obtenemos datos de entrenamiento y test
    dataset_method, dataset_params = messages["dataset_method"]
    X_train, X_test, y_train, y_test = return_X_y_train_test(
        dataset_method, dataset_params
    )
    L_train, U_train, Ly_train, Uy_train = train_test_split(
        X_train, y_train, test_size=0.8, random_state=5, stratify=y_train
    )
    # flash("{} {} {} {}".format(X_train, X_test, y_train, y_test))

    cls.fit(L_train, Ly_train, U_train)
    y_pred = cls.predict(X_test)
    scores = get_array_scores(y_test, y_pred)
    flash(scores)

    # Serializamos el nuevo modelo y lo guardamos en la bbdd
    serialize_store_coforest(form_data, cls, scores)

    # flash("{}".format(form_data))
    return redirect(url_for("home_blueprint.report_url"))


@login_required
@blueprint.route("/instances", methods=["GET", "POST"])
def instances(n_per_page=10):
    form = FlaskForm(request.form)

    if not current_user.is_authenticated:  # meter if admin
        return redirect(url_for("authentication_blueprint.login"))

    if "my_page" in request.form:
        page = int(request.form["my_page"])
        previous_page = int(request.form["previous_page"])
        checks = session.get("checks", None)
        update_checks(
            previous_page, request.form.getlist("checkbox-instance"), checks, n_per_page
        )

        if request.form["button_pressed"] == "deliminar":
            pass

        elif request.form["button_pressed"] == "descargar":
            filename = "selected_instances.csv"
            create_csv_selected_instances(list(checks.values()), filename)
            return send_from_directory(
                get_temporary_download_directory(), filename, as_attachment=True
            )

    else:
        page = 1
        checks = {}

    session["checks"] = checks
    post_pagination = Available_instances.all_paginated(page, n_per_page)
    post_pagination.items = get_instances_view_dictionary(
        post_pagination.items, checks.values()
    )

    return render_template(
        "home/instances-administration.html",
        segment=get_segment(request),
        post_pagination=post_pagination,
        selected=post_pagination.iter_pages(
            left_edge=1, left_current=1, right_current=1, right_edge=1
        ),
        form=form,
    )


@blueprint.route("/report_url", methods=["GET", "POST"])
@login_required
def report_url():
    form = ReportURLForm(request.form)

    if not current_user.is_authenticated:
        return redirect(url_for("authentication_blueprint.login"))

    if "report" in request.form:
        try:
            url = request.form["url"]
            type = request.form["type"]

            if type == "blacklist":
                type = Available_tags.black_list
            elif type == "whitelist":
                type = Available_tags.white_list

            existing_instance = Available_instances.query.filter_by(
                instance_URL=url
            ).first()

            if not existing_instance:
                existing_instance = Available_instances(instance_URL=url)
                db.session.add(existing_instance)
                db.session.flush()

            db.session.add(
                Candidate_instances(
                    instance_id=existing_instance.instance_id,
                    user_id=current_user.id,
                    date_reported=datetime.now(),
                    suggestions=type,
                )
            )

            db.session.commit()
            flash(
                "Tu URL ha sido reportada exitosamente. ¡Gracias por tu colaboración!"
            )

        except exc.SQLAlchemyError as e:
            flash("Error al reportar la URL. Inténtalo de nuevo más tarde.")
            db.session.rollback()
            logger.info("Error al reportar la URL: {}".format(e))

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
        return render_template("specials/page-404.html"), 404

    except:
        return render_template("specials/page-500.html"), 500


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template("specials/page-403.html"), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template("specials/page-404.html"), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template("specials/page-500.html"), 500
