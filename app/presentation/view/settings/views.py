from flask import render_template, request, redirect, url_for
from flask_login import login_required

from app import admin_required
from app.application import socketio as msocketio, event as mevent, student_intake as mstudent_intake
from . import settings
from app.application import settings as msettings
import json
from app.presentation.layout.utils import flash_plus, button_pressed


@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    data = {
        'default': default_settings,
        'template': settings_formio,
    }
    return render_template('/settings/settings.html', data=data)


@settings.route('/settings/upload_student_info', methods=['GET', 'POST'])
@admin_required
@login_required
def upload_student_info():
    try:
        if request.files['student_info_file']:
            mstudent_intake.import_student_info(request.files['student_info_file'])
        flash_plus('Guest info file is imported')
        return redirect(url_for('settings.show'))
    except Exception as e:
        flash_plus('Could not import guest file', e)


def update_settings_cb(msg, client_sid=None):
  try:
    data = msg['data']
    settings = json.loads(data['value'])
    msettings.set_setting_topic(settings)
    msettings.set_configuration_setting(data['setting'], data['value'])
    msocketio.send_to_room({'type': 'settings', 'data': {'status': True}}, client_sid)
  except Exception as e:
    msocketio.send_to_room({'type': 'settings', 'data': {'status': False, 'message': str(e)}}, client_sid)


def event_received_cb(msg, client_sid=None):
    mevent.process_event(msg['data']['event'])

msocketio.subscribe_on_type('settings', update_settings_cb)
msocketio.subscribe_on_type('event', event_received_cb)


