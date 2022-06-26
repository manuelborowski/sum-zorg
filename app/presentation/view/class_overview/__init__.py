from flask import Blueprint

class_overview = Blueprint('class_overview', __name__)

from . import views
