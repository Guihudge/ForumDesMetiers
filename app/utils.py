from fpdf import FPDF
from app.config import STUDENT_MESSAGE
from app.models import Jobs, User
from app import db
import sqlalchemy as sa

def convertjobsListToDict(jobsList):
    out = {}
    for j in jobsList:
        out[j.id] = j.Name
    
    return out

def _initPDF():
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("noto", fname="./font.ttf")
    pdf.add_font("noto", style="B", fname="./font_bold.ttf")
    pdf.set_font("noto", size=12)
    return pdf

def generateLoginPDF(datas, headers, outputPath, name, url_root):
    pdf = _initPDF()

    # Prof version
    for key in datas.keys():
        students = datas[key]

        pdf.write(text="Classe: " + key)
        pdf.ln()

        with pdf.table() as table:
            for data_row in headers:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
            for data_row in students:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        
        pdf.add_page()
    
    pdf.add_page()

    #Student message
    counter = 0
    for key in datas.keys():
        students = datas[key]
        for s in students: #format: Nom, Prénom, login, password
            lastname,firstname,login,pwd = s
            pdf.ln()
            pdf.write_html(text=STUDENT_MESSAGE.format(student=firstname+" "+lastname, url=url_root, login=login, pwd=pwd, section=key ))
            pdf.ln()

            counter += 1
            if counter >= 5:
                counter = 0
                pdf.add_page()
    
    pdf.output(outputPath + name)


def generateRepartitionPDF(slot1:dict, slot2:dict, slot3:dict):
    pdf = _initPDF()
    header = [("Élève", "Classe", "Rencontre 1","Rencontre 2", "Rencontre 3")]
    j = convertjobsListToDict(db.session.scalars(sa.select(Jobs)).all())

    with pdf.table() as table:
        for data_row in header:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        for k in slot1.keys():
            u:User = db.session.scalar(sa.Select(User).where(User.id == k))
            t = (u.displayName, u.classe, j[slot1[k][0]], j[slot1[k][1]], j[slot1[k][2]])
            row = table.row()
            for datum in t:
                row.cell(datum)
    
    pdf.add_page()
    with pdf.table() as table:
        for data_row in header:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        for k in slot2.keys():
            u:User = db.session.scalar(sa.Select(User).where(User.id == k))
            t = (u.displayName, u.classe, j[slot2[k][0]], j[slot2[k][1]], j[slot2[k][2]])
            row = table.row()
            for datum in t:
                row.cell(datum)
    
    pdf.add_page()
    with pdf.table() as table:
        for data_row in header:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)

        for k in slot3.keys():
            u:User = db.session.scalar(sa.Select(User).where(User.id == k))
            t = (u.displayName, u.classe, j[slot3[k][0]], j[slot3[k][1]], j[slot3[k][2]])
            row = table.row()
            for datum in t:
                row.cell(datum)
    
    pdf.output("static/repart.pdf")



