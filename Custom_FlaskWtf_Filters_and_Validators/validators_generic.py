from flask_wtf import FlaskForm
import re
from wtforms import DateField, EmailField, PasswordField, SelectField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, StopValidation


# Custom validator summary:
# Custom validator 1: Checks user input for prohibited chars.
# Custom validator 2: Checks user input for password strength requirements.
# Custom validator 3: Ensure user input is positive.
# Custom validator 4: Ensures current field and another specified field are different.
# Custom validator 5: Allows a datefield to be optional


# Custom validator 1: Ensure user input does not contain prohibited chars. 
user_input_allowed_letters = 'a-zA-Z'
user_input_allowed_numbers = '0-9'
user_input_allowed_symbols = '.@-#! '
# Escape the symbols for safe inclusion in regex pattern
user_input_allowed_symbols_escaped = re.escape(user_input_allowed_symbols or '')
user_input_allowed_all = ''.join([user_input_allowed_letters, 
                                user_input_allowed_numbers, 
                                user_input_allowed_symbols_escaped])
# Regular expression pattern to match the entire string
allowed_chars_check_pattern = r'^[' + user_input_allowed_all + r']+$'
# Define function (no prohibited chars = True).
def allowed_chars(user_input):
    if re.match(allowed_chars_check_pattern, str(user_input)):
        print(f'running allowed_chars_validator...  passed for input: {field.data}')
        return True
# Define validator
def allowed_chars_validator(form, field):
    if not re.match(allowed_chars_check_pattern, field.data):
        print(f'running allowed_chars_validator...  failed for input: {field.data}')
        raise ValidationError(f'Invalid input for "{field.label.text}" Please ensure user inputs contain only letters, numbers, and the following symbols: {user_input_allowed_symbols}')
    else:
        return field.data
        

# Custom validator 2: Ensure user-entered password meets strength requirements.
pw_req_length = 4
pw_req_letter = 2
pw_req_num = 2
pw_req_symbol = 0
# Define function (user_input is of sufficient strength = returns True)
def pw_strength(user_input):
    if (
        len(user_input) >= pw_req_length and 
        len(re.findall(r'[a-zA-Z]', user_input)) >= pw_req_letter and 
        len(re.findall(r'[0-9]', user_input)) >= pw_req_num and
        len(re.findall(r'[^a-zA-Z0-9]', user_input)) >= pw_req_symbol
        ):
        return True
# Define validator
def pw_strength_validator(form, field):
    if not pw_strength(field.data):
        print(f'Custom validator pw_strength_check_validator failed for input: {field.data}')
        raise ValidationError(f'Error: Invalid input for "{field.label.text}" Please ensure user inputs contain only letters, numbers, and the following symbols: {user_input_allowed_all}')
    else:
        return field.data


# Custom validator 3: Ensure user input is positive.
# Define function (returns true if user_input is a positive integer)
def is_positive(user_input):
    if user_input > 0:
        return True
# Define validator
def is_positive_validator(form, field):
    if not is_positive(field.data):
        print(f'Custom validator is_positive_validator failed for input: {field.data}')
        raise ValidationError(f'Error: Input for "{field.label.text}" must be positive.')
    else:
        return field.data


# Custom validator 4: Ensures current field and another specified field are different.
def not_equal_to_validator(comparison_field):
    def values_must_differ(form, field):
        compare_field = getattr(form, comparison_field)
        if field.data == compare_field.data:
            raise ValidationError(f"{field.label.text} must be different from {compare_field.label.text}.")
    return values_must_differ

# Custom validator 5: Allows a datefield to be optional
def optional_if_date_validator(Optional):
    """Custom validator: makes a DateField optional if no data entered"""
    def __call__(self, form, field):
        if not field.raw_data or not field.raw_data[0]:
            field.errors[:] = []
            raise StopValidation()