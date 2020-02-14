IDE Academy Certificates
========================

## Backend
To set up the backend:

1. Run `cp envvars.py.sample envvars.py` to make a working copy of the config
2. In `envvars.py` enter the correct path to the db
3. Run `virtualenv venv`
4. Activate the virtualenv: `. venv/bin/activate` (Windows: `venv\scripts\activate`)
5. Run `pip install -r ./requirements.txt` to install all depencencies
6. `python fill_db.py` to fill the database with the known workshops, or check out `python fill_db.py -h` first to see the options

To run it: `python run.py`

## Frontend
To set up the frontend (angular + backbone and more, `node` and `npm` are assumed to be installed already)

1. Change to directory frontend: `cd frontend`
2. Install gulp: `npm install -g gulp` (run with `sudo` if there are permission problems)
3. Install all dependencies `npm install` and get yourself some coffee, this’ll take way too long because *npm* :(
4. ...
5. profit?
6. Run `gulp` to build the static dependencies
