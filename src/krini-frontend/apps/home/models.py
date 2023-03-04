
from apps import db, login_manager


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
    