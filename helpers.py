import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image

def generatePDF(labelList, locationList, directionList, notes, imageList):
        
    pdf_buffer = BytesIO()

    #create canvas for PDF (612.0px, 792.0px) or (8.5in, 11in)
    PAGE_WIDTH, PAGE_HEIGHT = LETTER
    canvas = Canvas(pdf_buffer, pagesize=LETTER)
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(150, 10.2 * inch, "Library Processing Template:")

    #header border (x, y, width, height)
    canvas.rect(50, PAGE_HEIGHT - 75, PAGE_WIDTH - 100, 50)

    #book diagram image
    canvas.drawImage("static/booksDiagram.png", (PAGE_WIDTH - 512) / 2, PAGE_HEIGHT - 370, width = PAGE_WIDTH - 100, height=250)

    #create table
    table = createLabelTable(labelList, locationList, directionList)
    
    table_width, table_height = table.wrapOn(canvas, PAGE_WIDTH, PAGE_HEIGHT)

    #draw table on canvas (canvas, x, y)
    table.drawOn(canvas, (PAGE_WIDTH - 450) / 2, (PAGE_HEIGHT - 425) - table_height)

    #get image paths
    image_paths = getImagePaths(imageList)
    
    for image_path in image_paths:
        
        #move to new page
        canvas.showPage()

        #get image original dimensions
        with Image.open(image_path) as img:
            img_width, img_height = img.size

        #scale image if it is too large
        scaling_factor = min(PAGE_WIDTH / img_width, PAGE_HEIGHT / img_height)
        new_img_width = img_width * scaling_factor
        new_img_height = img_height * scaling_factor
        
        #add image to PDF
        canvas.drawImage(image_path, (PAGE_WIDTH - new_img_width) / 2, (PAGE_HEIGHT - new_img_height) / 2, width=new_img_width, height=new_img_height)   

    #remove images after inserting in PDF
    for image_path in image_paths:
        os.remove(image_path)

    #save and close PDF
    canvas.save()

    pdf_buffer.seek(0)

    return pdf_buffer

def createLabelTable(labelList, locationList, directionList):
    labels = []
    labelHeaders = [["Item", "Location", "Direction"]]

    #create own paragraph style for centered text
    custom_style = ParagraphStyle(
        name="CustomStyle",
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.black,
        alignment=0, #centered text 
        leading=12 
    )

    #add each label to labels list
    #covert each labelName to paragraph for wordwrapping
    for label in range(len(labelList)):
        labels.append([
            Paragraph(labelList[label], custom_style),
            Paragraph(locationList[label], custom_style),
            Paragraph(directionList[label], custom_style),
        ])

    #create data for table
    table_data = labelHeaders + labels

    #create table for labels
    table = Table(table_data, colWidths=[150, 150, 150])

    table.setStyle(TableStyle([
        #header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.white), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),

        #data styling
        ('GRID', (0, 1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white), 
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True)
    ]))

    return table


def getImagePaths(imageList):
    image_paths = []

    temp_image_dir = "temp"
    os.makedirs(temp_image_dir, exist_ok=True)

    for image in imageList:
        file_path = os.path.join(temp_image_dir, image.filename)
        image.save(file_path)
        image_paths.append(file_path)

    return image_paths
    
