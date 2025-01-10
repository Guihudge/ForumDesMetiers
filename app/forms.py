from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from app import db
import sqlalchemy as sa
from app.models import Jobs

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class JobsCreationForm(FlaskForm):
    jobsName = StringField("Nom du métier", validators=[DataRequired()])
    submit = SubmitField('Ajouter le metier')

    def validate_jobsName(self, jobs):
        jobs = db.session.scalar(sa.select(Jobs).where(Jobs.Name == jobs.data))
        if jobs is not None:
            raise ValidationError("Métier déjà crée")
