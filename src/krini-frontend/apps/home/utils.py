#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/03/30 21:06:56
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

DEFAULT_MODEL_NAME = "Default"

from apps.ssl_utils.ml_utils import (
    obtain_model,
    get_temporary_train_files_directory,
    serialize_model,
    get_temporary_download_directory,
    get_mock_values_fv,
)
from werkzeug.utils import secure_filename
from os import path, remove
from apps.authentication.models import Users
from apps.home.models import (
    Available_tags,
    Available_models,
    Available_co_forests,
    Available_democratic_cos,
    Available_tri_trainings,
    Available_instances,
    Candidate_instances,
)
import re
import pandas as pd
import json
from flask_login import current_user
from datetime import datetime
import time
from apps import db
from flask import flash, send_from_directory, send_file
import logging
import requests
import urllib.parse


def get_logger(
    name, fichero="log_krini", nivel_logger=logging.DEBUG, nivel_fichero=logging.DEBUG
):
    """
    Returns a logger with the given name and the given
    parameters.
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(nivel_logger)

    fh = logging.FileHandler(fichero)
    fh.setLevel(nivel_fichero)
    fh.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(fh)

    return logger


logger = get_logger("krini-frontend")


def get_callable_url(url):
    """
    Tries to get the URL content. If it fails, it tries
    to complete the URL
    """

    try:
        requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
            },
            timeout=5,
        ).content

        return url

    except requests.exceptions.RequestException:
        return complete_uncallable_url(url)


def complete_uncallable_url(url):
    """
    Tries to complete the URL with the protocol.
    Several checks are made.
    """
    try:
        parsed = urllib.parse.urlparse(url)

        if not parsed.netloc and not parsed.path:
            return None

        elif not parsed.netloc and parsed.path:
            url = parsed.path

        if not parsed.scheme:
            protocol = find_url_protocol(url)

            if not protocol:
                return None

            url = protocol + url

        requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
            },
            timeout=5,
        ).content

        return url

    except requests.exceptions.RequestException:
        return None


def find_url_protocol(url, protocols=["https://", "http://"]):
    """
    Tries to find a protocol for the given URL
    """
    for protocol in protocols:
        try:
            url = protocol + url
            requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
                },
                timeout=5,
            ).content

            return protocol

        except requests.exceptions.RequestException:
            pass

    return None


def save_bbdd_analized_instance(callable_url, fv, tag=-1):
    """
    Tries to save an analized instance in the database.
    If it fails, it returns False.
    """

    try:

        if current_user.is_authenticated:
            instance = Available_instances(
                instance_URL=callable_url,
                instance_fv=(fv,),
                instance_class=tag,
                instance_labels=([
                    Available_tags.sug_analized_review,
                    Available_tags.nueva,
                    Available_tags.sug_phishing
                    if tag == 1
                    else Available_tags.sug_legitimate,
                ],),
            )

            db.session.add(instance)
            db.session.flush()

            candidate_instance = Candidate_instances(
                instance_id=instance.instance_id,
                user_id=current_user.id if current_user.is_authenticated else -1,
                date_reported=datetime.now(),
                suggestions=Available_tags.sug_analized_review,
            )

            db.session.add(candidate_instance)
            db.session.commit()

        else:
            raise Exception("User not authenticated. {} not saved.".format(callable_url))

    except Exception as e:
        db.session.rollback()
        logger.error("Error saving instance in the database. {}".format(e))
        return False


def translate_array_js(selected):
    if bool(re.search(r"\d", selected)):
        splitted = selected.split(",")
        return [int(elem) for elem in splitted]
    
    return []


def get_selected_models_ids(selected):
    """
    Returns the ids of the selected models.
    If there are no selected models, it returns
    the default model or any other if the default
    model is not available.
    """
    selected_models = translate_array_js(selected)

    if len(selected_models) != 0:
        return selected_models  

    # We try to return the default model or any other if its empty
    default_id = Available_models.query.filter_by(
        model_name=DEFAULT_MODEL_NAME
    ).first()

    if default_id:
        return [default_id.model_id]
    
    else:
        random_model = Available_models.query.first()
        if random_model:
            return [random_model.model_id]
    
    return []


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


def make_array_safe(vector):
    return json.loads(json.dumps(vector))


def get_parameters(model, algorithm="semi-supervised"):
    if algorithm == "semi-supervised":
        return [], "red"

    elif algorithm == "CO-FOREST":
        return [
            "Max features = {}".format(model.max_features),
            "Thetha = {}".format(model.thetha),
            "Nº árboles = {}".format(model.n_trees),
        ], "pink"

    elif algorithm == "TRI-TRAINING":
        return [
            "Clasificador 1: {}".format(model.cls_one),
            "Clasificador 2: {}".format(model.cls_two),
            "Clasificador 3: {}".format(model.cls_three),
        ], "yellow"

    elif algorithm == "DEMOCRATIC-CO":
        information = cls_to_string_list(model.base_clss)
        information.append("Nº clasificadores = {}".format(model.n_clss))
        return information, "cyan"


def cls_to_string_list(mutable_clss):
    return [
        "Clasificador {}: {}".format(i + 1, cls) for i, cls in enumerate(mutable_clss)
    ]


def get_username(user_id):
    user = Users.query.filter_by(id=user_id).first()

    if user:
        return user.username.upper()
    else:
        return "?"


def get_model_dict(model, algorithm="semi-supervised"):
    params = get_parameters(model, algorithm)
    return {
        "model_name": model.model_name.upper(),
        "model_parameters": params[0],
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


def translate_tag_colour(tag):
    if tag == 0:
        return "legítimo", "green"
    elif tag == 1:
        return "phishing", "red"
    
    else:
        return "no disponible", "grey"


def get_instance_dict(instance):
    return {
        "instance_id": instance.instance_id,
        "reviewed_by": get_username(instance.reviewed_by),
        "instance_URL": instance.instance_URL,
        "instance_fv": instance.instance_fv,
        "instance_class": translate_tag_colour(instance.instance_class)[0],
        "badge_colour": translate_tag_colour(instance.instance_class)[1],
        "colour_list": instance.colour_list,
        "instance_labels": instance.instance_labels if instance.instance_labels else [],
        "is_selected": 0,
    }


def update_checks(previous_page, new_checks, checks, n_per_page):
    # Update previous page selected instances
    post_pagination = Available_instances.all_paginated(previous_page, n_per_page)
    ids_previous = [instance.instance_id for instance in post_pagination.items]
    checks_update = [int(id_elem) for id_elem in new_checks]

    for id_instance in ids_previous:
        if id_instance in checks_update and str(id_instance) not in checks:
            checks[str(id_instance)] = id_instance

        elif id_instance not in checks_update and str(id_instance) in checks:
            del checks[str(id_instance)]


def get_instances_view_dictionary(post_pagination_items, checks_values):
    new_items_list = [get_instance_dict(instance) for instance in post_pagination_items]
    ids_checked = list(checks_values)

    # Update view of the items in the requested page
    for item in new_items_list:
        if item["instance_id"] in ids_checked:
            item["is_selected"] = 1
        else:
            item["is_selected"] = 0

    return new_items_list


def create_csv_selected_instances(ids_instances, filename="selected_instances.csv"):
    instances = Available_instances.query.filter(
        Available_instances.instance_id.in_(ids_instances)
    ).all()

    data = []
    for instance in instances:
        fv = instance.instance_fv
        fv.append(instance.instance_class)
        data.append(fv)

    df = pd.DataFrame(data, columns=["f{}".format(i) for i in range(1, 20)] + ["tag"])

    download_directory = get_temporary_download_directory()
    download_path = path.join(download_directory, filename)

    # Ojo porque los enteros pasan a ser flotantes. No crea problemas pero podría.
    df.to_csv(download_path, index=False)


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
    if user_input == "1":
        return "csv"
    elif user_input == "2":
        return "generate"


def serialize_store_coforest(form_data, cls, scores):
    try:
        existing_instance = Available_co_forests.query.filter_by(
            model_name=form_data["model_name"]
        ).first()

        if existing_instance:
            form_data["model_name"] = form_data["model_name"] + time.time()

        file_name = form_data["model_name"] + ".pkl"

        serialize_model(cls, file_name)

        new_model = Available_co_forests(
            model_name=form_data["model_name"],
            created_by=current_user.id,
            file_name=file_name,
            model_scores=(scores,),
            model_notes=form_data["model_description"],
            creation_date=datetime.now(),
            is_visible=to_bolean(form_data["is_visible"]),
            is_default=to_bolean(form_data["is_default"]),
            random_state=form_data["random_state"],
            n_trees=form_data["n_trees"],
            thetha=form_data["thetha"],
            max_features=form_data["max_features"],
        )

        db.session.add(new_model)
        db.session.commit()
        flash("Modelo guardado correctamente.", "success")
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
    if user_input == "1":
        return "co-forest"
    elif user_input == "2":
        return "democratic-co"
    elif user_input == "3":
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
            form_data["max_features"] = "log2"

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
