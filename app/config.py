import os
basedir = os.path.abspath(os.path.dirname(__file__))

STUDENT_MESSAGE = """
Élève : {student} ({section})<br>
Le mercredi 12 mars, tu vas participer pendant 1h au forum des métiers du collège.<br>
Il va te permettre de rencontrer des professionnels de différents métiers, ce sera l’occasion pour toi de découvrir leur profession et/ou leurs formations.<br>
Tu dois aller sur <b> {url} </b> et utiliser l’identifiant et le mot de passe ci-dessous pour te connecter sur l’application où tu feras 5 vœux parmi les métiers proposés.<br>
<br>
Identifiant: \t<b>{login}</b><br>
Mot de passe: \t<b>{pwd}</b><br>
"""

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_PATH="./upload/"
    