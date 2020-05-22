IDE Academy Certificates
========================

## Backend

### 🚧 To set up the backend:

1. Run `cp envvars.py.sample envvars.py` to make a working copy of the config
2. In `envvars.py` enter the correct path to the db
3. Run `virtualenv venv`
4. Activate the virtualenv: `. venv/bin/activate` (Windows: `venv\scripts\activate`)
5. Run `pip install -r ./requirements.txt` to install all depencencies
6. `python fill_db.py` to fill the database with the known workshops, or check out `python fill_db.py -h` first to see the options*
7. As a local test IDP, [flask-saml2](https://github.com/timheap/flask-saml2) provides an example, which can be run at `./examples/idp.py` after some config
8. In flask-saml2, there are a few bugs ([a](https://github.com/timheap/flask-saml2/issues/23), [b](https://github.com/timheap/flask-saml2/issues/21), [c](https://github.com/timheap/flask-saml2/issues/19)) which have to be solved manually right now (May 2020) using:
    1. The code in [this PR](https://github.com/timheap/flask-saml2/pull/22/files)
    2. Defining a fallback `relay_state` in [the AssertionConsumer class](https://github.com/timheap/flask-saml2/blob/master/flask_saml2/sp/views.py#L79)
    3. Returning `value.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')` in [format_datetime in the idphandler](https://github.com/timheap/flask-saml2/blob/master/flask_saml2/sp/idphandler.py#L263)
9. In [metadata.xml](https://github.com/timheap/flask-saml2/blob/master/flask_saml2/sp/templates/flask_saml2_sp/metadata.xml#19) the `SingleLogoutService` line should also be removed because Surfconext doesn’t like that

(*) You’ll probably want to run something like `python fill_db.py -g /path/to/grades/ -a /path/to/csv/`, or with the `-r` flag to remove all previous entries so you don’t end up with double ones.

### 🏃‍♀️ To run it:
`python run.py`

### 🚀 To deploy it:
[This guide](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uswgi-and-nginx-on-ubuntu-18-04) should help you get started

## Frontend
To set up the frontend (`node` and `npm` are assumed to be installed already)

1. Change to directory frontend: `cd frontend`
2. Install gulp: `npm install -g gulp` (run with `sudo` if there are permission problems)
3. Install all dependencies `npm install` and get yourself some coffee, this’ll take way too long because *npm* :(
4. Run `gulp build` to build the static dependencies or `gulp` to let it watch
