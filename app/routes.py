from flask import render_template, flash, redirect, url_for
from app import app
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import *
from app.forms import LoginForm, JobsCreationForm, MakeWish, RegisterForm
from flask import request
from app.utils import convertjobsListToDict

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
    jobs = convertjobsListToDict(db.session.scalars(sa.select(Jobs)).all())
    if user.rightLevel == 0: # student
        whishName = None
        wish = db.session.scalar(sa.select(WhishList).where(WhishList.id == user.id))
        
        if wish is not None:
            whishName = []
            whishName.append(jobs[wish.first])
            whishName.append(jobs[wish.second])
            whishName.append(jobs[wish.third])
            whishName.append(jobs[wish.fourth])
            whishName.append(jobs[wish.fifth])
        return render_template("studentDashboard.html", wish=whishName)
    elif user.rightLevel == 100: # teatcher
        jobsNb = len(jobs)
        nbStudent = len(db.session.scalars(sa.select(User).where(User.rightLevel == 0)).all())
        nbWish = len(db.session.scalars(sa.select(WhishList)).all())
        return render_template("teatcherDashBoard.html", jobsNb = jobsNb,  nbStudent = nbStudent, nbWish = nbWish)
    else:
        app.logger.critical(f"User {user.username} get a non correct access level ({user.rightLevel})!")
        logout_user()
        return url_for(login)

@app.route("/jobsCreation", methods=['GET', 'POST'])
@login_required
def jobsCreation():
    global jobsList
    user:User = current_user
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = JobsCreationForm()
        if form.validate_on_submit():
            job = Jobs(Name=form.jobsName.data)
            db.session.add(job)
            db.session.commit()
            jobsList = db.session.scalars(sa.select(Jobs)).all()
            return redirect(url_for('jobsCreation'))
        return render_template("jobsCreate.html", form=form)

@app.route("/jobs")
@login_required
def jobs():
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
            w = db.session.scalar(sa.select(WhishList).where(WhishList.id == user.id))
            if w is not None:
                db.session.execute(
                    sa.update(WhishList)
                        .where(WhishList.id == user.id)
                        .values(first=form.first.data, second=form.second.data, third=form.third.data, fourth=form.fourth.data, fifth=form.fifth.data)
                )
            else:
                w = WhishList(id=user.id, first=form.first.data, second=form.second.data, third=form.third.data, fourth=form.fourth.data, fifth=form.fifth.data)
                db.session.add(w)
            
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template("jobsSelection.html", form=form)

@app.route("/summary", methods=['GET'])
@login_required
def summary():
    user:User = current_user
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        jobs = convertjobsListToDict(db.session.scalars(sa.select(Jobs)).all())
        Users = db.session.scalars(sa.select(User).where(User.rightLevel == 0)).all()
        s = []
        for u in Users:
            w = db.session.scalar(sa.select(WhishList).where(WhishList.id == u.id))
            if w is None:
                s.append([u.username, "--", "--", "--", "--", "--"])
            else:
                local = [u.username]
                local.append(jobs[w.first])
                local.append(jobs[w.second])
                local.append(jobs[w.third])
                local.append(jobs[w.fourth])
                local.append(jobs[w.fifth])
                s.append(local)

        return render_template("summary.html", s=s)

@app.route("/registerUser", methods=['GET', 'POST'])
@login_required
def registerUser():
    user:User = current_user
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            u = User(username=form.username.data)
            u.set_password(form.password.data)
            u.set_access(form.rightLevel.data)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template("registerUser.html", form=form)