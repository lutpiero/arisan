from flask import render_template, redirect, url_for, flash, request
from apps import db
from apps.account import blueprint
from apps.account.forms import AccountForm
from apps.treasurer.models import Account

@blueprint.route('/accounts')
def index():
    accounts = Account.query.all()
    return render_template('accounts/index.html', accounts=accounts)

@blueprint.route('/accounts/new', methods=['GET', 'POST'])
def new_account():
    form = AccountForm()
    if form.validate_on_submit():
        account = Account(
            name=form.name.data,    
            description=form.description.data,
            active=form.active.data
        )
        db.session.add(account)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('account.index'))
    return render_template('accounts/new_account.html', form=form)

@blueprint.route('/accounts/<int:id>/edit', methods=['GET', 'POST'])
def edit_account(id):
    account = Account.query.get_or_404(id)
    form = AccountForm(obj=account)
    if form.validate_on_submit():
        account.name = form.name.data
        account.description = form.description.data
        account.active = form.active.data
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('account.index'))
    return render_template('accounts/edit_account.html', form=form)

@blueprint.route('/accounts/<int:id>/delete', methods=['POST'])
def delete_account(id):
    account = Account.query.get_or_404(id)
    db.session.delete(account)
    db.session.commit()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('account.index'))
