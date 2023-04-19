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
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
)

from apps.ssl_utils.ml_utils import (
    obtain_model,
    get_temporary_train_files_directory,
    serialize_model,
    get_temporary_download_directory,
)
from apps import db
from apps.authentication.models import Users
from apps.home.exceptions import KriniNotLoggedException
from apps.home.models import (
    Available_tags,
    Available_models,
    Available_co_forests,
    Available_democratic_cos,
    Available_tri_trainings,
    Available_instances,
    Candidate_instances,
)
from werkzeug.utils import secure_filename
from os import path, remove, listdir
import re
import pandas as pd
import json
from flask_login import current_user
from datetime import datetime
import time
from flask import flash
import logging
import requests
import urllib.parse
from pickle import PickleError

from apps.home.exceptions import (
    KriniNotLoggedException,
    KriniDBException,
    KriniException,
)
from sqlalchemy import exc

CO_FOREST_CONTROL = "CO-FOREST"
TRI_TRAINING_CONTROL = "TRI-TRAINING"
DEMOCRATIC_CO_CONTROL = "DEMOCRATIC-CO"


def get_logger(
    name,
    file_name="log_krini",
    logger_level=logging.DEBUG,
    file_level=logging.DEBUG,
):
    """
    Returns a logger with the given name and the given
    parameters.

    Args:
        name (str): logger name.
        file_name(str, optional): file name. Defaults to "log_krini".
        logger_level (str, optional): Defaults to logging.DEBUG.
        file_level (str, optional): Defaults to logging.DEBUG.

    Returns:
        object: logger object.
    """
    new_logger = logging.getLogger(name)

    if new_logger.hasHandlers():
        new_logger.handlers.clear()

    new_logger.setLevel(logger_level)

    fh = logging.FileHandler(file_name)
    fh.setLevel(file_level)
    fh.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    new_logger.addHandler(fh)

    return new_logger


logger = get_logger("krini-frontend")


def sanitize_url(url):
    """
    Transform a dangerours URL into a not-clickable one.

    Args:
        url (str): The URL to sanitize.

    Returns:
        str: The sanitized URL.
    """
    url = url.replace("http", "hxxp")
    url = url.replace("://", "[://]")
    url = url.replace(".", "[.]")
    url = url.replace("?", "[?]")
    url = url.replace("&", "[&]")
    url = url.replace("=", "[=]")
    return url


def get_callable_url(url):
    """
    Checks if the URL is callable (is up).
    If not, it tries to complete it.

    Args:
        url (str): URL to check.

    Returns:
        str: The URL with the protocol, or None if it fails.
    """
    try:
        requests.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=5,
        ).content

        return url

    except requests.exceptions.RequestException:
        return complete_uncallable_url(url)


def complete_uncallable_url(url):
    """
    Tries to complete the URL with the protocol.
    Several checks are made.

    Args:
        url (str): The URL to check.

    Returns:
        str: The URL with the protocol, or None if it fails.
    """
    try:
        parsed = urllib.parse.urlparse(url)

        if not parsed.netloc and not parsed.path:
            return None

        if not parsed.netloc and parsed.path:
            url = parsed.path

        if not parsed.scheme:
            protocol = find_url_protocol(url)

            if not protocol:
                return None

            url = protocol + url

        requests.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=5,
        ).content

        return url

    except requests.exceptions.RequestException:
        return None


def find_url_protocol(url, protocols=[]):
    """
    Try to find the protocol of the URL.

    Args:
        url (str): The URL to check.
        protocols (list, optional): List of protocols to check.
                                    Defaults to [].

    Returns:
        str: The protocol of the URL, or None if it fails.
    """
    if len(protocols) == 0:
        protocols = ["https://", "http://"]

    for protocol in protocols:
        try:
            url = protocol + url
            requests.get(
                url,
                headers={"User-Agent": DEFAULT_USER_AGENT},
                timeout=5,
            ).content

            return protocol

        except requests.exceptions.RequestException:
            pass

    return None


