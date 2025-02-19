import os
import json
from io import BytesIO
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PIL import Image


def generatePDF(libraryName, orderNumber, labelList, locationList, directionList, notes, imageList):

    pdf_buffer = BytesIO()
    
    #create canvas for PDF (612.0px, 792.0px) or (8.5in, 11in)
    PAGE_WIDTH, PAGE_HEIGHT = LETTER
    canvas = Canvas(pdf_buffer, pagesize=LETTER)
    canvas.setTitle('')
    canvas.setFont("Helvetica", 20)
    canvas.setFillColorRGB(0.9, 0.9, 0.9)
    
    ### HEADER ### (x, y, width, height)
    canvas.setLineWidth(2) 
    canvas.rect(81, PAGE_HEIGHT - 60, PAGE_WIDTH - 162, 40)

    canvas.setFillColor(colors.black)

    #add orderNumber to header if entered
    if orderNumber != '':
        canvas.drawString(160, 10.35 * inch, "#" + orderNumber + " - Processing Template")
    else:
        canvas.drawString(180, 10.35 * inch, "Library Processing Template")


    ### LIBRARY NAME ###
    if libraryName != '':
        library_label = "Library:"

        #get label and name widths
        library_label_width = canvas.stringWidth(library_label, "Helvetica", 12)
        libraryNameWidth = canvas.stringWidth(libraryName, "Helvetica", 10)
        
        #coordinates for label
        x = (PAGE_WIDTH - library_label_width - libraryNameWidth) / 2
        y = 9.86 * inch
        padding = 5

        canvas.setFont("Helvetica", 10)
        canvas.drawString(x + library_label_width + padding, y, libraryName)

        #create rectangle for "Library:"
        canvas.setFillColor(colors.lightgrey)

        canvas.rect(x - padding, y - padding, library_label_width + padding, 12 + padding, stroke=0, fill=1)

        #place "Library:" on rectangle
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(colors.black)
        canvas.drawString(x, y, library_label)


    ### BOOK DIAGRAM ###
    canvas.drawImage("static/books_nonbold.png", (PAGE_WIDTH - 512) / 2, PAGE_HEIGHT - 350, width = PAGE_WIDTH - 100, height=250)


    ### LABEL IMAGES ###
    attachedLabels = []
    unattachedLabelLocations = ['Unattached', 'See Notes']

    #create a list of attached labels with {name, location, direction}
    for label in range(len(labelList)):
        if "Unattached" not in labelList[label] and locationList[label] not in unattachedLabelLocations:
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




def getLabelImageCoordinates(attachedlabels):

    with open("data/coordinates.json", "r") as file:
        data = json.load(file)

    label_XY_List = []

    for label in attachedlabels:
        name = label['name']
        location = label['location']
        direction = label['direction']  
           
        #Spine/AR/Lexile/Genre
        if 'Spine' in name or 'Lexile' in name or 'Small A/R' in name or 'Genre' in name:
            #Vertical
            if 'Vertical' in direction and location in data['vertical_spine_coords']:
                label_XY_List.append(data['vertical_spine_coords'][location])
            #Horizontal
            elif 'Horizontal' in direction and location in data['horizontal_spine_coords']:
                label_XY_List.append(data['horizontal_spine_coords'][location])

        #Barcode
        elif 'Barcode' in name:
            #Vertical
            if 'Vertical' in direction and location in data['vertical_barcodes_coords']:
                label_XY_List.append(data['vertical_barcodes_coords'][location])
            #Horizontal
            elif 'Horizontal' in direction and location in data['horizontal_barcodes_coords']:
                label_XY_List.append(data['horizontal_barcodes_coords'][location])

        #Property
        elif 'Property' in name:
            #Vertical
            if 'Vertical' in direction and location in data['vertical_property_coords']:
                label_XY_List.append(data['vertical_property_coords'][location])
            #Horizontal
            elif 'Horizontal' in direction and location in data['horizontal_property_coords']:
                label_XY_List.append(data['horizontal_property_coords'][location])

        #Large AR
        elif 'Large A/R' in name:
            if location in data['large_ar_coords']:
                label_XY_List.append(data['large_ar_coords'][location])
        
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

    temp_image_dir = "temp-images"
    os.makedirs(temp_image_dir, exist_ok=True)

    for image in imageList:
        file_path = os.path.join(temp_image_dir, image.filename)
        image.save(file_path)
        image_paths.append(file_path)

    return image_paths

#create a list of image paths for each label
def createLabelImages(attachedLabels):
    images = []

    temp_image_dir = "temp-labels"
    os.makedirs(temp_image_dir, exist_ok=True)

    labelNumber = 1

    for label in attachedLabels:

        #Barcode label
        if "Barcode" in label['name']:
            image_filename = f"BARCODE{labelNumber}.png"
            image = Image.open(os.path.join('static/label-images', 'BARCODE.png')).resize((35, 15))
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
            image = Image.open(os.path.join('static/label-images', 'SPINE.png')).resize((26, 15))
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
            image = Image.open(os.path.join('static/label-images', 'SMALLAR.png')).resize((26, 15))
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
            image = Image.open(os.path.join('static/label-images', 'LEXILE.png')).resize((26, 15))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Genre label
        elif "Genre" in label['name']:
            image_filename = f"GENRE{labelNumber}.png"
            image = Image.open(os.path.join('static/label-images', 'GENRE.png')).resize((26, 15))
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
            image = Image.open(os.path.join('static/label-images', 'LARGEAR.png')).resize((25, 25))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        #Property label
        elif "Property" in label['name']:
            image_filename = f"PROPERTY{labelNumber}.png"
            image = Image.open(os.path.join('static/label-images', 'PROPERTY.png')).resize((40, 15))
            if "Top to Bottom" in label['direction']:
                image = image.rotate(-90, expand=True)
            elif "Bottom to Top" in label['direction']:
                image = image.rotate(90, expand=True)

            file_path = os.path.join(temp_image_dir, image_filename)
            image.save(file_path)
            images.append(file_path)

        labelNumber += 1

    return images
