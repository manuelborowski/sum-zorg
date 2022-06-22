from . import care
from app import log, supervisor_required, flask_app
from flask import redirect, url_for, request, render_template
from flask_login import login_required, current_user
from app.presentation.view import datatables
from app.presentation.layout.utils import flash_plus
from app.application import socketio as msocketio, settings as msettings
import sys, json
import app.data
import app.application


@care.route('/care/care', methods=['POST', 'GET'])
@login_required
def show():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.show(table_configuration)
    # print('care.show', datetime.datetime.now() - start)
    return ret


@care.route('/care/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    # start = datetime.datetime.now()
    datatables.update(table_configuration)
    ret = datatables.ajax(table_configuration)
    # print('care.table_ajax', datetime.datetime.now() - start)
    return ret


@care.route('/care/table_action', methods=['GET', 'POST'])
@care.route('/care/table_action/<string:action>', methods=['GET', 'POST'])
@care.route('/care/table_action/<string:action>/<string:ids>', methods=['GET', 'POST'])
@login_required
# @supervisor_required
def table_action(action, ids=None):
    if ids:
        ids = json.loads(ids)
    if action == 'edit':
        return item_edit(ids)
    if action == 'add':
        return item_add()
    return redirect(url_for('care.show'))


item_common = {'post_data_endpoint': 'api.care_update', 'submit_endpoint': 'care.show', 'cancel_endpoint': 'care.show', 'api_key': flask_app.config['API_KEY']}


@supervisor_required
def item_edit(ids=None):
    try:
        if ids == None:
            chbx_id_list = request.form.getlist('chbx')
            if chbx_id_list:
                ids = chbx_id_list[0]  # only the first one can be edited
            if ids == '':
                return redirect(url_for('care.show'))
        else:
            id = ids[0]
        data = app.application.student_care.prepare_edit_form(id)
        data.update(item_common)
        data.update({"buttons": [("save", "Bewaar", "default"), ("cancel", "Annuleer", "warning")]})
        return render_template('formio.html', data=data)
    except Exception as e:
        log.error(f'Could not edit guest {e}')
        flash_plus('Kan gebruiker niet aanpassen', e)
    return redirect(url_for('care.show'))


@supervisor_required
def item_add():
    try:
        data = app.application.student_care.prepare_add_form()
        data.update(item_common)
        data.update({"buttons": [("save", "Bewaar", "default"), ("cancel", "Annuleer", "warning"), ("clear-ack", "Velden wissen", "warning")]})
        data['post_data_endpoint'] = 'api.care_add'
        return render_template('formio.html', data=data)
    except Exception as e:
        log.error(f'Could not add care {e}')
        flash_plus(f'Kan care niet toevoegen: {e}')
    return redirect(url_for('care.show'))


@care.route('/care/right_click/', methods=['POST', 'GET'])
@login_required
def right_click():
    try:
        if 'jds' in request.values:
            data = json.loads(request.values['jds'])
            if 'item' in data:
                if data['item'] == "delete":
                    app.application.student_care.delete_students(data['item_ids'])
                    return {"message": "Studenten zijn verwijderd, ververs het browserscherm"}
                if data['item'] == "add":
                    return {"redirect": {"url": f"/care/table_action/add"}}
                if data['item'] == "edit":
                    return {"redirect": {"url": f"/care/table_action/edit", "ids": data['item_ids']}}
    except Exception as e:
        log.error(f"Error in get_form: {e}")
        return {"status": False, "data": f"get_form: {e}"}
    return {"status": False, "data": "iets is fout gelopen"}


def get_filters():
    filters = []
    template = app.data.settings.get_datatables_config('care')
    template_cache = {t['data']: t for t in template}

    selects = [
        'f_gemotiveerd_verslag',
        'f_verslag_ontbindende_voorwaarden',
        'f_geen_verslag_specifieke_behoefte',
        'f_nood_aan_voorspelbaarheid',
        'f_ass',
        'f_add',
        'f_adhd',
        'f_dcd',
        'f_hoogbegaafd',
        'f_dyscalculie',
        'f_dyslexie',
        'f_dysorthografie',
        'f_stos_dysfasie',
        'f_andere',
    ]
    for select in selects:
        filters.append(
        {
            'type': 'select',
            'name': template_cache[select]['data'],
            'label': template_cache[select]['name'],
            'choices': [['none', 'X'], [True, 'J'], [False, 'N']],
            'default': 'default',
            'tt': template_cache[select]['tt']
        })

    return filters


def get_show_gauges():
    return ''


def get_pdf_template():
    return msettings.get_pdf_template('care-pdf-template')


table_configuration = {
    'view': 'care',
    'title': 'Zorg',
    'get_filters': get_filters,
    'get_show_info': get_show_gauges,
    'get_pdf_template': get_pdf_template,
    'href': [],
    'pre_filter': app.data.student_care.pre_filter,
    'format_data': app.application.student_care.format_data,
    'filter_data': app.data.student_care.filter_data,
    'search_data': app.data.student_care.search_data,
    'default_order': (1, 'asc'),
    'right_click': {
        'endpoint': 'care.right_click',
        'menu': [
            {'label': 'Nieuwe student', 'item': 'add', 'iconscout': 'plus-circle'},
            {'label': 'Student aanpassen', 'item': 'edit', 'iconscout': 'pen'},
            {'label': 'Studenten(en) verwijderen', 'item': 'delete', 'iconscout': 'trash-alt', 'ack': 'Bent u zeker dat u deze student(en) wilt verwijderen?'},
        ]
    }

}
