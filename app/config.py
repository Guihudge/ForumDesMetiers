import os
import secrets
basedir = os.path.abspath(os.path.dirname(__file__))

# Message for student id and pass. (Note: use html formating)
STUDENT_MESSAGE = """
Élève : {student} ({section})<br>
Le mercredi 12 mars, tu vas participer pendant 1h au forum des métiers du collège.<br>
Il va te permettre de rencontrer des professionnels de différents métiers, ce sera l’occasion pour toi de découvrir leur profession et/ou leurs formations.<br>
Tu dois aller sur <b> {url} </b> et utiliser l’identifiant et le mot de passe ci-dessous pour te connecter sur l’application où tu feras 5 vœux parmi les métiers proposés.<br>
<br>
Identifiant: \t<b>{login}</b><br>
Mot de passe: \t<b>{pwd}</b><br>
"""

REPARTION_STUDENT_MESSAGE="""
Nom Prénom : {name} \t Classe: {section} <br>
<center>
<p><b> FORUM des MÉTIERS 2024 / 2025 </b></p>
</center>
<li>
    <ul><b>→ En arrivant au réfectoire, prend ce document et de quoi prendre des notes. </b></ul>
    <ul><b>→ Déplace-toi dans le calme.</b></ul>
    <ul><b>→ Sois correct et poli avec tes interlocuteurs et écoute les autres afin d’éviter les répétitions.</b></ul>
    <ul><b>→ Respecte l’ordre ci-dessous.</b></ul>
</li>
<center>
<p>Voici les métiers que tu vas découvrir (entretien de 20 min environ) :</p>
</center>
<li>
    <ul>1er métier    {job1}</ul>
    <ul>2ème métier   {job2}</ul>
    <ul>3ème métier   {job3}</ul>
</li>
<br><br>
"""

TIMES_SLOT = ["8h-9h","9h-10h","10h15-11h15"]

#App config
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex()
    UPLOAD_PATH=os.environ.get('UPLOAD_PATH') or "./upload/"
    Open_Whish = True
    Setup_Done = False
    NC_Client = None
    BackupManager = None
    BackupErrorLog = []
    