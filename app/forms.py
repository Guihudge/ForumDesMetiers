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
    first = SelectField("1er voeu:")
    second = SelectField("2e voeu:")
    third = SelectField("3e voeu:")
    fourth = SelectField("4e voeu:")
    fifth = SelectField("5e voeu:")
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

class RegisterForm(FlaskForm):
    displayName = StringField('Nom prénom', validators=[DataRequired()])
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    classe = StringField('Classe', validators=[DataRequired()])
    rightLevel = SelectField("Niveaux d'acces", choices=[(0, "Élève"), (100, "Proffesseur")], validators=[DataRequired()])
    submit = SubmitField('Validé')

class BatchRegister(FlaskForm):
    file = FileField("Lsite au format csv.", validators=[DataRequired()])
    submit = SubmitField('Envoyé')