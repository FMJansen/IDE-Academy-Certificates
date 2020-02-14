# coding=utf-8

# -----------------
# ---- FILL DB ----
# -----------------

# Imports
import os # File handling
import csv # File handling
import re # File name handling
from datetime import datetime # File name handling
import logging # Verbose output
import argparse # Verbose output
import sys # Allow question about database removal

from app import db # Database for ideac
from app.models import Attendence # Database model for Attendence





# Allow passing arguments
parser = argparse.ArgumentParser(
    description="Fill the ideac database with content from csv files")
parser.add_argument("-v", "--verbose", action='count', default=0,
    help="increase output verbosity")
parser.add_argument("-f", "--folder", action="store",
    help="folder with the csv files (defaults to ./csv)")
parser.add_argument("-r", "--replace", action="store_true",
    help="[DANGEROUS 🚫] replace all content in the database")

# Allow optional verbose output
args = parser.parse_args()
if args.verbose == 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.verbose == 1:
    logging.basicConfig(level=logging.INFO)





# Allow emptying database before adding the new rows
def check_removal():
    sys.stdout.write("Are you sure you want to empty the database? [Y/n] ")
    choice = input().lower()
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if choice == '':
        return True
    elif choice in valid:
        return valid[choice]
    else:
        sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if args.replace:
    if check_removal():
        logging.warning("🗑  Emptying database")
        Attendence.query.delete()
    else:
        logging.warning("🤔  Okay never mind the -r then")

logging.info("Hej! Today we’ll be filling the database with some csv files.")
logging.info("☕ Apparently, you want quite some tea. So here you go, it’s hot")
logging.debug("Oh, sorry, you meant *all* the tea!")





# Ignore hidden files in folder
def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f





# Create database if it doesn’t exist yet
db.create_all()
logging.info("💽 Database created.")

# Get amount of rows at the start
start_amount = db.session.query(Attendence).count()

# Get list of files and start cycling through them
csv_file_list = listdir_nohidden(args.folder)
logging.info("🚲 Cycling through list of csv files/workshops.")
for csv_file in csv_file_list:

    # Get workshop name and date
    workshop = re.sub(" - Attempt Details.csv", "", csv_file)
    workshop = re.sub("Attendance for ", "", workshop)
    workshop_date = re.search("([A-Z])\w+ [0-9]+", workshop)
    workshop_date = datetime.strptime(workshop_date[0], "%b %d")
    workshop_name = re.sub("([A-Z])\w+ [0-9]+", "", workshop)
    workshop_name = workshop_name.strip()

    # Open csv file as text
    file_path = '{0}/{1}'.format(args.folder, csv_file)
    with open(file_path, 'rt') as csv_file:

        logging.info("Workshop name: {0} held on {1}".format(workshop_name,
            datetime.strftime(workshop_date, "%B %-d")))

        # Process csv file
        question_dict = csv.DictReader(csv_file)

        # Create current position variables
        current_student_number = False
        current_attendence = False

        # Loop through rows of file
        for question in question_dict:
            if not current_student_number:
                logging.debug("Creating first attendence")
                current_student_number = question['Org Defined ID']

                # Build new attendencee
                current_attendence = Attendence(
                    student_number = int(question['Org Defined ID']),
                    workshop_name = workshop_name,
                    workshop_date = workshop_date,
                )

            elif question['Org Defined ID'] != current_student_number:
                # New attendence, so save previous one
                logging.debug("Adding attendence to db")
                db.session.add(current_attendence)

                # Update current student number
                current_student_number = question['Org Defined ID']

                # Build new attendencee
                current_attendence = Attendence(
                    student_number = int(current_student_number),
                    workshop_name = workshop_name,
                    workshop_date = workshop_date,
                )

            # Add rating to current attendence
            if "familiar" in question['Q Text'] and question['Answer Match'] == "Checked":
                rating = int(question['Answer'][0])
                current_attendence.rating = rating

            # Add the message to future self to current attendence
            if "future" in question['Q Text']:
                current_attendence.future_self = question['Answer Match']



        logging.info("Some example data from this set:")
        logging.info("Message to future self: {0}".format(current_attendence.future_self))
        logging.info("Rating: {0}".format(current_attendence.rating))

        # Done with looping so save last attendence
        db.session.add(current_attendence)

        # Save attendences from this workshop to db
        logging.info("Saving attendences to database")
        db.session.commit()

        logging.info("☑️  Done with {0}".format("FIXME"))





new_amount = db.session.query(Attendence).count()
amount_added = new_amount - start_amount
logging.warning("✅ All done. Added {0} rows. New amount of attendences: {1}".format(amount_added, new_amount))
