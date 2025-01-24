from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, ValidationError, regexp
from app import db
import sqlalchemy as sa
from app.models import Jobs

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe (jjmmaaaa)', validators=[DataRequired()])
    remember_me = BooleanField('Ce souvenir de moi')
    submit = SubmitField('Connexion')

class JobsCreationForm(FlaskForm):
    jobsName = StringField("Nom du métier", validators=[DataRequired()])
    submit = SubmitField('Ajouter le metier')

    def validate_jobsName(self, jobs):
        jobs = db.session.scalar(sa.select(Jobs).where(Jobs.Name == jobs.data))
        if jobs is not None:
            raise ValidationError("Métier déjà crée")

class MakeWish(FlaskForm):
    first = SelectField("1er vœux:")
    second = SelectField("2e vœux:")
    third = SelectField("3e vœux:")
    fourth = SelectField("4e vœux:")
    fifth = SelectField("5e vœux:")
    submit = SubmitField('Valider')

    def validate(self, extra_validators):
        if not super().validate():
            return False

        # Check if all wish is different
        wishes = [self.first.data, self.second.data, self.third.data, self.fourth.data, self.fifth.data]

        if len(wishes) != len(set(wishes)):
            self.first.errors.append("Les vœux doivent être différents.")
            return False
        
        return True

# Account creation, student and teatcher
class RegisterForm(FlaskForm):
    displayName = StringField('Nom prénom', validators=[DataRequired()])
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    classe = StringField('Classe', validators=[DataRequired()])
    rightLevel = SelectField("Niveaux d'acces", choices=[(0, "Élève"), (100, "Proffesseur")], validators=[DataRequired()])
    submit = SubmitField('Valider')

# Batch student register
class BatchRegister(FlaskForm):
    file = FileField("Lsite au format csv.", validators=[DataRequired()])
    submit = SubmitField('Envoyer')

class SectionSummary(FlaskForm):
    section = SelectField("Classe")
    submit = SubmitField("Valider")