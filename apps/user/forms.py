from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo
from apps.authentication.models import Users, Role 




class UserEditForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True})
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
    roles = SelectMultipleField('Roles',coerce=int, validators=[DataRequired()])
    # roles = QuerySelectMultipleField('Roles', query_factory=lambda: Role.query.all(), get_label='name')

    submit = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(role.id, role.name) for role in Role.query.all()]

   
    def validate_email(self, field):
        if field.data != self.email.object_data and Users.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already registered.')