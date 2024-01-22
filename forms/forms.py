from Custom_FlaskWtf_Filters_and_Validators.filters_generic import strip_filter, lowercase_filter, uppercase_filter
from Custom_FlaskWtf_Filters_and_Validators.validators_generic import allowed_chars_validator, is_positive_validator, not_equal_to_validator, optional_if_date_validator, pw_strength_validator
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalRangeField, EmailField, HiddenField, IntegerField, PasswordField, SelectField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, Regexp, StopValidation


class LoginForm(FlaskForm):
    email = StringField('Email', filters=[strip_filter, lowercase_filter], validators=[DataRequired(), Email(), allowed_chars_validator])
    password = PasswordField('Password', filters=[strip_filter], validators=[DataRequired()])
    submit_button = SubmitField('Log In')

class BuyForm(FlaskForm):
    symbol = StringField('Stock symbol', filters=[strip_filter, uppercase_filter], validators=[DataRequired(), allowed_chars_validator], render_kw={'required': True})
    shares = IntegerField('Number of shares', validators=[DataRequired(), is_positive_validator], render_kw={'required': True})
    submit_button = SubmitField('Register')

class PasswordChangeForm(FlaskForm):
    email = EmailField('Email address:', filters=[strip_filter, lowercase_filter], validators=[DataRequired(), Email(), allowed_chars_validator], render_kw={'required': True, 'type': 'email'})
    password_old = PasswordField('Current password:', filters=[strip_filter], validators=[DataRequired()])
    password = PasswordField('New password:', filters=[strip_filter], validators=[DataRequired(), pw_strength_validator, not_equal_to_validator('password_old')])
    password_confirmation = PasswordField('New password confirmation:', filters=[strip_filter], validators=[DataRequired(), EqualTo('password', message='New password confirmation must match the new password.')], render_kw={'required': True})
    submit_button = SubmitField('Submit')

class PasswordResetRequestForm(FlaskForm):
    email = EmailField('Email address:', filters=[strip_filter, lowercase_filter], validators=[DataRequired(), Email(), allowed_chars_validator], render_kw={'autofocus': True, 'required': True, 'type': 'email'})
    submit_button = SubmitField('Submit')

class PasswordResetRequestNewForm(FlaskForm):
    password = PasswordField('New password:', filters=[strip_filter], validators=[DataRequired(), pw_strength_validator], render_kw={'autofocus': True, 'required': True})
    password_confirmation = PasswordField('New password confirmation:', filters=[strip_filter], validators=[DataRequired(), EqualTo('password', message='New password confirmation must match the new password.')], render_kw={'required': True})
    submit_button = SubmitField('Submit')

class ProfileForm(FlaskForm):
    name_full = StringField('Name:', render_kw={'readonly': True})
    name_first = StringField('Updated first name:', filters=[strip_filter], validators=[Optional(), allowed_chars_validator])
    name_last = StringField('Updated last name:', filters=[strip_filter], validators=[Optional(), allowed_chars_validator])
    username_old = StringField('Username:', filters=[strip_filter], validators=[Optional(), allowed_chars_validator])
    username = StringField('Updated username:', filters=[strip_filter], validators=[Optional(), allowed_chars_validator])
    email = EmailField('Email address:', render_kw={'readonly': True}) 
    created = DateField('Registered since:', format='%Y-%m-%d', render_kw={'readonly': True})
    accounting_method = SelectField('Accounting method:', validators=[Optional()], choices=[('FIFO', 'FIFO'), ('LIFO', 'LIFO')], coerce=str)
    tax_loss_offsets = SelectField('Tax loss offsets:', validators=[Optional()], choices=[('On', 'On'), ('Off', 'Off')], coerce=str)
    tax_rate_STCG = DecimalRangeField('Tax rate, short-term capital gains:', validators=[Optional()], default=30.00, render_kw={"min": 0, "max": 35, "step": 0.50})
    tax_rate_STCG_hidden = HiddenField('Tax Rate STCG Hidden')
    tax_rate_LTCG = DecimalRangeField('Tax rate, long-term capital gains:', validators=[Optional()], default=15.00, render_kw={"min": 0, "max": 35, "step": 0.50})
    tax_rate_LTCG_hidden = HiddenField('Tax Rate LTCG Hidden')
    submit_button = SubmitField('Submit')

class QuoteForm(FlaskForm):
    symbol = StringField('Stock symbol', filters=[strip_filter, uppercase_filter], validators=[DataRequired(), allowed_chars_validator], render_kw={'required': True})
    submit_button = SubmitField('Submit')

class RegisterForm(FlaskForm):
    name_first = StringField('First name:', filters=[strip_filter], validators=[DataRequired(), allowed_chars_validator], render_kw={'autofocus': True})
    name_last = StringField('Last name:', filters=[strip_filter], validators=[DataRequired(), allowed_chars_validator])
    email = EmailField('Email address:', filters=[strip_filter, lowercase_filter], validators=[DataRequired(), Email(), allowed_chars_validator], render_kw={'required': True, 'type': 'email'})
    username = StringField('Username:', filters=[strip_filter], validators=[DataRequired(), allowed_chars_validator], render_kw={'required': True})
    password = PasswordField('Password:', filters=[strip_filter], validators=[DataRequired(), pw_strength_validator])
    password_confirmation = PasswordField('Password confirmation:', filters=[strip_filter], validators=[DataRequired(), EqualTo('password', message='New password confirmation must match the new password.')], render_kw={'required': True})
    accounting_method = SelectField('Accounting method:', validators=[Optional()], choices=[('FIFO', 'FIFO'), ('LIFO', 'LIFO')], coerce=str)
    tax_loss_offsets = SelectField('Tax loss offsets:', validators=[Optional()], choices=[('On', 'On'), ('Off', 'Off')], coerce=str)
    tax_rate_STCG = DecimalRangeField('Tax rate, short-term capital gains:', validators=[Optional()], default=30.00, render_kw={"min": 0, "max": 35, "step": 0.50})
    tax_rate_STCG_hidden = HiddenField('Tax Rate STCG Hidden')
    tax_rate_LTCG = DecimalRangeField('Tax rate, long-term capital gains:', validators=[Optional()], default=15.00, render_kw={"min": 0, "max": 35, "step": 0.50})
    tax_rate_LTCG_hidden = HiddenField('Tax Rate LTCG Hidden')
    submit_button = SubmitField('Register')

class SellForm(FlaskForm):
    symbol = SelectField('Choose a stock to sell', validators=[DataRequired()], choices=[], coerce=str)
    shares = IntegerField('Select how many shares to sell', validators=[DataRequired(), is_positive_validator])
    submit = SubmitField('Submit')
