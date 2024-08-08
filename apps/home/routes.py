# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps import db

@blueprint.route('/index')
@login_required
def index():
    #print('123')
    #exit
    from apps.authentication.models import Users, Role, UserRoles

#app = create_app()
#app.app_context().push()

# Create roles
    #admin_role = Role(name='admin')
    #superadmin_role = Role(name='superadmin')
    #db.session.add(admin_role)
    #db.session.add(superadmin_role)
    #db.session.commit()

# Create super admin user
    #superadmin = Users(username='superadmin', email='superadmin@example.com')
    #superadmin.set_password('superadminpassword')
    #db.session.add(superadmin)
    #db.session.commit()

# Assign superadmin role to the user
    #user_role = UserRoles(user_id=superadmin.id, role_id=superadmin_role.id)
    #db.session.add(user_role)
    #db.session.commit() 
    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
