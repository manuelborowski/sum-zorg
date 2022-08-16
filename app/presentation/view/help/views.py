from flask import render_template

from . import help

@help.route('/help', methods=['POST', 'GET'])
def help():
    return render_template('help/help.html')
