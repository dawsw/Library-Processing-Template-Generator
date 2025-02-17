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

    #place book diagram image on PDF
    canvas.drawImage("static/books_nonbold.png", (PAGE_WIDTH - 512) / 2, PAGE_HEIGHT - 340, width = PAGE_WIDTH - 100, height=250)


    ### LABEL IMAGES ###
    attachedLabels = []

    #create a list of attached labels with {name, location, direction}
    for label in range(len(labelList)):
        if "Unattached" not in labelList[label]:
            attachedLabels.append({'name': labelList[label], 'location': locationList[label], 'direction': directionList[label]})


    #get all label image paths
    labelImagePaths = createLabelImages(attachedLabels)

    #get list of label coords
    labelCoords = getLabelImageCoordinates(attachedLabels)

    for label in range(len(attachedLabels)):
        image_path = labelImagePaths[label]

        # skip if label is unattached
        if image_path == '':
            continue

        #get x and y for label on canvas
        image_x = labelCoords[label][0]
        image_y = labelCoords[label][1]

        with Image.open(image_path) as img:
                img_width, img_height = img.size
        
        canvas.drawImage(image_path, image_x, image_y, width=img_width, height=img_height)

    #remove all templabel images
    for image in os.listdir('temp-labels'):
        os.remove('temp-labels/'+ image)
   
   
    ### TABLE ###
    table = createLabelTable(labelList, locationList, directionList)
    
    table_width, table_height = table.wrapOn(canvas, PAGE_WIDTH, PAGE_HEIGHT)

    #draw table on canvas (canvas, x, y)
    table.drawOn(canvas, (PAGE_WIDTH - 450) / 2, (PAGE_HEIGHT - 385) - table_height)

    table_y = (PAGE_HEIGHT - 385) - table_height
    note_y = table_y - 58

    ### NOTES ###
    canvas.setFillColor(colors.lightgrey)
    canvas.rect(81, table_y - 60, 40, 20, stroke=0, fill=1)

    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(86, note_y + 5, "Notes:")
    

    ### NOTES TEXT ###
    notes_y_position = note_y - 20  # Start below the top margin
    line_height = 10  # Space between lines
    notes_left_margin = 81  # Left margin
    notes_right_margin = 0  # Right margin
    usable_width = PAGE_WIDTH - notes_left_margin - notes_right_margin + 10

    paragraphs = notes.split("\n")

    canvas.setFont("Helvetica", 10)
    for paragraph in paragraphs:
        if paragraph.strip() == "":  #handle blank lines
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

            #draw the last line of the paragraph
            if line:
                if notes_y_position < 50:  #check again before drawing the last line
                    canvas.showPage()
                    canvas.setFont("Helvetica", 10)
                    notes_y_position = PAGE_HEIGHT - 50

                canvas.drawString(notes_left_margin, notes_y_position, line.strip())
                notes_y_position -= line_height  #move down after paragraph


    ### USER-UPLOADED IMAGES ###
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




def getLabelImageCoordinates(labels):
    label_XY_List = []

    for label in labels:      
        #Vertical Spine/AR/Lexile
        if ('Spine' in label['name'] or 'Lexile' in label['name'] or 'Small A/R' in label['name']) and 'Vertical' in label['direction']:
            location = label['location']
            if location in vertical_spine_ar_lexiles_coords:
                label_XY_List.append(vertical_spine_ar_lexiles_coords[location])

        #Vertical Barcode
        elif 'Barcode' in label['name'] and 'Vertical' in label['direction']:
            location = label['location']
            if location in vertical_barcodes_coords:
                label_XY_List.append(vertical_barcodes_coords[location])

        #Horizontal Spine/AR/Lexile
        elif ('Spine' in label['name'] or 'Lexile' in label['name'] or 'Small A/R' in label['name']) and 'Horizontal' in label['direction']:
            location = label['location']
            if location in horizontal_spine_ar_lexiles_coords:
                label_XY_List.append(horizontal_spine_ar_lexiles_coords[location])

        #Horizontal Barcode
        elif 'Barcode' in label['name'] and 'Horizontal' in label['direction']:
            location = label['location']
            print(location)
            if location in horizontal_barcodes_coords:
                label_XY_List.append(horizontal_barcodes_coords[location])

        #Large AR
        elif 'Large A/R' in label['name']:
            location = label['location']
            if location in large_ar_coords:
                label_XY_List.append(large_ar_coords[location])
        

    print(label_XY_List)
    return label_XY_List



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


