from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired

class AccountForm(FlaskForm):
    id = HiddenField('id')  
    name = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    active = BooleanField('Active', default=True)
    submit = SubmitField('Submit')
