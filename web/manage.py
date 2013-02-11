from flask.ext.script import Manager
from trackerapp import app, db, scheduler
from populate import create_products_with_prices

manager = Manager(app)

@manager.command
def initdb():
    """Creates all database tables."""
    db.create_all()

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
