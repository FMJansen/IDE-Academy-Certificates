# coding=utf-8

# ---------------
# ---- VIEWS ----
# ---------------

import logging # Logging for debugging
from flask import render_template, jsonify

from . import app # Get Flask app
from .models import Attendence # Get database models

@app.route("/get_workshops/<int:student_number>/")
def get_workshops(student_number):
    attendences = Attendence.query.filter_by(student_number=student_number)
    logging.warn("ℹ️  Amount of attendences: {0}".format(attendences.count()))
    if attendences is not None:
        return jsonify([i.serialize for i in attendences.all()])
    else:
        return "No attendences."


@app.route("/")
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return "404"

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
