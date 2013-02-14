import imp
from migrate.versioning import api
from trackerapp import db, app

def migrate():
    migration = app.config.get('SQLALCHEMY_MIGRATE_REPO') + '/versions/%03d_migration.py' % (api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO')) + 1)
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'), tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    a = api.upgrade(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    print 'New migration saved as ' + migration
    print 'Current database version: ' + str(api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO')))

if __name__ == '__main__':
    migrate()
