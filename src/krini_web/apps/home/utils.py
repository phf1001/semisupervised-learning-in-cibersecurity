#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   utils.py
@Time    :   2023/03/30 21:06:56
@Author  :   Patricia Hernando Fernández 
@Version :   1.0
@Contact :   phf1001@alu.ubu.es
"""

from apps.config import (
    CO_FOREST_CONTROL,
    TRI_TRAINING_CONTROL,
    DEMOCRATIC_CO_CONTROL,
    DEFAULT_USER_AGENT,
)
from apps.ssl_utils.ml_utils import (
    obtain_model,
    get_temporary_train_files_directory,
    serialize_model,
    get_temporary_download_directory,
    get_models_directory,
)
from apps.home.exceptions import (
    KriniNotLoggedException,
    KriniDBException,
    KriniException,
    KriniSSLException,
)
from apps import db
from apps.authentication.models import Users
from apps.home.models import (
    Available_tags,
    Available_models,
    Available_co_forests,
    Available_democratic_cos,
    Available_tri_trainings,
    Available_instances,
    Candidate_instances,
    Model_is_trained_with,
)
from apps.messages import (
    get_exception_message,
    get_message,
    get_formatted_message,
    get_constants_message,
)
from werkzeug.utils import secure_filename
from os import path, remove, listdir, sep, rename
import re
import pandas as pd
from numpy import int64, float64, array
import json
from flask import flash
from flask_login import current_user
from datetime import datetime
import logging
import requests
from requests.exceptions import RequestException
import urllib.parse
from pickle import PickleError
from sqlalchemy import exc


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
    Checks if the URL is callable (is up). If not, it tries to complete it.

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

    except requests.exceptions.SSLError:
        raise KriniSSLException(get_exception_message("error_ssl"))

    except RequestException:
        return complete_uncallable_url(url)


def complete_uncallable_url(url):
    """
    Tries to complete the URL with the protocol.  Several checks are made.

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

    except RequestException:
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

        except RequestException:
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

        raise KriniNotLoggedException("User is not logged in.")

    except (KriniNotLoggedException, exc.SQLAlchemyError):
        db.session.rollback()
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
    """Returns the selected models ids. If there are no selected models,
    it returns the default model or any other if there is none.

    Args:
        selected (str): String with the selected models.

    Returns:
        list: list of integers (ids)
    """
    selected_models = translate_array_js(selected)

    if len(selected_models) != 0:
        return selected_models

    default_id = Available_models.query.filter_by(is_default=True).first()

    if default_id:
        return [default_id.model_id]

    random_model = Available_models.query.first()
    if random_model:
        return [random_model.model_id]

    return []


def get_model(model_id):
    """Returns the model with the given id. If the file is not found,
    it raises an exception.

    THE MODEL EXISTS.

    Args:
        model_id (int): The id of the model.

    Returns:
        tuple: (model_name, model_object, model_scores)
    """
    requested_model = Available_models.query.filter_by(
        model_id=model_id
    ).first()

    if requested_model:
        model_name = requested_model.model_name
        model_file = requested_model.file_name
        model_scores = requested_model.model_scores

    cls, file_found = obtain_model(model_file)

    if not file_found:
        raise KriniException(get_exception_message("IA_file_not_found"))

    return model_name, cls, model_scores


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
            get_formatted_message("max_features", [model.max_features]),
            get_formatted_message("thetha", [model.thetha]),
            get_formatted_message("n_trees", [model.n_trees]),
        ], "pink"

    if algorithm == TRI_TRAINING_CONTROL:
        return [
            get_formatted_message("cls_number", [1, model.cls_one]),
            get_formatted_message("cls_number", [2, model.cls_two]),
            get_formatted_message("cls_number", [3, model.cls_three]),
        ], "yellow"

    if algorithm == DEMOCRATIC_CO_CONTROL:
        information = cls_to_string_list(model.base_clss)
        information.append(f"Nº clasificadores = {model.n_clss}")
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
        get_formatted_message("cls_number", [i + 1, cls])
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