def save_bbdd_analized_instance(callable_url, fv, tag=-1):
    """
    Tries to save an analized instance in the database.

    Args:
        callable_url (str): The URL of the instance.
        fv (list): The feature vector of the instance.
        tag (int, optional): If analized, the class tag. Defaults to -1.

    Raises:
        KriniNotLoggedException: if the user is not logged in.

    Returns:
        boolean: True if the instance was saved, False otherwise.
    """
    try:
        if current_user.is_authenticated:
            instance = Available_instances(
                instance_URL=callable_url,
                instance_fv=(fv,),
                instance_class=tag,
                instance_labels=(
                    [
                        Available_tags.sug_new_instance,
                        Available_tags.auto_classified,
                        Available_tags.sug_review,
                    ],
                ),
            )

            db.session.add(instance)
            db.session.flush()

            candidate_instance = Candidate_instances(
                instance_id=instance.instance_id,
                user_id=current_user.id
                if current_user.is_authenticated
                else -1,
                date_reported=datetime.now(),
                suggestions=Available_tags.sug_new_report,
            )

            db.session.add(candidate_instance)
            db.session.commit()
            return True

        raise KriniNotLoggedException(
            "User not authenticated. {} not saved.".format(callable_url)
        )

    except (KriniNotLoggedException, exc.SQLAlchemyError) as e:
        db.session.rollback()
        logger.error("Error saving instance in the database. {}".format(e))
        return False


def translate_array_js(selected):
    """
    Translates the array of selected models from
    javascript to python.

    Args:
        selected (str): String with the selected models.

    Returns:
        list: list of integers (ids)
    """
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

    Args:
        predicted_tags (list): list of tags.

    Returns:
        (list, int): sum of tags and majority tag.
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
    """
    Makes an array safe to be used with js.

    Args:
        vector (list): array

    Returns:
        list: safe array
    """
    return json.loads(json.dumps(vector))


def get_parameters(model, algorithm="SEMI-SUPERVISED"):
    """
    Returns information to display.

    Args:
        model (Available_models): model to get the parameters.
        algorithm (str, optional): Type. Defaults to "SEMI-SUPERVISED".
                                   Can be "CO-FOREST", "TRI-TRAINING"
                                   or "DEMOCRATIC-CO".

    Returns:
        (str, str): str with info and its bagde color.
    """
    if algorithm == "semi-supervised":
        return [], "red"

    if algorithm == CO_FOREST_CONTROL:
        return [
            "Max features = {}".format(model.max_features),
            "Thetha = {}".format(model.thetha),
            "Nº árboles = {}".format(model.n_trees),
        ], "pink"

    if algorithm == TRI_TRAINING_CONTROL:
        return [
            "Clasificador 1: {}".format(model.cls_one),
            "Clasificador 2: {}".format(model.cls_two),
            "Clasificador 3: {}".format(model.cls_three),
        ], "yellow"

    if algorithm == DEMOCRATIC_CO_CONTROL:
        information = cls_to_string_list(model.base_clss)
        information.append("Nº clasificadores = {}".format(model.n_clss))
        return information, "cyan"


def cls_to_string_list(mutable_clss):
    """
    Returns a list of strings with the classifiers
    information.

    Args:
        mutable_clss (list): _description_

    Returns:
        list: strings of each classifier.
    """
    return [
        "Clasificador {}: {}".format(i + 1, cls)
        for i, cls in enumerate(mutable_clss)
    ]


def get_username(user_id):
    """
    Returns the username of the user.

    Args:
        user_id (int): id of the user.

    Returns:
        str: username of the user.
    """
    user = Users.query.filter_by(id=user_id).first()

    if user:
        return user.username.upper()
    return "?"


def get_model_dict(model, algorithm="SEMI-SUPERVISED"):
    """
    Returns a dictionary with the information of the model.

    Args:
        model (Available_model): object to get the information.
        algorithm (str, optional): algorithm (str, optional): Type.
                                   Defaults to "SEMI-SUPERVISED".
                                   Can be "CO-FOREST", "TRI-TRAINING" or "DEMOCRATIC-CO"

    Returns:
        dict: dictionary with the information of the model.
    """
    params = get_parameters(model, algorithm)

    return {
        "model_name": model.model_name.upper(),
        "model_parameters": params[0],
        "algorithm": algorithm,
        "badge_colour": params[1],
        "created_by": get_username(model.created_by),
        "creation_date": str(model.creation_date)[:10],
        "is_default": model.is_default,
        "is_visible": model.is_visible,
        "model_scores": model.model_scores,
        "random_state": model.random_state,
        "model_notes": model.model_notes,
    }


