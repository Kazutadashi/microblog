import time
import sys
import json
from flask import render_template
from rq import get_current_job
from app import create_app, db
from app.api.tokens import get_token
from app.email import send_email
from app.models import Task, User, Post
import sqlalchemy as sa

# Another instance of this application is created here because RQ does not have access to microblog.py
# microblog.py is what is run when flask run --debug is used.
app = create_app()
# This makes the "app" variable the "current_app" variable essentially.
app.app_context().push()

def example(seconds):
    job = get_current_job()
    print('Starting task')
    for i in range(seconds):
        job.meta['progress'] = 100.0 * i / seconds
        job.save_meta()
        print(i)
        time.sleep(1)
    job.meta['progress'] = 100
    job.save_meta()
    print('Task complete')


def export_posts(user_id):
    try:
        user = db.session.get(User, user_id)
        _set_task_progress(0)
        data = []
        i = 0
        total_posts = db.session.scalar(sa.select(sa.func.count()).select_from(
            user.posts.select().subquery()))
        for post in db.session.scalars(user.posts.select().order_by(
            Post.timestamp.asc())):
            data.append({'body': post.body,
                         'timestamp': post.timestamp.isoformat() + 'Z'})
            time.sleep(5)
            i += 1
            _set_task_progress(100 * i // total_posts)

        send_email(
            '[Microblog] Your blog posts',
            sender=app.config['ADMINS'][0], recipients=[user.email],
            text_body=render_template('email/export_posts.txt', user=user),
            html_body=render_template('email/export_posts.html', user=user),
            attachments=[('posts.json', 'application/json', json.dumps({'posts': data}, indent=4))],
            sync=True
        )
    except Exception:
        _set_task_progress(100)
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = db.session.get(Task, job.get_id())
        task.user.add_notification('task_progress', {'task_id': job.get_id(), 'progress': progress})

        if progress >= 100:
            task.complete = True
        db.session.commit()