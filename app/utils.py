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
    pdf.set_font("noto", size=10)
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

def invertSlotDict(slot:dict):
    ts1, ts2, ts3 = {}, {}, {}
    for k in slot:
        j1, j2, j3 = slot[k]
        
        if j1 in ts1:
            ts1[j1].append(k)
        else:
            ts1[j1] = [k]
        
        if j2 in ts2:
            ts2[j2].append(k)
        else:
            ts2[j2] = [k]

        if j3 in ts3:
            ts3[j3].append(k)
        else:
            ts3[j3] = [k]
    return ts1, ts2, ts3

def formatUser(u:User):
    return f"{u.displayName} - {u.classe}"

def write_reprtition(pdf:FPDF, student:User,job1, job2, job3):
    with pdf.table() as table:
        header = table.row()
        header.cell(text=f"{student.displayName}", colspan=2)
        header.cell(text=f" Classe: {student.classe}", colspan=1)
        title = table.row()
        #pdf.set_fill_color(204, 204, 204)
        title.cell(text="FORUM des MÉTIERS 2024 / 2025", colspan=3, align="c")
        instruction = table.row()
        instruction.cell(text="-> En arrivant au réfectoire, prend ce document et de quoi prendre des notes.\n-> Déplace-toi dans le calme.\n-> Sois correct et poli avec tes interlocuteurs et écoute les autres afin d’éviter les répétitions.\n-> Respecte l’ordre ci-dessous.\n", colspan=3)
        empty = table.row()
        empty.cell(text="", colspan=3)
        welcome = table.row()
        #pdf.set_fill_color(204, 204, 204)
        welcome.cell(text="Voici les métiers que tu vas découvrir (entretien de 20 min environ) :", colspan=3, align="c")
        j1 = table.row()
        j1.cell(text="1er métier", colspan=1, align="c")
        j1.cell(text=job1, colspan=2, align="c")
        j2 = table.row()
        j2.cell(text="2ème métier", colspan=1, align="c")
        j2.cell(text=job2, colspan=2, align="c")
        j3 = table.row()
        j3.cell(text="3ème métier", colspan=1, align="c")
        j3.cell(text=job3, colspan=2, align="c")
    pdf.ln()
    




def generateRepartitionPDF(slot1:dict, slot2:dict, slot3:dict):
    pdf = _initPDF()
    header = [("Élève", "Classe", "Rencontre 1","Rencontre 2", "Rencontre 3")]
    j = convertjobsListToDict(db.session.scalars(sa.select(Jobs)).all())

    #Jobs per student
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
    
    # student per jobs
    
    header2 = [("Métier", "Élève 1","Élève 2")]
    header3 = [("Métier", "Élève 1","Élève 2", "Élève 3")]
    i = 1
    
    for slot,h in [(slot1, header2), (slot2, header3), (slot3, header3)]:
        timeSlot1, timeSlot2, timeSlot3 = invertSlotDict(slot)

        pdf.add_page()
        pdf.write(text=f"créneaux {i} - Slot 1\n")
        with pdf.table() as table:
            for data_row in h:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)

            for k in sorted(timeSlot1.keys()):
                jobs = j[k]
                nbStudent = len(timeSlot1[k])
                match nbStudent:
                    case 1:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot1[k][0]))
                        if len(h[0]) == 3:
                            t = (jobs, formatUser(u0), "")
                        else:
                            t = (jobs, formatUser(u0), "", "")
                    case 2:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot1[k][0]))
                        u1:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot1[k][1]))
                        if len(h[0]) == 3:
                            t = (jobs, formatUser(u0), formatUser(u1))
                        else:
                            t = (jobs, formatUser(u0), formatUser(u1), "")
                    case 3:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot1[k][0]))
                        u1:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot1[k][1]))
                        u2:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot1[k][2]))
                        t = (jobs, formatUser(u0), formatUser(u1), formatUser(u2))
                row = table.row()
                for datum in t:
                    row.cell(datum)
        
        pdf.add_page()
        pdf.write(text=f"créneaux {i} - Slot 2\n")
        with pdf.table() as table:
            for data_row in h:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)

            for k in sorted(timeSlot2.keys()):
                jobs = j[k]
                nbStudent = len(timeSlot2[k])
                match nbStudent:
                    case 1:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot2[k][0]))
                        if len(h[0]) == 3:
                            t = (jobs, formatUser(u0), "")
                        else:
                            t = (jobs, formatUser(u0), "", "")
                    case 2:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot2[k][0]))
                        u1:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot2[k][1]))
                        if len(h[0]) == 3:
                            t = (jobs, formatUser(u0), formatUser(u1))
                        else:
                            t = (jobs, formatUser(u0), formatUser(u1), "")
                    case 3:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot2[k][0]))
                        u1:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot2[k][1]))
                        u2:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot2[k][2]))
                        t = (jobs, formatUser(u0), formatUser(u1), formatUser(u2))
                row = table.row()
                for datum in t:
                    row.cell(datum)
        
        pdf.add_page()
        pdf.write(text=f"créneaux {i} - Slot 3\n")
        with pdf.table() as table:
            for data_row in h:
                    row = table.row()
                    for datum in data_row:
                        row.cell(datum)

            for k in sorted(timeSlot3.keys()):
                jobs = j[k]
                nbStudent = len(timeSlot3[k])
                match nbStudent:
                    case 1:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot3[k][0]))
                        if len(h[0]) == 3:
                            t = (jobs, formatUser(u0), "")
                        else:
                            t = (jobs, formatUser(u0), "", "")
                    case 2:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot3[k][0]))
                        u1:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot3[k][1]))
                        if len(h[0]) == 3:
                            t = (jobs, formatUser(u0), formatUser(u1))
                        else:
                            t = (jobs, formatUser(u0), formatUser(u1), "")
                    case 3:
                        u0:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot3[k][0]))
                        u1:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot3[k][1]))
                        u2:User = db.session.scalar(sa.Select(User).where(User.id == timeSlot3[k][2]))
                        t = (jobs, formatUser(u0), formatUser(u1), formatUser(u2))
                row = table.row()
                for datum in t:
                    row.cell(datum)
        i += 1
    
    pdf.add_page()
    pdf.add_page()
    addPage=0

    for studentID in slot1.keys():
        student:User = db.session.scalar(sa.Select(User).where(User.id == studentID))
        job1 = j[slot1[studentID][0]]
        job2 = j[slot1[studentID][1]]
        job3 = j[slot1[studentID][2]]
        write_reprtition(pdf, student,job1, job2, job3)

        addPage += 1
        if addPage == 3:
            pdf.add_page()
            addPage=0
    
    pdf.add_page()
    for studentID in slot2.keys():
        student:User = db.session.scalar(sa.Select(User).where(User.id == studentID))
        job1 = j[slot2[studentID][0]]
        job2 = j[slot2[studentID][1]]
        job3 = j[slot2[studentID][2]]
        write_reprtition(pdf, student,job1, job2, job3)

        addPage += 1
        if addPage == 3:
            pdf.add_page()
            addPage=0
    
    pdf.add_page()
    for studentID in slot3.keys():
        student:User = db.session.scalar(sa.Select(User).where(User.id == studentID))
        job1 = j[slot3[studentID][0]]
        job2 = j[slot3[studentID][1]]
        job3 = j[slot3[studentID][2]]
        write_reprtition(pdf, student,job1, job2, job3)

        addPage += 1
        if addPage == 3:
            pdf.add_page()
            addPage=0
        
        
    pdf.output("static/repart.pdf")



