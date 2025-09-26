from flask import render_template, flash, redirect, url_for, send_file
from app import app
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Jobs, WhishList
from app.forms import LoginForm, JobsCreationForm, MakeWish, RegisterForm, BatchRegister, SectionSelection, RepartForm, UserSelectionForm, SplitSectionForm
from flask import request
from app.utils import convertjobsListToDict, generateLoginPDF, generateRepartitionPDF
from app.config import Config
import csv
from app.repartition import Repartition
from wtforms import Label

UPLOAD_PATH="./upload/"

def getCurrentUser() -> User:
    if isinstance(current_user, User):
        return current_user
    else:
        raise TypeError("Unable to get logged user")

# Main app page, default redirect to login
@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('login'))

#Check if user is loged and get his username
@app.route("/me")
@login_required
def me():
    locUser:User = getCurrentUser()
    return f"Hi, {locUser.username}"

# Log an user
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
    user:User = getCurrentUser()
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
        return render_template("studentDashboard.html", wish=whishName, user=user, OpenWhish=Config.Open_Whish)
    elif user.rightLevel == 100: # teatcher
        jobsNb = len(jobs)
        nbStudent = len(db.session.scalars(sa.select(User).where(User.rightLevel == 0)).all())
        nbWish = len(db.session.scalars(sa.select(WhishList)).all())
        return render_template("teatcherDashBoard.html", jobsNb = jobsNb,  nbStudent = nbStudent, nbWish = nbWish, user=user, WhishOpen=Config.Open_Whish)
    else:
        app.logger.critical(f"User {user.username} get a non correct access level ({user.rightLevel})!")
        logout_user()
        return url_for("login")

@app.route("/jobsCreation", methods=['GET', 'POST'])
@login_required
def jobsCreation():
    global jobsList
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = JobsCreationForm()
        if form.validate_on_submit():
            job = Jobs(Name=form.jobsName.data, description=form.description.data)
            db.session.add(job)
            db.session.commit()
            return redirect(url_for('jobsCreation'))
        return render_template("jobsCreate.html", form=form, user=user)

# Display all jobs (add jobs desc?)
@app.route("/jobs")
@login_required
def jobs():
    user:User = getCurrentUser()
    jobs = sorted(db.session.scalars(sa.select(Jobs)).all(), key= lambda job: job.Name)
    return render_template("jobsList.html", jobs=jobs, user=user)

# Page where student make choice
@app.route("/jobselection", methods=['GET', 'POST'])
@login_required
def jobselection():
    user:User = getCurrentUser()
    if user.rightLevel != 0:
        return redirect(url_for('dashboard'))
    else:
        if Config.Open_Whish:
            # Jobs selection
            jobs = sorted(db.session.scalars(sa.select(Jobs)).all(), key= lambda job: job.Name)
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
            return render_template("jobsSelection.html", form=form, user=user)
        else:
            return redirect(url_for('dashboard'))

# Teatcher page to get global summury on all users
@app.route("/summary", methods=['GET'])
@login_required
def summary():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        jobs = convertjobsListToDict(db.session.scalars(sa.select(Jobs)).all())
        Users = db.session.scalars(sa.select(User).where(User.rightLevel == 0)).all()
        s = []
        for u in Users:
            w = db.session.scalar(sa.select(WhishList).where(WhishList.id == u.id))
            if w is None:
                s.append([u.displayName if u.displayName is not None else u.username, u.classe,"--", "--", "--", "--", "--"])
            else:
                
                local = [u.displayName if u.displayName is not None else u.username , u.classe]
                local.append(jobs[w.first])
                local.append(jobs[w.second])
                local.append(jobs[w.third])
                local.append(jobs[w.fourth])
                local.append(jobs[w.fifth])
                s.append(local)

        return render_template("summary.html", s=s, user=user)

@app.route("/registerUser", methods=['GET', 'POST'])
@login_required
def registerUser():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            u = User(username=form.username.data, displayName=form.displayName.data, classe=form.classe.data)
            u.set_password(form.password.data)
            u.set_access(form.rightLevel.data)
            db.session.add(u)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template("registerUser.html", form=form, user=user, title="Formulaire d'Inscription")
    
