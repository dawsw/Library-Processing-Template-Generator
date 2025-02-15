import os
from io import BytesIO
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


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
