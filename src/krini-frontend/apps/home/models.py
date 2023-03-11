
from apps import db
from decouple import config
from apps import create_app
from apps.config import config_dict
from sqlalchemy.dialects.postgresql import ENUM as pgEnum
from enum import Enum, unique

DEBUG = config('DEBUG', default=True, cast=bool)
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
app.app_context().push()


class Reported_URL(db.Model):
    """
    Create a Reported_URL table containing the 
    URLs that have been reported by logged users. 
    Acts like blacklist/whitelist.
    """

    __tablename__ = 'Reported_URLs'

    url_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(64))
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.url_id)


class Repeated_URL(db.Model):
    """
    Create a Repeated_URL table
    This table will contain the URLs that have been
    reported more than once and should be reviewerd 
    by an admin because the type reported is different
    than the one that was already stored.
    """

    __tablename__ = 'Repeated_URLs'

    url_id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64), db.ForeignKey('Reported_URLs.url'), unique=True, nullable=False)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]

            setattr(self, property, value)

    def __repr__(self):
        return str(self.url_id)


  
class Available_models(db.Model):
    """
    Create a Available_models table.
    This table will contain the models
    that are available for the user to choose.
    """

    __tablename__ = 'Available_models'

    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(64), unique=True, nullable=False)
    file_name = db.Column(db.String(64), unique=True, nullable=False)
    #algorithm = db.Column()

    def __init__(self, **kwargs):
        for property, value in kwargs.items():

            if hasattr(value, '__iter__') and not isinstance(value, str):
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
    

class CoForest_model(Available_models):
    pass