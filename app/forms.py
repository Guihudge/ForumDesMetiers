from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField, SelectMultipleField, IntegerField, RadioField
from wtforms.validators import DataRequired, ValidationError, regexp, Length
from app import db
import sqlalchemy as sa
from app.models import Jobs, User

class LoginForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Mot de passe (jjmmaaaa)', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Connexion')

class JobsCreationForm(FlaskForm):
    jobsName = StringField("Nom du métier", validators=[DataRequired()])
    description = StringField("Description", validators=[Length(max=512)])
    newJobs = True
    submit = SubmitField('Ajouter le metier')

    def validate_jobsName(self, jobs):
        jobs = db.session.scalar(sa.select(Jobs).where(Jobs.Name == jobs.data))
        if self.newJobs and jobs is not None:
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
            self.first.errors=["Les vœux doivent être différents."]
            return False
        
        return True

# Account creation, student and teatcher
class RegisterForm(FlaskForm):
    displayName = StringField('Nom prénom', validators=[DataRequired()])
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    classe = StringField('Classe')
    rightLevel = SelectField("Niveaux d'acces", choices=[(0, "Élève"), (100, "Professeur")], validators=[DataRequired()])
    submit = SubmitField('Valider')

    def validate(self, extra_validators):
        l = self.rightLevel.data

        if (int(l) == 0 and self.classe.data) or (int(l) == 100):
            return super().validate()
        else: 
            self.classe.errors=["Un élève doit avoirs une classe"]
            return False

# Batch student register
class BatchRegister(FlaskForm):
    file = FileField("Lsite au format csv.", validators=[DataRequired()])
    submit = SubmitField('Envoyer')

class UploadFile(FlaskForm):
    file = FileField("Fichier", validators=[DataRequired()])
    submit = SubmitField('Envoyer')

class SectionSelection(FlaskForm):
    section = SelectField("Classe")
    submit = SubmitField("Valider")

class RepartForm(FlaskForm):
    # Bad -> hard coded
    slot1 = SelectMultipleField("Créneau 1")
    nbStudentSlot1 = IntegerField("Élève(s) par intervenant")
    slot2 = SelectMultipleField("Créneau 2")
    nbStudentSlot2 = IntegerField("Élève(s) par intervenant")
    slot3 = SelectMultipleField("Créneau 3")
    nbStudentSlot3 = IntegerField("Élève(s) par intervenant")
    submit = SubmitField("Valider")

    def validate(self, extra_validators):
        if not super().validate():
            return False

        # Check if all wish is different
        nbStaction = len(self.slot1.choices)
        total = len(self.slot1.data) + len(self.slot3.data) + len(self.slot2.data)

        if nbStaction != total:
            self.slot1.errors.append("Erreur vérifier la section, il ne doit pas y avoirs de chevauchement")
            return False
        
        return True

class SplitSectionForm(FlaskForm):
    submit = SubmitField('Valider')

    @staticmethod
    def create_form(users:list[User]):
        form_name = 'SplitSection'
        fields = {
            
            'submit': SubmitField('Submit')
        }
        for user in users:
            # Champ pour le Groupe A
            field_name_a = f'choice_A_{user.id}'
            fields[field_name_a] = BooleanField(
                label='Groupe A',  # Le label n'est pas utilisé dans le tableau, mais doit être présent
                default=False
            )
            
            # Champ pour le Groupe B
            field_name_b = f'choice_B_{user.id}'
            fields[field_name_b] = BooleanField(
                label='Groupe B',
                default=False
            )
        
        # On utilise 'type' pour créer une nouvelle classe de formulaire
        return type(form_name, (FlaskForm,), fields)
    
class UserSelectionForm(FlaskForm):
    user_id = SelectField(
        'Sélectionner un utilisateur',
        validators=[DataRequired()],
        # La classe 'form-control' est pour Bootstrap
        render_kw={'class': 'form-control'} 
    )

class NextCloudLogin(FlaskForm):
    nc_server = StringField("Serveur NextCloud", validators=[DataRequired()])
    nc_username = StringField("utilisateur NextCloud")
    nc_password = PasswordField("NextCloud App Password")
    submit = SubmitField("Valider")