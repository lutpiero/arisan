from flask import render_template, redirect, url_for, session, current_app as app, request, flash
from flask_principal import Permission, RoleNeed, Identity, identity_loaded, identity_changed, AnonymousIdentity
from apps.treasurer import blueprint
from apps.treasurer.models import Transaction
from apps.treasurer.models import Journal, Transaction
from apps.treasurer.form_add_trx import TransactionForm
from apps import db, babel
from datetime import datetime
import json
import logging

# Define roles
admin_permission = Permission(RoleNeed('admin'))
superadmin_permission = Permission(RoleNeed('superadmin'))
any_admin_permission = admin_permission.union(superadmin_permission)



@blueprint.route('/transactions') 
@any_admin_permission.require(http_exception=403)

def transactions():
    form = TransactionForm()
    # Replace this with actual user fetching logic
    account_id = request.args.get('account_id')
    owner_id = request.args.get('owner_id')
    role = request.args.get('role')

    transaction_query = Transaction.query

    if account_id:
        transaction_query = transaction_query.filter(Transaction.account_id.is_(account_id))
    if owner_id: 
        transaction_query = transaction_query.filter(Transaction.owner_id.is_(owner_id))
    # if role:
    #     transaction_query = transaction_query.join(Users.roles).filter(Transaction.status.is_(role))

    transactions = transaction_query.all()
    return render_template('treasurer/index_trx.html', transactions=transactions,form=form)

@blueprint.route('/transactions/add', methods=['GET', 'POST']) 
def add_transaction():
    form = TransactionForm()
    if request.method == 'POST':
        
        if form.validate_on_submit():
            now = datetime.now()
            # Format the date and time
            formatted_now = now.strftime("%Y-%m-%dT%H:%M:%S")
            # form.trx_at.data = formatted_now
            transaction = Transaction(
                # trx_at=form.trx_at.data,#datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                # updated_at=formatted_now,
                description=form.description.data,
                debit=form.debit.data,
                credit=form.credit.data,
                account_id=form.account_id.data,
                status=form.status.data,
                owner_id=form.owner_id.data,
                treasurer_id=form.treasurer_id.data
            )
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction created successfully!', 'success')
            return redirect(url_for('treasurer.transactions'))  # Change 'index' to your desired endpoint
        else:
            app.logger.log(logging.ERROR,form.errors.items())
            now = datetime.now()
            # Format the date and time
            formatted_now = now.strftime("%Y-%m-%dT%H:%M:%S")
            flash('Failed!'+json.dumps(dict(form.errors.items()))+formatted_now, 'danger')
    return render_template('treasurer/add_trx.html', form=form)

@blueprint.route('/journals')
@superadmin_permission.require(http_exception=403)
def journals():
    # Replace this with actual role fetching logic
    roles = ['admin', 'user']
    return render_template('roles.html', roles=roles)

