from app import log
from app.data import student_intake as mstudent, settings as msettings
import app.data.settings
from app.application import formio as mformio
import sys, datetime, requests, json

def add_student(data):
    try:
        data['s_date_of_birth'] = mformio.datestring_to_date(data['s_date_of_birth'])
        data['i_intake_date'] = mformio.datetimestring_to_datetime(data['i_intake_date'])
        student = mstudent.add_student(data)
        log.info(f"Add intake: {student.s_last_name} {student.s_first_name}, {data}")
        return {"status": True, "data": {'id': student.id}}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def update_student(data):
    try:
        student = mstudent.get_first_student({'id': data['id']})
        if student:
            del data['id']
            data['s_date_of_birth'] = mformio.datestring_to_date(data['s_date_of_birth'])
            data['i_intake_date'] = mformio.datetimestring_to_datetime(data['i_intake_date'])
            student = mstudent.update_student(student, data)
            if student:
                log.info(f"Update intake: {student.s_last_name} {student.s_first_name}, {data}")
                return {"status": True, "data": {'id': student.id}}
        return {"status": False, "data": "Er is iets fout gegaan"}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        log.error(data)
        return {"status": False, "data": f'generic error {e}'}


def delete_students(ids):
    mstudent.delete_students(ids)


def get_unique_klassen():
    return mstudent.get_unique_klassen()

############## formio forms #############
def prepare_add_form():
    try:
        template = app.data.settings.get_json_template('intake-formio-template')
        now = datetime.datetime.now()
        return {'template': template,
                'defaults': {
                        'i_intake_date': mformio.datetime_to_datetimestring(now),
                        's_code': msettings.get_and_increment_default_student_code()
                }
                }
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


def prepare_edit_form(id):
    try:
        student = mstudent.get_first_student({"id": id})
        template = app.data.settings.get_json_template('intake-formio-template')
        template = mformio.prepare_for_edit(template, student.to_dict())
        return {'template': template,
                'defaults': student.to_dict()}
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
        raise e


############ care overview list #########
def format_data(db_list):
    out = []
    for student in db_list:
        em = student.to_dict()
        em.update({
            'row_action': student.id,
            'DT_RowId': student.id
        })
        if student.klas == '':
            em.update({'overwrite_row_color': "rgb(232, 182, 120)"})
        out.append(em)
    return out


################  Cron jobs ##################

# get list of students from sdh
# use rijksregisternummer as key to find a student
# fill in the classnumber and wisa internal number
def link_students_to_class_cron_task(opaque):
    try:
        if msettings.get_configuration_setting('cron-enable-update-student-class'):
            sdh_url = msettings.get_configuration_setting('sdh-base-url')
            sdh_key = msettings.get_configuration_setting('sdh-api-key')
            session = requests.Session()
            res = session.get(f'{sdh_url}/students?fields=rijksregisternummer,klascode,leerlingnummer', headers={'x-api-key': sdh_key})
            if res.status_code == 200:
                sdh_students = res.json()
                nbr_student_found = 0
                nbr_student_not_found = 0
                if sdh_students['status']:
                    log.info(f'{sys._getframe().f_code.co_name}, retrieved {len(sdh_students["data"])} students from SDH')
                    rijksregister_to_student = {s['rijksregisternummer']: s for s in sdh_students["data"]}
                    students = mstudent.get_students()
                    log.info(f'{sys._getframe().f_code.co_name}, {len(students)} students in database')

                    for student in students:
                        rijksregisternummer = student.s_rijksregister.replace('-', '').replace('.', '')
                        if rijksregisternummer != "" and rijksregisternummer in rijksregister_to_student:
                            nbr_student_found += 1
                            student.klas = rijksregister_to_student[rijksregisternummer]['klascode']
                            student.s_code = rijksregister_to_student[rijksregisternummer]['leerlingnummer']
                        else:
                            nbr_student_not_found += 1
                    mstudent.commit()
                    log.info(f'{sys._getframe().f_code.co_name}, students found {nbr_student_found}, students not found {nbr_student_not_found}')
                else:
                    log.error(f'{sys._getframe().f_code.co_name}: sdh returned {sdh_students["data"]}')

            else:
                log.error(f'{sys._getframe().f_code.co_name}: api call returned {res.status_code}')

    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')
