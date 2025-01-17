from fpdf import FPDF

def convertjobsListToDict(jobsList):
    out = {}
    for j in jobsList:
        out[j.id] = j.Name
    
    return out

def generateLoginPDF(datas, headers, outputPath, name):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("noto", fname="./font.ttf")
    pdf.add_font("noto", style="B", fname="./font_bold.ttf")
    pdf.set_font("noto", size=12)


    for key in datas.keys():
        l = datas[key]

        pdf.write(text=key)
        pdf.ln()

        with pdf.table() as table:
            for data_row in headers:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
            for data_row in l:
                row = table.row()
                for datum in data_row:
                    row.cell(datum)
        
        pdf.add_page()
    
    pdf.output(outputPath + name)
