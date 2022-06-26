import sys

import app.data.class_overview
from app import log, db
from sqlalchemy import text
from app.data.student_intake import StudenIntake

############ student overview list #########
def pre_filter():
    return db.session.query(StudenIntake)


def filter_data(query, filter):
    if filter and 'type' in filter[0] and filter[0]['type'] == 'checkbox':
        for cb in filter[0]['value']:
            query = query.filter(text(cb['id']), cb['checked'])
    for f in filter:
        if f['type'] == 'select' and f['value'] != 'none':
            query = query.filter(getattr(StudenIntake, f['name']) == (f['value'] == 'True'))
    return query


def search_data(search_string):
    search_constraints = []
    search_constraints.append(StudenIntake.s_first_name.like(search_string))
    search_constraints.append(StudenIntake.s_last_name.like(search_string))
    return search_constraints