def createLabelImages(attachedLabels):
    images = []

    temp_image_dir = "temp-labels"
    os.makedirs(temp_image_dir, exist_ok=True)

    labelNumber = 1

    for label in attachedLabels:

        #Barcode label
        if "Barcode" in label['name']:
            image_filename = f"BARCODE{labelNumber}.png"
            image = Image.open(os.path.join('static', 'BARCODE.png'))
            image = image.resize((35, 15))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Spine label
        elif "Spine" in label['name']:
            image_filename = f"SPINE{labelNumber}.png"
            image = Image.open(os.path.join('static', 'SPINE.png'))
            image = image.resize((26, 15))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Small AR label
        elif "Small A/R" in label['name']:
            image_filename = f"SMALLAR{labelNumber}.png"
            image = Image.open(os.path.join('static', 'SMALLAR.png'))
            image = image.resize((26, 15))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Lexile label
        elif "Lexile" in label['name']:
            image_filename = f"LEXILE{labelNumber}.png"
            image = Image.open(os.path.join('static', 'LEXILE.png'))
            image = image.resize((26, 15))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Large AR label
        elif "Large A/R" in label['name']:
            image_filename = f"LARGEAR{labelNumber}.png"
            image = Image.open(os.path.join('static', 'LARGEAR.png'))
            image = image.resize((25, 25))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        labelNumber += 1

    return images
    

vertical_barcodes_coords = {
    "1 (Standard Spine)": [299, 593], "2 (Standard A/R)": [299, 610], "5": [299, 648],
    "G": [193, 590], "H": [272, 590], "C": [325, 590], "D": [404, 590],
    "V": [404, 618], "U": [325, 618], "I": [272, 618], "T": [193, 618],
    "E": [193, 648], "F": [272, 648], "A": [325, 648], "B": [404, 648],
    "L": [58, 458], "M": [156, 458], "X": [156, 486], "W": [58, 486],
    "J": [58, 514], "K": [156, 514], "3": [252, 522],
    "P": [447, 458], "Q": [540, 458], "Z": [540, 486], "Y": [447, 486],
    "N": [447, 514], "O": [540, 514], "4": [347, 523]
}

vertical_spine_ar_lexiles_coords = {
    "1 (Standard Spine)": [299, 593], "2 (Standard A/R)": [299, 610], "5": [299, 656],
    "G": [193, 590], "H": [272, 590], "C": [325, 590], "D": [404, 590],
    "V": [404, 623], "U": [325, 623], "I": [272, 623], "T": [193, 623],
    "E": [193, 657], "F": [272, 657], "A": [325, 657], "B": [404, 657],
    "L": [58, 458], "M": [156, 458], "X": [156, 491], "W": [58, 491],
    "J": [58, 523], "K": [156, 523], "3": [252, 531],
    "P": [447, 458], "Q": [540, 458], "Z": [540, 491], "Y": [447, 491],
    "N": [447, 523], "O": [540, 523], "4": [347, 532]
}

horizontal_barcodes_coords = {
    "1 (Standard Spine)": [289, 593], "2 (Standard A/R)": [289, 608], "5": [289, 668],
    "G": [194, 590], "H": [252, 590], "C": [325, 590], "D": [383, 590],
    "V": [383, 628], "U": [325, 628], "I": [252, 628], "T": [194, 628],
    "E": [194, 668], "F": [252, 668], "A": [325, 668], "B": [383, 668],
    "L": [58, 458], "M": [136, 458], "X": [136, 494], "W": [58, 494],
    "J": [58, 534], "K": [136, 534], "3": [234, 542],
    "P": [447, 458], "Q": [520, 458], "Z": [520, 494], "Y": [447, 494],
    "N": [447, 534], "O": [520, 534], "4": [349, 543]
}

horizontal_spine_ar_lexiles_coords = {
    "1 (Standard Spine)": [293, 593], "2 (Standard A/R)": [293, 608], "5": [293, 668],
    "G": [194, 590], "H": [261, 590], "C": [325, 590], "D": [392, 590],
    "V": [392, 628], "U": [325, 628], "I": [261, 628], "T": [194, 628],
    "E": [194, 668], "F": [261, 668], "A": [325, 668], "B": [392, 668],
    "L": [58, 458], "M": [145, 458], "X": [145, 494], "W": [58, 494],
    "J": [58, 534], "K": [145, 534], "3": [241, 542],
    "P": [447, 458], "Q": [529, 458], "Z": [529, 494], "Y": [447, 494],
    "N": [447, 534], "O": [529, 534], "4": [349, 543]
}

large_ar_coords = {
    "1 (Standard Spine)": [293.5, 593], "2 (Standard A/R)": [293.5, 608], "5": [293.5, 656],
    "G": [193, 590], "H": [262, 590], "C": [325, 590], "D": [394, 590],
    "V": [394, 623], "U": [325, 623], "I": [262, 623], "T": [193, 623],
    "E": [193, 657], "F": [262, 657], "A": [325, 657], "B": [394, 657],
    "L": [57, 458], "M": [146, 458], "X": [146, 491], "W": [57, 491],
    "J": [57, 525], "K": [146, 525], "3": [242, 531],
    "P": [446, 458], "Q": [530, 458], "Z": [530, 491], "Y": [446, 491],
    "N": [446, 525], "O": [530, 525], "4": [347, 533]
}
