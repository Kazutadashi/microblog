from flask import render_template
from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread

# make an sync wrapper function to send the mail asynchronously
# which avoids waiting on the single process before continuing with the program
def send_async_email(app, msg):
    # with in this case works because it opens up basically a try catch that involves pushing
    # the app context, and then popping it when its done. This is because app has __enter__() and __exit__() methods
    # defined, which allow with to work with that object.
    # This is also the case with file like objects, since they have these __enter__ and __exit__ things setup
    with app.app_context():
        # The context is basically like a temporary global variable. It is made possible by thread-local storage
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    # create a new thread and use it call the function with the specified args
    # this basically "primes" the function and says "go do your work, and tell me if you have downtime so I
    # can continue exection elsewhere". You can also set daemon=True to say that this thread should just be killed
    # no matter what if nothing else is running.
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()



