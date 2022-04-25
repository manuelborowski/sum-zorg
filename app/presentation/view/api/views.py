from flask import request
from . import api
from app.application import registration as mregistration, student as mstudent
from app.data import settings as msettings
import json


@api.route('/api/student/add', methods=['POST'])
def student_add():
    data = json.loads(request.data)
    ret = mstudent.add_student(data)
    return(json.dumps(ret))


@api.route('/api/register/add', methods=['POST', 'GET'])
def register_add():
    data = json.loads(request.data)
    ret = mregistration.registration_add(data)
    return(json.dumps(ret))


@api.route('/api/register/done', methods=['POST', 'GET'])
def register_done():
    data = json.loads(request.data)
    ret = mregistration.registration_done(data['code'])
    return(json.dumps({"status": True}))


@api.route('/api/register/update', methods=['POST', 'GET'])
def register_update():
    data = json.loads(request.data)
    ret = mregistration.registration_update(data['code'], data)
    return(json.dumps(ret))


@api.route('/api/register/status/check', methods=['POST', 'GET'])
def register_check():
    data = json.loads(request.data)
    ret = mregistration.check_register_status(data['code'])
    return(json.dumps(ret))


@api.route('/api/timeslot/add', methods=['POST', 'GET'])
def timeslot_add():
    data = json.loads(request.data)
    ret = mregistration.timeslot_add_registration(data)
    return(json.dumps(ret))


@api.route('/api/registers/info', methods=['POST', 'GET'])
def registers_get_info():
    if msettings.use_register():
        ret = mregistration.register_cache.get_registers_info()
        return(json.dumps(ret))
    else:
        return(json.dumps({'status': False, 'data': 'register not used'}))

