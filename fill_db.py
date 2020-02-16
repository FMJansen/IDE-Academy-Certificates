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
parser.add_argument("-a", "--attendence", action="store",
    help="folder with the folders of csv files for the attendence - make sure the sub folders contain the semester (start month + year, 'Sep YYYY' or 'Feb YYYY') in which the workshop was held [defaults to ./attendences]")
parser.add_argument("-g", "--grades", action="store",
    help="folder with csv files with the grades [defaults to ./grades]")
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




# Define function to get the attendences from csv files in grades folder
def extract_grades(grades_folder):

    # Get list of files and start cycling through them
    grades_file_list = listdir_nohidden(grades_folder)
    logging.warning("👀 Checking folder {0}".format(grades_folder))
    logging.info("🚲 Cycling through list of grades csv files.")

    for grades_file in grades_file_list:

        file_path = '{0}/{1}'.format(grades_folder, grades_file)
        with open(file_path, 'rt') as csv_file:

            logging.info("🎓 Go through grades file.")

            # Process csv file
            student_dict = csv.DictReader(csv_file)

            # Loop through rows of file
            for student in student_dict:

                try:
                    student_number = student['\ufeffOrgDefinedId']
                except KeyError:
                    student_number = student['OrgDefinedId']

                for key, value in student.items():

                    if value == 'Present':

                        workshop = re.sub(" Scheme Symbol", "", key)

                        # Get workshop date
                        try:
                            workshop_date = re.search("([A-Z])\w+ [0-9]+", workshop)
                            date_str = workshop_date[0]
                            workshop_date = datetime.strptime(workshop_date[0], "%b %d")
                        except TypeError:
                            workshop_date = datetime.now()

                        # Get workshop name
                        workshop_name = re.sub("([A-Z])([a-z])+ [0-9]+( )*(:*)", "", workshop)
                        workshop_name = workshop_name.strip()

                        try:
                            student_number = int(student_number)
                        except ValueError:
                            student_number = re.sub("#", "", student_number)
                            student_number = int(student_number)

                        new_attendence = Attendence(
                            student_number = student_number,
                            workshop_name = workshop_name,
                            workshop_date = workshop_date,
                            date_str = date_str
                        )

                        db.session.add(new_attendence)

            db.session.commit()





# Define function to get the ratings and messages from one csv file
def extract_ratings_from(csv_file, folder, year, db):
    # Get workshop name and date
    workshop = re.sub(" - Attempt Details.csv", "", csv_file)
    workshop = re.sub("Attendance for ", "", workshop)
    workshop_date = re.search("([A-Z])\w+ [0-9]+", workshop)
    date_str = workshop_date[0]
    workshop_date = "{0} {1}".format(workshop_date[0], year)
    workshop_date = datetime.strptime(workshop_date, "%b %d %Y")
    workshop_name = re.sub("([A-Z])\w+ [0-9]+", "", workshop)
    workshop_name = workshop_name.strip()

    attendence = Attendence.query.filter(
        Attendence.workshop_name.ilike(workshop_name),
        Attendence.date_str == date_str).first()

    if attendence is None:
        logging.info("❓ Workshop in grades file, but no matching workshop found in quiz csv files")
        return
    else:
        logging.debug("{0} on {1}".format(attendence.workshop_name, attendence.date_str))

    """
    January workshops are in the folder of the semester starting in the previous year, so the year should be the one after that of September
    for those workshops
    """
    if workshop_date.month == 1:
        workshop_date = workshop_date.replace(year = workshop_date.year + 1)

    # Open csv file as text
    file_path = '{0}/{1}'.format(folder, csv_file)
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
                logging.debug("Finding first attendence")

                # Update current student number
                current_student_number = question['Org Defined ID']

                # Get new attendencee
                current_attendence = Attendence.query.filter(
                    Attendence.workshop_name.ilike(workshop_name),
                    Attendence.date_str == date_str,
                    Attendence.student_number == int(current_student_number))\
                    .first()

                if current_attendence is None:
                    logging.debug("🚨 Student {0} wasn’t present".format(current_student_number))
                    return
                else:
                    # Update workshop date to include year
                    current_attendence.workshop_date = workshop_date

            elif question['Org Defined ID'] != current_student_number:
                # New attendence, so save previous one
                logging.debug("Saving attendence to db")
                db.session.commit()

                # Update current student number
                current_student_number = question['Org Defined ID']

                # Get new attendencee
                current_attendence = Attendence.query.filter(
                    Attendence.workshop_name.ilike(workshop_name),
                    Attendence.date_str == date_str,
                    Attendence.student_number == int(current_student_number))\
                    .first()

                if current_attendence is None:
                    logging.debug("🚨 Student {0} wasn’t present".format(current_student_number))
                    return
                else:
                    # Update workshop date to include year
                    current_attendence.workshop_date = workshop_date

            # Add rating to current attendence
            if "familiar" in question['Q Text'] and question['Answer Match'] == "Checked":
                rating = int(question['Answer'][0])
                current_attendence.rating = rating

            # Add the message to future self to current attendence
            if "future" in question['Q Text']:
                current_attendence.future_self = question['Answer Match']



        logging.info("Some example data from this set: Message to future self [{0}] and rating [{1}]".format(current_attendence.future_self, current_attendence.rating))

        # Save attendences from this workshop to db
        logging.info("Saving last attendence to database")
        db.session.commit()

    logging.info("☑️  Done with {0}".format(workshop_name))





# Define function to go through list of folders with quiz data (rating/messages)
def cycle_through_folder_list(attendence_folder_list):

    logging.info("🚴‍♀️ Cycling through list of sub folders")

    for sub_folder in attendence_folder_list:

        # Create path for the sub folder
        csv_file_folder = "{0}/{1}".format(folder_containing_attendence, sub_folder)

        # Get year from sub folder name
        year = re.search("[0-9]+", sub_folder)[0]

        # Get list of files and start cycling through them
        csv_file_list = listdir_nohidden(csv_file_folder)
        logging.warning("👀 Checking folder {0}".format(csv_file_folder))
        logging.info("🚲 Cycling through list of csv files/workshops.")

        for csv_file in csv_file_list:
            extract_ratings_from(csv_file, csv_file_folder, year, db)





# Create database if it doesn’t exist yet
db.create_all()
logging.info("💽 Database created.")

# Get amount of rows at the start
start_amount = db.session.query(Attendence).count()

# Get folder with the csv files to cycle through and start cycling through them
grades_folder = args.grades
extract_grades(grades_folder)

# Get folder with the csv files to cycle through
folder_containing_attendence = args.attendence

# Get list of sub folders and start cycling through them
attendence_folder_list = listdir_nohidden(folder_containing_attendence)
cycle_through_folder_list(attendence_folder_list)





# Get amount of rows at the end
new_amount = db.session.query(Attendence).count()

# Calculate the amount of added rows
amount_added = new_amount - start_amount
logging.warning("✅ All done. Added {0} rows. New amount of attendences: {1}".format(amount_added, new_amount))