def get_model_dict(model):
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
    if model.model_algorithm == "cf":
        algorithm = CO_FOREST_CONTROL
        model = Available_co_forests.query.filter_by(
            model_id=model.model_id
        ).first()
    elif model.model_algorithm == "tt":
        algorithm = TRI_TRAINING_CONTROL
        model = Available_tri_trainings.query.filter_by(
            model_id=model.model_id
        ).first()
    elif model.model_algorithm == "dc":
        algorithm = DEMOCRATIC_CO_CONTROL
        model = Available_democratic_cos.query.filter_by(
            model_id=model.model_id
        ).first()
    else:
        algorithm = "SEMI-SUPERVISED"

    params = get_parameters(model, algorithm)

    return {
        "model_id": model.model_id,
        "model_version": extract_version(model.model_name),
        "model_name": model.model_name.upper(),
        "model_parameters": params[0],
        "algorithm": algorithm,
        "badge_colour": params[1],
        "created_by": get_username(model.created_by),
        "creation_date": str(model.creation_date)[:10],
        "is_default": model.is_default,
        "is_visible": model.is_visible,
        "model_scores": [round(score, 3) for score in model.model_scores],
        "random_state": model.random_state,
        "model_notes": model.model_notes,
        "is_selected": 0,
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
        return get_constants_message("legitimate"), "green"
    if tag == 1:
        return get_constants_message("phishing"), "red"
    return get_constants_message("unavailable"), "grey"


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
            "instance_fv": get_constants_message("no_vector"),
            "instance_class": -1,
            "badge_colour": "",
            "colour_list": "",
            "instance_labels": [],
            "instance_labels_colours": [],
            "is_selected": 0,
        }

    instance_labels = instance.instance_labels

    if instance_labels:
        instance_labels_colours = [
            Available_tags.get_colour(label) for label in instance_labels
        ]

    else:
        instance_labels_colours = None
        instance_labels = None

    return {
        "instance_id": instance.instance_id,
        "reviewed_by": get_username(instance.reviewed_by),
        "instance_URL": instance.instance_URL,
        "instance_fv": instance.instance_fv
        if instance.instance_fv
        else get_constants_message("no_vector"),
        "instance_class": translate_tag_colour(instance.instance_class)[0],
        "badge_colour": translate_tag_colour(instance.instance_class)[1],
        "colour_list": instance.colour_list,
        "instance_labels": instance_labels,
        "instance_labels_colours": instance_labels_colours,
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
        "suggestion_colour": Available_tags.get_colour(
            candidate_instance.suggestions
        ),
        "is_selected": 0,
    }