def translate_tag_colour(tag):
    """
    Translates the tag into a string and its colour.

    Args:
        tag (int): 0 legítima, 1 phishing

    Returns:
        (str, str): tuple with the tag and its colour.
    """
    if tag == 0:
        return "legítimo", "green"
    if tag == 1:
        return "phishing", "red"
    return "no disponible", "grey"


def get_instance_dict(instance, empty=False):
    """
    Transforms the object instance into a dictionary
    containing the instance information.

    Args:
        instance (object): instance to translate
        empty (bool): if True, returns an empty template

    Returns:
        dict: dictionary with the instance information
    """
    if empty:
        return {
            "instance_id": -1,
            "reviewed_by": "",
            "instance_URL": "",
            "instance_fv": "no hay ningún vector generado para esta instancia",
            "instance_class": -1,
            "badge_colour": "",
            "colour_list": "",
            "instance_labels": [],
            "is_selected": 0,
        }

    return {
        "instance_id": instance.instance_id,
        "reviewed_by": get_username(instance.reviewed_by),
        "instance_URL": instance.instance_URL,
        "instance_fv": instance.instance_fv
        if instance.instance_fv
        else "no hay ningún vector generado para esta instancia",
        "instance_class": translate_tag_colour(instance.instance_class)[0],
        "badge_colour": translate_tag_colour(instance.instance_class)[1],
        "colour_list": instance.colour_list,
        "instance_labels": instance.instance_labels
        if instance.instance_labels
        else [],
        "is_selected": 0,
    }


def get_candidate_instance_dict(candidate_instance, report_number):
    """
    Transforms the candidate instance object into a dictionary
    containing the notification information.

    Args:
        report_number (int): report number (to control checks)
        candidate_instance (object): instance to translate

    Returns:
        dict: dictionary with the candidate instance information
    """
    return {
        "report_number": report_number,
        "instance_id": candidate_instance.instance_id,
        "reported_by": get_username(candidate_instance.user_id),
        "instance_URL": Candidate_instances.get_instance_url(
            candidate_instance.instance_id
        ),
        "date_reported": str(candidate_instance.date_reported)[:16],
        "suggestion": candidate_instance.suggestions,
        "is_selected": 0,
    }


def update_checks(
    previous_page, new_checks, checks, n_per_page, sequence=False
):
    """
    Update previous page selected instances.
    Modifies the checks dictionary.
    Checks syntax: {str(instance_id): int(instance_id)}

    Args:
        previous_page (int): previous page selected
        new_checks (list): list of new checks ids (strings)
        checks (dict): dictionary of checks
        n_per_page (int): number of instances per page
        sequence (bool): if True, the checks are generated (sequence of numbers)
    """
    if sequence:
        offset = (previous_page - 1) * n_per_page
        ids_previous = [offset + i for i in range(n_per_page)]

    else:
        post_pagination = Available_instances.all_paginated(
            previous_page, n_per_page
        )
        ids_previous = [
            instance.instance_id for instance in post_pagination.items
        ]

    checks_update = [int(id_elem) for id_elem in new_checks]

    for id_instance in ids_previous:
        if id_instance in checks_update and str(id_instance) not in checks:
            checks[str(id_instance)] = id_instance

        elif id_instance not in checks_update and str(id_instance) in checks:
            del checks[str(id_instance)]

    return checks


