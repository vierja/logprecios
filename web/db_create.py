from migrate.versioning import api
###from config import SQLALCHEMY_DATABASE_URI
#from config import SQLALCHEMY_MIGRATE_REPO
from trackerapp import db, app
import os.path

def create():
	db.create_all()
	if not os.path.exists(app.config.get('SQLALCHEMY_MIGRATE_REPO')):
	    api.create(app.config.get('SQLALCHEMY_MIGRATE_REPO'), 'database repository')
	    api.version_control(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
	else:
	    api.version_control(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'), api.version(app.config.get('SQLALCHEMY_MIGRATE_REPO')))

if __name__ == "__main__":
	create()
