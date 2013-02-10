from flask.ext.script import Manager
from trackerapp import app, db, scheduler

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

if __name__ == '__main__':
    manager.run()