def update_batch_checks(
    modality, checks, previous_page=-1, n_per_page=-1, sequence=False
):
    """
    Update checks dictionary.
    Selects or deselects all instances in the page or above all instances.

    Args:
        modality (str): modality of the update
        checks (dict): dictionary of checks
        previous_page (int, optional): previous page selected. Defaults to -1.
        n_per_page (int, optional): number of instances per page. Defaults to -1.
        sequence (bool): if True, the checks are generated (sequence of numbers)

    Returns:
        dict: dictionary of checks updated
    """
    if modality == "deseleccionar_todos":
        checks = {}

    elif modality == "seleccionar_todos":
        if sequence:
            n_instances = Candidate_instances.query.count()
            checks = {str(i): i for i in range(n_instances)}
        else:
            instances = Available_instances.query.all()
            checks = {
                str(instance.instance_id): instance.instance_id
                for instance in instances
            }

    elif "page" in modality:
        if sequence:
            offset = (previous_page - 1) * n_per_page
            ids_previous = [offset + i for i in range(n_per_page)]
        else:
            post_pagination = Available_instances.all_paginated(
                previous_page, n_per_page
            )
            ids_previous = [
                instance.instance_id for instance in post_pagination.items
            ]

        if "deseleccionar_todos" in modality:
            for id_instance in ids_previous:
                if str(id_instance) in checks:
                    del checks[str(id_instance)]

        elif "seleccionar_todos" in modality:
            for id_instance in ids_previous:
                checks[str(id_instance)] = id_instance

    return checks


def get_instances_view_dictionary(post_pagination_items, checks_values):
    """
    Transforms the instances in the requested page to a dictionary
    with the information to be displayed in the view (includying if
    the instance is checked).

    Args:
        post_pagination_items (iter): instances in the requested page
        checks_values (dict.values()): ids of the instances that are checked

    Returns:
        list: list of dictionaries with the information of the instances
    """

    new_items_list = [
        get_instance_dict(instance) for instance in post_pagination_items
    ]
    ids_checked = list(checks_values)

    # Update view of the items in the requested page
    for item in new_items_list:
        if item["instance_id"] in ids_checked:
            item["is_selected"] = 1
        else:
            item["is_selected"] = 0

    return new_items_list


def get_candidate_instances_view_dictionary(
    post_pagination_items, checks_values, page, n_per_page
):
    """
    Transforms the candidate instances in the requested page to a dictionary
    with the information to be displayed in the view (includying if
    the instance is checked).

    Args:
        post_pagination_items (iter): instances in the requested page
        checks_values (dict.values()): ids of the instances that are checked

    Returns:
        list: list of dictionaries with the information of the instances
    """

    offset = (page - 1) * n_per_page
    new_items_list = [
        get_candidate_instance_dict(ci, offset + i)
        for i, ci in enumerate(post_pagination_items)
    ]
    ids_checked = list(checks_values)

    # Update view of the items in the requested page
    for item in new_items_list:
        if item["report_number"] in ids_checked:
            item["is_selected"] = 1
        else:
            item["is_selected"] = 0

    return new_items_list


def find_candidate_instance_sequence(previous_page, n_per_page, report_number):
    """
    Given a report number, returns the instance in the page.

    Args:
        previous_page (int): previous page, the one displayed before the request
        n_per_page (int): number of instances per page
        report_number (int): number of the instance above all displayed (order, starting in 0)

    Returns:
        CandidateInstance: instance selected
    """
    offset = (previous_page - 1) * n_per_page
    in_page = report_number - offset
    post_pagination = Candidate_instances.all_paginated(
        previous_page, n_per_page
    )
    return post_pagination.items[in_page]


def find_candidate_instances_sequence(report_numbers, n_per_page):
    """
    Given list of report numbers, returns the instances selected.

    Args:
        report_numbers (list): number of the instances above all displayed (order, starting in 0)

    Returns:
        list: list of instances selected (Candidate_instances objects)
    """

    affected_pages_reports = {}

    for report_number in report_numbers:
        page = int(report_number / n_per_page) + 1

        if page not in affected_pages_reports:
            affected_pages_reports[page] = [report_number]
        else:
            affected_pages_reports[page].append(report_number)

    candidate_instances = []

    for page, reports in affected_pages_reports.items():
        post_pagination = Candidate_instances.all_paginated(page, n_per_page)
        for report_number in reports:
            in_page = report_number - (page - 1) * n_per_page
            candidate_instances.append(post_pagination.items[in_page])

    return candidate_instances


