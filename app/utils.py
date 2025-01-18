from fpdf import FPDF
from app.config import STUDENT_MESSAGE

def convertjobsListToDict(jobsList):
    out = {}
    for j in jobsList:
        out[j.id] = j.Name
    
    return out

def generateLoginPDF(datas, headers, outputPath, name, url_root):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("noto", fname="./font.ttf")
    pdf.add_font("noto", style="B", fname="./font_bold.ttf")
    pdf.set_font("noto", size=12)

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
