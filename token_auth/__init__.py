from flask import Blueprint

token_auth = Blueprint(
    'token auth',
    __name__
)

from . import views