def remove_selected_reports(report_numbers, n_per_page):
    """
    Removes the selected reports from the database.

    Args:
        report_numbers (list): list of report numbers

    Returns:
        bool: True if the reports were removed successfully, False otherwise
    """
    try:
        selected_reports = find_candidate_instances_sequence(
            report_numbers, n_per_page
        )

        for report in selected_reports:
            db.session.delete(report)

        db.session.commit()
        return True

    except exc.SQLAlchemyError as e:
        logger.error("Error removing selected reports: {}".format(e))
        db.session.rollback()
        return False


def update_report(candidate_instance, action):
    """
    Updates the report, depending on the action.

    Args:
        candidate_instance (Candidate_instances): candidate instance to be updated
        action (str): action to be performed.
                      (aceptar, descartar, aceptar_todos, descartar_todos)

    Returns:
        bool: True if the report was updated successfully, False otherwise
    """

    all = False

    if "todos" in action:
        all = True

    if "aceptar" in action:
        done = accept_report(candidate_instance, all)

    elif "descartar" in action:
        done = reject_report(candidate_instance, all)

    return done


def reject_report(candidate_instance, all):
    """
    Rejects the report and removes it from the database.

    Args:
        candidate_instance (Candidate_instances): candidate instance to be rejected
        all (bool): True if all the instances with the same URL are rejected

    Returns:
        bool: True if the report was rejected successfully, False otherwise
    """
    try:
        if all:
            candidate_instances = Candidate_instances.query.filter_by(
                instance_id=candidate_instance.instance_id
            ).all()

            for ci in candidate_instances:
                db.session.delete(ci)

        else:
            db.session.delete(candidate_instance)

        db.session.commit()
        return True

    except exc.SQLAlchemyError as e:
        logger.error("Error rejecting report: {}".format(e))
        db.session.rollback()
        return False


def accept_report(candidate_instance, all):
    """
    Accepts the report, updates the main instance and removes it from the database.

    Args:
        candidate_instance (Candidate_instances): candidate instance to be accepted
        all (bool): True if all the instances with the same URL are accepted

    Returns:
        bool: True if the report was accepted successfully, False otherwise
    """
    try:
        modified = accept_incoming_suggestion(candidate_instance)

        if modified:
            deleted = reject_report(candidate_instance, all)

        if not modified or not deleted:
            raise exc.SQLAlchemyError("Error accepting suggestions")

        else:
            db.session.commit()
            return True

    except exc.SQLAlchemyError as e:
        logger.error("Error accepting report: {}".format(e))
        db.session.rollback()
        return False


def accept_incoming_suggestion(candidate_instance):
    """
    Accepts the incoming suggestion, updates the main instance.

    Args:
        candidate_instance (Candidate_instances): candidate instance report

    Returns:
        bool: True if the suggestion was accepted successfully, False otherwise
    """
    try:
        affected_instance = Available_instances.query.filter_by(
            instance_id=candidate_instance.instance_id
        ).first()

        old_labels = affected_instance.instance_labels
        new_labels = clean_suggested_tags(old_labels)

        if candidate_instance.suggestions == Available_tags.sug_black_list:
            affected_instance.colour_list = Available_tags.black_list
            new_labels.append(Available_tags.black_list)
            if Available_tags.white_list in new_labels:
                new_labels.remove(Available_tags.white_list)

        elif candidate_instance.suggestions == Available_tags.sug_white_list:
            affected_instance.colour_list = Available_tags.white_list
            new_labels.append(Available_tags.white_list)
            if Available_tags.black_list in new_labels:
                new_labels.remove(Available_tags.black_list)

        elif candidate_instance.suggestions == Available_tags.sug_phishing:
            affected_instance.instance_class = 1
            if Available_tags.auto_classified in new_labels:
                new_labels.remove(Available_tags.auto_classified)

        elif candidate_instance.suggestions == Available_tags.sug_legitimate:
            affected_instance.instance_class = 0
            if Available_tags.auto_classified in new_labels:
                new_labels.remove(Available_tags.auto_classified)

        affected_instance.instance_labels = new_labels
        affected_instance.reviewed_by = current_user.id
        db.session.commit()
        return True

    except exc.SQLAlchemyError as e:
        logger.error("Error accepting incoming suggestion: {}".format(e))
        db.session.rollback()
        return False


