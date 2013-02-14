from flask.ext.script import Manager
from trackerapp import app, db, scheduler
from populate import create_products_with_prices
from migrate.versioning import api
import os.path
import imp

manager = Manager(app)

@manager.command
def initdb():
    """Creates all database tables."""
    db.create_all()
    if not os.path.exists(app.config.get('SQLALCHEMY_MIGRATE_REPO')):
        api.create(app.config.get('SQLALCHEMY_MIGRATE_REPO'), 'database repository')
        api.version_control(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    else:
        api.version_control(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'), api.version(app.config.get('SQLALCHEMY_MIGRATE_REPO')))

@manager.command
def migratedb():
    migration = app.config.get('SQLALCHEMY_MIGRATE_REPO') + '/versions/%03d_migration.py' % (api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO')) + 1)
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'), tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    api.upgrade(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    print 'New migration saved as ' + migration
    print 'Current database version: ' + str(api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO')))

@manager.command
def downgradedb():
    v = api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    api.downgrade(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'), v - 1)
    print 'Current database version: ' + str(api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO')))

@manager.command
def upgradedb():
    api.upgrade(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO'))
    print 'Current database version: ' + str(api.db_version(app.config.get('SQLALCHEMY_DATABASE_URI'), app.config.get('SQLALCHEMY_MIGRATE_REPO')))

@manager.command
def dropdb():
    """Drops all database tables."""
    db.drop_all()

@manager.command
def resetdb():
    """Drops and creates all database tables."""
    db.drop_all()
    db.create_all()

@manager.command
def canceljobs():
    """Cancels all rq scheduled jobs"""
    list_of_job_instances = scheduler.get_jobs()
    for job in list_of_job_instances:
        print "Job %s cancelled" %job.id
        scheduler.cancel(job)

@manager.command
def populatedb():
    """Adds items with random prices to DB"""
    create_products_with_prices()

@manager.command
def resettest():
    dropdb()
    initdb()
    populatedb()


if __name__ == '__main__':
    manager.run()
