__all__ = ['tables', 'datatables', 'socketio', 'settings', 'warning', 'student_care', 'student_intake', 'cron']

import app.application.socketio
import app.application.tables
import app.application.warning
import app.application.datatables
import app.application.settings
import app.application.student_care
import app.application.student_intake
import app.application.cron

cron.subscribe_cron_task(1, student_intake.link_students_to_class_cron_task, None)