def clean_suggested_tags(tags):
    """
    Cleans the suggested tags of the instance.

    Args:
        tags (list): List tags.

    Returns:
        list: Cleaned list of tags.
    """
    cleaned_list = []

    if not tags:
        return cleaned_list

    available_suggested_tags = Available_tags.suggestion_tags

    for tag in tags:
        if tag not in available_suggested_tags:
            cleaned_list.append(tag)

    return cleaned_list


def create_csv_selected_instances(
    ids_instances, filename="selected_instances.csv"
):
    """
    Creates a csv containing the selected instances features
    vectors and tags

    Args:
        ids_instances (list): list containing ids
        filename (str, optional): Downloaded file name.
                                  Defaults to "selected_instances.csv".

    Returns:
        str: path of the downloaded file
    """
    instances = Available_instances.query.filter(
        Available_instances.instance_id.in_(ids_instances)
    ).all()

    data = []
    for instance in instances:
        fv = instance.instance_fv
        tag = instance.instance_class

        if fv and (tag == 0 or tag == 1):
            fv.append(tag)
            data.append(fv)

    df = pd.DataFrame(
        data, columns=["f{}".format(i) for i in range(1, 20)] + ["tag"]
    )

    download_directory = get_temporary_download_directory()
    download_path = path.join(download_directory, filename)

    # Ojo porque los enteros pasan a ser flotantes. No crea problemas pero podría.
    df.to_csv(download_path, index=False)
    return download_path


def clean_temporary_files(temporary_files_directory=None):
    """
    Deletes all files in the temporary directory.

    Args:
        temporary_files_directory (str, optional): Path to the temporary directory.
                                                   If none, downloaded instances are
                                                   cleaned.
    """
    if temporary_files_directory is None:
        temporary_files_directory = get_temporary_download_directory()

    for file in listdir(temporary_files_directory):
        file_path = path.join(temporary_files_directory, file)
        remove(file_path)


def save_files_to_temp(form_file_one, form_file_two):
    """Returns true y la tupla"""
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


def remove_selected_instances(ids_instances):
    """
    Removes the selected instances from the database.

    Args:
        ids_instances (list): list containing ids

    Raises:
        KriniDBException: raised if there is an error in the database
    """
    try:
        Available_instances.query.filter(
            Available_instances.instance_id.in_(ids_instances)
        ).delete(synchronize_session=False)

        Candidate_instances.query.filter(
            Candidate_instances.instance_id.in_(ids_instances)
        ).delete(synchronize_session=False)

        db.session.commit()

    except exc.SQLAlchemyError:
        db.session.rollback()
        raise KriniDBException(
            "Error al eliminar las instancias {}.".format(ids_instances)
        )


def translate_form_select_data_method(user_input):
    """
    Translates the user input to the corresponding method.

    Args:
        user_input (str): selected option

    Returns:
        str: "csv" or "generate", depending on the user input
    """
    if user_input == "1":
        return "csv"
    if user_input == "2":
        return "generate"


def translate_form_select_algorithm(user_input):
    """
    Translates the user input to the corresponding model.

    Args:
        user_input (str): selected option.

    Returns:
        str: "CO-FOREST", "DEMOCRATIC-CO" or "TRI-TRAINING",
             depending on the user input
    """
    if user_input == "1":
        return CO_FOREST_CONTROL
    if user_input == "2":
        return TRI_TRAINING_CONTROL
    if user_input == "3":
        return DEMOCRATIC_CO_CONTROL


