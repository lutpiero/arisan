from apps.home import blueprint
from apps import create_app, db
from apps.models import User  # Assuming you have a User model

apps = create_app()
apps.app_context().push()

# Create super admin user
superadmin = User(username='lutpiero', email='lutpiero@gmail.com', role='superadmin')
superadmin.set_password('P@$$w0rd')  # Assuming you have a set_password method

db.session.add(superadmin)
db.session.commit()

print("Super admin user created.")
