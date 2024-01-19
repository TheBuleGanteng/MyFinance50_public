from flask_wtf import FlaskForm
from wtforms import DateField, EmailField, PasswordField, SelectField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, StopValidation

# Custom filter summary:
# Custom filter 1: Strips user input.
# Custom filter 2: Converts user input to lowercase.
# Custom filter 3: Convert user input to uppercase.


# Custom filter 1: Strip user input.
def strip_filter(input):
    return input.strip() if input else input


# Custom filter 2: Convert user input to lowercase.
def lowercase_filter(input):
    return input.lower() if input else input


# Custom filter 3: Convert user input to uppercase.
def uppercase_filter(input):
    return input.upper() if input else input
    