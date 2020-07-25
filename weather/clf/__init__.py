from flask import Blueprint

weather_clf = Blueprint(
    'weather clf',
    __name__
)

from . import views
