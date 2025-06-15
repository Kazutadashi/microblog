# Microblog
Microblog is a project I worked on to better understand the Python framework [Flask](https://flask.palletsprojects.com/en/stable/). Initially I discovered Flask when learning about how to use [Dash](https://plotly.com/examples/). I really enjoyed using Dash, but I wanted to have a bit more flexibility in terms of site structure. This lead me to read about the Flask framework. I wanted to incorporate this framework into my tool-set so that I could build my own front facing web applications that integrate things I've learned whilst studying Machine Learning.

This project includes account creation, email support, full-text search using [Elasticsearch](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/installing-elasticsearch), background jobs using [Redis Queue](https://python-rq.org/), user-to-user private messaging, API endpoints, partial Spanish and Chinese localization, ORM, and much more.



![[Pasted image 20250612234544.png]]

Most of this project was created by following alongside Miguel Grinberg's
*"The Flask Mega-Tutorial"* with some changes of my own. If you are interested in doing this project yourself, I highly recommend visiting Miguel's [blog](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) which includes the full tutorial, or purchasing the tutorial in book form on [Amazon](https://amzn.to/3MQffrm).

![Pasted image 20250614234544](https://github.com/user-attachments/assets/141f15c2-ce5e-4492-ba9d-1a844231dc99)

![Pasted image 20250612234544](https://github.com/user-attachments/assets/470c6f2d-e27e-475f-a5d4-7263ec326250)

# Setup
If you would like to run this yourself, you can run a very basic version easily by first cloning the repository, creating a virtual environment, and then installing the requirements.

```bash
$ git clone https://github.com/Kazutadashi/microblog.git
$ cd microblog
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

After this has been finished, you will need to setup the database before running the application. This can be done via

```bash
$ flask db upgrade
$ flask run
```

`microblog` should now be running on http://127.0.0.1:5000 by default.

Note that this does not include anything else that requires external servers or tools. Each of these will need to be configured if you want them to run on this test instance. 
I will not include instructions on how to get all of these services running, but if you really want to, here is where you can find instructions:

| Service                                | Guide                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------------- |
| Email Support                          | https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support      |
| Full-Text Search                       | https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search |
| Background Jobs (Exporting User Posts) | https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxii-background-jobs |

# What I Learned
This tutorial was a fantastic introduction into the world of full stack development. Before this, I only had a very rudimentary understanding of building single page sites using HTML and JavaScript, and deploying something that could potentially be used in industry or that was more than just a small hobby project was out of the question.

I found it particularly interesting to learn about localization, password hashing, and the entire process behind sending password resets. The technology behind them was very simple yet powerful. Understanding how pages could be dynamically created using Jinja2 was a very eye opening moment for me as well with someone with such little exposure to this.

I believe now after finishing this book and project, I could make a reasonable attempt at making my own *useful* web application for all sorts of things, and more importantly incorporate my math and data analysis background into something productive.

## Challenges
The most difficult portion of this project was definitely the ORM style database. Having a "table" act as an object with its own methods was difficult to understand at first, especially when back population was included. Now that I've used it over the past few months working the project, I can see an amazing benefit of not just having everything be based on some complicated SQL query. 

# Technologies Used

Below is a list of some of the major technologies that are used in this project.

| Area                | Technology / Tool                           |
| ------------------- | ------------------------------------------- |
| **Framework**       | Flask, Flask-Bootstrap                      |
| **Templating**      | Jinja2                                      |
| **Forms**           | Flask-WTF, WTForms                          |
| **Database**        | SQLite (dev), SQLAlchemy                    |
| **Migrations**      | Flask-Migrate, Alembic                      |
| **User Management** | Flask-Login, Werkzeug (password hashing)    |
| **Email**           | Flask-Mail, SMTP (SendGrid, Mailgun, etc.)  |
| **I18n / Time**     | Flask-Babel, Flask-Moment                   |
| **Testing**         | unittest, coverage.py                       |
| **Async / Tasks**   | Redis Queue                                 |
| **API**             | JSON, custom Flask routes, JWT/token auth   |
| **Deployment**      | Linux, Docker, Gunicorn                     |
