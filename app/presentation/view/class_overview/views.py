from . import class_overview
from flask import redirect, url_for
from flask_login import login_required
from app.presentation.view import datatables
from app.application import socketio as msocketio, student_intake as mstudent
import datetime
import app.data.class_overview
import app.application.class_overview


@class_overview.route('/class_overview/class_overview', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration)
    # print('intake.show', datetime.datetime.now() - start)
    return ret


@class_overview.route('/class_overview/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret =  datatables.ajax(table_configuration)
    # print('intake.table_ajax', datetime.datetime.now() - start)
    return ret


@class_overview.route('/class_overview/table_action', methods=['GET', 'POST'])
@class_overview.route('/class_overview/table_action/<string:action>', methods=['GET', 'POST'])
@class_overview.route('/class_overview/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
def table_action(action, ids=None):
    return redirect(url_for('care.show'))


def get_filters():
    klassen = mstudent.get_unique_klassen()
    choices = [['all', 'alle klassen'],['', 'zonder klas']]
    choices.extend([[k, k] for k in klassen])
    filters = [{
            'type': 'select',
            'name': 'klas',
            'label': 'Selecteer klas',
            'choices': choices,
            'default': 'none',
            'tt': 'Selecteer een klas'
    }]
    return filters


def get_show_gauges():
    return ''


table_configuration = {
    'view': 'class_overview',
    'title': 'Klasoverzicht',
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'pre_filter': app.data.class_overview.pre_filter,
    'format_data': app.application.class_overview.format_data,
    'filter_data': app.data.student_intake.filter_data,
    'search_data': app.data.student_intake.search_data,
    'default_order': (1, 'asc'),
}
