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
import json

# DB Models
from apps.home.forms import ReportURLForm, SearchURLForm, NewModelForm, CheckBoxForm
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
from apps.ssl_utils.ml_utils import translate_tag, get_fv_and_info, get_mock_values_fv, get_co_forest, get_array_scores

# Utils
from apps.home.utils import *
logger = get_logger('krini-frontend')

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

    return render_template("specials/processing-url.html")


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


@blueprint.route("/nuevomodelo", methods=["GET", "POST"])
def new_model():

    form = NewModelForm()

    if not current_user.is_authenticated:
        return redirect(url_for("authentication_blueprint.login"))

    if "siguiente" in request.form:

        selected_method = translate_form_select_data_method(
            request.form["form_select_data_method"])

        # Se cargan los archivos del usuario. Si uno de los dos no carga,
        # se pasa a generar los conjuntos aleatoriamente
        if selected_method == "csv":
            selected_method, dataset_tuple = save_files_to_temp(
                form.uploaded_train_csv.data, form.uploaded_test_csv.data)

        # Esto no sé si funciona, probar el entero
        # N INSTANCES REFACTORIZAR PARA QUE SEA PORCENTAJE DE TRAIN
        # Si falla la carga también se genera
        if selected_method == "generate":
            dataset_tuple = check_n_instances(
                request.form["train_n_instances"])

        session["messages"] = {"form_data": request.form,
                               "dataset_method": dataset_tuple}

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
        dataset_method, dataset_params)
    L_train, U_train, Ly_train, Uy_train = train_test_split(
        X_train, y_train, test_size=0.8, random_state=5, stratify=y_train)
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
def instances():

    form = CheckBoxForm(request.form)
    

    if not current_user.is_authenticated:
        return redirect(url_for("authentication_blueprint.login"))

    if "my_page" in request.form:

        #page = int(request.args.get("page", 1))
        page = int(request.form["my_page"])
        logger.info("page form: {}".format(page))

        # Ids de las instancias en la bbdd
        for new_check in request.form.getlist('checkbox-instance'):
            session["checks"][new_check] = new_check

        logger.info("checks: {}".format(session["checks"]))

    else:
        page = 1
        session["checks"] = {}
        logger.info("page hardcoded: {}".format(page))


    post_pagination = Available_instances.all_paginated(page, 5)
    new_items_list = [get_instance_dict(instance) for instance in post_pagination.items]
    post_pagination.items = new_items_list
    selected = post_pagination.iter_pages(left_edge=1, left_current=1, right_current=1, right_edge=1)

    return render_template(
            "home/instances-administration.html", segment=get_segment(request), post_pagination=post_pagination, selected=selected, form=form)



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