def serialize_store_model(form_data, cls, scores, algorithm=CO_FOREST_CONTROL):
    """
    Stores the model in the database and pickles it. The operation is
    ATOMIC: if there is an error, the model is not stored and
    the pickle file is removed from the server.

    Storing name is the model name + version -> "COF 1.1.0"
    File name is the model name + version with - + .pkl -> "COF_1-0-0.pkl"

    Args:
        form_data (dict): dictionary containing the form data corrected.
        scores (list): list containing the scores of the model
        algorithm (int, optional): algorithm used. Can be "CO-FOREST",
                                   "DEMOCRATIC-CO", or "TRI-TRAINING".

    Raises:
        KriniException: exception raised if there is an error in the database,
                        while picking or with duplicate model names.

    Returns:
        bool: True if the model was stored correctly.
    """
    # TODO: TODOS LOS ALGORITMOS
    try:
        model_name = form_data["model_name"]
        model_version = form_data["model_version"]
        model_store_name = model_name + " " + model_version
        file_name = model_name + "_" + model_version.replace(".", "-") + ".pkl"

        existing_instance = Available_models.query.filter_by(
            model_name=model_store_name
        ).first()

        if existing_instance:
            raise KriniException(
                "Ya existe un modelo con ese nombre y esa versión <<{}>>.".format(
                    model_store_name
                )
            )

        file_location = serialize_model(cls, file_name)

        if algorithm == CO_FOREST_CONTROL:
            new_model = Available_co_forests(
                model_name=model_store_name,
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

        elif algorithm == DEMOCRATIC_CO_CONTROL:
            new_model = Available_democratic_cos(
                model_name=model_store_name,
                created_by=current_user.id,
                file_name=file_name,
                model_scores=(scores,),
                model_notes=form_data["model_description"],
                creation_date=datetime.now(),
                is_visible=to_bolean(form_data["is_visible"]),
                is_default=to_bolean(form_data["is_default"]),
                random_state=form_data["random_state"],
            )

        elif algorithm == TRI_TRAINING_CONTROL:
            new_model = Available_tri_trainings(
                model_name=model_store_name,
                created_by=current_user.id,
                file_name=file_name,
                model_scores=(scores,),
                model_notes=form_data["model_description"],
                creation_date=datetime.now(),
                is_visible=to_bolean(form_data["is_visible"]),
                is_default=to_bolean(form_data["is_default"]),
                random_state=form_data["random_state"],
            )

        db.session.add(new_model)
        db.session.commit()
        return True

    except PickleError:
        raise KriniException("Error al serializar el modelo.")

    except exc.SQLAlchemyError as e:
        logger.error("Error al guardar el modelo en la BD." + str(e))
        db.session.rollback()
        remove(file_location)
        raise KriniException("Error al guardar el modelo en la BD.")


def to_bolean(string):
    if string == "True":
        return True
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
    if user_input == "2":
        return "democratic-co"
    if user_input == "3":
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

    except Exception:
        raise Exception(
            "Corregir excepciones valores coforest (fichero utils.py)"
        )


def check_correct_values_tri_training(form_data):
    base_clss = ["kNN", "NB", "tree"]
    for i, keys_to_ckeck in enumerate(["cls_one", "cls_two", "cls_three"]):
        if form_data[keys_to_ckeck] not in base_clss:
            form_data[keys_to_ckeck] = base_clss[i]

    form_data["model_algorithm"] = "tri-training"

    return form_data


def check_correct_values_democratic_co(form_data):
    base_clss = ["kNN", "NB", "tree"]
    for i, keys_to_ckeck in enumerate(["cls_one", "cls_two", "cls_three"]):
        n_clss = "n_{}".format(keys_to_ckeck)

        if form_data[keys_to_ckeck] not in base_clss:
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

    except Exception:
        return None


def get_model(model_id):
    requested_model = Available_models.query.filter_by(
        model_id=model_id
    ).first()

    if requested_model:
        model_name = requested_model.model_name
        model_file = requested_model.file_name
        model_scores = requested_model.model_scores

    else:
        model_name = "Default model"
        model_file = "default.pkl"
        model_scores = (
            Available_models.query.filter_by(model_name="Default")
            .first()
            .model_scores
        )

    cls, file_found = obtain_model(model_file)

    if not file_found:
        model_name = "Default model"
        model_scores = (
            Available_models.query.filter_by(model_name="Default")
            .first()
            .model_scores
        )

    return model_name, cls, model_scores
