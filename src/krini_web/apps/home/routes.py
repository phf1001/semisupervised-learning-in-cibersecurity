#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   routes.py
@Time    :   2023/05/04 21:06:45
@Author  :   Patricia Hernando Fernández 
@Version :   5.0
@Contact :   phf1001@alu.ubu.es
"""
from os import remove
from pickle import PickleError
from sqlalchemy import exc
from sqlalchemy.orm import load_only
from apps import db
from apps.home import blueprint
from apps.home.exceptions import (
    KriniException,
    KriniNotLoggedException,
    KriniSSLException,
    KriniDBException,
)

from apps.home.utils import (
    get_logger,
    get_segment,
    get_callable_url,
    get_selected_models_ids,
    get_model,
    get_sum_tags_numeric,
    save_bbdd_analized_instance,
    sanitize_url,
    make_array_safe,
    update_batch_checks,
    update_checks,
    remove_selected_models,
    get_models_view_dictionary,
    translate_form_select_data_method,
    translate_form_select_algorithm,
    save_files_to_temp,
    check_n_instances,
    return_X_y_train_test,
    serialize_store_model,
    return_X_y_single,
    update_model_scores_db,
    get_model_dict,
    update_model,
    remove_selected_instances,
    get_instances_view_dictionary,
    create_csv_selected_instances,
    get_instance_dict,
    remove_selected_reports,
    find_candidate_instance_sequence,
    update_report,
    get_candidate_instances_view_dictionary,
    CO_FOREST_CONTROL,
    TRI_TRAINING_CONTROL,
    DEMOCRATIC_CO_CONTROL,
)
from apps.ssl_utils.ml_utils import (
    get_array_scores,
    get_co_forest,
    get_democratic_co,
    get_tri_training,
    get_fv_and_info,
    get_mock_values_fv,
    get_temporary_download_directory,
    translate_tag,
    deserialize_model,
)
from apps.home.forms import (
    ReportURLForm,
    SearchURLForm,
    ModelForm,
    InstanceForm,
    TestModelForm,
    SmallModelForm,
)
from apps.home.models import (
    Available_instances,
    Candidate_instances,
    Available_models,
    Available_tags,
)
from apps.authentication.models import Users
from apps.config import AVAILABLE_LANGUAGES, BABEL_DEFAULT, MAX_MODELS_DASHBOARD
from apps.messages import (
    get_message,
    get_form_message,
    get_exception_message,
    get_formatted_message,
)
from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    send_from_directory,
    after_this_request,
)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from werkzeug.exceptions import Forbidden
from datetime import datetime
import json
import numpy as np
import time
from sklearn.model_selection import train_test_split

logger = get_logger("krini-frontend")


@blueprint.route("/language=<language>")
def set_language(language=None):
    """Sets the language of the app.

    Args:
        language (str, optional): language to set. Defaults to None.

    Returns:
        redirect: redirects to the index page
    """
    if language in AVAILABLE_LANGUAGES:
        session["language"] = language
        flash(get_message("language_changed"), "success")

    else:
        session["language"] = BABEL_DEFAULT
        flash(get_message("language_not_changed"), "warning")

    return redirect(url_for("home_blueprint.index"))


@blueprint.route("/index", methods=["GET", "POST"])
def index():
    """Index page. It contains the form to analyze an URL.
    Redirects to a loading page and then to the dashboard.

    Returns:
        function: renders a loading page
    """
    form = SearchURLForm(request.form)
    session["checks"] = {}

    if not form.validate_on_submit():
        for key in form.errors.keys():
            message = get_form_message(form.errors[key][0])
            flash(message, "warning")

        session["messages"] = {}

        return render_template(
            "home/index.html",
            form=form,
            segment=get_segment(request),
            available_models=Available_models.get_visible_models_ids_and_names_list(),
        )

    url = request.form["url"]
    selected_models = request.form["selected_models"]
    quick_analysis = 1 if request.form.get("checkbox-quick-scan") else 0

    session["messages"] = {
        "url": url.replace(" ", ""),
        "models": selected_models,
        "quick_analysis": quick_analysis,
    }

    return render_template("specials/processing-url.html")


def trigger_mock_dashboard(models_ids, quick_analysis):
    """Triggers the dashboard with mock values.
    Coded to make the development process faster.

    Args:
        models_ids (list): list of models ids
        quick_analysis (int): 0 or 1 (False or True)

    Returns:
        function: redirects to the dashboard
    """
    time.sleep(1.5)
    fv, fv_extra_information = get_mock_values_fv()
    session["messages"] = {
        "fv": fv.tolist(),
        "fv_extra_information": fv_extra_information,
        "url": "http://phishing.cat.com/query?param=login@microsoft",
        "models_ids": models_ids,
        "quick_analysis": quick_analysis,
        "colour_list": "black-list",
        "update_bbdd": False,
    }
    session["checks"] = {}
    return redirect(url_for("home_blueprint.dashboard"))


@blueprint.route("/extract_fv", methods=["POST", "GET"])
def extract_fv():
    """Gets the feature vector for an URL. If the URL is not
    callable, it tries to reconstruct it. If there is an
    existing instance on the DB returns the FV.

    Raises:
        KriniException: if the URL is not callable and it
                        cannot be reconstructed. However, it
                        is catched and the user is redirected
                        to the index page.
    Returns:
        function: redirects to the dashboard
    """
    try:
        messages = session.get("messages", None)
        url = messages["url"]
        models_ids = messages["models"]
        quick_analysis = messages["quick_analysis"]
        colour_list = ""
        fv_extra_information = {}
        update_bbdd = False

        if url == "mock":
            return trigger_mock_dashboard(models_ids, quick_analysis)

        callable_url = get_callable_url(url)

        if callable_url is None:
            previous_instance = Available_instances.query.filter_by(
                instance_URL=url
            ).first()
            if previous_instance and previous_instance.instance_fv:
                callable_url = url
                fv = list(previous_instance.instance_fv)
                colour_list = (
                    previous_instance.colour_list
                    if previous_instance.colour_list
                    else ""
                )
                quick_analysis = 1
                flash(
                    get_exception_message("url_not_callable_recuperable"),
                    "info",
                )

            else:
                raise KriniException("Url not callable")

        else:  # The URL is callable and has protocol
            previous_instance = Available_instances.query.filter_by(
                instance_URL=callable_url
            ).first()

            if (
                previous_instance
                and previous_instance.instance_fv
                and quick_analysis
            ):
                fv = list(previous_instance.instance_fv)
                colour_list = (
                    previous_instance.colour_list
                    if previous_instance.colour_list
                    else ""
                )

            else:
                fv, fv_extra_information = get_fv_and_info(callable_url)
                fv = fv.tolist()

                if previous_instance:
                    colour_list = (
                        previous_instance.colour_list
                        if previous_instance.colour_list
                        else ""
                    )
                else:
                    if current_user.is_authenticated:
                        update_bbdd = (
                            True  # Will be stored with majority voting tag
                        )
                    colour_list = ""

        session["messages"] = {
            "fv": fv,
            "fv_extra_information": fv_extra_information,
            "url": callable_url,
            "models_ids": models_ids,
            "quick_analysis": quick_analysis,
            "colour_list": colour_list,
            "update_bbdd": update_bbdd,
        }

        return redirect(url_for("home_blueprint.dashboard"))

    except KriniSSLException as e:
        flash(str(e), "danger")
        return redirect(url_for("home_blueprint.index"))

    except KriniException:
        flash(get_formatted_message("not_callable_url", [url]), "danger")
        flash(get_message("tip_urls"), "info")
        return redirect(url_for("home_blueprint.index"))

    except (KeyError, ValueError, TypeError):
        session["messages"] = {}
        session["checks"] = {}
        flash(get_exception_message("incorrect_stream"), "danger")
        return redirect(url_for("home_blueprint.index"))


@blueprint.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """Analyzes the URL feature vector with the selected models.
    Renders the dashboard. All exceptions are catched and the user
    is redirected to the index page when something unexpected happens.

    Returns:
        function: renders the dashboard
    """
    try:
        session["checks"] = {}
        messages = session.get("messages", None)

        if messages:
            url = messages["url"]
            fv = np.array(messages["fv"])
            selected_models = get_selected_models_ids(messages["models_ids"])

            if len(selected_models) == 0:
                raise KriniException(get_message("no_models_available"))

            if len(selected_models) > MAX_MODELS_DASHBOARD:
                selected_models = selected_models[:MAX_MODELS_DASHBOARD]
                flash(get_message("too_many_models"), "warning")

            classifiers_info_tuples = [
                get_model(model_id) for model_id in selected_models
            ]

            model_names = [tupla[0] for tupla in classifiers_info_tuples]
            classifiers = [tupla[1] for tupla in classifiers_info_tuples]
            model_scores = [tupla[2] for tupla in classifiers_info_tuples]

            predicted_tags = [int(cls.predict(fv)[0]) for cls in classifiers]
            count, numeric_class = get_sum_tags_numeric(predicted_tags)
            messages["numeric_class"] = numeric_class

            # Stores using majority voting
            if messages["update_bbdd"]:
                save_bbdd_analized_instance(
                    url, [float(feat) for feat in messages["fv"]], numeric_class
                )
                messages["update_bbdd"] = False

            models_confidence = []
            for cls, prediction in zip(classifiers, predicted_tags):
                confidences = cls.predict_proba(fv)[0]
                if len(confidences) == 2:
                    models_confidence.append(int(100 * confidences[prediction]))
                else:
                    models_confidence.append(100)

            information_to_display = {
                "url": url if numeric_class == 0 else sanitize_url(url),
                "quick_analysis": messages["quick_analysis"],
                "fv": list(fv),
                "fv_extra_information": messages["fv_extra_information"],
                "class": translate_tag(numeric_class),
                "colour-list": messages["colour_list"],
                "model_names": make_array_safe(model_names),
                "sum_tags_numeric": make_array_safe(count),
                "predicted_tags_labeled": make_array_safe(
                    [translate_tag(tag, True) for tag in predicted_tags]
                ),
                "model_scores": json.dumps(model_scores),
                "model_confidence": make_array_safe(models_confidence),
            }

            # If we want resutls to be reset, put {} instead of messages
            session["messages"] = messages

            return render_template(
                "home/dashboard.html",
                segment=get_segment(request),
                information_to_display=information_to_display,
                language=session.get("language", BABEL_DEFAULT),
            )

        raise KriniException(get_message("no_info_display_dashboard"))

    except KriniException as e:
        session["messages"] = {}
        flash(e.message, "danger")
        return redirect(url_for("home_blueprint.index"))

    except (KeyError, ValueError, TypeError):
        session["messages"] = {}
        flash(
            get_message("no_info_available")
            + " "
            + get_message("no_info_display_dashboard"),
            "danger",
        )
        return redirect(url_for("home_blueprint.index"))


@blueprint.route("/report_false_positive", methods=["GET"])
def report_false_positive():
    """Reports a false result to the database. The user must be logged in.
    Redirects to the dashboard flashing a message.

    Returns:
        function: redirects to the dashboard
    """
    try:
        session["checks"] = {}

        if not current_user.is_authenticated:
            raise KriniNotLoggedException(get_message("not_logged"))

        messages = session.get("messages", None)
        if messages:
            url = messages["url"]
            tag = messages["numeric_class"]
            existing_instance = Available_instances.query.filter_by(
                instance_URL=url
            ).first()

            if existing_instance:
                if tag == 1:
                    suggestion = Available_tags.sug_legitimate
                elif tag == 0:
                    suggestion = Available_tags.sug_phishing
                else:
                    suggestion = Available_tags.sug_review

                report = Candidate_instances(
                    user_id=current_user.id,
                    instance_id=existing_instance.instance_id,
                    date_reported=datetime.now(),
                    suggestions=suggestion,
                )

                db.session.add(report)
                db.session.commit()
                flash(get_message("false_positive_reported"), "success")
                return redirect(url_for("home_blueprint.dashboard"))
            raise KriniException(get_exception_message("not_instance_found"))

        raise ValueError(get_exception_message("not_info_found"))

    except KriniNotLoggedException:
        session["messages"] = {}
        flash(get_exception_message("log_to_report"), "warning")
        return redirect(url_for("home_blueprint.index"))

    except KriniException:
        flash(get_exception_message("report_url_error"), "warning")
        return redirect(url_for("home_blueprint.dashboard"))

    except (KeyError, ValueError, TypeError):
        session["messages"] = {}
        flash(get_exception_message("incorrect_stream"), "danger")
        return redirect(url_for("home_blueprint.index"))


@login_required
@blueprint.route("/profile", methods=["GET"])
def profile():
    """Renders the profile page. The user must be logged in.

    Raises:
        Forbidden: if the user is not logged in

    Returns:
        function: renders the profile page
    """
    if not current_user.is_authenticated:
        raise Forbidden()

    n_reports_accepted = (
        Users.query.filter_by(id=current_user.id).first().n_urls_accepted
    )

    if n_reports_accepted is None:
        n_reports_accepted = 0

    n_reports_reviewing = 0
    users_reports = Candidate_instances.query.options(
        load_only("user_id")
    ).all()
    users_reports = [report.user_id for report in users_reports]

    for user_report in users_reports:
        if current_user.id == user_report:
            n_reports_reviewing += 1

    session["messages"] = {}
    session["checks"] = {}

    return render_template(
        "home/profile.html",
        n_reports_accepted=n_reports_accepted,
        n_reports_reviewing=n_reports_reviewing,
        segment=get_segment(request),
    )


@login_required
@blueprint.route("/models", methods=["GET", "POST"])
def models(n_per_page=10):
    """Displays the models page. The user must be logged in.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the models page
    """
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        form = FlaskForm(request.form)

        if "selected_page" in request.form:
            page = int(request.form["selected_page"])
            previous_page = int(request.form["previous_page"])
            checks = session.get("checks", None)

            if "crear" in request.form["button_pressed"]:
                session["messages"] = {"previous_page": page}
                return redirect(url_for("home_blueprint.new_model"))

            if (
                "testear" in request.form["button_pressed"]
                or "editar" in request.form["button_pressed"]
            ):
                session["messages"] = {
                    "previous_page": page,
                    "model_id": request.form["individual_model"],
                    "action": request.form["button_pressed"],
                }
                return (
                    redirect(url_for("home_blueprint.test_model"))
                    if "testear" in request.form["button_pressed"]
                    else redirect(url_for("home_blueprint.edit_model"))
                )

            if "seleccionar" in request.form["button_pressed"]:
                checks = update_batch_checks(
                    request.form["button_pressed"],
                    checks,
                    previous_page,
                    n_per_page,
                    items_class=Available_models,
                )

            else:
                checks = update_checks(
                    previous_page,
                    request.form.getlist("checkbox-model"),
                    checks,
                    n_per_page,
                    items_class=Available_models,
                )

            if "eliminar" in request.form["button_pressed"]:
                if "individual" in request.form["button_pressed"]:
                    if remove_selected_models(
                        [request.form["individual_model"]]
                    ):
                        flash(get_message("model_removed"), "success")

                else:
                    selected = list(checks.values())
                    if len(selected) == 0:
                        flash(get_message("model_not_selected"), "warning")
                    elif remove_selected_models(selected):
                        flash(get_message("models_removed"), "success")

                return redirect(url_for("home_blueprint.models"))

        else:
            page = 1
            checks = {}

    except (KriniException, KeyError, ValueError, TypeError):
        flash(get_exception_message("error_operation"), "danger")

    session["checks"] = checks if checks else {}
    post_pagination = Available_models.all_paginated(page, n_per_page)
    post_pagination.items = get_models_view_dictionary(
        post_pagination.items, checks.values()
    )

    return render_template(
        "home/models-administration.html",
        segment=get_segment(request),
        post_pagination=post_pagination,
        selected=post_pagination.iter_pages(
            left_edge=1, left_current=1, right_current=1, right_edge=1
        ),
        form=form,
    )


@blueprint.route("/new_model", methods=["GET", "POST"])
def new_model():
    """
    Creates a new model. The user must be logged in.
    Controls the form to create a new model.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the new model page or redirects to the loading page
    """
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    form = ModelForm()
    session["checks"] = {}

    if "siguiente" in request.form and form.validate_on_submit():
        selected_method = translate_form_select_data_method(
            request.form["form_select_data_method"]
        )

        selected_algorithm = translate_form_select_algorithm(
            request.form["form_select_ssl_alg"]
        )

        if selected_method == "csv":
            selected_method, dataset_tuple = save_files_to_temp(
                form.uploaded_train_csv.data, form.uploaded_test_csv.data
            )

            if selected_method != "csv":
                flash(
                    get_exception_message("error_csv")
                    + " "
                    + get_exception_message("sets_generated_random"),
                    "danger",
                )

        # If the uploaded files are not valid, it also generates the dataset
        if selected_method == "generate":
            dataset_tuple = check_n_instances(
                request.form["train_percentage_instances"]
            )

        session["messages"] = {
            "form_data": request.form,
            "algorithm": selected_algorithm,
            "dataset_method": dataset_tuple,
        }

        return render_template("specials/creating-model.html")

    for key in form.errors.keys():
        message = get_form_message(form.errors[key][0])
        flash(message, "warning")

    return render_template(
        "home/new-model.html",
        form=form,
        segment=get_segment(request),
        language=session.get("language", BABEL_DEFAULT),
    )


@blueprint.route("/creating_model", methods=["GET"])
def creating_model():
    """
    Creates and serializes the model and saves it in the database.
    It also trains the model with the dataset.

    Raises:
        Forbidden: error 403 if the user is not authenticated/authorized

    Returns:
        function: renders the models page if the model is created,
                  otherwise it returns the new model page displaying
                  the errors
    """
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        messages = session.get("messages", None)
        form_data = messages["form_data"]
        session["checks"] = {}

        # The classifier object is created
        if int(form_data["random_state"]) == -1:
            random_state = None
        else:
            random_state = int(form_data["random_state"])

        if messages["algorithm"] == CO_FOREST_CONTROL:
            cls = get_co_forest(
                n_trees=int(form_data["n_trees"]),
                theta=float(form_data["thetha"]),
                max_features=form_data["max_features"],
                random_state=random_state,
            )

        elif messages["algorithm"] == TRI_TRAINING_CONTROL:
            cls = get_tri_training(
                h_0=form_data["cls_one_tt"],
                h_1=form_data["cls_two_tt"],
                h_2=form_data["cls_three_tt"],
                random_state=random_state,
            )

        elif messages["algorithm"] == DEMOCRATIC_CO_CONTROL:
            base_cls = [form_data["cls_one"]] * int(form_data["n_cls_one"])
            base_cls += [form_data["cls_two"]] * int(form_data["n_cls_two"])
            base_cls += [form_data["cls_three"]] * int(form_data["n_cls_three"])

            if len(base_cls) == 0:
                raise KriniException(get_exception_message("no_base_cls"))

            cls = get_democratic_co(
                base_cls=base_cls, random_state=random_state
            )

        # Dataset is extracted
        dataset_method, dataset_params = messages["dataset_method"]

        (
            X_train,
            X_test,
            y_train,
            y_test,
            train_ids,
            test_ids,
        ) = return_X_y_train_test(dataset_method, dataset_params, get_ids=True)

        try:
            L_train, U_train, Ly_train, _ = train_test_split(
                X_train,
                y_train,
                test_size=0.8,
                stratify=y_train,
            )
        except ValueError:
            raise KriniException(get_exception_message("few_instances"))

        cls.fit(L_train, Ly_train, U_train)
        y_pred = cls.predict(X_test)
        y_pred_proba = cls.predict_proba(X_test)
        scores, message = get_array_scores(y_test, y_pred, y_pred_proba, True)

        if message:
            flash(message, "warning")

        # Model is serialized and stored. Also the train data.
        train_ids = set(train_ids)
        if train_ids.intersection(set(test_ids)):
            flash(get_message("optimistic_scores"), "info")

        if serialize_store_model(
            form_data, cls, scores, train_ids, messages["algorithm"]
        )[0]:
            flash(get_message("model_stored"), "success")

        return redirect(url_for("home_blueprint.models"))

    except KriniException as e:
        flash(str(e), "danger")
        session["messages"] = {}
        return redirect(url_for("home_blueprint.new_model"))

    except (ValueError, KeyError, TypeError):
        flash(get_exception_message("incorrect_stream"), "danger")
        session["messages"] = {}
        return redirect(url_for("home_blueprint.models"))


@login_required
@blueprint.route("/test_model", methods=["POST", "GET"])
def test_model():
    """
    Allows the user to test a model with a dataset
    (either uploaded or generated randomly).

    Raises:
        Forbidden: if the user is not authenticated/authorized

    Returns:
        function: renders the test model page if the model is tested,
                  or the models page if there is a major exception
    """
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    session["checks"] = {}

    try:
        form = TestModelForm()  # DO NOT INCLUDE REQUEST.FORM, FILES FAIL
        messages = session.get("messages", None)
        if "testear" not in messages["action"]:
            raise ValueError
        model_id = int(messages["model_id"])
        model = Available_models.query.get(model_id)
        analysis_scores = model.model_scores

        if "siguiente" in request.form:
            update_bd = 1 if request.form.get("checkbox-update-db") else 0
            omit_ids = 1 if request.form.get("checkbox-exclude-train") else 0

            # Model is unpickled
            cls = deserialize_model(model.file_name)

            # Test dataset is obtained
            selected_method = translate_form_select_data_method(
                request.form["form_select_data_method"]
            )

            if selected_method == "csv":
                try:
                    selected_method, params = save_files_to_temp(
                        form.uploaded_test_csv.data
                    )[1]

                    if selected_method != "csv":
                        raise ValueError

                    X_test, y_test = return_X_y_single(
                        selected_method,
                        model_id=model_id,
                        files_dict=params,
                        omit_train_ids=omit_ids,
                    )

                except ValueError:
                    raise KriniException(get_exception_message("error_csv"))

            if selected_method == "generate":
                X_test, y_test = return_X_y_single(
                    selected_method, model_id=model_id, omit_train_ids=omit_ids
                )

            if len(X_test) == 0:
                analysis_scores = model.model_scores
                raise KriniException(get_exception_message("no_test_available"))

            # Model is tested and updated
            y_pred = cls.predict(X_test)
            y_pred_proba = cls.predict_proba(X_test)
            analysis_scores, message = get_array_scores(
                y_test, y_pred, y_pred_proba, True
            )

            if message:
                flash(message, "warning")

            if update_bd:
                update_model_scores_db(model, analysis_scores)

            if not omit_ids:
                flash(get_message("warning_duplicates"), "info")

            if update_bd:
                flash(get_message("test_success_update_db"), "success")

            else:
                flash(get_message("test_success"), "success")

        return render_template(
            "home/test-model.html",
            model=get_model_dict(model),
            segment=get_segment(request),
            form=form,
            scores=json.dumps([analysis_scores]),
        )

    except KriniException as e:
        flash(str(e), "danger")
        return render_template(
            "home/test-model.html",
            model=get_model_dict(model),
            segment=get_segment(request),
            form=form,
            scores=json.dumps([analysis_scores]),
        )

    except (
        exc.SQLAlchemyError,
        AttributeError,
        PickleError,
        FileNotFoundError,
    ):
        session["messages"] = {}
        flash(get_exception_message("error_load_model"), "danger")
        return redirect(url_for("home_blueprint.models"))

    except (KeyError, ValueError, TypeError):
        session["messages"] = {}
        flash(get_exception_message("incorrect_stream"), "danger")
        return redirect(url_for("home_blueprint.models"))


@login_required
@blueprint.route("/edit_model", methods=["POST", "GET"])
def edit_model():
    """
    Allows the user to edit few parameters of a model.
    The serialized model name is also updated.

    Raises:
        Forbidden: if the user is not authenticated/authorized

    Returns:
        function: renders the test model page if the model is tested,
                  or the models page if there is a major exception
    """
    session["checks"] = {}
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        form = SmallModelForm()
        messages = session.get("messages", None)
        if "editar" not in messages["action"]:
            raise ValueError
        model_id = int(messages["model_id"])
        model = Available_models.query.get(model_id)

        if "siguiente" in request.form and form.validate_on_submit():
            if update_model(model, request.form):
                flash(get_message("model_updated"), "success")
            return redirect(url_for("home_blueprint.models"))

        for key in form.errors.keys():
            message = get_form_message(form.errors[key][0])
            flash(message, "warning")

        return render_template(
            "home/edit-model.html",
            model=get_model_dict(model),
            segment=get_segment(request),
            form=form,
        )

    except KriniException as e:
        flash(str(e), "danger")

    except (exc.SQLAlchemyError, AttributeError):
        flash(get_exception_message("error_load_model"), "danger")

    except (KeyError, ValueError, TypeError):
        flash(get_exception_message("incorrect_stream"), "danger")

    session["messages"] = {}
    return redirect(url_for("home_blueprint.models"))


@login_required
@blueprint.route("/instances", methods=["GET", "POST"])
def instances(n_per_page=10):
    """Main page of the instances. The user must be logged in and be an admin.

    Args:
        n_per_page (int, optional): Number of instances displayed. Defaults to 10.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the instances page in the selected page
    """
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        form = FlaskForm(request.form)

        if "selected_page" in request.form:
            page = int(request.form["selected_page"])
            previous_page = int(request.form["previous_page"])
            checks = session.get("checks", None)
            checks = update_checks(
                previous_page,
                request.form.getlist("checkbox-instance"),
                checks,
                n_per_page,
            )

            if "eliminar" in request.form["button_pressed"]:
                if "individual" in request.form["button_pressed"]:
                    remove_selected_instances(
                        [request.form["individual_instance"]]
                    )
                    flash(get_message("instance_deleted"), "success")

                else:
                    selected = list(checks.values())
                    if len(selected) > 0:
                        remove_selected_instances(list(checks.values()))
                        flash(get_message("instances_deleted"), "success")
                    else:
                        flash(get_message("instance_not_selected"), "warning")

                return redirect(url_for("home_blueprint.instances"))

            if "editar" in request.form["button_pressed"]:
                session["messages"] = {
                    "previous_page": page,
                    "instance_id": request.form["individual_instance"],
                }
                session["checks"] = {}
                return redirect(url_for("home_blueprint.edit_instance"))

            if "crear" in request.form["button_pressed"]:
                session["messages"] = {"previous_page": page}
                session["checks"] = {}
                return redirect(url_for("home_blueprint.new_instance"))

            if "seleccionar" in request.form["button_pressed"]:
                checks = update_batch_checks(
                    request.form["button_pressed"],
                    checks,
                    previous_page,
                    n_per_page,
                )

            elif request.form["button_pressed"] == "descargar":
                filename = "selected_instances.csv"
                download_path = create_csv_selected_instances(
                    list(checks.values()), filename
                )

                @after_this_request
                def remove_file(response):
                    remove(download_path)
                    return response

                return send_from_directory(
                    get_temporary_download_directory(),
                    filename,
                    as_attachment=True,
                )

        else:
            page = 1
            checks = {}

    except KriniDBException as e:
        flash(str(e), "warning")

    except KriniException:
        flash(get_exception_message("error_operation"), "danger")

    except (KeyError, ValueError, TypeError):
        flash(get_exception_message("incorrect_stream"), "danger")

    session["checks"] = checks if checks else {}
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


@login_required
@blueprint.route("/edit_instance", methods=["GET", "POST"])
def edit_instance():
    """Edits the selected instance. The user must be logged in and be an admin.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the updating page
    """
    session["checks"] = {}
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        form = InstanceForm()
        messages = session.get("messages", None)
        selected_instance = Available_instances.query.filter_by(
            instance_id=messages["instance_id"]
        ).first()
        instance_tags = selected_instance.instance_labels
        initial_value = (
            ",".join(instance_tags) if instance_tags is not None else ""
        )
        instance_dict = get_instance_dict(selected_instance)

        if "siguiente" in request.form:
            session["messages"] = {
                "form_data": request.form,
                "instance_id": selected_instance.instance_id,
                "instance_URL": selected_instance.instance_URL,
                "operation": "edit",
            }

            return render_template("specials/updating-instance.html")

        return render_template(
            "home/edit-instance.html",
            form=form,
            segment="instances",
            instance_tags=Available_tags.all_tags,
            initial_value=initial_value,
            operation="edit",
            instance_dict=instance_dict,
        )

    except KriniException:
        flash(get_exception_message("error_operation"), "danger")
        flash(get_exception_message("check_labels_length"), "info")
        return redirect(url_for("home_blueprint.instances"))

    except (KeyError, ValueError, TypeError):
        flash(get_exception_message("incorrect_stream"), "danger")
        return redirect(url_for("home_blueprint.instances"))


@login_required
@blueprint.route("/new_instance", methods=["GET", "POST"])
def new_instance():
    """Creates an instance. The user must be logged in and be an admin.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the updating page
    """
    session["checks"] = {}
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        form = InstanceForm()
        initial_value = ""
        instance_dict = get_instance_dict(-1, empty=True)
        validated = True
        form.validate_on_submit()

        for key in form.errors.keys():
            val = form.errors[key][0]
            if val in ("empty_url", "url_too_long"):
                validated = False
                flash(get_form_message(val), "warning")
                break

        if "siguiente" in request.form and validated:
            session["messages"] = {
                "form_data": request.form,
                "instance_id": -1,
                "instance_URL": request.form["url"],
                "operation": "new",
            }

            return render_template("specials/updating-instance.html")

        return render_template(
            "home/edit-instance.html",
            form=form,
            segment="instances",
            instance_tags=Available_tags.all_tags,
            initial_value=initial_value,
            operation="new",
            instance_dict=instance_dict,
        )

    except KriniException:
        session["messages"] = {}
        flash(get_exception_message("error_operation"), "danger")
        flash(get_exception_message("check_labels_length"), "info")
        return redirect(url_for("home_blueprint.instances"))


@blueprint.route("/updating_instance", methods=["POST", "GET"])
def updating_instance():
    """Loading page while the instance is updated. The user must be logged in
    and be an admin. ATOMICITY IS GUARANTEED.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the instances page
    """
    session["checks"] = {}
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        messages = session.get("messages", None)
        form_data = messages["form_data"]

        if messages["operation"] == "edit":
            selected_instance = Available_instances.query.filter_by(
                instance_id=messages["instance_id"]
            ).first()

        elif messages["operation"] == "new":
            instance_URL = messages["instance_URL"].replace(" ", "")
            selected_instance = Available_instances(instance_URL=instance_URL)
            db.session.add(selected_instance)
            db.session.flush()

        selected_labels = form_data["labels"]
        selected_labels = selected_labels.replace(" ", "")
        selected_labels = selected_labels.split(",")

        # Instance is updated
        if form_data["instance_class"] != "-1":
            selected_instance.instance_class = int(form_data["instance_class"])

        if form_data["instance_list"] == "black-list":
            selected_instance.colour_list = Available_tags.black_list
            selected_labels.append(Available_tags.black_list)
            if Available_tags.white_list in selected_labels:
                selected_labels.remove(Available_tags.white_list)

        elif form_data["instance_list"] == "white-list":
            selected_instance.instance_list = Available_tags.white_list
            selected_labels.append(Available_tags.white_list)
            if Available_tags.black_list in selected_labels:
                selected_labels.remove(Available_tags.black_list)

        selected_instance.instance_labels = list(set(selected_labels))
        selected_instance.reviewed_by = current_user.id

        if form_data["regenerate_fv"] != "-1":
            callable_url = get_callable_url(messages["instance_URL"])

            if callable_url is None:
                raise KriniException("No se puede llamar la URL.")

            fv = get_fv_and_info(callable_url)[0]
            selected_instance.instance_fv = fv.tolist()

        else:
            time.sleep(1.5)  # To show the loading page

        db.session.commit()
        session["messages"] = {}
        flash(get_message("successful_operation"), "success")
        return redirect(url_for("home_blueprint.instances"))

    except KriniException:
        flash(get_exception_message("vector_not_generated"), "danger")
        db.session.rollback()

    except exc.SQLAlchemyError:
        flash(get_exception_message("error_operation"), "danger")
        flash(get_message("warning_check_duplicate_instance"), "info")
        db.session.rollback()

    except (KeyError, ValueError, TypeError):
        flash(get_exception_message("incorrect_stream"), "danger")

    session["messages"] = {}
    return redirect(url_for("home_blueprint.instances"))


@login_required
@blueprint.route("/review_instances", methods=["GET", "POST"])
def review_instances(n_per_page=10):
    """Reviews for the reports. The user must be logged in and be an admin.

    Args:
        n_per_page (int, optional): Number of reports displayed. Defaults to 10.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the review page in the selected page
    """
    if not current_user.is_authenticated or current_user.user_rol != "admin":
        raise Forbidden()

    try:
        form = FlaskForm(request.form)

        if "selected_page" in request.form:
            page = int(request.form["selected_page"])
            previous_page = int(request.form["previous_page"])
            checks = session.get("checks", None)
            checks = update_checks(
                previous_page,
                request.form.getlist("checkbox-instance"),
                checks,
                n_per_page,
                sequence=True,
            )

            if "seleccionar" in request.form["button_pressed"]:
                checks = update_batch_checks(
                    request.form["button_pressed"],
                    checks,
                    previous_page,
                    n_per_page,
                    sequence=True,
                )

            elif "eliminar" in request.form["button_pressed"]:
                if len(checks.values()) == 0:
                    flash(get_message("reviews_not_selected"), "warning")
                elif remove_selected_reports(checks.values(), n_per_page):
                    flash(get_message("reviews_deleted"), "success")
                else:
                    flash(get_message("reviews_not_deleted"), "danger")
                return redirect(url_for("home_blueprint.review_instances"))

            if (
                "aceptar" in request.form["button_pressed"]
                or "descartar" in request.form["button_pressed"]
            ):
                selected_report = find_candidate_instance_sequence(
                    previous_page,
                    n_per_page,
                    int(request.form["report_number"]),
                )

                if update_report(
                    selected_report, request.form["button_pressed"]
                ):
                    flash(get_message("successful_operation"), "success")
                    return redirect(url_for("home_blueprint.review_instances"))
                flash(get_exception_message("error_operation"), "danger")

        else:
            page = 1
            checks = {}

    except KriniException:
        flash(get_exception_message("error_operation"), "danger")

    except (KeyError, ValueError, TypeError):
        flash(get_exception_message("incorrect_stream"), "danger")

    session["checks"] = checks if checks else {}
    post_pagination = Candidate_instances.all_paginated(page, n_per_page)
    post_pagination.items = get_candidate_instances_view_dictionary(
        post_pagination.items, checks.values(), page, n_per_page
    )

    return render_template(
        "home/instances-review.html",
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
    """Saves the reported instance in the database if it is not already there
    and adds the report to the database.

    Raises:
        Forbidden: error 403 if the user is not authenticated

    Returns:
        function: renders the report-url.html template with a flash
                  message that indicates the status of the report
    """
    session["checks"] = {}
    if not current_user.is_authenticated:
        raise Forbidden()

    form = ReportURLForm(request.form)

    if "report" in request.form and form.validate_on_submit():
        try:
            url = request.form["url"]
            url = url.replace(" ", "")
            report_type = request.form["type"]

            if report_type == "black-list":
                report_type = Available_tags.sug_black_list
            elif report_type == "white-list":
                report_type = Available_tags.sug_white_list

            existing_instance = Available_instances.query.filter_by(
                instance_URL=url
            ).first()
            if not existing_instance:
                existing_instance = Available_instances(
                    instance_URL=url,
                    instance_labels=(
                        [
                            Available_tags.sug_new_instance,
                            Available_tags.sug_review,
                        ],
                    ),
                )
                db.session.add(existing_instance)
                db.session.flush()

            db.session.add(
                Candidate_instances(
                    instance_id=existing_instance.instance_id,
                    user_id=current_user.id,
                    date_reported=datetime.now(),
                    suggestions=report_type,
                )
            )

            db.session.commit()
            flash(get_message("url_reported"), "success")

        except exc.SQLAlchemyError:
            flash(get_exception_message("error_operation"), "danger")
            db.session.rollback()

        return redirect(url_for("home_blueprint.report_url"))

    for key in form.errors.keys():
        message = get_form_message(form.errors[key][0])
        flash(message, "warning")

    return render_template(
        "home/report-url.html", form=form, segment=get_segment(request)
    )


@blueprint.route("/heroku_timeout")
def heroku_timeout():
    """Renders the Heroku timeout template.

    Returns:
        render_template: renders the template
    """
    return render_template("specials/page-408.html")


@blueprint.route("/<template>")
def route_template(template):
    """Renders the template passed as parameter.

    Args:
        template (str): template name

    Returns:
        render_template: renders the template
    """
    try:
        return render_template("specials/page-404.html"), 404

    except:  # skipcq: FLK-E722
        return render_template("specials/page-500.html"), 500


@blueprint.errorhandler(403)
def access_forbidden(error):
    """Handles the 403 error.

    Args:
        error (object): error object

    Returns:
        render_template: renders the template for error 403
    """
    return render_template("specials/page-403.html"), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    """Handles the 404 error.

    Args:
        error (object): error object

    Returns:
        render_template: renders the template for error 404
    """
    return render_template("specials/page-404.html"), 404


@blueprint.errorhandler(408)
def timeout_error(error):
    """Handles the 408 error.

    Args:
        error (object): error object

    Returns:
        render_template: renders the template for error 408
    """
    return render_template("specials/page-408.html"), 408


@blueprint.errorhandler(500)
def internal_error(error):
    """Handles the 500 error.

    Args:
        error (object): error object

    Returns:
        render_template: renders the template for error 500
    """
    return render_template("specials/page-500.html"), 500