from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
  {
    "display": "form",
    "components": [
      {
        "label": "General",
        "tableView": false,
        "key": "container",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Algemeen",
            "theme": "primary",
            "collapsible": true,
            "key": "algemeen",
            "type": "panel",
            "label": "Algemeen",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true,
                "saveOnEnter": false
              },
              {
                "label": "Standaard leerlingcode (tx)",
                "tableView": true,
                "key": "generic-default-student-code",
                "type": "textfield",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Users",
        "tableView": false,
        "key": "container1",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Gebruikers",
            "theme": "primary",
            "collapsible": true,
            "key": "algemeen",
            "type": "panel",
            "label": "Algemeen",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true,
                "saveOnEnter": false
              },
              {
                "label": "Detail template (formio)",
                "autoExpand": false,
                "tableView": true,
                "key": "user-formio-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Lijst template (JSON)",
                "autoExpand": false,
                "tableView": true,
                "key": "user-datatables-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Standaard niveau nieuwe oauth gebruiker",
                "labelPosition": "left-left",
                "widget": "choicesjs",
                "tableView": true,
                "data": {
                  "values": [
                    {
                      "label": "Gebruiker",
                      "value": "1"
                    },
                    {
                      "label": "Secretariaat",
                      "value": "3"
                    },
                    {
                      "label": "Administrator",
                      "value": "5"
                    }
                  ]
                },
                "key": "user-default-oath-level",
                "type": "select",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Class overview",
        "tableView": false,
        "key": "class_overview",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Klas overzicht",
            "theme": "primary",
            "collapsible": true,
            "key": "class_overview",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true,
                "saveOnEnter": false
              },
              {
                "label": "Detail template (formio)",
                "autoExpand": false,
                "tableView": true,
                "key": "class_overview-formio-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Lijst template (JSON)",
                "autoExpand": false,
                "tableView": true,
                "key": "class_overview-datatables-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Pdf template (JS)",
                "autoExpand": false,
                "tableView": true,
                "key": "class_overview-pdf-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Student Care",
        "tableView": false,
        "key": "visitors2",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Studenten ZORG",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate1",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true,
                "saveOnEnter": false
              },
              {
                "label": "Detail template (formio)",
                "autoExpand": false,
                "tableView": true,
                "key": "care-formio-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Lijst template (JSON)",
                "autoExpand": false,
                "tableView": true,
                "key": "care-datatables-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Pdf template (JS)",
                "autoExpand": false,
                "tableView": true,
                "key": "care-pdf-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Student Intake",
        "tableView": false,
        "key": "visitors1",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Studenten INSCHRIJVEN",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate1",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true,
                "saveOnEnter": false
              },
              {
                "label": "Detail template (formio)",
                "autoExpand": false,
                "tableView": true,
                "key": "intake-formio-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Lijst template (JSON)",
                "autoExpand": false,
                "tableView": true,
                "key": "intake-datatables-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "Pdf template (JS)",
                "autoExpand": false,
                "tableView": true,
                "key": "intake-pdf-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Cron",
        "tableView": false,
        "key": "cron",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Cron",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate3",
            "type": "panel",
            "label": "Smartschool",
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan ",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "label": "Cron template",
                "labelPosition": "left-left",
                "tooltip": "Check https://crontab.guru/ voor de layout van de cron template",
                "tableView": true,
                "persistent": false,
                "key": "cron-scheduler-template",
                "type": "textfield",
                "labelWidth": 20,
                "input": true
              },
              {
                "label": "Columns",
                "columns": [
                  {
                    "components": [
                      {
                        "label": "Start cron cyclus",
                        "tableView": false,
                        "defaultValue": false,
                        "key": "check-start-cron-cycle",
                        "type": "checkbox",
                        "input": true
                      }
                    ],
                    "width": 3,
                    "offset": 0,
                    "push": 0,
                    "pull": 0,
                    "size": "md",
                    "currentWidth": 3
                  },
                  {
                    "components": [
                      {
                        "label": "Start cron cyclus",
                        "showValidations": false,
                        "theme": "danger",
                        "tableView": false,
                        "key": "button-start-cron-cycle",
                        "conditional": {
                          "show": true,
                          "when": "cron.check-start-cron-cycle",
                          "eq": "true"
                        },
                        "type": "button",
                        "saveOnEnter": false,
                        "input": true
                      }
                    ],
                    "width": 6,
                    "offset": 0,
                    "push": 0,
                    "pull": 0,
                    "size": "md",
                    "currentWidth": 6
                  }
                ],
                "key": "columns",
                "type": "columns",
                "input": false,
                "tableView": false
              },
              {
                "label": "(1) VAN SDH, koppel student, via rijksregisternummer, aan klas",
                "tableView": false,
                "defaultValue": false,
                "key": "cron-enable-update-student-class",
                "type": "checkbox",
                "input": true
              }
            ],
            "collapsed": true
          }
        ]
      },
      {
        "label": "sdh",
        "tableView": false,
        "key": "sdh",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "School Data Hub",
            "theme": "primary",
            "collapsible": true,
            "key": "sdh",
            "type": "panel",
            "label": "Smartschool",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Opslaan ",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "label": "URL",
                "tableView": true,
                "persistent": false,
                "key": "sdh-base-url",
                "type": "textfield",
                "labelWidth": 20,
                "input": true
              },
              {
                "label": "Columns",
                "columns": [
                  {
                    "components": [
                      {
                        "label": "Toon sleutel",
                        "tableView": false,
                        "defaultValue": false,
                        "key": "sdh-show-key",
                        "type": "checkbox",
                        "input": true
                      }
                    ],
                    "width": 2,
                    "offset": 0,
                    "push": 0,
                    "pull": 0,
                    "size": "md",
                    "currentWidth": 2
                  },
                  {
                    "components": [
                      {
                        "label": "API sleutel",
                        "tableView": true,
                        "key": "sdh-api-key",
                        "conditional": {
                          "show": true,
                          "when": "sdh.sdh-show-key",
                          "eq": "true"
                        },
                        "type": "textfield",
                        "input": true
                      }
                    ],
                    "width": 5,
                    "offset": 0,
                    "push": 0,
                    "pull": 0,
                    "size": "md",
                    "currentWidth": 5
                  }
                ],
                "key": "columns",
                "type": "columns",
                "input": false,
                "tableView": false
              }
            ]
          }
        ]
      }
    ]
  }