from flask import render_template, redirect, url_for, session, current_app as app, request, flash
from flask_principal import Permission, RoleNeed, Identity, identity_loaded, identity_changed, AnonymousIdentity
from apps.user import blueprint
from apps.authentication.models import Users, Role
from apps.user.forms import UserEditForm
from apps import db
from apps import logging
# Define roles
admin_permission = Permission(RoleNeed('admin'))
superadmin_permission = Permission(RoleNeed('superadmin'))
any_admin_permission = admin_permission.union(superadmin_permission)


@blueprint.route('/users') 
@any_admin_permission.require(http_exception=403)
def users():
    # Replace this with actual user fetching logic
    username = request.args.get('username')
    email = request.args.get('email')
    role = request.args.get('role')

    users_query = Users.query

    if username:
        users_query = users_query.filter(Users.username.contains(username))
    if email: 
        users_query = users_query.filter(Users.email.contains(email))
    if role:
        users_query = users_query.join(Users.roles).filter(Role.name.contains(role))

    users = users_query.all()
    return render_template('users/users.html', users=users)

@blueprint.route('/roles')
@superadmin_permission.require(http_exception=403)
def roles():
    # Replace this with actual role fetching logic
    roles = ['admin', 'user']
    return render_template('roles.html', roles=roles)

@blueprint.route('/login/<role>')
def login(role):
    identity = Identity(role)
    identity_changed.send(app._get_current_object(), identity=identity)
    return redirect(url_for('main.index'))

@blueprint.route('/logout')
def logout():
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(app._get_current_object(), identity=AnonymousIdentity())
    return redirect(url_for('main.index'))

@blueprint.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@any_admin_permission.require(http_exception=403)
def edit_user(user_id):
    # perm = Users.user_permission(user_id)
    # Allow admins and superusers as well 
    # perm = perm.union(Users.role_permission('admin', 'superadmin'))

    # Check if the current user has the permission
    # if not perm.can():
    #     flash('You do not have permission to view this page.', 'danger')
    #     return redirect(url_for('home_blueprint.index'))
    
    user = Users.query.get_or_404(user_id)
    form = UserEditForm(obj=user)
    # form.roles.data = user.roles
    user_roles = []
    for user_role in user.roles:
        user_roles.append(user_role.id)
    if user_roles and request.method=='GET':    
        form.roles.data = user_roles
    # app.logger.setLevel(logging.INFO)
    # app.logger.info(form.roles)
   
    if request.method=='POST' and form.validate_on_submit():
        # form.populate_obj(user)

        # Handle password change if new password is provided
        if form.password.data:
            user.set_password(form.password.data)

        # Handle role assignment
        
        roles = []
        app.logger.log(logging.INFO,form.roles.data)
        # app.logger.info(form.roles.data)
        for role_id in form.roles.data:  # Assuming form field is named role_ids (list)
            role_instance = Role.query.get(role_id)
            app.logger.debug(role_id)
            if role_instance:
                roles.append(role_instance)

        # Clear existing roles (optional, depending on your logic)
        user.roles.clear()  # This removes existing associations

        # Associate roles with the user
        user.roles.extend(roles)

        db.session.add(user)
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('user.users'))
    
    if request.method=='POST': 
        flash('User updated failed', 'danger')


    return render_template('users/edit_user.html', form=form, user=user)