# Batch register using generated list from pronote
@app.route("/batchRegister", methods=['GET','POST'])
@login_required
def batchRegister():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = BatchRegister()
        if form.validate_on_submit():
            file = request.files[form.file.name]
            file.save(UPLOAD_PATH + "tmp.csv")
            csvfile = open(UPLOAD_PATH + "tmp.csv", encoding="ISO-8859-1")
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            loginlist = []
            userdata = {}
            for row in spamreader:
                if row[0] != "Nom de famille":
                    nom = row[0].lower().replace("-", " ").split(" ")
                    prenom = row[1].lower().replace(" ", "-").split("-")
                    login = prenom[0][0] + nom[0]
                    pwd = row[2].replace("/","")
                    classe = row[3].replace("=", "").replace('"', '')
                    idx = 2

                    while login in loginlist:
                        login += str(idx)
                        idx += 1
                    
                    u = User(username=login, displayName=(row[0] + " " + row[1]), classe=classe)
                    u.set_access(0)
                    u.set_password(pwd)

                    if classe in userdata:
                        userdata[classe].append((row[0], row[1], login, pwd)) #format: Nom, Prénom, login, password
                    else:
                        userdata[classe] = [(row[0], row[1], login, pwd)]
                    db.session.add(u)
                    loginlist.append(login)
            db.session.commit()
            
            
            generateLoginPDF(userdata, [("Nom", "Prénom", "Login", "Mot de passe")], "./static/", "Logins.pdf", request.url_root)

            return send_file("../static/Logins.pdf")
        return render_template("batch_register.html", form=form, user=user)
    
@app.route("/classeSummary", methods=['GET','POST'])
@login_required
def classeSummary():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        form = SectionSelection()
        form.section.choices = sorted(list(set(db.session.scalars(sa.select(User.classe).where(User.rightLevel == 0)).all())))
        if form.validate_on_submit():
            jobs = convertjobsListToDict(db.session.scalars(sa.select(Jobs)).all())
            Users = db.session.scalars(sa.select(User).where(User.rightLevel == 0).where(User.classe == form.section.data)).all()
            s = []
            for u in Users:
                w = db.session.scalar(sa.select(WhishList).where(WhishList.id == u.id))
                if w is None:
                    s.append([u.displayName if u.displayName is not None else u.username, u.classe,"--", "--", "--", "--", "--"])
                else:
                
                    local = [u.displayName if u.displayName is not None else u.username , u.classe]
                    local.append(jobs[w.first])
                    local.append(jobs[w.second])
                    local.append(jobs[w.third])
                    local.append(jobs[w.fourth])
                    local.append(jobs[w.fifth])
                    s.append(local)
            return render_template("summary.html", s=s, user=user)

        return render_template("section_selection.html", form=form, user=user)
    
@app.route("/switchWishStatus", methods=['GET'])
@login_required
def switchWishStatus():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        Config.Open_Whish = not Config.Open_Whish
        return redirect(url_for('dashboard'))
    
@app.route("/repart", methods=['GET','POST'])
@login_required
def repart():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        sections = sorted(list(set(db.session.scalars(sa.select(User.classe).where(User.rightLevel == 0)).all())))
        form = RepartForm()
        form.slot1.choices = sections
        form.slot2.choices = sections
        form.slot3.choices = sections

        if form.validate_on_submit():
            
            slot1UserId = []
            slot2UserId = []
            slot3UserId = []
            
            for section in form.slot1.data:
                slot1UserId += db.session.scalars(sa.select(User.id).where(User.classe == section)).all()
            
            for section in form.slot2.data:
                slot2UserId += db.session.scalars(sa.select(User.id).where(User.classe == section)).all()
            
            for section in form.slot3.data:
                slot3UserId += db.session.scalars(sa.select(User.id).where(User.classe == section)).all()

            jobs = db.session.scalars(sa.select(Jobs.id)).all()
            repartitionSlot1 = Repartition(jobs, slot1UserId, form.nbStudentSlot1.data)
            repartitionSlot2 = Repartition(jobs, slot2UserId, form.nbStudentSlot2.data)
            repartitionSlot3 = Repartition(jobs, slot3UserId, form.nbStudentSlot3.data)

            generateRepartitionPDF(repartitionSlot1, repartitionSlot2, repartitionSlot3)

            return send_file("../static/repart.pdf")

        return render_template("repart.html", user=user, form=form)
    
