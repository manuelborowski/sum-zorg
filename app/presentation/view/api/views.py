from flask import request
from . import api
from app.application import  student_care as mstudent_care, student_intake as mstudent_intake, user as muser
from app.data import settings as msettings
from app import flask_app
import json
from functools import wraps


def key_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        try:
            if request.headers.get('x-api-key') == flask_app.config['API_KEY']:
                return func(*args, **kwargs)
        except:
            pass
        return json.dumps({"status": False, "data": f'Key not valid'})
    return decorator


@api.route('/api/care/add', methods=['POST'])
@key_required
def care_add():
    data = json.loads(request.data)
    ret = mstudent_care.add_student(data)
    return(json.dumps(ret))


@api.route('/api/care/update', methods=['POST'])
@key_required
def care_update():
    data = json.loads(request.data)
    ret = mstudent_care.update_student(data)
    return(json.dumps(ret))


@api.route('/api/intake/add', methods=['POST'])
@key_required
def intake_add():
    data = json.loads(request.data)
    ret = mstudent_intake.add_student(data)
    return(json.dumps(ret))


@api.route('/api/intake/update', methods=['POST'])
@key_required
def intake_update():
    data = json.loads(request.data)
    ret = mstudent_intake.update_student(data)
    return(json.dumps(ret))


@api.route('/api/user/add', methods=['POST'])
@key_required
def user_add():
    data = json.loads(request.data)
    ret = muser.add_user(data)
    return(json.dumps(ret))


@api.route('/api/user/update', methods=['POST'])
@key_required
def user_update():
    data = json.loads(request.data)
    ret = muser.update_user(data)
    return(json.dumps(ret))


