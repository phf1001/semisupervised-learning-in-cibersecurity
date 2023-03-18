from apps import db
from decouple import config
from apps import create_app
from apps.config import config_dict
import enum
from sqlalchemy import Integer, Enum
from sqlalchemy.ext.mutable import MutableList

DEBUG = config("DEBUG", default=True, cast=bool)
get_config_mode = "Debug" if DEBUG else "Production"

try:
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit("Error: Invalid <config_mode>. Expected values [Debug, Production] ")

app = create_app(app_config)
app.app_context().push()


# class Available_tags(enum.Enum):
#     """
#     Create an Available_tags table containing the
#     tags that are available for the instances.
#     """
#     white_list = 1
#     black_list = 2
#     nueva = 3
#     revisar = 4
#     mal_etiquetada_clasificador = 5
#     sug_white_list = 6
#     sug_black_list = 7
#     sug_phishing = 8
#     sug_legitimate = 9


class Available_tags:
    """
    Create an Available_tags table containing the
    tags that are available for the instances.
    """

    tags = [
        "white_list",
        "black_list",
        "nueva",
        "revisar",
        "mal_etiquetada_clasificador",
        "sug_white_list",
        "sug_black_list",
        "sug_phishing",
        "sug_legitimate",
    ]

    black_list = "black_list"
    white_list = "white_list"
    nueva = "nueva"
    revisar = "revisar"
    mal_etiquetada_clasificador = "mal_etiquetada_clasificador"
    sug_white_list = "sug_white_list"
    sug_black_list = "sug_black_list"
    sug_phishing = "sug_phishing"
    sug_legitimate = "sug_legitimate"


class Available_instances(db.Model):
    """
    Create an Available_instances table containing the
    URLs that are available for the user to use.
    """

    __tablename__ = "Available_instances"

    instance_id = db.Column(db.Integer, primary_key=True)
    instance_URL = db.Column(db.String(64), unique=True)
    date = db.Column(db.DateTime)
    reported_by = db.Column(db.Integer, db.ForeignKey("Users.id"))
    reviewed_by = db.Column(db.Integer, db.ForeignKey("Users.id"))
    instance_class = db.Column(db.Integer)
    instance_fv = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)))
    tags = db.Column(
        MutableList.as_mutable(db.ARRAY(db.String(64)))
    )  # db.Column(db.ARRAY(Enum(Available_tags)))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return (
            str(self.instance_id)
            + " "
            + str(self.instance_URL)
            + " "
            + str(self.reported_by)
            + " "
            + str(self.reviewed_by)
        )


class Candidate_instances(db.Model):
    """
    Create a Candidate_instances table.
    This table will contain the instances reported
    by users that are not yet in the Available_instances table
    and will be once they are reviewed by an admin.
    """

    __tablename__ = "Candidate_instances"

    instance_id = db.Column(db.Integer, primary_key=True)
    instance_URL = db.Column(db.String(64), unique=True, nullable=False)
    reported_by = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)))
    date = db.Column(MutableList.as_mutable(db.ARRAY(db.DateTime)))
    suggestions = db.Column(MutableList.as_mutable(db.ARRAY(db.String(64))))
    instance_fv = db.Column(MutableList.as_mutable(db.ARRAY(db.Integer)))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return (
            str(self.instance_id)
            + " "
            + str(self.instance_URL)
            + " "
            + str(self.reported_by)
            + " "
            + str(self.suggestions)
        )


class Available_models(db.Model):
    """
    Create a Available_models table.
    This table will contain the models
    that are available for the user to choose.
    """

    __tablename__ = "Available_models"

    model_id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    model_name = db.Column(db.String(64), unique=True, nullable=False)
    file_name = db.Column(db.String(16), unique=True, nullable=False)
    creation_date = db.Column(db.DateTime)
    is_default = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True)
    model_scores = db.Column(MutableList.as_mutable(db.ARRAY(db.Float)), default=[0.0, 0.0, 0.0])
    random_state = db.Column(db.Integer)
    model_notes = db.Column(db.String(128))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, "__iter__") and not isinstance(value, str):
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.model_id)

    @staticmethod
    def get_models_ids_and_names_list():
        """
        Returns a list of tuples with the model id and name
        """
        models = Available_models.query.all()
        return [(model.model_id, model.model_name) for model in models]


class Available_co_forests(Available_models):

    __tablename__ = "Available_co_forests"
    model_id = db.Column(None, db.ForeignKey("Available_models.model_id"), primary_key=True)
    n_trees = db.Column(db.Integer, default=6, nullable=False)
    thetha = db.Column(db.Float, default=0.75, nullable=False)
    max_features = db.Column(db.String(8), default='log2', nullable=False)

class Available_tri_trainings(Available_models):

    __tablename__ = "Available_tri_trainings"
    model_id = db.Column(None, db.ForeignKey("Available_models.model_id"), primary_key=True)
    cls_one = db.Column(db.String(8), nullable=False)
    cls_two = db.Column(db.String(8), nullable=False)
    cls_three = db.Column(db.String(8), nullable=False)

class Available_democratic_cos(Available_models):

    __tablename__ = "Available_democratic_cos"
    model_id = db.Column(None, db.ForeignKey("Available_models.model_id"), primary_key=True)
    n_clss = db.Column(db.Integer, default=3, nullable=False)
    base_clss = db.Column(MutableList.as_mutable(db.ARRAY(db.String(8))), nullable=False)