def update_checks(
    previous_page,
    new_checks,
    checks,
    n_per_page,
    sequence=False,
    items_class=Available_instances,
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
        items_class (class): class of the items
    """
    if sequence:
        offset = (previous_page - 1) * n_per_page
        ids_previous = [offset + i for i in range(n_per_page)]

    else:
        post_pagination = items_class.all_paginated(previous_page, n_per_page)

        if items_class == Available_instances:
            ids_previous = [
                instance.instance_id for instance in post_pagination.items
            ]

        elif items_class == Available_models:
            ids_previous = [model.model_id for model in post_pagination.items]

    checks_update = [int(id_elem) for id_elem in new_checks]

    for id_previous in ids_previous:
        if id_previous in checks_update and str(id_previous) not in checks:
            checks[str(id_previous)] = id_previous

        elif id_previous not in checks_update and str(id_previous) in checks:
            del checks[str(id_previous)]

    return checks


def update_batch_checks(
    modality,
    checks,
    previous_page=-1,
    n_per_page=-1,
    sequence=False,
    items_class=Available_instances,
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
        items_class (class): class of the items

    Returns:
        dict: dictionary of checks updated
    """
    if modality == "deseleccionar_todos":
        checks = {}

    elif modality in ("seleccionar_todos", "seleccionar_todos_contrarios"):
        if sequence:
            n_instances = Candidate_instances.query.count()
            checks = {str(i): i for i in range(n_instances)}
        else:
            instances = items_class.query.all()

            if items_class == Available_models:
                checks = {
                    str(model.model_id): model.model_id for model in instances
                }

            elif items_class == Available_instances:
                if modality == "seleccionar_todos":
                    checks = {
                        str(instance.instance_id): instance.instance_id
                        for instance in instances
                    }

                elif modality == "seleccionar_todos_contrarios":
                    selected = set(checks.values())

                    checks = {
                        str(instance.instance_id): instance.instance_id
                        for instance in instances
                        if instance.instance_id not in selected
                    }

    elif "page" in modality:
        if sequence:
            offset = (previous_page - 1) * n_per_page
            ids_previous = [offset + i for i in range(n_per_page)]
        else:
            post_pagination = items_class.all_paginated(
                previous_page, n_per_page
            )

            if items_class == Available_instances:
                ids_previous = [
                    instance.instance_id for instance in post_pagination.items
                ]

            elif items_class == Available_models:
                ids_previous = [
                    model.model_id for model in post_pagination.items
                ]

        if "deseleccionar_todos" in modality:
            for id_previous in ids_previous:
                if str(id_previous) in checks:
                    del checks[str(id_previous)]

        elif "seleccionar_todos" in modality:
            for id_previous in ids_previous:
                checks[str(id_previous)] = id_previous

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
        report_number (int): number of the instance above all displayed
                             (order, starting in 0)

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
        report_numbers (list): number of the instances above all displayed
                               (order, starting in 0)

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

    except exc.SQLAlchemyError:
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
    bulk_update = False

    if "todos" in action:
        bulk_update = True

    if "aceptar" in action:
        done = accept_report(candidate_instance, bulk_update)

    elif "descartar" in action:
        done = reject_report(candidate_instance, bulk_update)

    return done


def reject_report(candidate_instance, bulk_update):
    """
    Rejects the report and removes it from the database.

    Args:
        candidate_instance (Candidate_instances): candidate instance to be rejected
        bulk_update (bool): True if all the instances with the same URL are rejected

    Returns:
        bool: True if the report was rejected successfully, False otherwise
    """
    try:
        if bulk_update:
            candidate_instances = Candidate_instances.query.filter_by(
                instance_id=candidate_instance.instance_id
            ).all()

            for ci in candidate_instances:
                db.session.delete(ci)

        else:
            db.session.delete(candidate_instance)

        db.session.commit()
        return True

    except exc.SQLAlchemyError:
        db.session.rollback()
        return False


def accept_report(candidate_instance, bulk_update):
    """
    Accepts the report, updates the main instance and removes it from the database.

    Args:
        candidate_instance (Candidate_instances): candidate instance to be accepted
        bulk_update (bool): True if all the instances with the same URL are accepted

    Returns:
        bool: True if the report was accepted successfully, False otherwise
    """
    try:
        modified = accept_incoming_suggestion(candidate_instance)

        if modified:
            deleted = reject_report(candidate_instance, bulk_update)

        if not modified or not deleted:
            raise exc.SQLAlchemyError("Error accepting suggestions")

        user_reporting_id = candidate_instance.user_id
        user_reporting = Users.query.filter_by(id=user_reporting_id).first()

        if user_reporting.n_urls_accepted is None:
            user_reporting.n_urls_accepted = 0
        else:
            user_reporting.n_urls_accepted += 1

        db.session.flush()
        db.session.commit()
        return True

    except (exc.SQLAlchemyError, AttributeError):
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

        new_labels.append(Available_tags.reviewed)
        affected_instance.instance_labels = [*set(new_labels)]
        affected_instance.reviewed_by = current_user.id
        db.session.commit()
        return True

    except exc.SQLAlchemyError:
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
    ids, vectors and tags

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

    if len(instances) == 0:
        raise KriniDBException(get_message("instance_not_selected"))

    data = []
    for instance in instances:
        fv = instance.instance_fv
        tag = instance.instance_class

        if fv and tag in (0, 1):
            data.append([instance.instance_id] + fv + [tag])

    if len(data) == 0:
        raise KriniDBException(get_exception_message("no_fv_among_instances"))

    df = pd.DataFrame(
        data,
        columns=["instance_id"] + [f"f{i}" for i in range(1, 20)] + ["tag"],
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


def save_files_to_temp(form_file_one, form_file_two=None):
    """Save files to temp directory

    Args:
        form_file_one (str): file one.
        form_file_two (str): file two. Defaults to None.

    Returns:
        tuple: tuple and dictionary with the files {tipo: path}
    """
    dataset_tuple = ("csv", {})
    previous_filename = ""

    if form_file_two is None:
        file_types = ["test"]
        files = [form_file_one]
    else:
        file_types = ["train", "test"]
        files = [form_file_one, form_file_two]

    for tipo, f in zip(file_types, files):
        if f is not None:
            filename = secure_filename(f.filename)

            if filename == previous_filename:
                filename = "copy_" + filename

            path_one = get_temporary_train_files_directory()
            file_path = path.join(path_one, filename)
            f.save(file_path)
            dataset_tuple[1][tipo] = file_path
            previous_filename = filename

        # If one file fails, also generated
        else:
            return "generate", ()

    return "csv", dataset_tuple


def check_n_instances(n_instances):
    """
    Checks if the percentage of instances is valid.

    Args:
        n_instances (str): percentage of instances to check

    Returns:
        tuple: method and percentage of instances. If the number of instances
               is not valid, the number of instances is set to 80.
    """
    try:
        n_instances = int(n_instances)

        if 0 < n_instances < 100:
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
        raise KriniDBException(get_message("instances_not_deleted"))


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


def remove_selected_models(ids_models):
    """
    Removes the selected models from the database.
    It also deletes the file with the pickled model.

    MODELS 1, 2 and 3 are not deleted.

    Args:
        ids_models (list): list containing ids

    Returns:
        bool: True if some model has been deleted, False otherwise

    Raises:
        KriniDBException: raised if there is an error in the database
    """
    try:
        models_path = get_models_directory()
        flash_msg = False
        some_deleted = False

        for model_id in ids_models:
            if model_id not in ("1", "2", "3", 1, 2, 3):
                model = Available_models.query.filter_by(
                    model_id=model_id
                ).first()

                model_path = models_path + sep + model.file_name
                if path.exists(model_path):
                    remove(model_path)

                Available_models.query.filter_by(model_id=model_id).delete()
                db.session.commit()
                some_deleted = True

            else:
                flash_msg = True

        if flash_msg:
            flash(get_exception_message("protected_models"), "info")

        return some_deleted

    except exc.SQLAlchemyError:
        db.session.rollback()
        raise KriniDBException(get_message("models_not_removed"))


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
        return DEMOCRATIC_CO_CONTROL
    if user_input == "3":
        return TRI_TRAINING_CONTROL


def serialize_store_model(
    form_data, cls, scores, train_ids, algorithm=CO_FOREST_CONTROL
):
    """
    Stores the model in the database and pickles it. The operation is
    ATOMIC: if there is an error, the model is not stored and
    the pickle file is removed from the server.

    Storing name is the model name + version -> "COF 1.1.0"
    File name is the model name + version with - + .pkl -> "COF_1-0-0.pkl"

    Trainings ids are stored in the relation table.
    All default models are updated if needed.

    Args:
        form_data (dict): dictionary containing the form data corrected.
        scores (list): list containing the scores of the model
        algorithm (int, optional): algorithm used. Can be "CO-FOREST",
                                   "DEMOCRATIC-CO", or "TRI-TRAINING".
        train_ids (set): set containing the ids of the trainings used.

    Raises:
        KriniException: exception raised if there is an error in the database,
                        while picking or with duplicate model names.

    Returns:
        (bool, int): True if the model was stored correctly and its id.
    """
    file_location = None
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
                get_formatted_message("model_name_exists", [model_store_name])
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
                random_state=int(form_data["random_state"]),
                n_trees=int(form_data["n_trees"]),
                thetha=round(float(form_data["thetha"]), 3),
                max_features=form_data["max_features"],
            )

        elif algorithm == DEMOCRATIC_CO_CONTROL:
            base_clss = [form_data["cls_one"]] * int(form_data["n_cls_one"])
            base_clss += [form_data["cls_two"]] * int(form_data["n_cls_two"])
            base_clss += [form_data["cls_three"]] * int(
                form_data["n_cls_three"]
            )

            new_model = Available_democratic_cos(
                model_name=model_store_name,
                created_by=current_user.id,
                file_name=file_name,
                model_scores=(scores,),
                model_notes=form_data["model_description"],
                creation_date=datetime.now(),
                is_visible=to_bolean(form_data["is_visible"]),
                is_default=to_bolean(form_data["is_default"]),
                random_state=int(form_data["random_state"]),
                n_clss=len(base_clss),
                base_clss=(base_clss,),
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
                random_state=int(form_data["random_state"]),
                cls_one=form_data["cls_one_tt"],
                cls_two=form_data["cls_two_tt"],
                cls_three=form_data["cls_three_tt"],
            )

        db.session.add(new_model)
        db.session.flush()
        model_id = new_model.model_id

        if to_bolean(form_data["is_default"]):
            done = Available_models.update_default_model(model_id)
            if not done:
                raise KriniException(get_message("default_not_updated"))

        for instance_id in set(train_ids):
            new_row = Model_is_trained_with(model_id, int(instance_id))
            db.session.add(new_row)

        db.session.commit()
        return True, model_id

    except PickleError:
        raise KriniException(get_message("model_not_serialized"))

    except exc.SQLAlchemyError:
        db.session.rollback()
        if file_location:
            remove(file_location)
        raise KriniException(
            get_exception_message("error_storing_model_or_training_data")
        )


def extract_version(model_name):
    """Extracts the version of a model.

    Args:
        model_name (str): name of the model.

    Returns:
        str: version of the model.
    """
    return model_name.split(" ")[-1]


def update_model(model, form_data, models_path=None):
    """Updates the model in the database and the file system.
    If the model is not in the file system, it is not updated.
    Also updates the default model if it is the one being updated.

    Args:
        model (Available_models): model to be updated.
        form_data (dict): dictionary containing the form data corrected.
        models_path (str, optional): path to the models directory.

    Raises:
        KriniException: if there is an error in the database or the file system.

    Returns:
        bool: True if the model was updated correctly.
    """
    try:
        if model.model_id not in ("1", "2", "3", 1, 2, 3):
            new_model_version = form_data["model_version"]

            if models_path is None:
                models_path = get_models_directory()

            new_file_name = (
                model.file_name.split("_")[0]
                + "_"
                + new_model_version.replace(".", "-")
                + ".pkl"
            )

            old_file_location = models_path + sep + model.file_name
            new_file_location = models_path + sep + new_file_name

            if path.isfile(old_file_location):
                rename(old_file_location, new_file_location)

            else:
                raise KriniDBException(
                    get_exception_message("serialized_not_found")
                )

            model.model_name = (
                model.model_name.split(" ")[0] + " " + new_model_version
            )
            model.file_name = new_file_name

            new_notes = form_data["model_description"]
            if len(new_notes) > 0:
                model.model_notes = new_notes

            model.is_visible = to_bolean(form_data["is_visible"])
            update_defaults = to_bolean(form_data["is_default"])

            if update_defaults:
                done = Available_models.update_default_model(model.model_id)
                if not done:
                    raise KriniDBException(get_message("default_not_updated"))

            db.session.flush()
            db.session.commit()
            return True

        flash(get_exception_message("protected_models_edit"), "info")
        return False

    except exc.SQLAlchemyError:
        db.session.rollback()
        raise KriniException(get_message("model_not_updated"))

    except KriniDBException as e:
        raise KriniException(str(e))


def to_bolean(string):
    """Transforms a string to a boolean.

    Args:
        string (str): string to be transformed.

    Returns:
        bool: True if the string is "True", False otherwise.
    """
    if string == "True":
        return True
    return False


def get_models_view_dictionary(post_pagination_items, checks_values):
    """
    Transforms the models in the requested page to a dictionary
    with the information to be displayed in the view (includying if
    the instance is checked).

    Args:
        post_pagination_items (iter): models in the requested page
        checks_values (dict.values()): ids of the instances that are checked

    Returns:
        list: list of dictionaries with the information of the instances
    """
    new_items_list = [get_model_dict(model) for model in post_pagination_items]
    ids_checked = list(checks_values)

    # Update view of the items in the requested page
    for item in new_items_list:
        if item["model_id"] in ids_checked:
            item["is_selected"] = 1
        else:
            item["is_selected"] = 0

    return new_items_list


def return_X_y_train_test(dataset_method, dataset_params, get_ids=False):
    """
    Returns X and y for training and testing.
    Based on the dataset_method and dataset_params.

    Warning: only reviewd instances will be used to train if generate is selected.

    Args:
        dataset_method (str): "csv" or "generate"
        dataset_params (int or dict): percentage*100 of instances to be used for
                                      training or dictionary {train:file, test:file}
        get_ids (bool, optional): If true, returns the ids. Defaults to False.

    Raises:
        KriniException: if there is an error

    Returns:
        tuple: X_train, y_train, X_test, y_test, train_ids, test_ids (if get_ids=True)
        tuple: X_train, y_train, X_test, y_test (if get_ids=False)
    """
    try:
        if dataset_method == "csv":
            X_train, y_train, train_ids = extract_X_y_csv(
                dataset_params["train"], get_ids
            )
            X_test, y_test, test_ids = extract_X_y_csv(
                dataset_params["test"], get_ids
            )

        elif dataset_method == "generate":
            instances = Available_instances.query.filter(
                Available_instances.reviewed_by.isnot(None)
            ).all()

            instances = [
                [instance.instance_id]
                + instance.instance_fv
                + [instance.instance_class]
                for instance in instances
                if instance.instance_fv and instance.instance_class in (1, 0)
            ]

            df = pd.DataFrame(
                data=instances,
                columns=["instance_id"]
                + [f"f{i}" for i in range(1, 20)]
                + ["instance_class"],
            )

            train_percentage = int(dataset_params) / 100

            train = df.sample(frac=train_percentage)
            test = df.drop(train.index)

            X_train = train.iloc[:, 1:-1].values
            y_train = train.iloc[:, -1].values
            train_ids = train.iloc[:, 0].values

            X_test = test.iloc[:, 1:-1].values
            y_test = test.iloc[:, -1].values
            test_ids = test.iloc[:, 0].values

        if get_ids:
            return X_train, X_test, y_train, y_test, train_ids, test_ids

        return X_train, X_test, y_train, y_test

    except ValueError as e:
        logger.info(e)
        raise KriniException(get_exception_message("error_extracting_X_y"))


def return_X_y_single(
    dataset_method, model_id=-1, files_dict={}, omit_train_ids=False
):
    """
    Returns X and y not sampled.
    Based on the dataset_method and dataset_params.
    If csv, params must be a dictionary {test:file}.

    Warning: only not training instances will be returned
    if omit_train_ids is True and a valid model_id is provided.

    Args:
        dataset_method (str): "csv" or "generate"
        model_id (int, optional): model_id. Defaults to -1.
        files_dict (dict): dictionary {test:file}
        omit_train_ids (bool, optional): If true, instances seen during
                                         training will be ommited.
                                         Defaults to False.

    Raises:
        KriniException: if there is an error

    Returns:
        tuple: X, y
    """
    try:
        if dataset_method == "csv" and not omit_train_ids:
            X_test, y_test = extract_X_y_csv(files_dict["test"])

        elif dataset_method == "csv" and omit_train_ids:
            model_training_ids = get_model_training_ids(model_id)
            X_test_full, y_test_full, test_ids = extract_X_y_csv(
                files_dict["test"], get_ids=True
            )

            X_test = []
            y_test = []

            for i, instance_id in enumerate(test_ids):
                if instance_id not in model_training_ids:
                    X_test.append(X_test_full[i])
                    y_test.append(y_test_full[i])

            X_test = array(X_test)
            y_test = array(y_test)

        elif dataset_method == "generate" and omit_train_ids:
            model_training_ids = get_model_training_ids(model_id)
            X_test, y_test = get_all_instances_database_rows(
                exclude_ids=model_training_ids
            )

        elif dataset_method == "generate" and not omit_train_ids:
            X_test, y_test = get_all_instances_database_rows()

        return X_test, y_test

    except ValueError:
        raise KriniException(get_exception_message("error_generating_dataset"))


def get_all_instances_database_rows(exclude_ids=set()):
    """
    Returns all instances from the database as X and y.

    Args:
        exclude_ids (set, optional): ids to be excluded. Defaults to set().

    Throws:
        exc.SQLAlchemyError: if there is an error
    """
    instances = Available_instances.query.filter(
        Available_instances.reviewed_by.isnot(None)
    ).all()

    instances = [
        instance.instance_fv + [instance.instance_class]
        for instance in instances
        if instance.instance_fv
        and instance.instance_id not in exclude_ids
        and instance.instance_class in (1, 0)
    ]

    df = pd.DataFrame(
        data=instances,
        columns=[f"f{i}" for i in range(1, 20)] + ["instance_class"],
    )

    X_test = df.iloc[:, :-1].values
    y_test = df.iloc[:, -1].values
    return X_test, y_test


def get_model_training_ids(model_id):
    """Returns the instances ids used to train a model.

    Args:
        model_id (int): model_id

    Throws:
        exc.SQLAlchemyError: if there is an error

    Returns:
        set: set of instance_ids used to train.
    """
    model_training_rows = Model_is_trained_with.query.filter_by(
        model_id=model_id
    ).all()

    return {row.instance_id for row in model_training_rows}


def extract_X_y_csv(file_name, get_ids=False):
    """Extracts the X and y from a csv file.

    Args:
        file_name (str): name of the file to extract the data from
        get_ids (bool, optional): if True, the ids of the instances
                                  are also returned. Defaults to False.

    Raises:
        KriniException: if the file does not have the correct format

    Returns:
        (array, array, array): tuple with arrays of the features,
                               tags and ids if desired
    """
    try:
        df = pd.read_csv(file_name)

    except (FileNotFoundError, ValueError):
        if path.exists(file_name):
            remove(file_name)
        raise KriniException(get_exception_message("incorrect_file"))

    if not check_correct_pandas(df):
        if path.exists(file_name):
            remove(file_name)
        raise KriniException(get_exception_message("incorrect_file_format"))

    # Instance_id is not used for training
    X = df.iloc[:, 1:-1].values
    y = df.iloc[:, -1].values
    instances_ids = df.iloc[:, 0].values
    remove(file_name)

    if get_ids:
        return X, y, instances_ids
    return X, y


def check_correct_pandas(df):
    """Checks if the dataframe is correct and can
    be used to train/test a model.

    Args:
        df (dataframe): dataframe to check

    Returns:
        true if the dataframe is correct, false otherwise
    """
    columns_expected = (
        ["instance_id"] + [f"f{i}" for i in range(1, 20)] + ["tag"]
    )

    # All except instance_id and f10
    booleans_expected = (
        [f"f{i}" for i in range(1, 10)]
        + [f"f{i}" for i in range(11, 20)]
        + ["tag"]
    )

    if len(df.columns) != 21:
        return False

    if not all(df.columns == columns_expected):
        return False

    for column_type in df.dtypes:
        if column_type not in [int64, float64, int, float]:
            return False

    for column in booleans_expected:
        for unique in df[column].unique():
            if unique not in [0, 1]:
                return False

    return True


def update_model_scores_db(model, scores):
    """
    Updates the scores of a model in the database.

    Args:
        model (Available_models): model to update
        scores (list): list with the scores to update

    Raises:
        KriniDBException: if there is an error
    """
    try:
        model.model_scores = scores
        db.session.commit()

    except exc.SQLAlchemyError:
        db.session.rollback()
        raise KriniDBException(get_exception_message("error_updating_scores"))


def translate_form_select_ssl_alg(user_input):
    """Translates the user input to the correct value.

    Args:
        user_input (str): user input. It can be "1", "2" or "3".

    Returns:
        str: the correct value for the algorithm.
                It can be "co-forest", "democratic-co" or "tri-training".
    """
    if user_input == "1":
        return "co-forest"
    if user_input == "2":
        return "democratic-co"
    if user_input == "3":
        return "tri-training"


def get_segment(request):
    """Extracts the segment of the url.

    Args:
        request (request): request object

    Returns:
        str: segment of the url
    """
    try:
        segment = request.path.split("/")[-1]

        if segment == "":
            segment = "index"

        return segment

    except Exception:
        return None