@app.route("/jobsEdit", methods=['GET','POST'])
@login_required
def jobsEdit():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for('dashboard'))
    else:
        id = request.args['id']
        jobs = sorted(db.session.scalars(sa.select(Jobs).where(Jobs.id == id)).all(), key= lambda job: job.Name)
        form = JobsCreationForm()
        form.newJobs = False
        form.jobsName.data = jobs[0].Name
        form.description.data = jobs[0].description
        form.submit.label = Label(form.submit.id, "Modifier le métier")

        if form.validate_on_submit():
            print(f"Données du formulaire reçues : {request.form}")
            db.session.execute(sa.update(Jobs).where(Jobs.id == id).values(Name=request.form["jobsName"], description=request.form["description"]))
            db.session.commit()
            return redirect(url_for('jobs'))
        return render_template("jobsCreate.html", form=form, user=user)

@app.route("/splitSectionStep1", methods=['GET', 'POST'])
@login_required
def splitSectionStep1():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for("dashboard"))
    else:
        form = SectionSelection()
        form.section.choices = sorted(list(set(db.session.scalars(sa.select(User.classe).where(User.rightLevel == 0)).all())))
        if form.validate_on_submit():
            return(redirect(url_for("splitSectionStep2", section=form.section.data)))
    return render_template("section_selection.html", form=form, user=user)


@app.route("/splitSectionStep2", methods=['GET', 'POST'])
@login_required
def splitSectionStep2():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for("dashboard"))
    else:
        if not 'section' in request.args.keys():
            return redirect(url_for("splitSectionStep1"))
        
        section = request.args['section']
        Users = db.session.scalars(sa.select(User).where(User.rightLevel == 0).where(User.classe == section)).all()
        FormClass = SplitSectionForm.create_form(Users)
        form = FormClass()

        if form.validate_on_submit():
            is_valid = True
            results = {}
            
            for user in Users:
                field_name_a = f'choice_A_{user.id}'
                field_name_b = f'choice_B_{user.id}'
                
                is_in_group_a = getattr(form, field_name_a).data
                is_in_group_b = getattr(form, field_name_b).data
                
                # Validation d'exclusivité : (A AND NOT B) OR (B AND NOT A)
                # Ceci équivaut à (A XOR B)
                if (is_in_group_a and is_in_group_b) or (not is_in_group_a and not is_in_group_b):
                    is_valid = False
                    # Vous pouvez ajouter ici un message d'erreur spécifique à Flask
                    form.submit.errors.append(f"Erreur pour {user.username}: Vous devez sélectionner un et un seul groupe (A ou B).")
                    break # Arrêter la boucle et la validation
                    
                # Si la validation réussit pour cet utilisateur
                results[user.id] = {
                    'A': is_in_group_a,
                    'B': is_in_group_b
                }

            if is_valid:
                for stu in results:
                    db.session.execute(sa.update(User).where(User.id == stu).values(classe=section + ("A" if results[stu]["A"] else "B")))
                db.session.commit()
                return redirect(url_for('dashboard'))

        return render_template('splitSection.html', form=form, users=Users)

@app.route("/getUser", methods=['GET', 'POST'])
@login_required
def getUser():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for("dashboard"))
    else:
        form = UserSelectionForm()
        data = []

        for u in sorted(list(set(db.session.scalars(sa.select(User).where(User.rightLevel == 0)).all())), key= lambda user: user.displayName):
            data.append((u.id, u.displayName))

        form.user_id.choices = data
        if form.validate_on_submit():
            if 'redirect' in request.args.keys():
                return redirect(url_for(request.args['redirect'], id=form.user_id.data))
            else:
                return(redirect(url_for("dashboard")))
    return render_template("user_selection.html", form=form)

@app.route("/editUser", methods=['GET', 'POST'])
@login_required
def editUser():
    user:User = getCurrentUser()
    if user.rightLevel != 100:
        return redirect(url_for("dashboard"))
    else:
        if not 'id' in request.args.keys():
                return redirect(url_for("getUser", redirect="editUser"))
        id = int(request.args["id"])
        student:User = db.session.scalars(sa.select(User).where(User.id == id)).all()[0]
        form = RegisterForm()

        form.username.data = student.username
        form.username.validators = []
        
        form.displayName.data = student.displayName
        form.displayName.validators = []
        
        form.classe.data = student.classe
        
        del form.password


        if form.validate_on_submit():
            db.session.execute(sa.update(User).where(User.id == id).values(username=request.form["username"], rightLevel=request.form["rightLevel"], displayName=request.form["displayName"], classe=request.form["classe"]))
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            print("Validation Error")
        return render_template("registerUser.html", form=form, user=user, title="Modification de l'utilisateur")
