from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, DateTimeField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from apps.authentication.models import Users
from apps.treasurer.models import Account
from flask_babel import lazy_gettext as _l


def validate_at_least_one_field(form, field):
        if not form.credit.data and not form.debit.data:
            raise ValidationError('At least one of the fields must be filled.')
        
class TransactionForm(FlaskForm):
    # trx_at = DateTimeField('Transaction Date', format='%Y-%m-%d %H:%M:%S')
    # updated_at = DateTimeField('Updated Date', format='%Y-%m-%d %H:%M:%S')
    description = TextAreaField('Description', validators=[DataRequired()])
    debit = FloatField('Debit', validators=[validate_at_least_one_field])
    credit = FloatField('Credit', validators=[validate_at_least_one_field])
    account_id = SelectField('Account', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()])
    owner_id = SelectField('Owner', coerce=int, validators=[DataRequired()])
    treasurer_id = SelectField(_l('Treasurer'), coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.owner_id.choices = [(user.id, user.username) for user in Users.query.all()]
        self.treasurer_id.choices = [(user.id, user.username) for user in Users.query.all()]
        self.account_id.choices = [(account.id, account.name) for account in Account.query.all()]

    
