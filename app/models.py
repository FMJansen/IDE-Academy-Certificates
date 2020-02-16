# coding=utf-8

# ----------------
# ---- MODELS ----
# ----------------

# Get Flask app and db
from . import db



# Define class for an attendence (one person at one workshop)
class Attendence(db.Model):
    # Define columns/properties
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.Integer, nullable=False)
    workshop_name = db.Column(db.String(255), nullable=False)
    workshop_date = db.Column(db.DateTime)
    date_str = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    future_self = db.Column(db.Text, nullable=True)

    # Define representation
    def __repr__(self):
        return '{0}'.format(self.workshop_name)

    @property
    def serialize(self):
        return {
            'workshop_name': self.workshop_name,
            'workshop_date': self.workshop_date,
            'rating': self.rating,
            'future_self': self.future_self
        }
