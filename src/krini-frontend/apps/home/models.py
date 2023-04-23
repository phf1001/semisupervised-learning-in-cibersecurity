#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
@File    :   models.py
@Time    :   2023/03/30 21:06:32
@Author  :   Patricia Hernando Fernández 
@Version :   2.0
@Contact :   phf1001@alu.ubu.es
"""
from apps import db
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.exc import SQLAlchemyError


class Available_instances(db.Model):
    """
    Create an Available_instances table containing the
    URLs that are available for the user to use.

    Args:
        db.Model (class): SQLAlchemy model class

    Returns:
        object: SQLAlchemy model object
    """

    __tablename__ = "Available_instances"

    instance_id = db.Column(db.Integer, primary_key=True)
    reviewed_by = db.Column(
        db.Integer, db.ForeignKey("Users.id"), nullable=True
    )
    instance_URL = db.Column(db.String(64), unique=True, nullable=False)
    instance_fv = db.Column(MutableList.as_mutable(db.ARRAY(db.Float)))
    instance_class = db.Column(db.Integer)
    colour_list = db.Column(db.String(64))
    instance_labels = db.Column(MutableList.as_mutable(db.ARRAY(db.String(64))))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return str(self.instance_id) + " " + str(self.instance_URL)

    @staticmethod
    def all_paginated(page=1, per_page=15):
        """Returns a SQLAlchemy pagination object with the items in that page.

        Args:
            page (int, optional): Page to display. Defaults to 1.
            per_page (int, optional): Number of items per page. Defaults to 15.

        Returns:
            object: SQLAlchemy pagination object
        """
        return Available_instances.query.paginate(page, per_page, False)


class Candidate_instances(db.Model):
    """
    Create a Candidate_instances table.
    This table will contain the instances reported
    by users that are not yet in the Available_instances table
    and will be once they are reviewed by an admin.

    Args:
        db.Model (class): SQLAlchemy model class

    Returns:
        object: SQLAlchemy model object
    """

    __tablename__ = "Candidate_instances"

    date_reported = db.Column(db.DateTime, primary_key=True)
    instance_id = db.Column(
        db.Integer,
        db.ForeignKey("Available_instances.instance_id"),
        primary_key=True,
    )
    user_id = db.Column(db.Integer, db.ForeignKey("Users.id"), primary_key=True)
    suggestions = db.Column(db.Text, nullable=False)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return (
            str(self.instance_id)
            + " "
            + str(self.date_reported)
            + " "
            + str(self.user_id)
            + " "
            + str(self.suggestions)
        )

    @staticmethod
    def all_paginated(page=1, per_page=15):
        """Returns a SQLAlchemy pagination object with the items in that page.

        Args:
            page (int, optional): Page to display. Defaults to 1.
            per_page (int, optional): Number of items per page. Defaults to 15.

        Returns:
            object: SQLAlchemy pagination object
        """
        return Candidate_instances.query.paginate(page, per_page, False)

    @staticmethod
    def get_instance(instance_id):
        return Candidate_instances.query.filter_by(
            instance_id=instance_id
        ).first()

    @staticmethod
    def get_instance_by_user(instance_id, user_id):
        return Candidate_instances.query.filter_by(
            instance_id=instance_id, user_id=user_id
        ).first()

    @staticmethod
    def get_instance_url(instance_id):
        return (
            Available_instances.query.filter_by(instance_id=instance_id)
            .first()
            .instance_URL
        )


class Available_tags:
    """
    Create an Available_tags table containing the
    tags that are available for the instances.
    """

    black_list = "black-list"
    white_list = "white-list"
    auto_classified = "auto-classified"
    reviewed = "reviewed"

    sug_white_list = "suggestion-white-list"
    sug_black_list = "suggestion-black-list"
    sug_phishing = "suggestion-phishing"
    sug_legitimate = "suggestion-legitimate"

    sug_new_instance = "new-instance"
    sug_review = "recommendation-review"
    sug_new_report = "suggestion-review-new-scanned"

    suggestion_tags = [
        sug_white_list,
        sug_black_list,
        sug_phishing,
        sug_legitimate,
        sug_new_instance,
        sug_review,
        sug_new_report,
    ]
    all_tags = [
        black_list,
        white_list,
        auto_classified,
        sug_white_list,
        sug_black_list,
        sug_phishing,
        sug_legitimate,
        sug_new_instance,
        sug_review,
        sug_new_report,
        reviewed,
    ]

    @staticmethod
    def get_colour(tag):
        if (
            tag == Available_tags.white_list
            or tag == Available_tags.sug_white_list
        ):
            return "#58B1CD"

        if (
            tag == Available_tags.black_list
            or tag == Available_tags.sug_black_list
        ):
            return "#878C8A"

        if tag == Available_tags.auto_classified:
            return "#CE7E00"

        if tag == Available_tags.sug_phishing:
            return "#E96A61"

        if tag == Available_tags.sug_legitimate:
            return "#7bbE5E"

        if tag == Available_tags.sug_new_instance:
            return "#800080"

        if tag == Available_tags.sug_review:
            return "#BAB55E"

        if tag == Available_tags.sug_new_report:
            return "#FF00A9"

        if tag == Available_tags.reviewed:
            return "#3FB59E"

        else:
            return "#FF7518"


class Available_models(db.Model):
    """
    Create a Available_models table.
    This table will contain the models
    that are available for the user to choose.

    Args:
        db.Model (class): SQLAlchemy model class

    Returns:
        object: SQLAlchemy model object
    """

    __tablename__ = "Available_models"

    model_id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(
        db.Integer, db.ForeignKey("Users.id"), nullable=False
    )
    model_name = db.Column(db.String(64), unique=True, nullable=False)
    file_name = db.Column(db.String(64), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime)
    is_default = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)
    model_scores = db.Column(
        MutableList.as_mutable(db.ARRAY(db.Float)),
        default=[0.0, 0.0, 0.0, 0.0, 0.0],
    )
    random_state = db.Column(db.Integer)
    model_notes = db.Column(db.String(128))
    model_algorithm = db.Column(db.String(2), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "gm",
        "polymorphic_on": model_algorithm,
    }

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.model_id)

    @staticmethod
    def get_models_ids_and_names_list():
        """Returns a list of tuples with the model id and name

        Returns:
            list: list of tuples with the model id and name
        """
        models = Available_models.query.all()
        return [(model.model_id, model.model_name) for model in models]

    @staticmethod
    def get_visible_models_ids_and_names_list():
        """Returns a list of tuples with the model id and name
        if the model is visible.

        Returns:
            list: list of tuples with the model id and name
        """
        models = Available_models.query.all()
        return [
            (model.model_id, model.model_name)
            for model in models
            if model.is_visible
        ]

    @staticmethod
    def update_default_model(model_id):
        """Updates the default model to the model with the given id.

        Args:
            model_id (int): id of the model to be set as default.

        Returns:
            bool: True if the model was updated, False otherwise.
        """
        try:
            default_models = Available_models.query.filter_by(
                is_default=True
            ).all()
            for model in default_models:
                model.is_default = False

            model = Available_models.query.filter_by(model_id=model_id).first()
            if model:
                model.is_default = True
                db.session.commit()
                return True
            else:
                raise SQLAlchemyError

        except SQLAlchemyError:
            db.session.rollback()
            return False

    @staticmethod
    def all_paginated(page=1, per_page=15):
        """Returns a SQLAlchemy pagination object with the items in that page.

        Args:
            page (int, optional): Page to display. Defaults to 1.
            per_page (int, optional): Number of items per page. Defaults to 15.

        Returns:
            object: SQLAlchemy pagination object
        """
        return Available_models.query.paginate(page, per_page, False)


class Available_co_forests(Available_models):
    """
    Create a Available_co_forests table.
    This table will contain the co-forests
    that are available for the user to choose.

    Args:
        Available_models (class): parent class
    """

    __tablename__ = "Available_co_forests"
    model_id = db.Column(
        None,
        db.ForeignKey("Available_models.model_id", ondelete="CASCADE"),
        primary_key=True,
    )
    n_trees = db.Column(db.Integer, default=6, nullable=False)
    thetha = db.Column(db.Float, default=0.75, nullable=False)
    max_features = db.Column(db.String(8), default="log2", nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "cf",
    }


class Available_tri_trainings(Available_models):
    """
    Create a Available_tri_trainings table.
    This table will contain the tri-trainings
    that are available for the user to choose.

    Args:
        Available_models (class): parent class
    """

    __tablename__ = "Available_tri_trainings"
    model_id = db.Column(
        None,
        db.ForeignKey("Available_models.model_id", ondelete="CASCADE"),
        primary_key=True,
    )
    cls_one = db.Column(db.String(8), nullable=False)
    cls_two = db.Column(db.String(8), nullable=False)
    cls_three = db.Column(db.String(8), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "tt",
    }


class Available_democratic_cos(Available_models):
    """
    Create a Available_democratic_cos table.
    This table will contain the democratic-cos
    that are available for the user to choose.

    Args:
        Available_models (class): parent class
    """

    __tablename__ = "Available_democratic_cos"
    model_id = db.Column(
        None,
        db.ForeignKey("Available_models.model_id", ondelete="CASCADE"),
        primary_key=True,
    )
    n_clss = db.Column(db.Integer, default=3, nullable=False)
    base_clss = db.Column(
        MutableList.as_mutable(db.ARRAY(db.String(8))), nullable=False
    )

    __mapper_args__ = {
        "polymorphic_identity": "dc",
    }


class Model_is_trained_with(db.Model):
    """
    Create a relation table storing which
    instances have been used to train a model.

    Args:
        db.Model (class): SQLAlchemy model class

    Returns:
        object: SQLAlchemy model object
    """

    __tablename__ = "Model_is_trained_with"

    instance_id = db.Column(
        db.Integer,
        db.ForeignKey("Available_instances.instance_id", ondelete="CASCADE"),
        primary_key=True,
    )
    model_id = db.Column(
        db.Integer,
        db.ForeignKey("Available_models.model_id", ondelete="CASCADE"),
        primary_key=True,
    )

    def __repr__(self):
        return str(self.instance_id) + " " + str(self.model_id)

    def __init__(self, id_model, id_instance):
        self.model_id = id_model
        self.instance_id = id_instance
