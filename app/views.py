# coding=utf-8

# ---------------
# ---- VIEWS ----
# ---------------

import logging # Logging for debugging
from datetime import datetime # Showing date on certificate
from flask import render_template, request, send_from_directory, url_for, make_response, redirect
from flask_saml2.exceptions import CannotHandleAssertion

from . import app, sp # Get Flask app and Flask SAML SP
from .models import Attendence # Get database models





@app.errorhandler(CannotHandleAssertion)
def handle_assertion_exception(err):
    app.logger.warn("Got an exception in get_auth_data probs: {0}".format(err))
    return "We can’t handle that SAML", 500





@app.route('/static/<kind>/<path:path>')
def send_js(kind, path):
    dir = '../static/{0}'.format(kind)
    return send_from_directory(dir, path)





@app.route("/certificate/", methods=['GET', 'POST'])
def generate_certificate():
    if request.method == 'POST':
        name = request.form['name']
    else:
        name = request.cookies.get('name')

    try:
        auth_data = sp.get_auth_data_in_session()
    except KeyError:
        return redirect(url_for('index'), code=302)
    netid = auth_data.attributes['urn:mace:dir:attribute-def:uid']
    attendences = Attendence.query.filter_by(netid=netid)\
        .order_by(Attendence.workshop_date)

    resp = make_response(render_template("certificate.html",
        attendences=attendences.all(),
        name=name,
        netid=netid,
        now=datetime.now()))

    resp.set_cookie('name', name)

    return resp



@app.route("/printing/")
def printing():
    return render_template('printing.html')



@app.route("/")
def index():
    if sp.is_user_logged_in():
        return render_template('index.html')
    else:
        login_url = url_for('flask_saml2_sp.login')
        return render_template('splash.html', login_url=login_url)



@app.errorhandler(404)
def page_not_found(e):
    return "404"

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
