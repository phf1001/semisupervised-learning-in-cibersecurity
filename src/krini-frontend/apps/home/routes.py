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
from os import path, remove

# DB Models
from apps.home.forms import ReportURLForm, SearchURLForm, NewModelForm
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
from sklearn.model_selection import train_test_split
from apps.ssl_utils.ml_utils import obtain_model, translate_tag, get_temporary_train_files_directory, get_fv_and_info, get_mock_values_fv, get_co_forest, get_tri_training, get_democratic_co, get_array_scores, serialize_model


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

def save_files_to_temp(form_file_one, form_file_two):
    """
    Returns true y la tupla
    """
    dataset_tuple = ("csv", {})

    for tipo, f in zip(["train", "test"], [form_file_one, form_file_two]):

        if f is not None:
            filename = secure_filename(f.filename)
            path_one = get_temporary_train_files_directory()
            file_path = path.join(path_one, filename)
            f.save(file_path)
            dataset_tuple[1][tipo] = file_path

        # Si cualquiera de los dos es None ya genera
        else:
            return "generate", ()

    return "csv", dataset_tuple


def check_n_instances(n_instances):
    try:
        n_instances = int(n_instances)

        if n_instances > 0 and n_instances < 100:
            dataset_tuple = ("generate", n_instances)
        else:
            dataset_tuple = ("generate", 80)

        return dataset_tuple

    except ValueError:
        return ("generate", 80)


def translate_form_select_data_method(user_input):
    if user_input == '1':
        return "csv"
    elif user_input == '2':
        return "generate"


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

    #Obtenemos datos de entrenamiento y test
    dataset_method, dataset_params = messages["dataset_method"]
    X_train, X_test, y_train, y_test = return_X_y_train_test(dataset_method, dataset_params)
    L_train, U_train, Ly_train, Uy_train = train_test_split(
            X_train, y_train, test_size=0.8, random_state=5, stratify=y_train)
    #flash("{} {} {} {}".format(X_train, X_test, y_train, y_test))

    cls.fit(L_train, Ly_train, U_train)
    y_pred = cls.predict(X_test)
    scores = get_array_scores(y_test, y_pred)
    flash(scores)

    #Serializamos el nuevo modelo y lo guardamos en la bbdd
    serialize_store_coforest(form_data, cls, scores)

    #flash("{}".format(form_data))
    return redirect(url_for("home_blueprint.report_url"))



def serialize_store_coforest(form_data, cls, scores):
    
    try:
        
        existing_instance = Available_co_forests.query.filter_by(model_name = form_data["model_name"]).first()

        if existing_instance:
            form_data["model_name"] = form_data["model_name"] + time.time()

        file_name = form_data["model_name"] + ".pkl"

        serialize_model(cls, file_name)

        new_model = Available_co_forests(  
            model_name = form_data["model_name"],
            created_by = current_user.id,
            file_name = file_name,
            model_scores = (scores,),
            model_notes = form_data["model_description"],
            creation_date = datetime.now(),
            is_visible = to_bolean(form_data["is_visible"]),
            is_default = to_bolean(form_data["is_default"]),
            random_state = form_data["random_state"],
            n_trees = form_data["n_trees"],
            thetha = form_data["thetha"],
            max_features = form_data["max_features"]
        )
        
        db.session.add(new_model)
        db.session.commit()
        flash("Modelo guardado correctamente.")
        return True

    except Exception as e:
        flash("Error al guardar el modelo." + str(e))
        return False

def to_bolean(string):
    if string == "True":
        return True
    else:
        return False
    
def return_X_y_train_test(dataset_method, dataset_params):
    # params diccionario train:file, test:file o un entero

    if dataset_method == "csv":
        X_train, y_train = extract_X_y_csv(dataset_params["train"])
        X_test, y_test = extract_X_y_csv(dataset_params["test"])
 

    # if generate etc

    return X_train, X_test, y_train, y_test


def extract_X_y_csv(file_name):
    # Comprobar dimensiones, que está bien todo etc

    df = pd.read_csv(file_name)
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values
    remove(file_name)
    return X, y


def translate_form_select_ssl_alg(user_input):
    if user_input == '1':
        return "co-forest"
    elif user_input == '2':
        return "democratic-co"
    elif user_input == '3':
        return "tri-training"


def correct_user_input(form_data):

    form_data = correct_model_values(form_data)

    selected_algorithm = form_data.get("model_algorithm", None)

    if selected_algorithm == "tri-training":
        form_data = check_correct_values_tri_training(form_data)
    elif selected_algorithm == "democratic-co":
        form_data = check_correct_values_democratic_co(form_data)
    else:
        form_data = check_correct_values_coforest(form_data)


def correct_model_values(form_data):

    # Comprobar nombres no duplicados, versiones bien introducidas, etc
    return form_data


def check_correct_values_coforest(form_data):

    try:

        if not isinstance(form_data.get("max_features", None), str):
            form_data["max_features"] = 'log2'

        if not isinstance(form_data.get("thetha", None), float):
            form_data["thetha"] = 0.75

        if not isinstance(form_data.get("n_trees", None), int):
            form_data["n_trees"] = 6

        form_data["model_algorithm"] = "co-forest"

        return form_data

    except Exception as e:
        raise Exception("ay sigueña")


def check_correct_values_tri_training(form_data):

    base_clss = ["kNN", "NB", "tree"]
    for i, keys_to_ckeck in enumerate(["cls_one", "cls_two", "cls_three"]):

        if not form_data[keys_to_ckeck] in base_clss:
            form_data[keys_to_ckeck] = base_clss[i]

    form_data["model_algorithm"] = "tri-training"

    return form_data


def check_correct_values_democratic_co(form_data):

    base_clss = ["kNN", "NB", "tree"]
    for i, keys_to_ckeck in enumerate(["cls_one", "cls_two", "cls_three"]):

        n_clss = "n_{}".format(keys_to_ckeck)

        if not form_data[keys_to_ckeck] in base_clss:
            form_data[keys_to_ckeck] = base_clss[i]
            form_data[n_clss] = 1

        elif not isinstance(form_data[n_clss], int):
            form_data[n_clss] = 0

    form_data["model_algorithm"] = "democratic-co"

    return form_data


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

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template("specials/page-403.html"), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template("specials/page-404.html"), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template("specials/page-500.html"), 500
