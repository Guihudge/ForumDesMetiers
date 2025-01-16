from flask import render_template, flash, redirect, url_for
from app import app
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import *
from app.forms import LoginForm, JobsCreationForm, MakeWish
from flask import request
from urllib.parse import urlsplit

@app.route('/')
@app.route('/index')
@login_required
def index():
    return "Hello, World!"

@app.route("/me")
@login_required
def me():
    locUser:User = current_user
    return f"Hi, {locUser.username}"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            app.logger.info(f"Invalid login or password, user:{form.username.data}")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    user:User = current_user
    if user.rightLevel == 0: # student
        return "Student need to choose jobs"
    elif user.rightLevel == 100: # teatcher
        return "Teatcher panel! \n - Jobs creation\n- Students creation\n-close jobs selection"
    else:
        app.logger.critical(f"User {user.username} get a non correct access level ({user.rightLevel})!")
        logout_user()
        return url_for(login)

@app.route("/jobsCreation", methods=['GET', 'POST'])
@login_required
def jobsCreation():
    user:User = current_user
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = JobsCreationForm()
        if form.validate_on_submit():
            job = Jobs(Name=form.jobsName.data)
            db.session.add(job)
            db.session.commit()
            return redirect(url_for('jobsCreation'))
        return render_template("jobsCreate.html", form=form)

@app.route("/jobs")
@login_required
def jobsList():
    jobs = db.session.scalars(sa.select(Jobs)).all()
    return render_template("jobsList.html", jobs=jobs)

@app.route("/jobselection", methods=['GET', 'POST'])
@login_required
def jobselection():
    user:User = current_user
    if user.rightLevel != 0:
        return redirect(url_for('dashboard'))
    else:
        # Jobs selection
        jobs = db.session.scalars(sa.select(Jobs)).all()
        form = MakeWish()
        jobsList = [(i.id, i.Name) for i in jobs]
        form.first.choices = jobsList
        form.second.choices = jobsList
        form.third.choices = jobsList
        form.fourth.choices = jobsList
        form.fifth.choices = jobsList
        if form.validate_on_submit():
            print(form.first.data)
            w = WhishList(id=user.id, first=form.first.data, second=form.second.data, third=form.third.data, fourth=form.fourth.data, fifth=form.fifth.data)
            db.session.add(w)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template("jobsSelection.html", form=form)