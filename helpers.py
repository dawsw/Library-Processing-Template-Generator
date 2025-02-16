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
    canvas.setFont("Helvetica", 20)
    canvas.setFillColorRGB(0.9, 0.9, 0.9)
    
    #header border (x, y, width, height)
    canvas.setLineWidth(2) 
    canvas.rect(81, PAGE_HEIGHT - 60, PAGE_WIDTH - 162, 40)

    canvas.setFillColor(colors.black)
    canvas.drawString(180, 10.35 * inch, "Library Processing Template")

    #book diagram image
    canvas.drawImage("static/books_nonbold.png", (PAGE_WIDTH - 512) / 2, PAGE_HEIGHT - 340, width = PAGE_WIDTH - 100, height=250)

    #create table
    table = createLabelTable(labelList, locationList, directionList)
    
    table_width, table_height = table.wrapOn(canvas, PAGE_WIDTH, PAGE_HEIGHT)

    #draw table on canvas (canvas, x, y)
    table.drawOn(canvas, (PAGE_WIDTH - 450) / 2, (PAGE_HEIGHT - 385) - table_height)

    table_y = (PAGE_HEIGHT - 385) - table_height
    note_y = table_y - 58

    #notes rectangle
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(81, table_y - 60, 40, 20, stroke=0, fill=1)

    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(86, note_y + 5, "Notes:")
    
    #notes
    notes_y_position = note_y - 20  # Start below the top margin
    line_height = 10  # Space between lines
    notes_left_margin = 81  # Left margin
    notes_right_margin = 0  # Right margin
    usable_width = PAGE_WIDTH - notes_left_margin - notes_right_margin + 10

    paragraphs = notes.split("\n")

    canvas.setFont("Helvetica", 10)
    for paragraph in paragraphs:
        if paragraph.strip() == "":  # Handle blank lines
            notes_y_position -= line_height  # Add spacing for blank lines
        else:
            words = paragraph.split()
            line = ""

            for word in words:
                if canvas.stringWidth(line + " " + word, "Helvetica", 12) < usable_width:
                    line += " " + word
                else:
                    # Check if we need a new page before writing text
                    if notes_y_position < 50:  # Bottom margin reached
                        canvas.showPage()
                        canvas.setFont("Helvetica", 10)  # Reset font after new page
                        notes_y_position = PAGE_HEIGHT - 50  # Reset position for new page

                    # Draw text and update Y position
                    canvas.drawString(notes_left_margin, notes_y_position, line.strip())
                    notes_y_position -= line_height
                    line = word  # Start new line

            # Draw the last line of the paragraph
            if line:
                if notes_y_position < 50:  # Check again before drawing the last line
                    canvas.showPage()
                    canvas.setFont("Helvetica", 10)
                    notes_y_position = PAGE_HEIGHT - 50

                canvas.drawString(notes_left_margin, notes_y_position, line.strip())
                notes_y_position -= line_height  # Move down after paragraph

    #if user uploaded images
    if imageList != '':
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
        alignment=1, #centered text 
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), 
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
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


def createLabelImages(labelList, directionList):
    images = []

    temp_image_dir = "tempLabels"
    os.makedirs(temp_image_dir, exist_ok=True)

    labelNumber = 1

    for label in range(len(labelList)):

        #Barcode label
        if "Barcode" in labelList[label] and "Unattached" not in labelList[label]:
            image_filename = f"BARCODE{labelNumber}.png"
            image = Image.open(os.path.join('static', 'BARCODE.png'))

            if "Top to Bottom" in directionList[label]:
                image = image.rotate(-90, expand=True)
                image = image.resize((25, 60))
            elif "Bottom to Top" in directionList[label]:
                image = image.rotate(90, expand=True)
                image = image.resize((25, 60))
            elif "Horizontal" in directionList[label]:
                image = image.resize((60, 25))

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Spine label
        elif "Spine" in labelList[label] and "Unattached" not in labelList[label]:
            image_filename = f"SPINE{labelNumber}.png"
            image = Image.open(os.path.join('static', 'SPINE.png'))

            if "Top to Bottom" in directionList[label]:
                image = image.rotate(-90, expand=True)
                image = image.resize((35, 50))
            elif "Bottom to Top" in directionList[label]:
                image = image.rotate(90, expand=True)
                image = image.resize((35, 50))
            elif "Horizontal" in directionList[label]:
                image = image.resize((50, 35))

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Small AR label
        elif "Small AR" in labelList[label] and "Unattached" not in labelList[label]:
            image_filename = f"SMALLAR{labelNumber}.png"
            image = Image.open(os.path.join('static', 'SMALLAR.png'))

            if "Top to Bottom" in directionList[label]:
                image = image.rotate(-90, expand=True)
                image = image.resize((35, 50))
            elif "Bottom to Top" in directionList[label]:
                image = image.rotate(90, expand=True)
                image = image.resize((35, 50))
            elif "Horizontal" in directionList[label]:
                image = image.resize((50, 35))

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Lexile label
        elif "Lexile" in labelList[label] and "Unattached" not in labelList[label]:
            image_filename = f"LEXILE{labelNumber}.png"
            image = Image.open(os.path.join('static', 'LEXILE.png'))

            if "Top to Bottom" in directionList[label]:
                image = image.rotate(-90, expand=True)
                image = image.resize((35, 50))
            elif "Bottom to Top" in directionList[label]:
                image = image.rotate(90, expand=True)
                image = image.resize((35, 50))
            elif "Horizontal" in directionList[label]:
                image = image.resize((50, 35))

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Large AR label
        elif "Large AR" in labelList[label] and "Unattached" not in labelList[label]:
            image_filename = f"LARGEAR{labelNumber}.png"
            image = Image.open(os.path.join('static', 'LARGEAR.png'))

            if "Top to Bottom" in directionList[label]:
                image = image.rotate(-90, expand=True)
                image = image.resize((50, 65))
            elif "Bottom to Top" in directionList[label]:
                image = image.rotate(90, expand=True)
                image = image.resize((50, 65))
            elif "Horizontal" in directionList[label]:
                image = image.resize((65, 50))

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)
        
        labelNumber += 1
        

    return images
    



