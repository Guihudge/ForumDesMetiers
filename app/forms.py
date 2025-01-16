from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
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

class MakeWish(FlaskForm):
    first = SelectField("1er voeux:")
    second = SelectField("2e voeux:")
    third = SelectField("3e voeux:")
    fourth = SelectField("4e voeux:")
    fifth = SelectField("5e voeux:")
    submit = SubmitField('Validé')

    def validate(self, extra_validators):
        if not super().validate():
            return False

        # Récupérer les valeurs des champs
        wishes = [self.first.data, self.second.data, self.third.data, self.fourth.data, self.fifth.data]

        # Vérifier les doublons
        if len(wishes) != len(set(wishes)):
            self.first.errors.append("Les vœux doivent être différents.")
            return False
        
        return True
