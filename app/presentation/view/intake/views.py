from . import intake
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings, student_intake as mstudent
import sys, json
import app.data
import app.application


@intake.route('/intake/intake', methods=['POST', 'GET'])
@supervisor_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration)
    # print('intake.show', datetime.datetime.now() - start)
    return ret


@intake.route('/intake/table_ajax', methods=['GET', 'POST'])
@supervisor_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret =  datatables.ajax(table_configuration)
    # print('intake.table_ajax', datetime.datetime.now() - start)
    return ret


@intake.route('/intake/table_action', methods=['GET', 'POST'])
@intake.route('/intake/table_action/<string:action>', methods=['GET', 'POST'])
@intake.route('/intake/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@supervisor_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    if action == 'edit':
        return item_edit(ids)
    if action == 'add':
        return item_add()
    return redirect(url_for('intake.show'))


item_common = {'post_data_endpoint': 'api.intake_update', 'submit_endpoint': 'intake.show', 'cancel_endpoint': 'intake.show', 'api_key': flask_app.config['API_KEY']}


@supervisor_required
def item_delete(ids=None):
    try:
        if ids == None:
            ids = request.form.getlist('chbx')
        app.application.student_intake.delete_students(ids)
    except Exception as e:
        log.error(f'could not delete intake {request.args}: {e}')
    return redirect(url_for('intake.show'))


@supervisor_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('intake.show'))
        else:
            id = ids[0]
        data = app.application.student_intake.prepare_edit_form(id)
        data.update(item_common)
        data.update({"buttons": [("save", "Bewaar", "default"), ("cancel", "Annuleer", "warning")]})
        return render_template('formio.html', data=data)
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('intake.show'))


@supervisor_required
def item_add():
    try:
        data = app.application.student_intake.prepare_add_form()
        data.update(item_common)
        data.update({"buttons": [("save", "Bewaar", "default"), ("cancel", "Annuleer", "warning"), ("clear-ack", "Velden wissen", "warning")]})
        data['post_data_endpoint'] = 'api.intake_add'
        return render_template('formio.html', data=data)
    except Exception as e:
        log.error(f'Could not add intake {e}')
        flash_plus(f'Kan intake niet toevoegen: {e}')
    return redirect(url_for('intake.show'))


@intake.route('/intake/right_click/', methods=['POST', 'GET'])
@supervisor_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
            if 'item' in data:
                if data['item'] == "delete":
                    app.application.student_intake.delete_students(data['item_ids'])
                    return {"message": "Studenten zijn verwijderd, ververs het browserscherm"}
                if data['item'] == "add":
                    return {"redirect": {"url": f"/intake/table_action/add"}}
                if data['item'] == "edit":
                    return {"redirect": {"url": f"/intake/table_action/edit", "ids": data['item_ids']}}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}
    return {"status": False, "data": "iets is fout gelopen"}


def get_filters():
    klassen = mstudent.get_unique_klassen()
    choices = [['all', 'alle klassen'],['', 'zonder klas']]
    choices.extend([[k, k] for k in klassen])
    klasgroepen = mstudent.get_unique_klasgroepen()
    klasgroep_choices = [[json.dumps(k), g] for g, k in klasgroepen.items()]
    klasgroep_choices = sorted(klasgroep_choices, key=lambda x: x[1])
    klasgroep_choices = [['all', 'alle klassen'],['', 'zonder klas']] + klasgroep_choices
    filters = [
        # {
        #     'type': 'select',
        #     'name': 'klas',
        #     'label': 'Selecteer klas',
        #     'choices': choices,
        #     'default': 'none',
        #     'tt': 'Selecteer een klas'
        # },
        {
            'type': 'select',
            'name': 'klasgroep',
            'label': 'Selecteer klas',
            'choices': klasgroep_choices,
            'default': 'none',
            'tt': 'Selecteer een klas'
        },
    ]
    return filters


def get_show_gauges():
    return ''


def get_pdf_template():
    return msettings.get_pdf_template('intake-pdf-template')


table_configuration = {
    'view': 'intake',
    'title': 'Inschrijven',
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'get_pdf_template': get_pdf_template,
    'href': [],
    'legend': '<span style="background-color:rgb(232, 182, 120)">Geen klas</span>',
    'pre_filter': app.data.student_intake.pre_filter,
    'format_data': app.application.student_intake.format_data,
    'filter_data': app.data.student_intake.filter_data,
    'search_data': app.data.student_intake.search_data,
    'default_order': (1, 'asc'),
    'right_click': {
        'endpoint': 'intake.right_click',
        'menu': [
            {'label': 'Nieuwe student', 'item': 'add', 'iconscout': 'plus-circle'},
            {'label': 'Student aanpassen', 'item': 'edit', 'iconscout': 'pen'},
            {'label': 'Studenten(en) verwijderen', 'item': 'delete', 'iconscout': 'trash-alt', 'ack': 'Bent u zeker dat u deze student(en) wilt verwijderen?'},
        ]
    }
}
